import configparser
import sys
import CommonUtil
import os

VIPR_HOST = None
VIPR_PORT = 4443
PICKLE_FILE_NAME = None
COOKIE_DIR_ABS_PATH = None

def load_config():
    global VIPR_HOST, VIPR_PORT, PICKLE_FILE_NAME, COOKIE_DIR_ABS_PATH
    parser = configparser.ConfigParser()
    try:
        config_file = CommonUtil.get_file_location('config', 'cli_config.ini')
        parser.read(config_file)
        VIPR_HOST = parser['vipr']['HOST']
        VIPR_PORT = parser['vipr']['PORT']
        PICKLE_FILE_NAME = parser['input']['PICKLE_FILE']
        COOKIE_DIR_ABS_PATH = parser['general']['COOKIE_DIR_ABS_PATH']

        if not COOKIE_DIR_ABS_PATH:
            COOKIE_DIR_ABS_PATH = os.path.dirname( __file__ )

    except:
        print('Error occurred reading ViPR config file:%s,%s' %(sys.exc_info()[0],sys.exc_info()[1]))
