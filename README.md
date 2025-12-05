# Up2Git

<p align="center">
  <img src="https://raw.githubusercontent.com/HuangJiaLian/Up2Git/refs/heads/main/icons/icon.svg" alt="Up2Git Logo" width="128" height="128">
</p>

**Upload clipboard images to GitHub with a keyboard shortcut.**

Copy an image → Press `Alt+Shift+U` → Get a shareable URL!

## Install

```bash
sudo dpkg -i up2git_1.0.0_amd64.deb
```

## Setup

1. Run `up2git`
2. Right-click the tray icon → **Settings**
3. Enter your [GitHub token](https://github.com/settings/tokens) (select "repo" scope)
4. Enter your repository name (e.g., `username/my-repo`)
5. Click Save

## Set Keyboard Shortcut

1. Open **System Settings → Keyboard → Shortcuts**
2. Add a custom shortcut:
   - **Command**: `up2git --trigger`
   - **Shortcut**: `Alt+Shift+U`

## Usage

- **Quick upload**: Copy image, press `Alt+Shift+U`
- **Manual upload**: Right-click tray icon → Upload from Clipboard
- **View history**: Right-click tray icon → Recent Uploads

The URL is automatically copied to your clipboard!

## License

MIT
