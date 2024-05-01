from dataclasses import dataclass, fields
import toml
from pathlib import Path

DEFAULT_CONFIG_FILE = Path.home() / '.dspy_tool.toml'


@dataclass
class Config:
    """Dataclass for storing configuration information."""
    @property
    def section_name(self):
        """Return the name of the section in the config file."""
        return type(self).__name__

    def save_config(self, config_file: Path = DEFAULT_CONFIG_FILE):
        """Write the config to the config file."""
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = toml.load(f)
            data[self.section_name] = self.to_dict()
        else:
            data = {self.section_name: self.to_dict()}
        print(f"Saving config for {self.section_name} in {config_file}")
        with open(config_file, 'w') as f:
            toml.dump(data, f)

    @classmethod
    def load_config(cls, config_file: Path = DEFAULT_CONFIG_FILE):
        if not config_file.exists():
            print(f"Config file {config_file} does not exist. Using default values.")
            return cls()
        with open(config_file, 'r') as f:
            data = toml.load(f)

        section_name = cls.__name__
        if section_name in data:
            values = data[section_name]
            print(f"Loaded config for {section_name} in {config_file}")
            return cls(**values)
        else:
            return cls()

    def to_dict(self):
        """Return a dictionary representation of the config."""
        return {field.name: getattr(self, field.name) for field in fields(self)}
