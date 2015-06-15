"""
Copyright 2015 EMC Corporation
All Rights Reserved
EMC Confidential: Restricted Internal Distribution
81ff427ffd0a66013a8e07b7b967d6d6b5f06b1b.ViPR
"""

from CmdUtil import MyCmd
import pickle
import ConfigUtil
import CommonUtil
import os
import sys
import getpass
import ViPRConnection
import Constants
import json
import CreateInputs

VERSION_URI = "/upgrade/target-version"
WADL_URI = "/application.wadl"
XSD_URI = "/application.wadl/xsd0.xsd"
SYSSVC_WADL_URI = "/syssvc-application.wadl"
SYSSVC_XSD_URI = "/syssvc-application.wadl/xsd0.xsd"

def login(user, pswd):
    """ Log into ViPR """
    cookie = ViPRConnection.login(user, pswd)
    if cookie:
        #print("Copying cookie to: %s" % os.path.join(COOKIE_DIR, COOKIE_FILE_NAME))
        with open(os.path.join(ConfigUtil.COOKIE_DIR_ABS_PATH, Constants.COOKIE_FILE_NAME), 'w+') as f:
            f.write(cookie)
    return cookie

try:

    ConfigUtil.load_config()

    # Get username, password from arguments or prompt user
    if sys.argv and len(sys.argv) > 1:
        if sys.argv[1] == "help" or len(sys.argv) != 5:
            print()
            print("Ensure that the host name/ip in the config/cli_config.ini file is updated before running the ViPRShell command")
            print()
            print("python ViPRShell -u name -p password")
            sys.exit()
        user = sys.argv[2]
        pswd = sys.argv[4]
    else:
        user = input("login as: ")
        pswd = getpass.getpass()

    # Login user
    cookie = login(user, pswd)

    # Get ViPR version
    response = ViPRConnection.submitHttpRequest('GET', VERSION_URI, cookie)
    version_json = json.loads(response.text)
    vipr_version = version_json["target_version"]

    pickle_file_name = Constants.PICKLE_FILE_NAME.format(vipr_version)
    # Check if this pickle version is available
    if not os.path.isfile(pickle_file_name):
        # Create directory if it doesn't exist
        if not os.path.exists('../descriptors'):
            os.makedirs('../descriptors')
        if not os.path.exists('../pickles'):
            os.makedirs('../pickles')

        # GET WADLs and XSDs
        response = ViPRConnection.submitHttpRequest('GET', WADL_URI, cookie, xml=True)
        with open('../descriptors/application.xml', 'w+') as f:
            f.write(response.text)
        response = ViPRConnection.submitHttpRequest('GET', SYSSVC_WADL_URI, cookie, xml=True)
        with open('../descriptors/syssvc-application.xml', 'w+') as f:
            f.write(response.text)
        response = ViPRConnection.submitHttpRequest('GET', XSD_URI, cookie, xml=True)
        if not response:
            raise Exception('XSD not found')
        with open('../descriptors/xsd0.xsd', 'w+') as f:
            f.write(response.text)
        response = ViPRConnection.submitHttpRequest('GET', SYSSVC_XSD_URI, cookie, xml=True)
        if not response:
            raise Exception('System service XSD not found')
        with open('../descriptors/syssvc-xsd0.xsd', 'w+') as f:
            f.write(response.text)

        CreateInputs.create_inputs(pickle_file_name)

    with open(CommonUtil.get_file_location('pickles', pickle_file_name), 'rb') as f:
        cli_inputs = pickle.load(f)

    prompt = MyCmd(cli_inputs)
    prompt.prompt = 'ViPRShell:/> '
    prompt.cmdloop('Starting ViPR Shell...')

except Exception as e:
    print(e)
    #import traceback
    #traceback.print_exc()