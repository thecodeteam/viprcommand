"""
Copyright 2015 EMC Corporation
All Rights Reserved
EMC Confidential: Restricted Internal Distribution
81ff427ffd0a66013a8e07b7b967d6d6b5f06b1b.ViPR
"""

from cmd import Cmd
import ViPRConnection
import os
import json
import CommonUtil
import xml.dom.minidom
import shlex
import xml.etree.cElementTree as ET
import ConfigUtil
import logging

logger = logging.getLogger(__name__)
ID_KEY = '{id}'
BULK_KEY = 'bulk'
RESPONSE_TYPE_KEY = 'accept'
RESPONSE_TYPE_XML = 'xml'
RESPONSE_TYPE_JSON = 'json'
PARAMS_KEY = 'params'
ACTIONS_KEY = 'actions'
COOKIE_FILE_NAME = 'cf'

class MyCmd(Cmd):

    curr_context = None
    curr_path = None


    def __init__(self, cli_utils):
        Cmd.__init__(self)
        global curr_context, curr_path, execute_action
        self._context = cli_utils.wadl_context
        curr_context = cli_utils.wadl_context
        curr_path = ''
        execute_action = ''
        cli_utils = cli_utils
        CommonUtil.cli_utils = cli_utils

    def do_quit(self, args):
        """Quits the program."""
        logger.info("CMD: quit")
        self.do_logout(args)
        print("Quitting.")
        raise SystemExit

    def do_ls(self, args):
        """ lists resources """
        logger.info("CMD: ls %s" % args)
        try:
            if args:
                if args.startswith('/'):
                    temp_context = self.__get_context_for_path(args[1:], self._context)
                else:
                    temp_context = self.__get_context_for_path(args, curr_context)
            else:
                temp_context = curr_context

            if temp_context:

                sub_context = list(temp_context.keys())

                # Remove actions from here and print it separately
                actions_dict = None
                if ACTIONS_KEY in temp_context:
                    actions_dict = temp_context[ACTIONS_KEY]
                    sub_context.remove(ACTIONS_KEY)

                if ID_KEY in temp_context and BULK_KEY in temp_context:
                    # Print ids if 'bulk' is present
                    sub_context.remove(ID_KEY)
                    try:
                        cookie = self.__get_cookie()
                        response = ViPRConnection.submitHttpRequest('GET', curr_path+"/bulk", cookie)
                        if response:
                            self.__print_bulk_response(response.text)
                    except Exception as e:
                        print(str(e))
                        logger.error(str(e))
                elif ID_KEY in temp_context and ACTIONS_KEY in temp_context and 'GET' in temp_context[ACTIONS_KEY]:
                    # Print ids if 'GET' is present
                    sub_context.remove(ID_KEY)
                    try:
                        cookie = self.__get_cookie()
                        response = ViPRConnection.submitHttpRequest('GET', curr_path, cookie)
                        if response:
                            self.__print_get_all_response(response.text)
                    except Exception as e:
                        print(str(e))
                        logger.error(str(e))

                print('  '.join(sub_context))

                # Print actions
                if actions_dict:
                    print('\nActions:-')
                    print('  '.join(actions_dict.keys()))
            else:
                print('Wrong path')
        except Exception as e:
            print(str(e))

    def do_ll(self, args):
        """ List resources in detail """
        logger.info("CMD: ll %s" % args)
        try:
            if args:
                if args.startswith('/'):
                    temp_context = self.__get_context_for_path(args[1:], self._context)
                else:
                    temp_context = self.__get_context_for_path(args, curr_context)
            else:
                temp_context = curr_context

            if temp_context:
                sub_context = list(temp_context.keys())

                # Remove actions from here and print it separately
                actions_dict = None
                if ACTIONS_KEY in temp_context:
                    actions_dict = temp_context[ACTIONS_KEY]
                    sub_context.remove(ACTIONS_KEY)

                if ID_KEY in temp_context and BULK_KEY in temp_context:
                    # Print ids if 'bulk' is present
                    sub_context.remove(ID_KEY)
                    try:
                        cookie = self.__get_cookie()
                        # TODO: check if bulk exists
                        response = ViPRConnection.submitHttpRequest('GET', curr_path+"/bulk", cookie)
                        if response:
                            detail_response = ViPRConnection.submitHttpRequest('POST', curr_path+"/bulk", cookie, payload=response.text)
                            if detail_response:
                                self.__print_ll_response(detail_response.text)
                    except Exception as e:
                        print(str(e))
                        logger.error(str(e))

                elif ID_KEY in temp_context and ACTIONS_KEY in temp_context and 'GET' in temp_context[ACTIONS_KEY]:
                    # Print ids if 'GET' is present
                    sub_context.remove(ID_KEY)
                    try:
                        cookie = self.__get_cookie()
                        response = ViPRConnection.submitHttpRequest('GET', curr_path, cookie)
                        if response:
                            self.__print_ll_response(response.text)
                    except Exception as e:
                        print(str(e))
                        logger.error(str(e))

                print('  '.join(sub_context))

                if actions_dict:
                    print('\nActions:-')
                    print('  '.join(actions_dict.keys()))
            else:
                print('Wrong path')
        except Exception as e:
            print(str(e))
            logger.error(str(e))

    def do_cd(self, args):
        """change context"""
        logger.info("CMD: cd %s" % args)
        global curr_context, curr_path
        if args:
            if args == '..':
                last_index = curr_path.rfind('/')
                if last_index == 0:
                    last_index = 1
                args = curr_path[:last_index]
            if args.startswith('/'):
                temp_context = self.__get_context_for_path(args[1:], self._context)
                if temp_context:
                    curr_context = temp_context
                    if args != '/':
                        curr_path = args
                    else:
                        curr_path = ''
                else:
                    print('Wrong path')
                    logger.error("Wrong path %s" % args)
            else:
                temp_context = self.__get_context_for_path(args, curr_context)
                if temp_context:
                    curr_context = temp_context
                    curr_path += '/' + args
                else:
                    print('Wrong path')
                    logger.error("Wrong path %s" % args)
            self.prompt = 'ViPRShell:' + curr_path + '/>'
        return

    def do_GET(self, args):
        """ GET resource """
        logger.info("CMD: GET %s" % args)
        try:
            if ACTIONS_KEY not in curr_context:
                print('GET is not available')
                return

            actions_dict = curr_context[ACTIONS_KEY]
            if 'help' == args:
                if actions_dict['GET']:
                    CommonUtil.print_query_params(actions_dict['GET'].query_params)
                return

            cookie = self.__get_cookie()
            args_dict = self.__convert_args_to_dict(args)
            query_str = ''
            if actions_dict['GET'] and actions_dict['GET'].query_params:
                query_str = self.__process_return_query_params(args_dict, actions_dict['GET'].query_params)
            accept_type = args_dict[RESPONSE_TYPE_KEY] if RESPONSE_TYPE_KEY in args_dict else ''
            response = ViPRConnection.submitHttpRequest('GET', curr_path+query_str, cookie, xml=True if accept_type == RESPONSE_TYPE_XML else False)
            if response:
                self.__print_response(response.text, accept_type)
        except Exception as e:
            print(str(e))
            logger.error(str(e))

    def do_POST(self, args):
        """ Create resource """
        logger.info("CMD: POST %s" % args)
        global execute_action
        try:
            if ACTIONS_KEY not in curr_context:
                print('POST is not available')
                return

            actions_dict = curr_context[ACTIONS_KEY]
            # this is used when any default action is called
            if execute_action:
                curr_action = execute_action
            else:
                curr_action = 'POST'

            if 'help' == args:
                if actions_dict[curr_action]:
                    CommonUtil.print_query_params(actions_dict[curr_action].query_params)
                    CommonUtil.print_attributes(actions_dict[curr_action].method_name)
                return

            post_payload, query_str, content_type = self.__process_args(args, actions_dict[curr_action])
            cookie = self.__get_cookie()
            if execute_action:
                post_url = curr_path + '/' + execute_action
            else:
                post_url = curr_path

            response = ViPRConnection.submitHttpRequest('POST', post_url+query_str, cookie, payload=post_payload, contentType=content_type)
            if response:
                self.__print_response(response.text)
        except Exception as e:
            print(str(e))
            logger.error(str(e))

    def do_PUT(self, args):
        """ Update resource """
        logger.info("CMD: PUT %s" % args)
        try:
            if ACTIONS_KEY not in curr_context:
                print('PUT is not available')
                return

            actions_dict = curr_context[ACTIONS_KEY]
            if 'help' == args:
                if actions_dict['PUT']:
                    CommonUtil.print_query_params(actions_dict['PUT'].query_params)
                    CommonUtil.print_attributes(actions_dict['PUT'].method_name)
                return

            put_payload, query_str, content_type = self.__process_args(args, actions_dict['PUT'])
            cookie = self.__get_cookie()
            response = ViPRConnection.submitHttpRequest('PUT', curr_path+query_str, cookie, payload=put_payload, contentType=content_type)
            if response:
                self.__print_response(response.text)
        except Exception as e:
            print(str(e))
            logger.error(str(e))

    def do_login(self, args):
        """ Log into ViPR """
        logger.info("CMD: login %s" % args)
        if not args:
            print("login -username name -password pswd")
        else:
            try:
                args_arr = args.split()
                if args_arr[0] == "help":
                    print("login -username name -password pswd")
                    return
                cookie = ViPRConnection.login(args_arr[1], args_arr[3])
                if cookie:
                    #print("Copying cookie to: %s" % os.path.join(COOKIE_DIR, COOKIE_FILE_NAME))
                    with open(os.path.join(ConfigUtil.COOKIE_DIR_ABS_PATH, COOKIE_FILE_NAME), 'w+') as f:
                        f.write(cookie)
            except Exception as e:
                print(str(e))
                logger.error(str(e))

    def do_logout(self, args):
        """ Log out from ViPR """
        cookie = None
        logger.info("CMD: logout")
        try:
            try:
                cookie = self.__get_cookie()
            except Exception as e:
                logger.info("Cookie not found")
                pass
            if cookie:
                print("Logging out")
                logger.info("Logging out user")
                ViPRConnection.logout(cookie)
                os.remove(os.path.join(ConfigUtil.COOKIE_DIR_ABS_PATH, COOKIE_FILE_NAME))
        except Exception as e:
            print(str(e))
            logger.error(str(e))

    # TODO: make this recursive
    def do_find(self, args):
        """ Search for context """
        logger.info("CMD: find %s" % args)
        if not args:
            return
        args_arr = args.split()
        find_me = args_arr[0]
        found_paths = list()
        CommonUtil.find_paths(found_paths, self._context, find_me)
        print('\n'.join(found_paths))



    def completedefault(self, text, line, begidx, endidx):
        if not text or text == '/':
            completions = list(self._context.keys())
        else:
            if text.startswith('/'):
                completions = self.__get_completions_for_partial_path(text[1:], self._context, True)
            else:
                completions = self.__get_completions_for_partial_path(text, curr_context)

        return completions

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    # TODO: args[0] can be path
    def default(self, args):
        global execute_action
        try:
            if not args:
                return

            args_arr = args.split()
            action = args_arr[0]
            if ACTIONS_KEY not in curr_context:
                print('%s is not available' % action)
                return

            actions_dict = curr_context[ACTIONS_KEY]
            if action not in actions_dict:
                print('%s is not available' % action)
                return

            execute_action = action
            self.do_POST(' '.join(args_arr[1:]))

        except Exception as e:
            print(str(e))
            logger.error(str(e))
        finally:
            execute_action = None

    def __get_context_for_path(self, path, context_search):
        temp_context = context_search
        if path:
            path_arr = path.split('/')
            for p in path_arr:
                if p in temp_context:
                    temp_context = temp_context[p]
                else:
                    # Check if {*id} exists in this context
                    id_keys = [x for x in temp_context.keys() if '{' in x]
                    # Assuming only one id key
                    if id_keys:
                        temp_context = temp_context[id_keys[0]]
                    else:
                        return None
        return temp_context

    def __get_completions_for_partial_path(self, path, context_search, start=False):
        path_arr = path.split('/')
        temp_context = context_search
        completions = []

        for p in path_arr[:-1]:
            key = self.__get_id_key(p)
            if key in temp_context:
                temp_context = temp_context[key]
            else:
                return []

        last_element = path_arr[len(path_arr)-1]
        prefix = '/'.join(path_arr[:-1])
        if prefix:
            prefix += '/'
        # start is TRUE for paths starting with '/', so adding it to prefix.
        if start:
            prefix = '/' + prefix
        for k in temp_context:
            if k.startswith(last_element):
                completions.append(prefix + k)
        return completions

    def __get_cookie(self):
        cookie = ''
        cf_path = os.path.join(ConfigUtil.COOKIE_DIR_ABS_PATH, COOKIE_FILE_NAME)
        if os.path.isfile(cf_path):
            with open(cf_path, 'r') as f:
                cookie = f.read()
        if not cookie:
            raise Exception("Cookie file not found. Login first")
        return cookie

    def __read_payload_file(self, fname):
        payload = None
        if os.path.isfile(fname):
            with open(fname, 'r') as f:
                payload = f.read()
        if not payload:
            raise Exception("Payload file not found")
        return payload

    def __print_bulk_response(self, response_text):
        response_json = json.loads(response_text)
        if response_json and response_json['id']:
            print('\n'.join(response_json['id']))
            print('')

    def __print_get_all_response(self, response_text):
        response_json = json.loads(response_text)
        if response_json:
            ids = list()
            for k, v in response_json.items():
                for item in v:
                    if 'id' in item:
                        ids.append(item['id'])
                    elif 'op_id' in item:
                        # this is only for tasks response
                        ids.append(item['op_id'])
                    else:
                        # This happens for san-fabrics API
                        ids.append(item)
                        #print('unknown item found')
                break
            if ids:
                print('\n'.join(ids))

    def __print_ll_response(self, response_text):
        response_json = json.loads(response_text)
        if response_json:
            table = [('ID', 'NAME')]
            for k, v in response_json.items():
                for item in v:
                    if 'id' in item:
                        table.append((item['id'], item['name']))
                    elif 'op_id' in item:
                        # this is only for tasks response
                        table.append((item['op_id'], item['name']))
                    else:
                        # This happens for san-fabrics API
                        table.append((item, ''))
                        #print('unknown item found')
                break
            CommonUtil.print_table(table)
            print(' ')

    # Check if key is ID, then convert to {id}
    def __get_id_key(self, key):
        if key and key.startswith('urn:'):
            return ID_KEY
        return key

    def __print_response(self, response_text, accept_type=''):
        if not response_text:
            return

        if accept_type == RESPONSE_TYPE_JSON:
            print(json.dumps(json.loads(response_text), indent=4))
        elif accept_type == RESPONSE_TYPE_XML:
            response_xml = xml.dom.minidom.parseString(response_text)
            print(response_xml.toprettyxml())
        else:
            response_json = json.loads(response_text)
            if response_json:
                table = [('Name', 'Value')]
                self.__prepare_response_Table(response_json, table)
                CommonUtil.print_table(table)

    def __prepare_response_Table(self, element, table, prefix=''):
        if isinstance(element, list):
            for e in element:
                self.__prepare_response_Table(e, table, prefix)
        elif isinstance(element, dict):
            for k,v in element.items():
                if not isinstance(v, dict) and not isinstance(v, list):
                    table.append((prefix+k, str(v)))
                else:
                    table.append((prefix+k, ''))
                    self.__prepare_response_Table(v, table, prefix+'  ')
        else:
            table.append(('', str(element)))

    def __convert_args_to_dict(self, args):
        args_dict = dict()
        if args:
            args_arr = shlex.split(args)
            # TODO: check for array out of bounds
            for key, val in zip(args_arr[0::2], args_arr[1::2]):
                key = key[1:]
                if ':' in key:
                    # dict object
                    key_arr = key.split(':')
                    curr_dict = args_dict
                    for k in key_arr[:-1]:
                        if not k in curr_dict:
                            curr_dict[k] = dict()
                        curr_dict = curr_dict[k]
                    curr_dict[key_arr[-1]] = self.__parse_arg_val(val)
                else:
                    args_dict[key] = self.__parse_arg_val(val)
        return args_dict

    def __process_args(self, args, action_params_obj=None):
        query_str = ''
        content_type = 'application/xml'
        payload = ''
        if args and action_params_obj:
            root_element = action_params_obj.method_name
            query_params = action_params_obj.query_params.keys()

            root = ET.Element(root_element)
            args_arr = shlex.split(args)
            # Checking for direct json or xml file
            if args_arr[0] == 'json':
                payload = self.__read_payload_file(args_arr[1])
                content_type = 'application/json'
            elif args_arr[0] == 'xml':
                payload = self.__read_payload_file(args_arr[1])
                content_type = 'application/xml'
            else:
                # TODO: check for array out of bounds
                for key, val in zip(args_arr[0::2], args_arr[1::2]):
                    key = key[1:]

                    # check if val is "name:xxx", if so convert name to ID
                    val = self.__process_arg_val(key, val)

                    if key in query_params:
                        query_str += key+'='+val+'&'
                        continue
                    curr_element = root
                    if ':' in key:
                        key_arr = key.split(':')

                        for k in key_arr[:-1]:
                            sub = curr_element.find(k)
                            if not sub:
                                sub = ET.SubElement(curr_element, k)
                            curr_element = sub
                        child_element_tag = key_arr[-1]
                    else:
                        child_element_tag = key

                    if ',' in val:
                        val_arr = [x for x in val.split(',') if x]
                        for v in val_arr:
                            sub = ET.SubElement(curr_element, child_element_tag)
                            sub.text = v
                    else:
                        curr_element = ET.SubElement(curr_element, child_element_tag)
                        curr_element.text = val

                payload = ET.tostring(root) #encoding='utf8'
        return payload, '?' + query_str[:-1] if query_str else '', content_type

    def __process_arg_val(self, arg_key, arg_val):
        if 'name:' in arg_val:
            name = arg_val.split(':', 1)[1]
            return self.__get_id_by_key(arg_key, name, self._context)
        return arg_val

    def __parse_arg_val(self, arg_val):
        if ',' in arg_val:
            return arg_val.split(',')
        else:
            return arg_val

    # Remove query parameters from arguments dict and prepare them as URI query string
    def __process_return_query_params(self, args_dict, query_params_dict):
        query_str = ''
        for k, v in query_params_dict.items():
            if k in args_dict:
                query_str += k+'='+args_dict[k]+'&'
                args_dict.pop(k)
        if query_str:
            return '?' + query_str[:-1]
        return ''

    def __get_id_by_key(self, key, search_name, search_context):
        try:
            search_paths = CommonUtil.get_search_path_by_key(key, search_context)
            cookie = self.__get_cookie()
            # search for this name in all search paths
            for path in search_paths:
                response = ViPRConnection.submitHttpRequest('GET', path+"?name="+search_name, cookie)
                if response:
                    search_json = json.loads(response.text)
                    if search_json and search_json["resource"]:
                        return search_json["resource"][0]["id"]
        except Exception:
            raise Exception("Name: %s not found" % search_name)