import argparse
from pathlib import Path
from typing import List

from textual.app import App, ComposeResult
from textual.widgets import Tree, Footer, TextArea
from textual.widgets.tree import TreeNode
from pyperclip import copy as pc_copy

from dspy_tool.cli.dsp_codec import process_dsp_file
from dspy_tool.cli.utils.config.fm_config import FileManagerConfig


__version__ = "0.0.1"


def list_dirs(cfg: FileManagerConfig):
    print("DSP File Directories:")
    for dsp_dir in cfg.dsp_dirs:
        print(dsp_dir)


def add_dir(cfg: FileManagerConfig, dir: Path):
    if dir.exists() and dir.is_file():
        dir = dir.parent
    if dir.as_posix() not in cfg.dsp_dirs:
        cfg.dsp_dirs.append(dir.as_posix())
        print(f"Added {dir} to the DSP directories.")
        cfg.save_config()
    else:
        print(f"{dir} is already in the DSP directories.")


def remove_dir(cfg: FileManagerConfig, dir: Path):
    if dir.exists() and dir.is_file():
        dir = dir.parent
    if dir.as_posix() in cfg.dsp_dirs:
        cfg.dsp_dirs.remove(dir.as_posix())
        print(f"Removed {dir} from the DSP directories.")
        cfg.save_config()
    else:
        print(f"{dir} is not in the DSP directories.")


def _get_all_drives():
    for drive in range(ord("A"), ord("Z") + 1):
        drive = chr(drive) + ":\\"
        if Path(drive).exists():
            yield drive


def _get_dsp_file_list(cfg: FileManagerConfig):
    dsp_dirs = [Path(i) for i in cfg.dsp_dirs]
    for dsp_dir in dsp_dirs:
        if dsp_dir.is_absolute():
            if dsp_dir.exists() and dsp_dir.is_dir():
                for file in dsp_dir.rglob("*.dsp"):
                    yield file
            else:
                print(f"{dsp_dir} does not exist.")
        else:
            for drive in _get_all_drives():
                for file in Path(drive, dsp_dir).rglob("*.dsp"):
                    yield file


def _generate_file_tree(file_list: List[Path], root_node: TreeNode):
    for file in file_list:
        for parent in list(root_node.children):
            if str(parent.label) == file.parent.as_posix():
                parent.add_leaf(file.name).data = file
                break
        else:
            root_node.add(file.parent.as_posix()).add_leaf(file.name).data = file


class FileManagerApp(App):
    BINDINGS = [
        ("c", "copy", "Copy the selected text"),
        ("s", "change_style", "Change the style"),
        ("o", "open", "Open file in explorer"),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = "css.tcss"

    themes = ["vscode_dark", "monokai", "css", "github_light", "dracula"]

    def __init__(self, cfg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg = cfg

    def compose(self) -> ComposeResult:
        self.file_tree = Tree("DSP Files", id="sidebar")
        # print(type(tree.root))
        _generate_file_tree(list(_get_dsp_file_list(self.cfg)), self.file_tree.root)
        self.file_tree.root.expand_all()
        self.file_tree.on_event
        yield self.file_tree
        self.text_area = TextArea.code_editor(
            "Python Code", language="python", read_only=True
        )
        yield self.text_area
        yield Footer()

    def action_change_style(self):
        next_theme = self.themes.index(self.text_area.theme) + 1
        if next_theme == len(self.themes):
            # Out of range
            next_theme = 0
        self.text_area.theme = self.themes[next_theme]
        if next_theme == 3:
            self.dark = False
        else:
            self.dark = True

    def on_tree_node_highlighted(self, node: Tree.NodeHighlighted):
        data = node.node.data
        if data:
            with data.open(encoding="utf-8") as f:
                code = process_dsp_file(
                    data, data.parent, data.stem, "", "", False, True, True, True
                )
                if code == "":
                    self.text_area.text = "No python code"
                elif code is not None:
                    self.text_area.text = code
                else:
                    self.text_area.text = (
                        "It seems that we have something wrong when decoded dsp file.\nThis is the origin file:\n"
                        + f.read()
                    )

    def action_open(self):
        node = self.file_tree.cursor_node
        if node and node.data:
            import subprocess

            subprocess.Popen(
                ["explorer.exe", "/select,", node.data.as_posix().replace("/", "\\")]
            )

    def on_tree_clicked(self, click_event):
        print(click_event)

    def action_copy(self):
        self.text_area.selected_text
        pc_copy(self.text_area.selected_text)


def main():
    parser = argparse.ArgumentParser(description="DSP File Manager Tool")
    parser.add_argument(
        "-d",
        "--dsp-dirs",
        action="store_true",
        help="output the dsp directories.",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list the dsp files.",
    )
    parser.add_argument(
        "-a",
        "--add",
        type=str,
        help="add a dsp directory.",
    )
    parser.add_argument(
        "-r",
        "--remove",
        type=str,
        help="remove a dsp directory.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="DSP File Manager Tool v" + __version__,
    )

    args = parser.parse_args()

    cfg = FileManagerConfig.load_config()

    if args.dsp_dirs:
        list_dirs(cfg)
    elif args.list:
        app = FileManagerApp(cfg)
        app.run()
    elif args.add:
        add_dir(cfg, Path(args.add))
    elif args.remove:
        remove_dir(cfg, Path(args.remove))


if __name__ == "__main__":
    main()
