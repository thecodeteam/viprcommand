import xml.etree.ElementTree as ET
from collections import OrderedDict
import XSDParser
import pickle
from CLIInputs import CLIInputs
from CLIInputs import ActionParams

cli_inputs = CLIInputs()
ACTIONS_KEY = 'actions'
ID_START = '{'
ID_KEY = '{id}'


def method_param_parser(element):
    if 'search' == element.get('id'):
        action_params = ActionParams()
        action_params.query_params["name"] = "xs:string"
        action_params.query_params["tag"] = "xs:string"
        action_params.query_params["project"] = "xs:string"
        action_params.query_params["wwn"] = "xs:string"
        action_params.query_params["initiator_port"] = "xs:string"
        return action_params

    for req in element:
        if 'request' in req.tag:
            action_params = ActionParams()
            for rep in req:
                if 'param' in rep.tag:
                    action_params.query_params[rep.get("name")] = rep.get("type")
                elif 'representation' in rep.tag:
                    action_params.method_name = rep.get('element')
            return action_params
    return None


def parse_wadl(wadl_file_name):
    global child3_dict
    tree = ET.parse(wadl_file_name)
    root = tree.getroot()

    for child in root:
        tag = child.tag
        tag_name = tag[tag.index('}')+1:]
        if 'resources' == tag_name:
            for child2 in child:
                child2_tag = child2.tag
                child2_tag_name = child2_tag[child2_tag.index('}')+1:]
                if 'resource' == child2_tag_name:
                    child2_path = child2.get('path')
                    path_arr = [x for x in child2_path.split('/') if x]

                    if path_arr and 'internal' == path_arr[0]:
                        continue

                    parent_context = cli_inputs.wadl_context
                    for p in path_arr:
                        if ID_START in p:
                            p = ID_KEY
                        if p not in parent_context:
                            parent_context[p] = dict()
                            #break
                        parent_context = parent_context[p]

                    super_actions = parent_context[ACTIONS_KEY] if ACTIONS_KEY in parent_context else dict()
                    for child3 in child2:
                        child3_tag = child3.tag
                        child3_tag_name = child3_tag[child3_tag.index('}')+1:]
                        if 'resource' == child3_tag_name:
                            # Build sub-context
                            child3_path = child3.get('path')
                            #path_arr = child3_path[1:].split('/')
                            path_arr = [x for x in child3_path.split('/') if x]

                            curr_context = parent_context
                            child3_dict = dict()
                            for p in path_arr:
                                if ID_START in p:
                                    p = ID_KEY
                                if p not in curr_context:
                                    curr_context[p] = dict()
                                curr_context = curr_context[p]

                            # loop through children
                            actions = curr_context[ACTIONS_KEY] if ACTIONS_KEY in curr_context else dict()
                            for child4 in child3:
                                child4_name = child4.get('name')
                                if child4_name not in ['GET', 'POST', 'PUT']:
                                    # ignoring param elements for {id}
                                    continue
                                # TODO: create Action object
                                actions[child4_name] = method_param_parser(child4)
                            curr_context[ACTIONS_KEY] = actions
                        else:
                            # Add methods
                            child3_name = child3.get('name')
                            if child3_name not in ['GET', 'POST', 'PUT']:
                                # ignoring param elements for {id}
                                continue
                            # TODO: create Action object
                            super_actions[child3_name] = method_param_parser(child3)
                    if super_actions:
                        parent_context[ACTIONS_KEY] = super_actions


# moving leaf context that has only POST as Actions
def post_process_context():
    modify_values = dict()
    look_for_post_actions(modify_values, cli_inputs.wadl_context, '')
    for path, val in modify_values.items():
        temp_context = cli_inputs.wadl_context
        path_arr = [x for x in path.split('/') if x]
        for p in path_arr[:-1]:
            temp_context = temp_context[p]
        if ACTIONS_KEY in temp_context:
            actions_dict = temp_context[ACTIONS_KEY]
        else:
            actions_dict = dict()
            temp_context[ACTIONS_KEY] = actions_dict

        action = path_arr[-1]
        temp_context.pop(action)
        actions_dict[action] = val
    #print(modify_values)

def look_for_post_actions(modify_values, curr_context, full_key):
    for first_key, first_value in curr_context.items():
        # if value is just 'actions' with only 'POST'
        if isinstance(first_value, dict) and len(first_value) == 1 and ACTIONS_KEY in first_value:
            actions = first_value[ACTIONS_KEY]
            if len(actions) == 1 and 'POST' in actions:
                post_obj = actions['POST']
                modify_values[full_key + "/" + first_key] = post_obj

        # look for POST in child paths
        if ACTIONS_KEY != first_key and isinstance(first_value, dict):
            look_for_post_actions(modify_values, first_value, full_key + "/" + first_key)


try:
    parse_wadl('../descriptors/application.xml')
    post_process_context()
    print(cli_inputs.wadl_context)

    XSDParser.parse_xsd('../descriptors/xsd0.xsd', cli_inputs)

    with open('../pickles/ViPR-2.1-context.pickle', 'wb') as f:
        pickle.dump(cli_inputs, f)


except Exception as e:
    print(e)
    import traceback
    traceback.print_exc()

#ordered_context = OrderedDict(sorted(context.items(), key=lambda t: t[0]))
#print(ordered_context)

