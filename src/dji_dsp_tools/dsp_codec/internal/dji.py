""" This module contains the Dji class. """

import xml.etree.ElementTree as ET

from dji_dsp_tools.dsp_codec.internal.attribute import Attribute
from dji_dsp_tools.dsp_codec.internal.code import Code


class Dji:
    """ Dji class """
    def __init__(self,
                 attribute: Attribute,
                 code: Code):
        self.attribute = attribute
        self.code = code

    def get_xml_element(self) -> ET.Element:
        """ Get XML element """
        dji = ET.Element("dji")
        dji.append(self.attribute.get_xml_element())
        dji.append(self.code.get_xml_element())
        return dji

    def get_xml_string(self) -> str:
        """ Get XML string """
        return ET.tostring(self.get_xml_element(), encoding="unicode", short_empty_elements=False)

    @classmethod
    def from_xml_element(cls, dji_xml_element: ET.Element) -> "Dji":
        """ Get Dji from XML element """
        return cls(
            Attribute.from_xml_element(dji_xml_element.find("attribute")),
            Code.from_xml_element(dji_xml_element.find("code"))
        )

    @classmethod
    def from_xml_string(cls, dji_xml_string: str) -> "Dji":
        """ Get Dji from XML string """
        return cls.from_xml_element(ET.fromstring(dji_xml_string))
