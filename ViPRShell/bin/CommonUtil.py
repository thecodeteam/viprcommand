"""
Copyright 2015 EMC Corporation
All Rights Reserved
EMC Confidential: Restricted Internal Distribution
81ff427ffd0a66013a8e07b7b967d6d6b5f06b1b.ViPR
"""

import json
import xml.dom.minidom
import xml.etree.ElementTree as ET
import os
import Constants

cli_utils = None

def print_table( table):
    col_width = [max(len(str(x)) for x in col) for col in zip(*table)]
    for line in table:
        print("| " + " | ".join("{0:{1}}".format(x, col_width[i])
                            for i, x in enumerate(line)) + " |")

def print_query_params(query_params):
    if not query_params:
        return
    print('Query Parameters:-')
    table = [('Name', 'Type')]
    for n, t in query_params.items():
        table.append((n,t))
    print_table(table)

def print_attributes(element_name):
    if not element_name:
        return

    if element_name not in cli_utils.xsd_elements_dict:
        print("Invalid element name %s" % element_name)
        return

    attributes = cli_utils.xsd_elements_dict[element_name]
    table = [('NAME', 'TYPE', 'MIN', 'MAX')]
    for xsd_element in attributes:
        __prepare_attributes_table(xsd_element, table)
    #print as table
    print("Payload Fields:-")
    print_table(table)

    #print as json
    '''help_dict = dict()
    for xsd_element in attributes:
        __prepare_attributes_json(xsd_element, help_dict)
    if help_dict:
        print('\nJSON Payload:-')
        print(json.dumps(help_dict, indent=4))'''

    # print as xml
    help_xml = ET.Element(element_name)
    for xsd_element in attributes:
        __prepare_attributes_xml(xsd_element, help_xml)
    print('\nXML Payload:-')
    response_xml = xml.dom.minidom.parseString(ET.tostring(help_xml, encoding='utf8'))
    print(response_xml.toprettyxml())


def __prepare_attributes_table(xsd_element, table, prefix=''):
    if xsd_element.ref:
        ref_name = xsd_element.ref
        table.append((prefix+ref_name, '', xsd_element.min_occurs, xsd_element.max_occurs))
        try:
            ref_attributes = cli_utils.xsd_elements_dict[ref_name] if ref_name in cli_utils.xsd_elements_dict else cli_utils.attirbute_type_dict[ref_name]
            for r in ref_attributes:
                __prepare_attributes_table(r, table, prefix+'  ')
        except Exception:
            # this is to handle elements like
            # <xs:element name="san_zone" nillable="true" type="xs:anyType"/>
            #table.append((prefix+ref_name, '', 'N' if xsd_element.min_occurs else 'Y'))
            pass
    elif xsd_element.base:
        base_name_type = xsd_element.base
        if base_name_type in cli_utils.name_type_dict:
            base_attributes = cli_utils.xsd_elements_dict[cli_utils.name_type_dict[base_name_type]]
        else:
            base_attributes = cli_utils.unknown_xsd_elements_dict[base_name_type]
        for b in base_attributes:
            __prepare_attributes_table(b, table, prefix)
    elif xsd_element.type and not xsd_element.type.startswith('xs'):
        ref_name = xsd_element.type
        ref_attributes = cli_utils.xsd_elements_dict[ref_name] if ref_name in cli_utils.xsd_elements_dict else cli_utils.unknown_xsd_elements_dict[ref_name]
        table.append((prefix+xsd_element.name, '', xsd_element.min_occurs, xsd_element.max_occurs))
        for r in ref_attributes:
            __prepare_attributes_table(r, table, prefix+'  ')
    else:
        table.append((prefix+xsd_element.name, 'List' if not xsd_element.type else xsd_element.type, xsd_element.min_occurs, xsd_element.max_occurs))
        if xsd_element.children:
            for c in xsd_element.children:
                __prepare_attributes_table(c, table, prefix+'  ')

    return

def __prepare_attributes_json(xsd_element, help_dict, prefix=''):
    if xsd_element.ref:
        ref_name = xsd_element.ref
        try:
            ref_attributes = cli_utils.xsd_elements_dict[ref_name] if ref_name in cli_utils.xsd_elements_dict else cli_utils.unknown_xsd_elements_dict[ref_name]
            new_dict = dict()
            help_dict[ref_name] =  new_dict
            for r in ref_attributes:
                __prepare_attributes_json(r, new_dict, prefix)
        except Exception:
            if "unbounded" == xsd_element.max_occurs:
                help_dict[ref_name] = [""]
            else:
                help_dict[ref_name] = ""
    elif xsd_element.base:
        base_name_type = xsd_element.base
        if base_name_type in cli_utils.name_type_dict:
            base_attributes = cli_utils.xsd_elements_dict[cli_utils.name_type_dict[base_name_type]]
        else:
            base_attributes = cli_utils.unknown_xsd_elements_dict[base_name_type]
        for b in base_attributes:
            __prepare_attributes_json(b, help_dict, prefix)
    elif xsd_element.type and not xsd_element.type.startswith('xs'):
        ref_name = xsd_element.type
        ref_attributes = cli_utils.xsd_elements_dict[ref_name] if ref_name in cli_utils.xsd_elements_dict else cli_utils.unknown_xsd_elements_dict[ref_name]
        new_dict = dict()
        help_dict[xsd_element.name] = new_dict
        for r in ref_attributes:
            __prepare_attributes_json(r, new_dict, prefix+'   ')
    else:
        new_dict = help_dict
        if not xsd_element.type:
            new_dict = dict()
            help_dict[xsd_element.name] = [new_dict]
        else:
            if "unbounded" == xsd_element.max_occurs:
                help_dict[xsd_element.name] = [""]
            else:
                help_dict[xsd_element.name] = "" #xsd_element.type
        if xsd_element.children:
            for c in xsd_element.children:
                __prepare_attributes_json(c, new_dict, prefix+'   ')

    return

def __prepare_attributes_xml(xsd_element, help_xml):
    if xsd_element.ref:
        ref_name = xsd_element.ref
        sub = ET.SubElement(help_xml, ref_name)
        ref_attributes = []
        try:
            ref_attributes = cli_utils.xsd_elements_dict[ref_name] if ref_name in cli_utils.xsd_elements_dict else cli_utils.unknown_xsd_elements_dict[ref_name]
        except Exception:
            pass
        for r in ref_attributes:
            __prepare_attributes_xml(r, sub)
    elif xsd_element.base:
        base_name_type = xsd_element.base
        if base_name_type in cli_utils.name_type_dict:
            base_attributes = cli_utils.xsd_elements_dict[cli_utils.name_type_dict[base_name_type]]
        else:
            base_attributes = cli_utils.unknown_xsd_elements_dict[base_name_type]
        for b in base_attributes:
            __prepare_attributes_xml(b, help_xml)
    elif xsd_element.type and not xsd_element.type.startswith('xs'):
        ref_name = xsd_element.type
        ref_attributes = cli_utils.xsd_elements_dict[ref_name] if ref_name in cli_utils.xsd_elements_dict else cli_utils.unknown_xsd_elements_dict[ref_name]
        sub = ET.SubElement(help_xml, xsd_element.name)
        for r in ref_attributes:
            __prepare_attributes_xml(r, sub)
    else:
        new_xml = help_xml
        sub = ET.SubElement(help_xml, xsd_element.name)
        if not xsd_element.type:
            new_xml = sub
        if xsd_element.children:
            for c in xsd_element.children:
                __prepare_attributes_xml(c, new_xml)

    return

def get_file_location(file_dir, filename):
    src_dir = os.path.dirname( __file__ )
    parent_dir = os.path.split(src_dir)[0]
    return os.path.join(parent_dir, file_dir, filename)

def find_paths(found_paths, curr_context, find_me, full_key=''):
    for first_key, first_value in curr_context.items():
        if Constants.ACTIONS_KEY == first_key:
            continue

        path_now = full_key + "/" + first_key
        if find_me in path_now:
            found_paths.append(path_now)

        if isinstance(first_value, dict):
            find_paths(found_paths, first_value, find_me, path_now)

def get_search_path_by_key(key, context):
    found_paths = list()
    find_paths(found_paths, context, key)
    search_path = key+"s/search"
    for p in found_paths:
        if search_path in p:
            return p
    return None

