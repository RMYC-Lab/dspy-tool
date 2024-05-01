import argparse
import datetime
import re
from pathlib import Path
from typing import Union, Tuple
from urllib.parse import unquote

from dspy_tool.dsp_codec.file import DspFile

__version__ = "0.0.4"

DEBUG = False

DELETE_COMMENTS_RE = r" *?#block.*?\n"

PYTHON_CODE_RE = r"<python_code><!\[CDATA\[(.*?)\]\]><\/python_code>"

CHINSES_RE = r"((_[0-9A-F]{2}){3})"


def process_py_file(
    input_file_path: Path,
    output_file_path: Path,
    file_name: str,
    title: str,
    creator: str,
    raw: bool,
    std_out: bool,
    delete_comments: bool,
    process_chinese: bool,
) -> Union[str, None]:
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
        dsp_file.dji.code.python_code = re.sub(DELETE_COMMENTS_RE, "", python_code)
    if raw:
        if std_out:
            return dsp_file.dji.get_xml_string()
        else:
            if not file_name.endswith(".xml"):
                file_name += "_raw.xml"
            with open(output_file_path / file_name, "wb") as file:
                file.write(dsp_file.dji.get_xml_string().encode(encoding="utf-8"))
    else:
        if std_out:
            return dsp_file.get_dsp_data().decode(encoding="utf-8")
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
    process_chinese: bool,
) -> Union[str, None]:
    if not file_name:
        file_name = DspFile.get_file_name(input_file_path.name)
    if (not file_name.endswith(".py") and not raw) or (
        not file_name.endswith(".xml") and raw
    ):
        file_name = f"{file_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    with input_file_path.open("rb") as file:
        dsp_data = file.read().decode(encoding="utf-8")
        if not dsp_data.startswith("<dji><attribute>"):
            dsp_data = DspFile.decode_dsp(dsp_data.encode(encoding="utf-8")).decode(
                encoding="utf-8"
            )
    if delete_comments:
        dsp_data = re.sub(DELETE_COMMENTS_RE, "", dsp_data)
    if process_chinese:
        for line in dsp_data.split("\n"):
            if decode_chinese(line)[0]:
                dsp_data = dsp_data.replace(
                    line, line + "  ## " + " -> ".join(decode_chinese(line))
                )
    if raw:
        if std_out:
            return dsp_data
        else:
            if not file_name.endswith(".xml"):
                file_name += "_raw.xml"
            with open(output_file_path / file_name, "wb") as file:
                file.write(dsp_data.encode(encoding="utf-8"))
    else:
        code = re.findall(PYTHON_CODE_RE, dsp_data, re.S)
        if not code:
            print("No python code found in the dsp file.")
            return ""
        if std_out:
            return code[0]
        else:
            if not file_name.endswith(".py"):
                file_name += ".py"
            with open(output_file_path / file_name, "w", encoding="utf-8") as file:
                file.write(code[0])


def decode_chinese(data: str) -> Tuple[str, str]:
    origin = re.findall(CHINSES_RE, data)
    return "".join([i[0] for i in origin]), "".join(
        [unquote(i[0].replace("_", "%")) for i in origin]
    )


def main():
    parser = argparse.ArgumentParser(description="DSP File Codec Tool")
    parser.add_argument("input", type=str, help="the input file path.")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="the output file path. (defaults to current dir)",
        default=".",
    )
    parser.add_argument(
        "-f", "--file-name", type=str, help="the file name. (defaults to auto generate)"
    )
    parser.add_argument(
        "-s", "--std-out", action="store_true", help="output to the standard output."
    )
    parser.add_argument(
        "-r",
        "--raw",
        action="store_true",
        help="output raw xml data. (defaults to False)",
    )
    parser.add_argument(
        "--dc",
        "--delete-comments",
        action="store_true",
        help="try to delete comments for blocks. (defaults to False)",
    )
    parser.add_argument(
        "--pc",
        "--process-chinese",
        action="store_true",
        help="try to decode chinese characters. (defaults to False)",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        help="the title of the file. (defaults to the 'Untitled')",
        default="Untitled",
    )
    parser.add_argument(
        "-c",
        "--creator",
        type=str,
        help="the creator of the file. (defaults to 'Anonymous')",
        default="Anonymous",
    )
    parser.add_argument("--debug", action="store_true", help="enable debug mode.")
    parser.add_argument(
        "-v",
        "--version",
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
            ret = process_py_file(
                input_file_path,
                output_file_path,
                args.file_name,
                args.title,
                args.creator,
                args.raw,
                args.std_out,
                args.dc,
                args.pc,
            )
            if args.std_out:
                print(ret)
        elif input_file_path.suffix == ".dsp":
            ret = process_dsp_file(
                input_file_path,
                output_file_path,
                args.file_name,
                args.title,
                args.creator,
                args.raw,
                args.std_out,
                args.dc,
                args.pc,
            )
            if args.std_out:
                print(ret)
        else:
            raise ValueError(f"The input file is not a valid file. Path: {args.input}")


if __name__ == "__main__":
    main()
