"""
KSAS Auto-Updater
Checks for updates from GitHub and prompts the user.
"""

import requests
import logging
import threading
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self, current_version, repo_url):
        self.current_version = current_version
        self.repo_url = repo_url
        # Construct raw URL for version.txt
        # e.g., https://github.com/user/repo.git -> https://raw.githubusercontent.com/user/repo/main/version.txt
        self.raw_url = None
        if "github.com" in repo_url:
            clean_url = repo_url.replace('.git', '').rstrip('/')
            parts = clean_url.split('/')
            if len(parts) >= 2:
                user = parts[-2]
                repo = parts[-1]
                self.raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/main/version.txt"

    def check_for_updates(self):
        """
        Check for updates synchronously by reading version.txt from GitHub.
        Returns (is_available, latest_version, release_url)
        """
        if not self.raw_url:
            logger.warning("Invalid GitHub Repo URL for updater.")
            return False, None, None

        try:
            response = requests.get(self.raw_url, timeout=5)
            if response.status_code == 200:
                latest_version = response.text.strip()
                
                if self._is_newer(latest_version):
                    return True, latest_version, self.repo_url
            else:
                logger.warning(f"GitHub raw content returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            
        return False, None, None

    def _is_newer(self, latest_version):
        """Compare semantic versions."""
        try:
            current_parts = [int(x) for x in self.current_version.split('.')]
            latest_parts = [int(x) for x in latest_version.split('.')]
            
            return latest_parts > current_parts
        except:
            return False

    def check_async(self, parent_window=None):
        """Run check in background and prompt if update found."""
        def _check():
            available, version, url = self.check_for_updates()
            if available:
                # Schedule UI update on main thread
                if parent_window:
                    parent_window.after(0, lambda: self._prompt_update(parent_window, version))
        
        threading.Thread(target=_check, daemon=True).start()

    def _prompt_update(self, parent, version):
        """Show update dialog and execute git pull if accepted."""
        msg = f"A new version of KSAS is available!\n\nCurrent: {self.current_version}\nLatest: {version}\n\nDo you want to update now?\n(The application will close)"
        
        if messagebox.askyesno("Update Available", msg, parent=parent):
            self.update_now(parent)

    def update_now(self, parent):
        """Execute git pull and restart/exit."""
        try:
            # Check if git is available
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            
            # Execute pull
            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Update Successful", 
                                  "Update completed successfully!\n\nPlease restart the application.",
                                  parent=parent)
                sys.exit(0)
            else:
                logger.error(f"Git pull failed: {result.stderr}")
                messagebox.showerror("Update Failed", 
                                   f"Git pull failed:\n{result.stderr}\n\nPlease update manually.",
                                   parent=parent)
                
        except FileNotFoundError:
            messagebox.showerror("Error", "Git is not installed or not in PATH.", parent=parent)
        except Exception as e:
            logger.error(f"Update error: {e}")
            messagebox.showerror("Error", f"An error occurred during update:\n{e}", parent=parent)
