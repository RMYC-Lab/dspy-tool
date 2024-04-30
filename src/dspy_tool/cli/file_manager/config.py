from dataclasses import dataclass, field
from typing import List
from dspy_tool.cli.utils.config import Config


@dataclass
class FileManagerConfig(Config):
    """Dataclass for storing configuration information for the file manager."""
    dsp_dirs: List[str] = field(default_factory=list)


a = FileManagerConfig(dsp_dirs=['a', 'b', 'c'])
print(a.dsp_dirs[0])
a.save_config()
b = FileManagerConfig.load_config()
print(b.dsp_dirs)

