import xml.etree.ElementTree as ET
from CLIInputs import XSDElement
from CLIInputs import ChildXSDElement

cli_inputs = None

def __parse_element(element, xsd_element):
    if element.get('type'):
        xsd_element.name = element.get('name')
        type = element.get('type')
        if type.startswith('xs') or type not in cli_inputs.name_type_dict:
            xsd_element.type = type
        else:
            xsd_element.type = cli_inputs.name_type_dict[type]
        xsd_element.min_occurs = element.get('minOccurs') if 'minOccurs' in element.attrib else '1'
        xsd_element.max_occurs = element.get('maxOccurs') if 'maxOccurs' in element.attrib else '1'
        return
    if element.get('ref'):
        xsd_element.ref = element.get('ref')
        xsd_element.min_occurs = element.get('minOccurs') if 'minOccurs' in element.attrib else '1'
        xsd_element.max_occurs = element.get('maxOccurs') if 'maxOccurs' in element.attrib else '1'
        return

    for complex_type in element:
        for seq in complex_type:
            for c in seq:
                new_xsd_element = ChildXSDElement()
                xsd_element.children.append(new_xsd_element)
                __parse_element(c, new_xsd_element)
            break
        break
    xsd_element.name = element.get('name')
    xsd_element.min_occurs = element.get('minOccurs') if 'minOccurs' in element.attrib else '1'
    xsd_element.max_occurs = element.get('maxOccurs') if 'maxOccurs' in element.attrib else '1'
    return

def parse_xsd(xsd_file, cli_inputs_param):
    global cli_inputs

    cli_inputs = cli_inputs_param

    tree = ET.parse(xsd_file)
    root = tree.getroot()
    for child in root:
        tag_name = child.tag[child.tag.index('}')+1:]
        if 'element' == tag_name:
            cli_inputs.name_type_dict[child.get('type')] = child.get('name')

    for child in root:
        tag_name = child.tag[child.tag.index('}')+1:]
        if 'complexType' == tag_name:
            attributes = list()
            child_name = child.get('name')
            if child_name in cli_inputs.name_type_dict:
                cli_inputs.xsd_elements_dict[cli_inputs.name_type_dict[child_name]] = attributes
            else:
                cli_inputs.unknown_xsd_elements_dict[child_name] = attributes

            for complex_type_children in child:
                complex_type_child_tag_name = complex_type_children.tag[complex_type_children.tag.index('}')+1:]
                if 'sequence' == complex_type_child_tag_name:
                    for c in complex_type_children:
                        xsd_element = XSDElement()
                        __parse_element(c, xsd_element)
                        attributes.append(xsd_element)
                elif 'complexContent' == complex_type_child_tag_name:
                    for extension in complex_type_children:
                        attributes.append(XSDElement(base=extension.get('base')))
                        for seq in extension:
                            for elem in seq:
                                try:
                                    xsd_element = XSDElement()
                                    __parse_element(elem, xsd_element)
                                    attributes.append(xsd_element)
                                except Exception:
                                    import traceback
                                    traceback.print_exc()
                            break
                        break



