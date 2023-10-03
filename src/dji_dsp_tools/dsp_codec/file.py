"""
DSP file format.
DSP 文件格式
"""

import base64
import hashlib
import os

from datetime import datetime
from uuid import uuid4
from Crypto.Cipher import AES

from dji_dsp_tools.dsp_codec.internal.attribute import Attribute
from dji_dsp_tools.dsp_codec.internal.code import Code
from dji_dsp_tools.dsp_codec.internal.dji import Dji
from dji_dsp_tools.dsp_codec.internal.fvd import FirmwareVersionDependency
from dji_dsp_tools.dsp_codec.internal.code_type import CodeType

# Extracted from DJI's RoboMaster S1 app.
DSP_KEY = b'TRoP4GWuc30k6WUp'
DSP_IV = b'bP3crVEO6wABzOc0'
DSP_MKEY = 'wwxnMmF8'


class DspFile:
    """ DSP file class. """
    def __init__(self, dji: Dji, file_name: str):
        self.dji = dji
        self.file_name = file_name

    @staticmethod
    def compute_guid() -> str:
        """Compute the GUID.

        Returns:
            str: the GUID
        """
        return str(uuid4()).replace("-", "")

    @staticmethod
    def pkcs7_pad(data: bytes) -> bytes:
        """PKCS7 padding.

        Args:
            data (bytes): the data

        Returns:
            bytes: the padded data
        """
        padding = AES.block_size - (len(data) % AES.block_size)
        return data + bytes([padding] * padding)

    @staticmethod
    def pkcs7_unpad(data: bytes) -> bytes:
        """PKCS7 unpadding.

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
        """Decode the DSP file.

        Args:
            raw_byte (bytes): the raw data

        Returns:
            bytes: the decoded data
        """
        cipher_text = base64.standard_b64decode(raw_byte)

        cipher = AES.new(DSP_KEY, AES.MODE_CBC, DSP_IV)
        plain_byte = DspFile.pkcs7_unpad(cipher.decrypt(cipher_text))

        return plain_byte

    @staticmethod
    def encode_dsp(plain_byte: bytes) -> bytes:
        """Encode the DSP file.

        Args:
            plain_byte (bytes): the plain data

        Returns:
            bytes: the encoded data
        """
        plain_byte = DspFile.pkcs7_pad(plain_byte)

        cipher = AES.new(DSP_KEY, AES.MODE_CBC, DSP_IV)
        cipher_text = cipher.encrypt(plain_byte)

        base64_text = base64.standard_b64encode(cipher_text)

        return base64_text

    @classmethod
    def new(cls, creator: str = "Anonymous", title: str = "Untitled", file_name: str = "") -> "DspFile":
        """Create a new DSP file.

        Args:
            creator (str, optional): the creator. Defaults to "Anonymous".
            title (str, optional): the title. Defaults to "Untitled".
            file_name (str, optional): the file name. Defaults to "".

        Returns:
            DspFile: DspFile object
        """
        return cls.new_with_python_code(creator, title, "", file_name)

    @classmethod
    def new_with_python_code(cls, creator: str = "Anonymous", title: str = "Untitled", python_code: str = "", file_name: str = "") -> "DspFile":
        """Create a new DSP file with Python code.

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
        if creator:
            raise ValueError("Creator cannot be empty")
        title = title.strip()
        if title:
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
                app_max_version=""
            ),
            code=Code(
                python_code=python_code,
                scratch_description=""
            )
        )

        if file_name:
            file_name = title

        return cls(dji, file_name)

    @classmethod
    def load(cls, path: str) -> "DspFile":
        """Load a DSP file.

        Args:
            path (str): the path of the DSP file.

        Returns:
            DspFile: DspFile object
        """
        with open(path, "rb") as file:
            dsp_data = file.read()

        xml_data = cls.decode_dsp(dsp_data)
        dji = Dji.from_xml_string(xml_data.decode())

        guid = dji.attribute.guid
        file_name = os.path.splitext(path)[0]
        file_name = os.path.split(file_name)[1]
        if file_name.lower().endswith(guid):
            file_name = file_name[:file_name.lower().rfind(guid)]
            if file_name.endswith("_"):
                file_name = file_name[:-1]

        return cls(dji, file_name)

    def set_python_code(self, python_code: str) -> None:
        """Set the Python code.

        Args:
            python_code (str): Python code
        """
        self.dji.code.python_code = python_code.strip()

    def python_code(self) -> str:
        """Get the Python code.

        Returns:
            str: Python code
        """
        return self.dji.code.python_code

    def save(self, path: str) -> None:
        """Save the DSP file.

        Args:
            path (str): the path of the DSP file.
        """
        self.dji.attribute.modify_time = datetime.now()
        self.compute_signature()

        xml_data = self.dji.get_xml_string()
        dsp_data = self.encode_dsp(xml_data.encode())

        file_name = os.path.join(
            path, f"{self.file_name}_{self.dji.attribute.guid}.dsp")
        with open(file_name, "wb") as file:
            file.write(dsp_data)

    def calc_signature(self) -> str:
        """Calculate the signature.

        Returns:
            str: the signature
        """
        md5_source = (
            DSP_MKEY +
            self.dji.attribute.creation_date.strftime("%Y/%m/%d") +
            self.dji.attribute.title +
            self.dji.attribute.creator +
            self.dji.attribute.firmware_version_dependency.value +
            self.dji.attribute.guid +
            self.dji.code.python_code +
            self.dji.code.scratch_description +
            self.dji.attribute.code_type.name.lower()
        )
        md5_sum = hashlib.md5(md5_source.encode()).hexdigest()
        return md5_sum[7:23]

    def compute_signature(self) -> None:
        """Compute the signature.
        """
        self.dji.attribute.sign = self.calc_signature()
