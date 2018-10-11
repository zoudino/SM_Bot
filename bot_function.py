import requests
from requests.auth import HTTPBasicAuth
import json
from httplib2 import Http
import socket


def validate_CI(ci):
    # building the connection and putting all the CI data into the array.
    # feeling confused about
    with open("./CI.json", "r") as read_file:
        data_api = json.load(read_file)
    all_CIs = []
    answer = False
    for x in range(len(data_api['content'])):
        all_CIs.append(data_api['content'][x]['Computer']['ConfigurationItem'].lower())
    for y in range(len(all_CIs)):
        if ci == all_CIs[y]:
            answer = True
    return answer

#
def get_all_CI():
    url = 'http://157.56.181.15:13080/SM/9/rest/computers'
    data = requests.get(url, auth=HTTPBasicAuth('chatbot', 'CHATBOT')).json()
    result = 'success'
    with open('./CI.json','w') as outfile:
        json.dump(data, outfile)
    return result

def create_ticket(CI_value, change_request):
    CI_value = CI_value.upper()
    # now, we need to create a ticket
    url_request = 'http://157.56.181.15:13080/SM/9/rest/requests'
    # Define the Json data to create a ticket
    request_data = {
        "Request": {
        "AffectedCI": "" + CI_value,
        "AffectedService":"CI1013981",
        "AssignedGroup": "Asset Management",
        "BriefDescription": "Test!! Please ignore. Asset Update Request - "+ CI_value + " " + change_request,
        "Subcategory": "Universal",
        "Description": [
            "This is for test purpose. Please ignore it. Thanks for your understanding. "
        ],
        "Impact": "4",
        "Model": "Universal",
        "ModelName": "Universal",
        "Priority": "4",
        "Reason": "4",
        "Source":"5 - Chat",
        "RequestorName": "Dino Zou",
        "Status": ""+ change_request,
        "Urgency": "3"
        }
    }
    # We post the value in here. If we got success, the system will return a json
    resp = requests.post(url = url_request, auth=HTTPBasicAuth('chatbot', 'CHATBOT'),json= request_data)
    if resp.status_code == 200:
          # extract the ticket number and return to the user
          ticket = resp.json()
          ticket = ticket['Request']['Number']
          result = "Congrats!! We created a ticket for you. Write it down on your paper " + ticket
          return result
    else:
        return resp.status_code
        # if we get success, we should return a ticket number to the user

def check_IP_address(ip):
    """
       Building the connection wit service manager
       url = 'http://157.56.181.15:13080/SM/9/rest#Computer'
       data = requests.get(url,auth = HTTPBasicAuth('chatbot','CHATBOT')).json()
    """
    fake_data = ['127.0.0.1']
    if ip == fake_data[0]:
        return True
    else:
        return False

def validate_IP_address(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False
