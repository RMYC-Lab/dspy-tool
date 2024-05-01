from dataclasses import dataclass, field
from typing import List
from pathlib import Path
from os.path import expandvars

from dspy_tool.cli.utils.config.config import Config

LocalLow = Path.home() / "AppData" / "LocalLow"


def get_desktop():
    import winreg

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders",
        )
        return expandvars(winreg.QueryValueEx(key, "Desktop")[0])
    except FileNotFoundError:
        return Path.home() / "Desktop"


def get_download():
    import winreg

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders",
        )
        return expandvars(
            winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
        )
    except FileNotFoundError:
        return Path.home() / "Downloads"


@dataclass
class FileManagerConfig(Config):
    """Dataclass for storing configuration information for the file manager."""

    dsp_dirs: List[str] = field(
        default_factory=lambda: [
            Path(i).as_posix()
            for i in [
                LocalLow / "DJI/RoboMaster/dsp_projects",
                "/Program Files (x86)/DJI Education Hub/**",
                get_desktop(),
                get_download(),
            ]
        ]
    )
