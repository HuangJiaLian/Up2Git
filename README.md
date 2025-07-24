# Up2Git - GitHub File Uploader

<p align="center">
  <img src="icons/icon_cloud_upload.png" alt="Up2Git Logo" width="128" height="128">
</p>

<p align="center">
  <strong>A fast and elegant Linux application for uploading files to GitHub and getting shareable URLs instantly.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Linux-blue" alt="Platform: Linux">
  <img src="https://img.shields.io/badge/python-3.8+-green" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT">
</p>

---

## ✨ Features

- 🚀 **Lightning Fast**: Upload images and files with a single keyboard shortcut
- 📋 **Auto-Copy URLs**: File URLs are automatically copied to your clipboard
- ⌨️ **Global Hotkey**: Press `Alt+Shift+U` from anywhere to upload clipboard content
- 🎯 **System Tray**: Runs quietly in the background with an elegant cloud icon
- � **Smart Notifications**: Get notified when uploads complete
- 📁 **Multiple Sources**: Upload from clipboard, file dialog, or drag & drop file paths
- 🌐 **GitHub Integration**: Direct integration with your GitHub repositories
- 🎨 **Beautiful Icons**: Three professionally designed icon styles to choose from

## 🖼️ Perfect for:

- **Markdown Documentation**: Instantly get URLs for images in your docs
- **Blog Posts**: Quick image hosting for articles and tutorials
- **GitHub Issues**: Upload screenshots and files effortlessly
- **Academic Papers**: Host diagrams and figures
- **Technical Documentation**: Quick file sharing for teams

## 📦 Installation

### Prerequisites

- **Linux Mint** (or any Linux distribution with system tray support)
- **Python 3.8+**
- **Conda** (Miniconda or Anaconda)

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Up2Git.git
   cd Up2Git
   ```

2. **Run the automated setup:**
   ```bash
   chmod +x tools/setup.sh
   ./tools/setup.sh
   ```

3. **Configure your GitHub credentials:**
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

4. **Test your configuration:**
   ```bash
   conda activate up2git
   python tools/test_config.py
   ```

5. **Start the application:**
   ```bash
   ./up2git.sh
   ```

## 🔧 GitHub Token Setup

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Set expiration and select **"repo"** scope
4. Copy the generated token to your `.env` file

⚠️ **Security Note**: Never share your GitHub token publicly. The `.env` file is already in `.gitignore`.

## 🎹 Keyboard Shortcut Setup

Set up the global keyboard shortcut in your system:

1. Open **System Settings → Keyboard → Shortcuts → Custom Shortcuts**
2. Add a new shortcut:
   - **Name**: `Up2Git Upload`
   - **Command**: `/full/path/to/Up2Git/src/trigger_upload.sh`
   - **Shortcut**: `Alt+Shift+U`

## 🚀 Usage

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

## 📁 Project Structure

```
Up2Git/
├── src/
│   ├── main.py              # Main application
│   ├── run.sh              # Launcher script
│   └── trigger_upload.sh   # Global shortcut trigger
├── icons/
│   ├── icon_cloud_upload.png    # Cloud style icon
│   ├── icon_folder_upload.png   # Folder style icon
│   └── icon_upload_circle.png   # Circle style icon
├── tools/
│   ├── create_icons.py     # Icon generation script
│   ├── test_config.py      # Configuration tester
│   └── setup.sh           # Automated setup script
├── docs/
│   └── screenshots/        # Application screenshots
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🎨 Icon Styles

Choose from three beautiful icon styles:

| Cloud Upload | Folder Upload | Circle Upload |
|:------------:|:-------------:|:-------------:|
| ![Cloud](icons/icon_cloud_upload.png) | ![Folder](icons/icon_folder_upload.png) | ![Circle](icons/icon_upload_circle.png) |
| Default - Represents cloud storage | Professional folder style | GitHub-style circular design |

To change icons:
```bash
# Copy your preferred icon style to the main icon location
cp icons/icon_folder_upload.png icons/icon_cloud_upload.png  # Use folder style
cp icons/icon_upload_circle.png icons/icon_cloud_upload.png  # Use circle style
```

## 🔧 Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_TOKEN` | Your GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `GITHUB_REPO` | Target repository (username/repo) | `username/my-files` |
| `UPLOAD_FOLDER` | Folder in repo for uploads | `uploads` |
| `BASE_BRANCH` | Target branch | `main` or `master` |

### Generated URLs

Files are uploaded to GitHub and accessible via:
```
https://raw.githubusercontent.com/username/repository/branch/folder/filename
```

Perfect for markdown: `![image](https://raw.githubusercontent.com/...)`

## 🐛 Troubleshooting

### Common Issues

**Icon not showing in system tray:**
- Restart the application: `pkill -f "python.*main.py" && ./up2git.sh`
- Check if system tray is enabled in your desktop environment

**Upload fails:**
- Verify your GitHub token has `repo` scope
- Check if the repository exists and you have write access
- Run `python tools/test_config.py` to diagnose issues

**Keyboard shortcut not working:**
- Ensure `src/trigger_upload.sh` is executable: `chmod +x src/trigger_upload.sh`
- Use absolute path in keyboard shortcut settings
- Verify the application is running

**Notifications not showing:**
- Install `python3-dbus`: `sudo apt install python3-dbus`
- Notifications will fall back to system tray messages

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI
- Icons created with [Pillow](https://python-pillow.org/)
- GitHub API integration
- Inspired by the need for quick file sharing in documentation workflows

---

<p align="center">
  Made with ❤️ for the Linux community
</p>
