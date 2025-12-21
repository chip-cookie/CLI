"""
Git Utility Library
===================
Provides helper functions for git operations such as checking installation
and cloning repositories.
"""

import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from app.logger import logger


def is_git_installed() -> bool:
    """Check if git is installed and available in the PATH."""
    return shutil.which("git") is not None


def get_repo_name(url: str) -> str:
    """Extract repository name from a GitHub URL."""
    try:
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        name = path.split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name if name else "repo"
    except Exception:
        return "repo"


def clone_repo(url: str, target_dir: Path) -> bool:
    """Clone a git repository to the target directory.
    
    Args:
        url: The git repository URL.
        target_dir: The directory where the repo should be cloned. 
                    (The directory itself, not a parent)
    
    Returns:
        True if successful, False otherwise.
    """
    if not is_git_installed():
        logger.error("Git is not installed on this system.")
        return False

    try:
        if target_dir.exists() and any(target_dir.iterdir()):
             logger.warning(f"Target directory {target_dir} is not empty.")
             # We proceed, but git clone might fail if dir is not empty.
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cloning {url} into {target_dir}...")
        subprocess.run(
            ["git", "clone", url, str(target_dir)],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Clone successful.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during cloning: {e}")
        return False
