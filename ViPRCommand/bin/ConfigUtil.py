"""
Copyright EMC Corporation 2015.
Distributed under the MIT License.
(See accompanying file LICENSE or copy at http://opensource.org/licenses/MIT)
"""

""" This class parses config file: cli_config.ini """

import configparser
import sys
import CommonUtil
import os
import logging

VIPR_HOST = None
VIPR_PORT = 4443
COOKIE_DIR_ABS_PATH = None


# This method is called once when main class is invoked
def load_config():
    logger = logging.getLogger(__name__)
    global VIPR_HOST, VIPR_PORT, COOKIE_DIR_ABS_PATH
    parser = configparser.ConfigParser()
    try:
        config_file = CommonUtil.get_file_location('config', 'cli_config.ini')
        parser.read(config_file)
        VIPR_HOST = parser['vipr']['HOST']
        VIPR_PORT = parser['vipr']['PORT']
        COOKIE_DIR_ABS_PATH = parser['general']['COOKIE_DIR_ABS_PATH']

        if not COOKIE_DIR_ABS_PATH:
            COOKIE_DIR_ABS_PATH = os.path.dirname( __file__ )

        logger.info("ViPR host: %s" % VIPR_HOST)
        logger.info("ViPR port: %s" % VIPR_PORT)
        logger.info("Cookie path: %s" % COOKIE_DIR_ABS_PATH)

    except:
        print('Error occurred reading ViPR config file:%s,%s' %(sys.exc_info()[0],sys.exc_info()[1]))
