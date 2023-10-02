""" This module contains the Dji class. """

import xml.etree.ElementTree as ET

from dji_dsp_tools.dsp_codec.internal.attribute import Attribute, get_attribute_from_xml_element
from dji_dsp_tools.dsp_codec.internal.code import Code, get_code_from_xml_element


class Dji:
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


def get_dji_from_xml_element(dji_xml_element: ET.Element) -> Dji:
    """ Get Dji from XML element """
    return Dji(
        get_attribute_from_xml_element(dji_xml_element.find("attribute")),
        get_code_from_xml_element(dji_xml_element.find("code"))
    )
