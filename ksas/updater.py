"""
KSAS Auto-Updater
Checks for updates from GitHub and prompts the user.
"""

import requests
import logging
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
import os

logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self, current_version, repo_url):
        self.current_version = current_version
        self.repo_url = repo_url
        # Convert repo URL to API URL
        # e.g., https://github.com/user/repo -> https://api.github.com/repos/user/repo/releases/latest
        self.api_url = None
        if "github.com" in repo_url:
            parts = repo_url.rstrip('/').split('/')
            if len(parts) >= 2:
                user = parts[-2]
                repo = parts[-1]
                self.api_url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"

    def check_for_updates(self):
        """
        Check for updates synchronously.
        Returns (is_available, latest_version, release_url)
        """
        if not self.api_url:
            logger.warning("Invalid GitHub Repo URL for updater.")
            return False, None, None

        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get('tag_name', '').lstrip('v')
                html_url = data.get('html_url', self.repo_url)
                
                if self._is_newer(latest_tag):
                    return True, latest_tag, html_url
            else:
                logger.warning(f"GitHub API returned {response.status_code}")
                
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
                    parent_window.after(0, lambda: self._prompt_update(parent_window, version, url))
        
        threading.Thread(target=_check, daemon=True).start()

    def _prompt_update(self, parent, version, url):
        """Show update dialog."""
        msg = f"A new version of KSAS is available!\n\nCurrent: {self.current_version}\nLatest: {version}\n\nDo you want to download it now?"
        if messagebox.askyesno("Update Available", msg, parent=parent):
            webbrowser.open(url)
