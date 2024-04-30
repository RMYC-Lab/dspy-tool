"""
DSP file format.
DSP 文件格式
"""

import base64
import hashlib
import os
import re

from datetime import datetime
from uuid import uuid4
from Crypto.Cipher import AES

from dspy_tool.dsp_codec.internal.attribute import Attribute
from dspy_tool.dsp_codec.internal.code import Code
from dspy_tool.dsp_codec.internal.dji import Dji
from dspy_tool.dsp_codec.internal.fvd import FirmwareVersionDependency
from dspy_tool.dsp_codec.internal.code_type import CodeType

# Extracted from DJI's RoboMaster S1 app.
DSP_KEY = b"TRoP4GWuc30k6WUp"
DSP_IV = b"bP3crVEO6wABzOc0"
DSP_MKEY = "wwxnMmF8"

FILE_NAME_COMPILE = re.compile(
    r"^(?P<file_name>.*?)([_-](\d{14}|[a-zA-Z0-9]{32}))*(([_\-\.]raw)?\.(dsp|py|xml))?$"
)


class DspFile:
    """DSP file class."""

    def __init__(self, dji: Dji, file_name: str):
        self.dji = dji
        self.file_name = file_name

    @staticmethod
    def compute_guid() -> str:
        """Compute the GUID. 生成 GUID

        Returns:
            str: the GUID
        """
        return str(uuid4()).replace("-", "")

    @staticmethod
    def get_file_name(original_file_name: str) -> str:
        """Get the file name. 获取文件名

        Args:
            original_file_name (str): the original file name

        Returns:
            str: the file name
        """
        return FILE_NAME_COMPILE.match(original_file_name).group("file_name")

    @staticmethod
    def _pkcs7_pad(data: bytes) -> bytes:
        """PKCS7 padding. PKCS7 填充

        Args:
            data (bytes): the data

        Returns:
            bytes: the padded data
        """
        padding = AES.block_size - (len(data) % AES.block_size)
        return data + bytes([padding] * padding)

    @staticmethod
    def _pkcs7_unpad(data: bytes) -> bytes:
        """PKCS7 unpadding. PKCS7 去填充

        Args:
            data (bytes): the data

        Raises:
            ValueError: Invalid PKCS7 padding

        Returns:
            bytes: the unpadded data
        """
        padding = data[-1]
        if padding > AES.block_size or data[-padding:] != bytes([padding] * padding):
            raise ValueError("Invalid PKCS7 padding")
        return data[:-padding]

    @staticmethod
    def decode_dsp(raw_byte: bytes) -> bytes:
        """Decode the DSP file. 解码 DSP 文件

        Args:
            raw_byte (bytes): the raw data

        Returns:
            bytes: the decoded data
        """
        cipher_text = base64.standard_b64decode(raw_byte)

        cipher = AES.new(DSP_KEY, AES.MODE_CBC, DSP_IV)
        plain_byte = DspFile._pkcs7_unpad(cipher.decrypt(cipher_text))

        return plain_byte

    @staticmethod
    def encode_dsp(plain_byte: bytes) -> bytes:
        """Encode the DSP file. 编码 DSP 文件

        Args:
            plain_byte (bytes): the plain data

        Returns:
            bytes: the encoded data
        """
        plain_byte = DspFile._pkcs7_pad(plain_byte)

        cipher = AES.new(DSP_KEY, AES.MODE_CBC, DSP_IV)
        cipher_text = cipher.encrypt(plain_byte)

        base64_text = base64.standard_b64encode(cipher_text)

        return base64_text

    @classmethod
    def new(
        cls, creator: str = "Anonymous", title: str = "Untitled", file_name: str = ""
    ) -> "DspFile":
        """Create a new DSP file. 创建一个新的 DSP 文件

        Args:
            creator (str, optional): the creator. Defaults to "Anonymous".
            title (str, optional): the title. Defaults to "Untitled".
            file_name (str, optional): the file name. Defaults to "".

        Returns:
            DspFile: DspFile object
        """
        return cls.new_with_python_code(creator, title, "", file_name)

    @classmethod
    def new_with_python_code(
        cls,
        creator: str = "Anonymous",
        title: str = "Untitled",
        python_code: str = "",
        file_name: str = "",
    ) -> "DspFile":
        """Create a new DSP file with Python code. 创建一个新的带有 Python 代码的 DSP 文件

        Args:
            creator (str, optional): the creator. Defaults to "Anonymous".
            title (str, optional): the title. Defaults to "Untitled".
            python_code (str, optional): the existing python code. Defaults to "".
            file_name (str, optional): the file name. Defaults to "".

        Raises:
            ValueError: Error Values

        Returns:
            DspFile: DspFile object
        """
        creator = creator.strip()
        if not creator:
            raise ValueError("Creator cannot be empty")
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty")

        guid = cls.compute_guid()

        dji = Dji(
            attribute=Attribute(
                creation_date=datetime.now(),
                sign="",
                modify_time=datetime.now(),
                guid=guid,
                creator=creator,
                firmware_version_dependency=FirmwareVersionDependency(),
                title=title,
                code_type=CodeType.PYTHON_CODE,
                app_min_version="",
                app_max_version="",
            ),
            code=Code(python_code=python_code, scratch_description=""),
        )

        if file_name:
            file_name = title

        return cls(dji, file_name)

    @classmethod
    def load(cls, path: str) -> "DspFile":
        """Load a DSP file. 加载一个 DSP 文件

        Args:
            path (str): the path of the DSP file.

        Returns:
            DspFile: DspFile object
        """
        with open(path, "rb") as file:
            dsp_data = file.read()

        xml_data = cls.decode_dsp(dsp_data)
        dji = Dji.from_xml_string(xml_data.decode())

        file_name = cls.get_file_name(os.path.basename(path))

        return cls(dji, file_name)

    def set_python_code(self, python_code: str) -> None:
        """Set the Python code. 设置 Python 代码

        Args:
            python_code (str): Python code
        """
        self.dji.code.python_code = python_code.strip()

    def get_python_code(self) -> str:
        """Get the Python code. 获取 Python 代码

        Returns:
            str: Python code
        """
        return self.dji.code.python_code

    def get_dsp_data(self) -> bytes:
        """Get the DSP data. 获取 DSP 数据

        Returns:
            bytes: DSP data
        """
        self.compute_signature()

        xml_data = self.dji.get_xml_string()
        dsp_data = self.encode_dsp(xml_data.encode())

        return dsp_data

    def save(
        self, path: str, file_name: str = "", change_modify_time: bool = True
    ) -> None:
        """Save the DSP file. 保存 DSP 文件

        Args:
            path (str): the path of the DSP file.
        """
        if change_modify_time:
            self.dji.attribute.modify_time = datetime.now()

        dsp_data = self.get_dsp_data()

        if not file_name:
            file_name = f"{self.file_name}_{self.dji.attribute.guid}.dsp"

        with open(os.path.join(path, file_name), "wb") as file:
            file.write(dsp_data)

    def calc_signature(self) -> str:
        """Calculate the signature. 计算签名
        不确保计算出来的签名与 DJI 官方的签名一致。现有 Robomaster App 不会检查签名是否正确。

        Returns:
            str: the signature
        """
        md5_source = (
            DSP_MKEY
            + self.dji.attribute.creation_date.strftime("%Y/%m/%d")
            + self.dji.attribute.title
            + self.dji.attribute.creator
            + self.dji.attribute.firmware_version_dependency.value
            + self.dji.attribute.guid
            + self.dji.code.python_code
            + self.dji.code.scratch_description
            + self.dji.attribute.code_type.name.lower()
        )
        md5_sum = hashlib.md5(md5_source.encode()).hexdigest()
        return md5_sum[7:23]

    def compute_signature(self) -> None:
        """Compute the signature. 计算签名"""
        self.dji.attribute.sign = self.calc_signature()
