#!/usr/bin/env python3
"""
Up2Git - GitHub File Uploader
Simple application with system tray that uploads clipboard content to GitHub
"""

import os
import sys
import base64
import time
import json
from datetime import datetime
from pathlib import Path

# Suppress Qt session management warning
os.environ['SESSION_MANAGER'] = ''

# GUI and system libraries
try:
    import requests
    import pyperclip
    from PIL import Image
    from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QMessageBox, 
                                QFileDialog, QDialog, QVBoxLayout, QLineEdit, 
                                QFormLayout, QPushButton, QLabel, QHBoxLayout,
                                QWidget, QGridLayout, QWidgetAction, QFrame)
    from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QFileSystemWatcher, QSize, QByteArray
    from PyQt5.QtGui import QIcon, QPixmap, QImage, QCursor
    from plyer import notification
    from dotenv import load_dotenv
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"Warning: Some dependencies not available: {e}")

class GitHubUploader:
    """Handle GitHub API operations for file uploads"""
    
    def __init__(self, token, repo, branch="main"):
        self.token = token
        self.repo = repo
        self.branch = branch
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def upload_file(self, file_path, content, folder="uploads"):
        """Upload file to GitHub repository"""
        url = f"https://api.github.com/repos/{self.repo}/contents/{folder}/{file_path}"
        
        # Check if file already exists
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                sha = response.json()['sha']
            else:
                sha = None
        except:
            sha = None
        
        # Prepare data for upload
        data = {
            "message": f"Upload {file_path}",
            "content": base64.b64encode(content).decode('utf-8'),
            "branch": self.branch
        }
        
        if sha:
            data["sha"] = sha
        
        # Upload file
        response = requests.put(url, headers=self.headers, json=data)
        
        if response.status_code in [200, 201]:
            return f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{folder}/{file_path}"
        else:
            raise Exception(f"Upload failed: {response.status_code} - {response.text}")

class UploadWorker(QThread):
    """Worker thread for file uploads"""
    finished = pyqtSignal(str)  # URL
    error = pyqtSignal(str)     # Error message
    
    def __init__(self, uploader, file_path, content):
        super().__init__()
        self.uploader = uploader
        self.file_path = file_path
        self.content = content
    
    def run(self):
        try:
            url = self.uploader.upload_file(self.file_path, self.content)
            self.finished.emit(url)
        except Exception as e:
            self.error.emit(str(e))

class SettingsDialog(QDialog):
    """Settings dialog for GitHub configuration"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Up2Git Settings")
        self.setModal(True)
        self.resize(650, 240)  # Increased width to 650px and height to 240px
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Form layout for settings
        form_layout = QFormLayout()
        
        self.token_input = QLineEdit(self.settings.get('token', ''))
        self.token_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("GitHub Token:", self.token_input)
        
        self.repo_input = QLineEdit(self.settings.get('repo', ''))
        form_layout.addRow("Repository (user/repo):", self.repo_input)
        
        self.folder_input = QLineEdit(self.settings.get('folder', 'uploads'))
        form_layout.addRow("Upload Folder:", self.folder_input)
        
        self.branch_input = QLineEdit(self.settings.get('branch', 'main'))
        form_layout.addRow("Branch:", self.branch_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_settings(self):
        self.settings['token'] = self.token_input.text()
        self.settings['repo'] = self.repo_input.text()
        self.settings['folder'] = self.folder_input.text()
        self.settings['branch'] = self.branch_input.text()
        
        # Persist settings to config file
        self._save_to_file()
        self.accept()
    
    def _save_to_file(self):
        """Save settings to persistent config file"""
        import pathlib
        
        # Use XDG config directory for proper Linux standards
        config_dir = pathlib.Path.home() / '.config' / 'up2git'
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / 'config.env'
        
        with open(config_file, 'w') as f:
            f.write(f"GITHUB_TOKEN={self.settings['token']}\n")
            f.write(f"GITHUB_REPO={self.settings['repo']}\n")
            f.write(f"UPLOAD_FOLDER={self.settings['folder']}\n")
            f.write(f"BASE_BRANCH={self.settings['branch']}\n")
        
        print(f"Settings saved to: {config_file}")

class Up2GitApp:
    """Main application class"""
    
    MAX_HISTORY_ITEMS = 10
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.uploader = None
        self.tray_icon = None
        self.history = []
        self.settings = self.load_settings()
        self.load_history()
        self.setup_github_uploader()
        self.setup_tray()
        self.setup_file_watcher()
        self.setup_global_hotkey()
    
    def get_history_file(self):
        """Get the path to the history file"""
        config_dir = Path.home() / '.config' / 'up2git'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'history.json'
    
    def load_history(self):
        """Load upload history from file"""
        history_file = self.get_history_file()
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.history = json.load(f)
                print(f"Loaded {len(self.history)} history items")
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
    
    def save_history(self):
        """Save upload history to file"""
        history_file = self.get_history_file()
        try:
            with open(history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def add_to_history(self, filename, url, thumbnail_data=None):
        """Add an upload to history"""
        entry = {
            'filename': filename,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'is_image': filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')),
            'thumbnail': thumbnail_data  # Base64 encoded thumbnail for images
        }
        
        # Add to beginning of list
        self.history.insert(0, entry)
        
        # Keep only MAX_HISTORY_ITEMS
        if len(self.history) > self.MAX_HISTORY_ITEMS:
            self.history = self.history[:self.MAX_HISTORY_ITEMS]
        
        self.save_history()
        self.update_history_menu()
    
    def create_thumbnail(self, image_data, size=64):
        """Create a thumbnail from image data, returns base64 encoded PNG"""
        try:
            from io import BytesIO
            img = Image.open(BytesIO(image_data))
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save to bytes
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    def load_settings(self):
        """Load settings from config file or environment variables"""
        import pathlib
        
        # First, try to load from user config file (~/.config/up2git/config.env)
        config_file = pathlib.Path.home() / '.config' / 'up2git' / 'config.env'
        if config_file.exists():
            load_dotenv(str(config_file))
            print(f"Loaded config from: {config_file}")
        else:
            # Fallback to .env file in current directory
            env_path = '.env'
            if os.path.exists(env_path):
                load_dotenv(env_path)
                print(f"Loaded .env from: {env_path}")
            else:
                print(f"No config file found. Settings dialog will open.")
        
        # Get settings from environment
        settings = {
            'token': os.getenv('GITHUB_TOKEN', ''),
            'repo': os.getenv('GITHUB_REPO', ''),
            'folder': os.getenv('UPLOAD_FOLDER', 'uploads'),
            'branch': os.getenv('BASE_BRANCH', 'main'),
            'hotkey': os.getenv('GLOBAL_HOTKEY', '<alt>+<shift>+u')
        }
        
        print(f"Settings loaded: repo={settings['repo']}, folder={settings['folder']}, branch={settings['branch']}")
        print(f"Token loaded: {'Yes' if settings['token'] else 'No'}")
        
        return settings
    
    def setup_github_uploader(self):
        """Initialize GitHub uploader if settings are available"""
        if self.settings['token'] and self.settings['repo']:
            try:
                self.uploader = GitHubUploader(
                    self.settings['token'],
                    self.settings['repo'],
                    self.settings['branch']
                )
            except Exception as e:
                self.show_message("Error", f"Failed to setup GitHub uploader: {e}")
    
    def setup_tray(self):
        """Setup system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Up2Git", "System tray is not available!")
            sys.exit(1)
        
        # Create tray icon - try embedded first, then fallback
        try:
            # Try to load icon from embedded resource
            icon_data = self.get_embedded_icon()
            if icon_data:
                pixmap = QPixmap()
                pixmap.loadFromData(icon_data)
                icon = QIcon(pixmap)
            else:
                # Fallback to simple colored icon
                pixmap = QPixmap(64, 64)
                pixmap.fill(Qt.blue)
                icon = QIcon(pixmap)
        except Exception:
            # Final fallback
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.blue)
            icon = QIcon(pixmap)
        
        self.tray_icon = QSystemTrayIcon(icon, self.app)
        
        # Create context menu
        self.menu = QMenu()
        
        upload_clipboard_action = self.menu.addAction("Upload from Clipboard")
        upload_clipboard_action.triggered.connect(self.upload_from_clipboard)
        
        upload_file_action = self.menu.addAction("Upload File...")
        upload_file_action.triggered.connect(self.upload_file_dialog)
        
        self.menu.addSeparator()
        
        # History submenu
        self.history_menu = self.menu.addMenu("Recent Uploads")
        self.update_history_menu()
        
        self.menu.addSeparator()
        
        settings_action = self.menu.addAction("Settings...")
        settings_action.triggered.connect(self.show_settings)
        
        self.menu.addSeparator()
        
        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self.app.quit)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
        
        # Set tooltip
        self.tray_icon.setToolTip("Up2Git - GitHub File Uploader")
    
    def update_history_menu(self):
        """Update the history submenu with recent uploads"""
        if not hasattr(self, 'history_menu'):
            return
        
        self.history_menu.clear()
        
        if not self.history:
            empty_action = self.history_menu.addAction("No recent uploads")
            empty_action.setEnabled(False)
            return
        
        # Create a widget for the grid layout
        for i, entry in enumerate(self.history[:self.MAX_HISTORY_ITEMS]):
            action = self.history_menu.addAction(self._create_history_icon(entry), 
                                                  self._truncate_filename(entry['filename']))
            action.setToolTip(f"{entry['filename']}\n{entry['url']}\n{entry['timestamp'][:10]}")
            # Use lambda with default argument to capture the URL correctly
            action.triggered.connect(lambda checked, url=entry['url']: self.copy_url_to_clipboard(url))
        
        # Add separator and clear option
        self.history_menu.addSeparator()
        clear_action = self.history_menu.addAction("Clear History")
        clear_action.triggered.connect(self.clear_history)
    
    def _create_history_icon(self, entry):
        """Create an icon for a history entry (thumbnail for images, file icon for others)"""
        if entry.get('is_image') and entry.get('thumbnail'):
            try:
                # Decode base64 thumbnail
                thumb_data = base64.b64decode(entry['thumbnail'])
                pixmap = QPixmap()
                pixmap.loadFromData(thumb_data)
                if not pixmap.isNull():
                    return QIcon(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                print(f"Error loading thumbnail: {e}")
        
        # Default file icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        return QIcon(pixmap)
    
    def _truncate_filename(self, filename, max_length=25):
        """Truncate filename for display"""
        if len(filename) <= max_length:
            return filename
        return filename[:max_length-3] + "..."
    
    def copy_url_to_clipboard(self, url):
        """Copy URL to clipboard and show notification"""
        pyperclip.copy(url)
        self.show_message("Copied", "URL copied to clipboard")
    
    def clear_history(self):
        """Clear upload history"""
        self.history = []
        self.save_history()
        self.update_history_menu()
        self.show_message("History", "Upload history cleared")
    
    def get_embedded_icon(self):
        """Get embedded icon data or load from file"""
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Use the main icon with transparent background
            icon_path = os.path.join(script_dir, "icons", "icon.svg")
            
            if os.path.exists(icon_path):
                with open(icon_path, 'rb') as f:
                    return f.read()
            else:
                # Try alternative paths including fallbacks
                alt_paths = [
                    os.path.join(script_dir, "icons", "icon_variant2_improved.svg"),
                    os.path.join(script_dir, "icons", "icon_variant2_improved.png"),
                    os.path.join(script_dir, "icons", "icon_variant2.svg"),
                    os.path.join(script_dir, "icons", "icon_variant2.png"),
                    os.path.join(script_dir, "icon.svg"),
                    os.path.join(os.getcwd(), "icons", "icon.svg"),
                    os.path.join(os.getcwd(), "icon.svg"),
                    # Fallback to old icon if nothing found
                    os.path.join(script_dir, "icons", "icon_cloud_upload.png")
                ]
                
                for path in alt_paths:
                    if os.path.exists(path):
                        with open(path, 'rb') as f:
                            return f.read()
        except Exception as e:
            print(f"Error loading icon: {e}")
        
        return None
    
    def setup_file_watcher(self):
        """Setup file system watcher for trigger file"""
        self.watcher = QFileSystemWatcher()
        # Use fixed location for trigger file to work with PyInstaller
        self.trigger_file = "/tmp/.upload_trigger"
        
        print(f"Watching for trigger file: {self.trigger_file}")
        
        # Watch tmp directory for trigger file
        self.watcher.directoryChanged.connect(self.check_trigger)
        self.watcher.addPath("/tmp")
        
        # Also check periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_trigger)
        self.timer.start(1000)  # Check every second
    
    def check_trigger(self):
        """Check if trigger file exists and process upload"""
        if os.path.exists(self.trigger_file):
            print("Trigger file detected! Processing upload...")
            try:
                os.remove(self.trigger_file)
                print("Trigger file removed, starting clipboard upload...")
                self.upload_from_clipboard()
            except Exception as e:
                print(f"Error removing trigger file: {e}")
                pass  # Ignore errors removing trigger file
    
    def setup_global_hotkey(self):
        """Setup global hotkey for triggering uploads"""
        print("🔧 Global hotkey setup...")
        print("ℹ️  Using file-based trigger system")
        print("🔗 To set up keyboard shortcut:")
        print("   1. Go to System Settings > Keyboard > Shortcuts")
        print("   2. Create custom shortcut with command:")
        print(f"      {os.getcwd()}/trigger_shortcut.sh")
        print("   3. Assign Alt+Shift+U (or any key combination)")
        print("✅ File-based trigger system is ready!")
    
    def upload_from_clipboard(self):
        """Upload content from clipboard"""
        print("upload_from_clipboard called")
        
        if not self.uploader:
            print("Error: No uploader configured")
            self.show_message("Error", "GitHub uploader not configured. Please check settings.")
            return
        
        print("Uploader is configured, checking clipboard...")
        
        # Get clipboard content
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        # Try to get image from clipboard first
        pixmap = clipboard.pixmap()
        if not pixmap.isNull():
            print("Found image in clipboard")
            # Convert pixmap to bytes using QBuffer
            from PyQt5.QtCore import QBuffer, QIODevice
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, 'PNG')
            content = buffer.data().data()
            
            # Generate filename
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            print(f"Uploading image: {filename}")
            self.upload_content(filename, content)
        elif mime_data.hasUrls():
            # Handle files copied from file manager (e.g., Ctrl+C on a file)
            urls = mime_data.urls()
            if urls:
                file_url = urls[0]
                if file_url.isLocalFile():
                    local_path = file_url.toLocalFile()
                    print(f"Found file URL in clipboard: {local_path}")
                    if os.path.isfile(local_path):
                        try:
                            with open(local_path, 'rb') as f:
                                content = f.read()
                            # Add timestamp prefix to filename
                            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
                            original_filename = os.path.basename(local_path)
                            filename = f"{timestamp}_{original_filename}"
                            print(f"Uploading file: {filename}")
                            self.upload_content(filename, content)
                        except Exception as e:
                            print(f"Error reading file: {e}")
                            self.show_message("Error", f"Failed to read file: {e}")
                    else:
                        print(f"File not found: {local_path}")
                        self.show_message("Error", f"File not found: {local_path}")
                else:
                    print("Only local files are supported")
                    self.show_message("Error", "Only local files are supported!")
            else:
                print("No valid file URL in clipboard")
                self.show_message("Error", "No valid file URL in clipboard!")
        elif mime_data.hasText():
            # Try text content (fallback for plain text paths)
            text = clipboard.text().strip()
            if os.path.isfile(text):
                # It's a file path as plain text
                print(f"Found file path in clipboard: {text}")
                try:
                    with open(text, 'rb') as f:
                        content = f.read()
                    filename = os.path.basename(text)
                    print(f"Uploading file: {filename}")
                    self.upload_content(filename, content)
                except Exception as e:
                    print(f"Error reading file: {e}")
                    self.show_message("Error", f"Failed to read file: {e}")
            else:
                print(f"Found text in clipboard: {len(text)} characters")
                # Save as text file
                timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
                filename = f"text_{timestamp}.txt"
                content = text.encode('utf-8')
                print(f"Uploading text: {filename}")
                self.upload_content(filename, content)
        else:
            print("No image, file, or text found in clipboard")
            self.show_message("Info", "No image, file, or text found in clipboard")
    
    def upload_file_dialog(self):
        """Show file dialog and upload selected file"""
        if not self.uploader:
            self.show_message("Error", "GitHub uploader not configured. Please check settings.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select file to upload",
            "",
            "All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                filename = os.path.basename(file_path)
                self.upload_content(filename, content)
            except Exception as e:
                self.show_message("Error", f"Failed to read file: {e}")
    
    def upload_content(self, filename, content):
        """Upload content using worker thread"""
        folder = self.settings.get('folder', 'uploads')
        print(f"upload_content called with filename: {filename}, content size: {len(content)}")
        
        # Store content info for history (after upload completes)
        self._pending_upload = {
            'filename': filename,
            'content': content,
            'is_image': filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))
        }
        
        # Start upload in worker thread
        self.worker = UploadWorker(self.uploader, filename, content)
        self.worker.finished.connect(self.upload_finished)
        self.worker.error.connect(self.upload_error)
        self.worker.start()
        print("Upload worker started")
        
        # Show uploading message
        # self.show_message("Uploading", f"Uploading {filename}...")
    
    def upload_finished(self, url):
        """Handle successful upload"""
        print(f"upload_finished called with url: {url}")
        
        # Add to history
        if hasattr(self, '_pending_upload') and self._pending_upload:
            thumbnail = None
            if self._pending_upload['is_image']:
                thumbnail = self.create_thumbnail(self._pending_upload['content'])
            
            self.add_to_history(
                self._pending_upload['filename'],
                url,
                thumbnail
            )
            self._pending_upload = None
        
        # Copy URL to clipboard
        pyperclip.copy(url)
        
        # Show notification (avoid newlines and special chars that crash notify-send)
        self.show_message("Upload Success", "URL copied to clipboard")
    
    def upload_error(self, error):
        """Handle upload error"""
        print(f"upload_error called: {error}")
        self.show_message("Error", f"Upload failed: {error}")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.settings)
        if dialog.exec_() == QDialog.Accepted:
            self.setup_github_uploader()
            self.show_message("Settings", "Settings saved successfully!")
    
    def show_message(self, title, message):
        """Show notification message using Qt tray icon (most reliable in bundled apps)"""
        # Use Qt's built-in tray notification - works reliably in PyInstaller bundles
        try:
            if self.tray_icon:
                # Use NoIcon to avoid the default "i" icon, our tray icon will be shown
                self.tray_icon.showMessage(title, message, QSystemTrayIcon.NoIcon, 5000)
                print(f"Tray notification shown: {title}")
                return
        except Exception as e:
            print(f"Tray message failed: {e}")
        
        # Fallback: try notify-send via subprocess (may crash in PyInstaller)
        import subprocess
        import shutil
        
        notify_send = shutil.which('notify-send') or '/usr/bin/notify-send'
        try:
            # Run in a separate process to avoid crashes affecting main app
            subprocess.Popen(
                [notify_send, title, message],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"notify-send failed: {e}")
    
    def run(self):
        """Run the application"""
        # Set application properties
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("Up2Git")
        
        return self.app.exec_()

def main():
    """Main entry point"""
    # Handle --trigger flag (for keyboard shortcut integration)
    if '--trigger' in sys.argv:
        trigger_file = "/tmp/.upload_trigger"
        try:
            from pathlib import Path
            Path(trigger_file).write_text(str(time.time()))
            return 0
        except Exception as e:
            print(f"Error creating trigger: {e}")
            return 1
    
    # Handle --help flag
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Up2Git - GitHub File Uploader")
        print()
        print("Usage:")
        print("  up2git           Start the system tray application")
        print("  up2git --trigger Trigger upload from clipboard (for keyboard shortcuts)")
        print("  up2git --help    Show this help message")
        print()
        print("Set your system keyboard shortcut to run: up2git --trigger")
        return 0
    
    # Check if dependencies are available
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not available")
        print("Please install dependencies: pip install -r requirements.txt")
        return 1
    
    # Run GUI application
    try:
        app = Up2GitApp()
        return app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
