"""
Copyright 2015 EMC Corporation
All Rights Reserved
EMC Confidential: Restricted Internal Distribution
81ff427ffd0a66013a8e07b7b967d6d6b5f06b1b.ViPR
"""

import json
import requests
requests.packages.urllib3.disable_warnings()
import xml.etree.ElementTree as ET
import ConfigUtil

LOGIN_URI = "/login"
LOGOUT_URI = "/logout"
SEC_AUTHTOKEN_HEADER = "X-SDS-AUTH-TOKEN"

session = requests.session()

def _getURL(uri):
    return "https://{0}:{1}{2}".format(ConfigUtil.VIPR_HOST, ConfigUtil.VIPR_PORT, uri)

def set_logger(self, logger):
    self._logger = logger

def login(user, password):
    global session
    url = _getURL(LOGIN_URI)
    headers = {'ACCEPT': 'application/json'}
    if session:
        session.close()
    session = requests.session()
    response = session.get(url, auth=(user, password), verify=False, headers=headers)
    #self.print_package(response)
    if response.status_code != requests.codes['ok']:
        # for invalid credentials ViPR returns html
        if 'text/html' in response.headers['Content-Type']:
            err = "Invalid username or password"
        else:
            error_json = json.loads(response.text)
            err = error_json["details"]
        raise Exception(err)
    if 'x-sds-auth-token' not in response.headers:
        raise Exception("Invalid Login")
    token = response.headers['x-sds-auth-token']

    return token

def logout(token):
    submitHttpRequest("GET", LOGOUT_URI, token)
    session.close()

def getHeaders(token, contentType='application/json', xml=False):
    if (xml):
        headers = {'Content-Type': contentType, 'ACCEPT': 'application/xml, application/octet-stream'}
    else:
        headers = {'Content-Type': contentType, 'ACCEPT': 'application/json, application/octet-stream'}
    headers[SEC_AUTHTOKEN_HEADER] = token
    return headers

def submitHttpRequest(httpMethod, uri, token, contentType='application/json', payload=None, xml=False):
    headers = getHeaders(token, contentType, xml)
    url = _getURL(uri)

    if httpMethod == 'GET':
        response = session.get(url, verify=False, headers=headers)
    elif httpMethod == 'POST':
        response = session.post(url, data=payload, verify=False, headers=headers)
    elif httpMethod == 'PUT':
        response = session.put(url, data=payload, headers=headers, verify=False)
    else:
        raise Exception("Unknown/Unsupported HTTP method: " + httpMethod)
    if response.status_code == requests.codes['ok'] or response.status_code == 202:
            #_logger.debug("Response: %s" % response.text)
            return response
    else:
        if response.status_code == 401:
            # 401 response is html, so not parsing response
            error_details = "Unauthorized"
        elif 'text/html' in response.headers['Content-Type']:
            root = ET.fromstring(response.text)
            print(response.text)
            error_details = root.find("head/title").text
        else:
            error_json = json.loads(response.text)
            if "details" in error_json:
                error_details = error_json["details"]
            else:
                error_details = response.reason

        raise Exception("%s: %s" % (str(response.status_code), error_details))

