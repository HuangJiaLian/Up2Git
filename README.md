# Up2Git - GitHub File Uploader

<p align="center">
  <img src="https://raw.githubusercontent.com/HuangJiaLian/Up2Git/refs/heads/main/icons/icon.svg" alt="Up2Git Logo" width="128" height="128">
</p>

<p align="left">
  <strong>A lightweight system tray application for Linux that provides seamless file and clipboard content uploads to GitHub repositories.</strong> 
  <img src="https://img.shields.io/badge/platform-Linux-blue" alt="Platform: Linux">
  <img src="https://img.shields.io/badge/python-3.11+-green" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT">
</p>

<p align="left">
  <img src="https://img.shields.io/badge/platform-Linux-blue" alt="Platform: Linux">
  <img src="https://img.shields.io/badge/python-3.11+-green" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT">
</p>

---

## Features

- **Clipboard Upload**: Upload images and text from clipboard with configurable hotkey
- **File Upload**: Upload any file type through integrated file dialog
- **Keyboard Shortcuts**: Global hotkey support (default: Alt+Shift+U)
- **System Tray Integration**: Minimal background operation with system tray interface
- **Auto-start Support**: Optional automatic startup with system boot
- **Configuration Management**: Simple settings dialog for GitHub credentials
- **Direct URL Generation**: Automatic generation of shareable GitHub raw URLs


## Use Cases

- **Markdown Documentation**: Instantly get URLs for images in your docs
- **Blog Posts**: Quick image hosting for articles and tutorials
- **GitHub Issues**: Upload screenshots and files effortlessly
- **Academic Papers**: Host diagrams and figures
- **Technical Documentation**: Quick file sharing for teams

## Installation

### Prerequisites

- **Linux** (tested on Linux Mint)
- **Python 3.11+**
- **Conda** (recommended) or pip

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HuangJiaLian/Up2Git.git
   cd Up2Git
   ```

2. **Create conda environment:**
   ```bash
   conda create -n up2git python=3.11
   conda activate up2git
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your GitHub credentials:**
   Create a `.env` file:
   ```bash
   nano .env
   ```
   Add your GitHub token and repository:
   ```env
   GITHUB_TOKEN=your_github_personal_access_token
   GITHUB_REPO=username/repository-name
   UPLOAD_FOLDER=uploads
   BASE_BRANCH=main
   ```

5. **Start the application:**
   ```bash
   python up2git_unified.py
   ```

## GitHub Token Setup

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Set expiration and select **"repo"** scope
4. Copy the generated token to your `.env` file

**Security Note**: Never share your GitHub token publicly. The `.env` file is already in `.gitignore`.

## Keyboard Shortcut Setup

Set up the global keyboard shortcut in your system:

1. **Make the trigger script executable:**
   ```bash
   chmod +x trigger_shortcut.sh
   ```

2. **Set up system keyboard shortcut:**
   - Go to System Settings → Keyboard → Shortcuts
   - Add custom shortcut with command: `/full/path/to/Up2Git/trigger_shortcut.sh`
   - Assign Alt+Shift+U (or your preferred combination)

### Auto-start Setup

Enable automatic startup with your system:
```bash
chmod +x setup_autostart.sh
./setup_autostart.sh
```

## Usage

### Quick Upload (Recommended)
1. Copy an image to clipboard (screenshot, copy image from browser, etc.)
2. Press `Alt+Shift+U`
3. Get the GitHub URL instantly in your clipboard!

### Manual Upload
- **Right-click** the system tray icon
- Select **"Upload File..."**
- Choose your file and get the URL

### System Tray Menu
- **Upload from Clipboard** - Same as `Alt+Shift+U`
- **Upload File...** - Open file dialog
- **Settings...** - Configure GitHub settings
- **Quit** - Close the application

## Project Structure

```
Up2Git/
├── up2git_unified.py          # Main application
├── trigger.py                 # Trigger file creator
├── trigger_shortcut.sh        # Keyboard shortcut wrapper
├── autostart.sh              # System startup script
├── setup_autostart.sh        # Autostart installer
├── up2git-autostart.desktop  # Desktop entry for autostart
├── icons/
│   └── icon.svg              # Application icon (transparent SVG)
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md               # This file
```

## Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_TOKEN` | Your GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `GITHUB_REPO` | Target repository (username/repo) | `username/my-files` |
| `UPLOAD_FOLDER` | Folder in repo for uploads | `uploads` |
| `BASE_BRANCH` | Target branch | `main` or `master` |

### Settings Dialog

Access via right-click menu → Settings to configure:
- GitHub Token
- Repository
- Upload Folder
- Branch

### Generated URLs

Files are uploaded to GitHub and accessible via:
```
https://raw.githubusercontent.com/username/repository/branch/folder/filename
```

Perfect for markdown: `![image](https://raw.githubusercontent.com/...)`

## Supported File Types

- **Images**: PNG, JPG, GIF, BMP (from clipboard or files)
- **Text**: Any text content from clipboard
- **Files**: Any file type through file dialog

## Troubleshooting

### Common Issues

**Icon not showing in system tray:**
- Restart the application: `python up2git_unified.py`
- Check if system tray is enabled in your desktop environment

**Upload fails:**
- Verify your GitHub token has `repo` scope
- Check if the repository exists and you have write access
- Check your `.env` file configuration

**Keyboard shortcut not working:**
- Ensure `trigger_shortcut.sh` is executable: `chmod +x trigger_shortcut.sh`
- Use absolute path in keyboard shortcut settings
- Verify the application is running

**Dependencies missing:**
- Run `pip install -r requirements.txt` in your conda environment
- Make sure you activated the conda environment: `conda activate up2git`

### Debug Mode

Run from terminal to see debug output:
```bash
conda activate up2git
python up2git_unified.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI
- Icons created with [Pillow](https://python-pillow.org/)
- GitHub API integration
- Inspired by the need for quick file sharing in documentation workflows

---

<p align="center">
  Made with ❤️ for the Linux community
</p>
