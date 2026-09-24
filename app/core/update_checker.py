import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, Tuple
from PySide6.QtCore import QThread, Signal

GITHUB_REPO = "raza6589his-collab/Appforge"
CURRENT_VERSION = "1.0.0"

def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parses a version string like 'v1.2.3' or '1.2.3' into a comparable tuple (1, 2, 3)"""
    cleaned = version_str.lstrip("vV").strip()
    parts = []
    for p in cleaned.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            break
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])

def fetch_latest_release(repo: str = GITHUB_REPO, timeout: int = 6) -> Optional[Dict[str, Any]]:
    """
    Fetches latest release info from GitHub API.
    Returns parsed dict or None if no release or error.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AppForge-Update-Checker",
            "Accept": "application/vnd.github.v3+json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data
    except urllib.error.HTTPError as e:
        # 404 means no releases yet
        return None
    except Exception:
        return None
    return None

class UpdateCheckerWorker(QThread):
    """
    Background worker thread to check for new AppForge releases on GitHub without blocking the GUI.
    """
    update_found = Signal(dict)    # Emits info dict if newer version available
    up_to_date = Signal(str)       # Emits current version if already latest
    check_error = Signal(str)      # Emits error string if network/api failed

    def __init__(self, current_version: str = CURRENT_VERSION, repo: str = GITHUB_REPO):
        super().__init__()
        self.current_version = current_version
        self.repo = repo

    def run(self):
        try:
            release_data = fetch_latest_release(self.repo)
            if not release_data:
                self.up_to_date.emit(self.current_version)
                return

            tag_name = release_data.get("tag_name", "")
            remote_ver = parse_version(tag_name)
            local_ver = parse_version(self.current_version)

            if remote_ver > local_ver:
                # Find direct download asset (.exe or .zip) if present
                assets = release_data.get("assets", [])
                download_url = release_data.get("html_url", f"https://github.com/{self.repo}/releases")
                for asset in assets:
                    name = asset.get("name", "").lower()
                    if name.endswith(".exe") or name.endswith(".zip") or name.endswith(".msi"):
                        download_url = asset.get("browser_download_url", download_url)
                        break

                info = {
                    "version": tag_name,
                    "title": release_data.get("name") or f"AppForge {tag_name}",
                    "notes": release_data.get("body", "تغییرات جدید و بهبودهای نرم‌افزار"),
                    "release_url": release_data.get("html_url", f"https://github.com/{self.repo}/releases"),
                    "download_url": download_url,
                    "published_at": release_data.get("published_at", "")
                }
                self.update_found.emit(info)
            else:
                self.up_to_date.emit(self.current_version)
        except Exception as e:
            self.check_error.emit(str(e))
