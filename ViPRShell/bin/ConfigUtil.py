"""
Copyright 2015 EMC Corporation
All Rights Reserved
EMC Confidential: Restricted Internal Distribution
81ff427ffd0a66013a8e07b7b967d6d6b5f06b1b.ViPR
"""

import configparser
import sys
import CommonUtil
import os
import logging

VIPR_HOST = None
VIPR_PORT = 4443
COOKIE_DIR_ABS_PATH = None


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
