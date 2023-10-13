""" Code class """

import xml.etree.ElementTree as ET

"""
由于 xml.etree.ElementTree 库不支持 CDATA，所以需要自定义一个 CDATA 类型的元素。
参考：https://stackoverflow.com/questions/174890/how-to-output-cdata-using-elementtree
定义了一个函数 CDATA 和一个自定义的 _serialize_xml 方法，用于生成包含 CDATA 部分的 XML 输出。
注意：由于覆盖了库中内置的方法，所以要注意兼容性问题。
"""

CDATA_HEAD = "![CDATA["


def CDATA(text=""):
    element = ET.Element(CDATA_HEAD)
    element.text = text
    return element


ET._original_serialize_xml = ET._serialize_xml


def _serialize_xml(write, elem, qnames, namespaces, short_empty_elements, **kwargs) -> None:
    if elem.tag == CDATA_HEAD:
        write(f"<{CDATA_HEAD}{elem.text}]]>")
        return
    else:
        return ET._original_serialize_xml(write, elem, qnames, namespaces, short_empty_elements, **kwargs)


ET._serialize_xml = ET._serialize['xml'] = _serialize_xml


class Code:
    """ Code class """
    def __init__(self,
                 python_code: str = "",
                 scratch_description: str = ""):
        self.python_code = python_code
        self.scratch_description = scratch_description

    def get_xml_element(self) -> ET.Element:
        """ Get XML element """
        code = ET.Element("code")
        ET.SubElement(code, "python_code").append(CDATA(self.python_code))
        ET.SubElement(code, "scratch_description").append(CDATA(self.scratch_description))
        return code

    @classmethod
    def from_xml_element(cls, code_xml_element: ET.Element) -> "Code":
        """ Get Code from XML element """
        return cls(
            code_xml_element.find("python_code").text,
            code_xml_element.find("scratch_description").text
        )
