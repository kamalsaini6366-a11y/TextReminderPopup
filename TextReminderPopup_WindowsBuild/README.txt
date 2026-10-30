TEXT REMINDER POPUP — BUILD A WINDOWS EXE WITHOUT INSTALLING PYTHON ON YOUR PC

This package lets GitHub build the Windows .exe in its cloud machine. You do not install Python on your own computer. You do need a GitHub account and a web browser.

1. Open https://github.com/new and create a repository named TextReminderPopup (a public repository is easiest for a beginner; do not upload private data).
2. Upload the files from this folder, including the hidden .github/workflows/build-windows-exe.yml file. Easiest: extract this ZIP, then use GitHub's Add file > Upload files. Make sure the workflow path is exactly .github/workflows/build-windows-exe.yml.
3. Open the repository's Actions tab.
4. Select “Build Windows EXE” in the left menu and click “Run workflow”. If you don't see it, first commit/upload the workflow file to the main branch and refresh.
5. Wait for the workflow to finish successfully.
6. Open the completed workflow run and download the artifact named “TextReminderPopup-Windows-EXE”.
7. Extract the downloaded artifact ZIP. Run TextReminderPopup.exe by double-clicking it.

The Python runtime and PyInstaller are installed only on GitHub's temporary Windows build machine, not on your PC.

Notes:
- This requires internet access and a GitHub account. GitHub may show a SmartScreen warning for an unsigned EXE; only run the EXE you built from this source and follow your organization's security rules.
- Keep the app open for reminders to fire. This version does not automatically start with Windows.
- Reminder data is saved under %APPDATA%\TextReminderPopup\reminders.json.
