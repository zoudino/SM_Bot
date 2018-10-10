def validate_CI(ci):
    # building the connection and putting all the CI data into the array.
    # feeling confused about
    with open("./CI.json", "r") as read_file:
        data_api = json.load(read_file)
    all_CIs = []
    answer = False
    for x in range(len(data_api['content'])):
        all_CIs.append(data_api['content'][x]['ucmdbNode']['ConfigurationItem'])
    for y in range(len(all_CIs)):
        if ci == all_CIs[y]:
            answer = True

    return answer

def get_all_CI():
    url = 'http://157.56.181.15:13080/SM/9/rest/ucmdbNodes'
    data = requests.get(url, auth=HTTPBasicAuth('chatbot', 'CHATBOT')).json()
    with open('./CI.json','w') as outfile:
        json.dump(data, outfile)


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