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

try:
    ConfigUtil.load_config()
    with open(CommonUtil.get_file_location('pickles', ConfigUtil.PICKLE_FILE_NAME), 'rb') as f:
        cli_inputs = pickle.load(f)
    #print(cli_inputs.wadl_context)

    prompt = MyCmd(cli_inputs)
    prompt.prompt = 'ViPRcli:/> '
    prompt.cmdloop('Starting ViPR CLI...')

except Exception as e:
    print(e)
    import traceback
    traceback.print_exc()