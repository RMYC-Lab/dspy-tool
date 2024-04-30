import argparse
import datetime
import re
from pathlib import Path

from dspy_tool import __version__
from dspy_tool.dsp_codec.file import DspFile
from dspy_tool.dsp_codec.internal.dji import Dji

# __version__ = "0.0.1"

DEBUG = False

DELETE_COMMENTS_RE = r"\n *?#block.+?\n"

PYTHON_CODE_RE = r"<python_code><!\[CDATA\[(.+?)\]\]><\/python_code>"


def process_py_file(
    input_file_path: Path,
    output_file_path: Path,
    file_name: str,
    title: str,
    creator: str,
    raw: bool,
    std_out: bool,
    delete_comments: bool,
) -> None:
    if not file_name:
        file_name = DspFile.get_file_name(input_file_path.name)
    if (not file_name.endswith(".dsp") and not raw) or (
        not file_name.endswith(".xml") and raw
    ):
        file_name = f"{file_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    with open(input_file_path, "r", encoding="utf-8") as file:
        python_code = file.read()
    dsp_file = DspFile.new_with_python_code(creator, title, python_code, file_name)
    if delete_comments:
        python_code = dsp_file.get_python_code()
        dsp_file.dji.code.python_code = re.sub(DELETE_COMMENTS_RE, "\n", python_code)
    if raw:
        if std_out:
            print(dsp_file.dji.get_xml_string())
        else:
            if not file_name.endswith(".xml"):
                file_name += "_raw.xml"
            with open(output_file_path / file_name, "wb") as file:
                file.write(dsp_file.dji.get_xml_string().encode())
    else:
        if std_out:
            print(dsp_file.get_dsp_data().decode(encoding="utf-8"))
        else:
            if not file_name.endswith(".dsp"):
                file_name += ".dsp"
            dsp_file.save(str(output_file_path), file_name)


def process_dsp_file(
    input_file_path: Path,
    output_file_path: Path,
    file_name: str,
    title: str,
    creator: str,
    raw: bool,
    std_out: bool,
    delete_comments: bool,
) -> None:
    if not file_name:
        file_name = DspFile.get_file_name(input_file_path.name)
    if (not file_name.endswith(".py") and not raw) or (
        not file_name.endswith(".xml") and raw
    ):
        file_name = f"{file_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    with input_file_path.open("rb") as file:
        dsp_data = DspFile.decode_dsp(file.read()).decode(encoding="utf-8")
    if delete_comments:
        dsp_data = re.sub(DELETE_COMMENTS_RE, "\n", dsp_data)
    if raw:
        if std_out:
            print(dsp_data)
        else:
            if not file_name.endswith(".xml"):
                file_name += "_raw.xml"
            with open(output_file_path / file_name, "wb") as file:
                file.write(dsp_data.encode())
    else:
        if std_out:
            print(re.findall(PYTHON_CODE_RE, dsp_data, re.S)[0])
        else:
            if not file_name.endswith(".py"):
                file_name += ".py"
            with open(output_file_path / file_name, "w", encoding="utf-8") as file:
                file.write(re.findall(PYTHON_CODE_RE, dsp_data, re.S)[0])


def main():
    parser = argparse.ArgumentParser(description="DSP File Codec Tool")
    parser.add_argument("input", type=str, help="the input file path.")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="the output file path. (defaults to current dir)",
        default=".",
    )
    parser.add_argument(
        "--file-name", "-f", type=str, help="the file name. (defaults to auto generate)"
    )
    parser.add_argument(
        "--std-out", "-s", action="store_true", help="output to the standard output."
    )
    parser.add_argument(
        "--raw",
        "-r",
        action="store_true",
        help="output raw xml data. (defaults to False)",
    )
    parser.add_argument(
        "--delete-comments",
        "--dc",
        action="store_true",
        help="try to delete comments for blocks. (defaults to False)",
    )
    parser.add_argument(
        "--title",
        "-t",
        type=str,
        help="the title of the file. (defaults to the 'Untitled')",
        default="Untitled",
    )
    parser.add_argument(
        "--creator",
        "-c",
        type=str,
        help="the creator of the file. (defaults to 'Anonymous')",
        default="Anonymous",
    )
    parser.add_argument("--debug", action="store_true", help="enable debug mode.")
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="DSP File Codec Tool v" + __version__,
    )

    args = parser.parse_args()

    if args.debug:
        global DEBUG
        DEBUG = True

    if DEBUG:
        print(args)
    input_file_path = Path(args.input)
    output_file_path = Path(args.output)
    if not input_file_path.exists():
        raise FileNotFoundError(f"The input file does not exist. Path: {args.input}")
    if input_file_path.is_file():
        if input_file_path.suffix == ".py":
            if not args.std_out:
                if not output_file_path.exists():
                    output_file_path.mkdir(parents=True)
            process_py_file(
                input_file_path,
                output_file_path,
                args.file_name,
                args.title,
                args.creator,
                args.raw,
                args.std_out,
                args.delete_comments,
            )
        elif input_file_path.suffix == ".dsp":
            process_dsp_file(
                input_file_path,
                output_file_path,
                args.file_name,
                args.title,
                args.creator,
                args.raw,
                args.std_out,
                args.delete_comments,
            )
        else:
            raise ValueError(f"The input file is not a valid file. Path: {args.input}")


if __name__ == "__main__":
    main()
