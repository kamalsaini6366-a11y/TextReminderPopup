import tkinter as tk
from tkinter import ttk, messagebox
import json, os, sys
from datetime import datetime

APP_NAME = "Text Reminder Popup"
CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "TextReminderPopup")
CONFIG_FILE = os.path.join(CONFIG_DIR, "reminders.json")

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("650x520")
        self.root.minsize(560, 430)
        self.root.configure(padx=14, pady=14)
        self.reminders = []
        self.after_ids = {}
        self._build()
        self._load()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(500, self.schedule_all)

    def _build(self):
        ttk.Label(self.root, text="Text Reminder Popup", font=("Segoe UI", 17, "bold")).pack(anchor="w")
        ttk.Label(self.root, text="Type a message, choose how often it should pop up, then click Add Reminder.").pack(anchor="w", pady=(2, 12))
        ttk.Label(self.root, text="Message").pack(anchor="w")
        self.message = tk.Text(self.root, height=5, wrap="word", font=("Segoe UI", 10))
        self.message.pack(fill="x", pady=(4, 10))
        row = ttk.Frame(self.root)
        row.pack(fill="x", pady=(0, 10))
        ttk.Label(row, text="Repeat every").pack(side="left")
        self.interval = tk.StringVar(value="30")
        ttk.Entry(row, textvariable=self.interval, width=7).pack(side="left", padx=(8, 5))
        self.unit = tk.StringVar(value="minutes")
        ttk.Combobox(row, textvariable=self.unit, values=("seconds", "minutes", "hours", "days"), state="readonly", width=10).pack(side="left")
        self.start_now = tk.BooleanVar(value=False)
        ttk.Checkbutton(row, text="Show first popup immediately", variable=self.start_now).pack(side="left", padx=12)
        ttk.Button(row, text="Add Reminder", command=self.add).pack(side="right")
        ttk.Label(self.root, text="Saved reminders (select one to remove)").pack(anchor="w")
        columns = ("message", "interval", "next")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10, selectmode="browse")
        self.tree.heading("message", text="Message")
        self.tree.heading("interval", text="Repeat")
        self.tree.heading("next", text="Next popup")
        self.tree.column("message", width=330)
        self.tree.column("interval", width=95, anchor="center")
        self.tree.column("next", width=140, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=(5, 8))
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Remove Selected", command=self.remove).pack(side="left")
        ttk.Button(bottom, text="Test Popup", command=self.test_popup).pack(side="left", padx=8)
        ttk.Label(bottom, text="Keep this app running for reminders.").pack(side="right")

    def _seconds(self, amount, unit):
        factor = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}[unit]
        return amount * factor

    def add(self):
        msg = self.message.get("1.0", "end").strip()
        try:
            amount = int(self.interval.get().strip())
            if amount < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid interval", "Enter a whole number greater than zero.")
            return
        if not msg:
            messagebox.showerror("Message required", "Type some content first.")
            return
        seconds = self._seconds(amount, self.unit.get())
        now = datetime.now().timestamp()
        item = {"id": str(int(now * 1000)), "message": msg, "amount": amount, "unit": self.unit.get(),
                "interval_seconds": seconds, "next_time": now if self.start_now.get() else now + seconds}
        self.reminders.append(item)
        self.message.delete("1.0", "end")
        self._save()
        self.refresh()
        self.schedule(item)

    def remove(self):
        sel = self.tree.selection()
        if not sel:
            return
        rid = sel[0]
        self.cancel(rid)
        self.reminders = [r for r in self.reminders if r["id"] != rid]
        self._save()
        self.refresh()

    def refresh(self):
        for x in self.tree.get_children():
            self.tree.delete(x)
        for r in self.reminders:
            next_time = datetime.fromtimestamp(r["next_time"]).strftime("%d %b %H:%M:%S")
            interval = f'{r["amount"]} {r["unit"]}'
            msg = r["message"].replace("\n", " ")
            if len(msg) > 60: msg = msg[:57] + "..."
            self.tree.insert("", "end", iid=r["id"], values=(msg, interval, next_time))

    def schedule_all(self):
        now = datetime.now().timestamp()
        for r in self.reminders:
            if r["next_time"] < now:
                r["next_time"] = now + r["interval_seconds"]
            self.schedule(r)
        self._save()
        self.refresh()

    def schedule(self, item):
        self.cancel(item["id"])
        delay = max(0, int((item["next_time"] - datetime.now().timestamp()) * 1000))
        self.after_ids[item["id"]] = self.root.after(delay, lambda rid=item["id"]: self.fire(rid))

    def cancel(self, rid):
        aid = self.after_ids.pop(rid, None)
        if aid:
            try: self.root.after_cancel(aid)
            except tk.TclError: pass

    def fire(self, rid):
        item = next((r for r in self.reminders if r["id"] == rid), None)
        if not item: return
        self.show_popup(item["message"])
        item["next_time"] = datetime.now().timestamp() + item["interval_seconds"]
        self._save()
        self.refresh()
        self.schedule(item)

    def show_popup(self, msg):
        win = tk.Toplevel(self.root)
        win.title("Reminder")
        win.attributes("-topmost", True)
        win.geometry("440x220")
        win.resizable(True, True)
        frame = ttk.Frame(win, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Reminder", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))
        text = tk.Text(frame, wrap="word", height=5, font=("Segoe UI", 11), relief="flat")
        text.pack(fill="both", expand=True)
        text.insert("1.0", msg)
        text.configure(state="disabled")
        ttk.Button(frame, text="Dismiss", command=win.destroy).pack(anchor="e", pady=(8, 0))
        win.lift()
        win.focus_force()
        win.bell()

    def test_popup(self):
        msg = self.message.get("1.0", "end").strip()
        if not msg:
            sel = self.tree.selection()
            if sel:
                item = next((r for r in self.reminders if r["id"] == sel[0]), None)
                msg = item["message"] if item else ""
        if not msg:
            messagebox.showinfo("Test Popup", "Type a message or select a saved reminder first.")
            return
        self.show_popup(msg)

    def _save(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.reminders, f, ensure_ascii=False, indent=2)
        except OSError as e:
            messagebox.showerror("Save error", str(e))

    def _load(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.reminders = data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            self.reminders = []
        # If a reminder was missed while app was closed, show it shortly after launch.
        now = datetime.now().timestamp()
        for r in self.reminders:
            if r.get("next_time", now) < now:
                r["next_time"] = now + 3
        self.refresh()

    def close(self):
        self._save()
        for rid in list(self.after_ids):
            self.cancel(rid)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    ReminderApp(root)
    root.mainloop()
