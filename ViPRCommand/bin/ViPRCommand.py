"""
Copyright EMC Corporation 2015.
Distributed under the MIT License.
(See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
"""

"""
This is main class when invoked will connect to ViPR and open prompt to run commands.
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
from CLIInputs import CLIInputs
import logging
import logging.config

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
    # Initiating logging
    logs_dir = CommonUtil.get_file_dir_location('logs')
    log_config_path = CommonUtil.get_file_location('config', 'logging.conf')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    os.environ['ViPR_COMMAND_LOG_DIR'] = logs_dir
    logging.config.fileConfig(log_config_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.info("## Starting ViPRCommand ##")

    ConfigUtil.load_config()

    # Get username, password from arguments or prompt user
    if sys.argv and len(sys.argv) > 1:
        if sys.argv[1] == "help" or len(sys.argv) != 5:
            print("python ViPRCommand -u name -p password")
            sys.exit()
        user = sys.argv[2]
        pswd = sys.argv[4]
        print("Connecting to ViPR: %s" % ConfigUtil.VIPR_HOST)
    else:
        print("Connecting to ViPR: %s" % ConfigUtil.VIPR_HOST)
        # user = input("login as: ")
        try: input = raw_input
        except NameError: pass
        user = input("login as: ")
        pswd = getpass.getpass()

    # Login user
    cookie = login(user, pswd)
    logger.info("Logged in as user %s" % user)

    # Get ViPR version - used to name pickle file
    response = ViPRConnection.submitHttpRequest('GET', VERSION_URI, cookie)
    version_json = json.loads(response.text)
    vipr_version = version_json["target_version"]
    logger.info("ViPR Version: %s" % vipr_version)

    # pickle file name format:  {vipr_version}-context.pickle
    pickle_file_name = Constants.PICKLE_FILE_NAME.format(vipr_version)
    pickle_dir_path = CommonUtil.get_file_dir_location('pickles')
    pickle_file_path = os.path.join(pickle_dir_path, pickle_file_name)
    logger.info("Pickle file: %s" % pickle_file_name)

    # Check if this pickle version is available
    if not os.path.exists(pickle_file_path):
        logger.info("Pickle file not found, so creating")
        # Create directory if it doesn't exist
        descriptors_dir_path = CommonUtil.get_file_dir_location('descriptors')
        if not os.path.exists(descriptors_dir_path):
            os.makedirs(descriptors_dir_path)
        if not os.path.exists(pickle_dir_path):
            os.makedirs(pickle_dir_path)

        # GET WADLs and XSDs
        response = ViPRConnection.submitHttpRequest('GET', WADL_URI, cookie, xml=True)
        with open(os.path.join(descriptors_dir_path, 'application.xml'), 'w+') as f:
            f.write(response.text)

        response = ViPRConnection.submitHttpRequest('GET', SYSSVC_WADL_URI, cookie, xml=True)
        with open(os.path.join(descriptors_dir_path, 'syssvc-application.xml'), 'w+') as f:
            f.write(response.text)

        response = ViPRConnection.submitHttpRequest('GET', XSD_URI, cookie, xml=True)
        if not response:
            raise Exception('XSD not found')
        with open(os.path.join(descriptors_dir_path, 'xsd0.xsd'), 'w+') as f:
            f.write(response.text)

        response = ViPRConnection.submitHttpRequest('GET', SYSSVC_XSD_URI, cookie, xml=True)
        if not response:
            raise Exception('System service XSD not found')
        with open(os.path.join(descriptors_dir_path, 'syssvc-xsd0.xsd'), 'w+') as f:
            f.write(response.text)

        # Parse WADLs and XSDs and store data to pickle file
        CreateInputs.create_inputs(pickle_file_path)

    # Read pickle file and store to variable: cli_inputs
    with open(pickle_file_path, 'rb') as f:
        cli_inputs = CLIInputs()
        cli_inputs.wadl_context = pickle.load(f)
        cli_inputs.xsd_elements_dict = pickle.load(f)
        cli_inputs.unknown_xsd_elements_dict = pickle.load(f)
        cli_inputs.name_type_dict = pickle.load(f)

    prompt = MyCmd(cli_inputs)
    prompt.prompt = 'ViPRCommand:/> '
    prompt.cmdloop('Starting ViPR Command...')

except Exception as e:
    print(str(e))