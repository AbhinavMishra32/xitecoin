from enum import Enum
import xml.etree.ElementTree as ET

def import_xml_settings(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    def parse_element(element):
        if len(element):
            return {child.tag: parse_element(child) for child in element}
        else:
            return element.text
        
    settings = parse_element(root)
    return settings

settings = import_xml_settings('blockchain_settings.xml')
print(settings)


class Settings(Enum):
    BLOCKCHAIN_NAME = settings["blockchain"]["name"] # type: ignore
    BLOCKCHAIN_DIFFICULITY = int(settings["blockchain"]["difficulity"]) # type: ignore
    

print(Settings.BLOCKCHAIN_NAME.value, Settings.BLOCKCHAIN_DIFFICULITY.value)