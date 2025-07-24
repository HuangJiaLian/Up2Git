#!/usr/bin/env python3
"""
Up2Git - GitHub File Uploader
Simple application with system tray that uploads clipboard content to GitHub
"""

import os
import sys
import base64
import time
from datetime import datetime

# GUI and system libraries
try:
    import requests
    import pyperclip
    from PIL import Image
    from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QMessageBox, 
                                QFileDialog, QDialog, QVBoxLayout, QLineEdit, 
                                QFormLayout, QPushButton, QLabel, QHBoxLayout)
    from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QFileSystemWatcher
    from PyQt5.QtGui import QIcon, QPixmap
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
        self.accept()

class Up2GitApp:
    """Main application class"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.uploader = None
        self.tray_icon = None
        self.settings = self.load_settings()
        self.setup_github_uploader()
        self.setup_tray()
        self.setup_file_watcher()
        self.setup_global_hotkey()
    
    def load_settings(self):
        """Load settings from environment variables or .env file"""
        # Try to load from .env file
        env_path = '.env'
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"Loaded .env from: {env_path}")
        else:
            print(f"No .env file found at: {os.path.abspath(env_path)}")
        
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
        menu = QMenu()
        
        upload_clipboard_action = menu.addAction("Upload from Clipboard")
        upload_clipboard_action.triggered.connect(self.upload_from_clipboard)
        
        upload_file_action = menu.addAction("Upload File...")
        upload_file_action.triggered.connect(self.upload_file_dialog)
        
        menu.addSeparator()
        
        settings_action = menu.addAction("Settings...")
        settings_action.triggered.connect(self.show_settings)
        
        menu.addSeparator()
        
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.app.quit)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
        # Set tooltip
        self.tray_icon.setToolTip("Up2Git - GitHub File Uploader")
    
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
        
        # Try to get image from clipboard
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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            print(f"Uploading image: {filename}")
            self.upload_content(filename, content)
        else:
            # Try text content
            text = clipboard.text()
            if text:
                print(f"Found text in clipboard: {len(text)} characters")
                # Save as text file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"text_{timestamp}.txt"
                content = text.encode('utf-8')
                print(f"Uploading text: {filename}")
                self.upload_content(filename, content)
            else:
                print("No image or text found in clipboard")
                self.show_message("Info", "No image or text found in clipboard")
    
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
        
        # Start upload in worker thread
        self.worker = UploadWorker(self.uploader, filename, content)
        self.worker.finished.connect(self.upload_finished)
        self.worker.error.connect(self.upload_error)
        self.worker.start()
        
        # Show uploading message
        self.show_message("Uploading", f"Uploading {filename}...")
    
    def upload_finished(self, url):
        """Handle successful upload"""
        # Copy URL to clipboard
        pyperclip.copy(url)
        
        # Show notification
        self.show_message("Success", f"✅ Uploaded! URL copied:\n{url}")
    
    def upload_error(self, error):
        """Handle upload error"""
        self.show_message("Error", f"Upload failed: {error}")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.settings)
        if dialog.exec_() == QDialog.Accepted:
            self.setup_github_uploader()
            self.show_message("Settings", "Settings saved successfully!")
    
    def show_message(self, title, message):
        """Show notification message"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Up2Git",
                timeout=3
            )
        except:
            # Fallback to tray message
            if self.tray_icon:
                self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 3000)
    
    def run(self):
        """Run the application"""
        # Set application properties
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("Up2Git")
        
        return self.app.exec_()

def main():
    """Main entry point"""
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
