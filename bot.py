import logging
import random
import requests
from requests.auth import HTTPBasicAuth
import json
from apiclient.discovery import build, build_from_document
from flask import Flask, render_template, request, json, make_response
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
import socket
# import a module
import bot_function
# setting the default deadline to solve the server not response issue
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)

app = Flask(__name__)
INTERACTIVE_TEXT_BUTTON_ACTION = "doTextButtonAction"
INTERACTIVE_IMAGE_BUTTON_ACTION = "doImageButtonAction"
INTERACTIVE_BUTTON_PARAMETER_KEY = "param_key"
BOT_HEADER = 'Card Bot Python'

"""This is coodinate to track the progress of the conversation. So, we can locate the u """
tracker = {"start":0, "1":0,"2":0,"3":0,"yes":0, "no":0,"cancel":0}
"Variables that will be used in checking information of the SM"
ip_address = ''
error_message = 0
CI = ''
username =''

@app.route('/', methods=['POST'])
def home_post():
    """Respond to POST requests to this endpoint.
    All requests sent to this endpoint from Hangouts Chat are POST
    requests.
    """
    event_data = request.get_json()
    resp = None
    global username
    # Extracting the username for 'hi'
    username = event_data["message"]["sender"]["email"]
    location = username.index('@globalpay.com')
    username = username[:location]

    # If the bot is removed from the space, it doesn't post a message
    # to the space. Instead, log a message showing that the bot was removed.
    if event_data['type'] == 'REMOVED_FROM_SPACE':
        logging.info('Bot removed from  %s' % event_data['space']['name'])
        return 'OK'

    elif event_data['type']  == 'ADDED_TO_SPACE' and event_data['space']['type'] == 'ROOM':
        resp = { 'text': ('Thanks for adding me to {}!'.format(event_data['space']['name'])) }

    elif event_data['type']  == 'ADDED_TO_SPACE' and event_data['space']['type'] == 'DM':
        resp = { 'text': ('Thanks for adding me to a DM, {}!'.format(event_data['user']['displayName'])) }

    elif event_data['type'] == 'MESSAGE':
        resp = create_card_response(event_data['message']['text']) # changed

    space_name = event_data['space']['name']

    logging.info(resp)

    # Uncomment the following line for a synchronous response.
    #return json.jsonify(resp)

    # Asynchronous response version:
    thread_id = None
    if event_data['message']['thread'] != None:
        thread_id = event_data['message']['thread']

    # Need to return a response to avoid an error in the Flask app
    send_async_response(resp, space_name, thread_id)
    return 'OK'

@app.route('/', methods=['GET'])
def home_get():
    return render_template('home.html')
    
def send_async_response(response, space_name, thread_id):
    """Sends a response back to the Hangouts Chat room asynchronouslyslls.
    Args:
      response: the response payload
      spaceName: The URL of the Hangouts Chat room
    """

    # The following two lines of code update the thread that raised the event.
    # Delete them if you want to send the message in a new thread.
    if thread_id != None:
        response['thread'] = thread_id
    ##################################
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('service-acct.json', scopes)
    http_auth = credentials.authorize(Http())
    chat = build('chat', 'v1', http=http_auth)
    chat.spaces().messages().create(
        parent=space_name,
        body=response).execute()



def create_card_response(event_message):

    response = dict()  
    cards = list()
    widgets = list()
    header = None

    global tracker, ip_address, error_message, CI, username

    words = event_message.lower().split()
    # Event message = @"Service Manager bot"  debug
    words = words[3:]

    # let's add some conversation into the bot. So, we can add some flexability into our chat.
    GREETING_KEYWORDS = ("hello", "hi","hey","what's up")
    for word in words:
        if word == 'header':
            header = {
                'header': {
                    'title': 'Service Manager Ticket Support',
                    'subtitle': 'This bot is designed to help you quickly upadte the information of a ticket',
                    'imageUrl': 'https://goo.gl/aeDtrS', # This picture is not working and will be replaced soon.
                    'imageStyle': 'IMAGE'
                }
            }
        elif word in GREETING_KEYWORDS and tracker['start'] == 0:
            widgets.append({
                    'image':{'imageUrl':'https://media.giphy.com/media/xT9IgG50Fb7Mi0prBC/giphy.gif'}
            })
            widgets.append({
                'textParagraph': {
                    'text': 'Hi ' + username + '. Happy to help you. Please type "start" to see what I can do.'
                }
            })
        elif word == 'friday' and tracker['start'] == 0:
            widgets.append({
                    'image':{'imageUrl':'https://media.giphy.com/media/l2Sqf1Y2g9C3F97kA/giphy.gif'}
            })
            widgets.append({
                'textParagraph': {
                    'text': 'Happy Friday:)'
                }
            })
        elif word =='start' and tracker['start'] == 0:
            widgets.append({
                'textParagraph' : {
                    'text':'Oh yeah. Love to help:) Please select one: <br>1. Save the Earth <br>2.Open a ticket to update a CI'
                }
             })
            tracker['start'] += 1 # start == 1
        elif word == 'start' and tracker['start'] == 1:
            tracker = {key:0 for key in tracker}
            widgets.append({
                'textParagraph': {
                    'text': 'How can I help you today? <br>1.Open a ticket<br>2.Open a ticket to update a CI'
                }
            })
        elif word == '1' and tracker['1'] == 0 and tracker['2'] == 0:
            widgets.append({
                'image': {'imageUrl': 'https://media.giphy.com/media/n07CBTpZzjybm/giphy.gif'}
            })
            widgets.append({
                'textParagraph': {
                    'text': "Amazing choice!! Let's call our old friend superman for help. He should be arrive in a second........failed. Please type 'start' to restart the whole process"
                }
            })
        elif word == '2' and tracker['2'] == 0:
            widgets.append({
                 'textParagraph' : {
                    'text':'You have selected option2, open a ticket to update a configuration item. Please indicate the CI you want update <br>1.Unique configuration item identifier<br>2.IP address<br>3.Hostname<br>Cancel<br>Please select one of these options'
                }
            })
            tracker['2'] += 1 #2== 1
            tracker['cancel'] += 1 # cancel == 1
        elif word == '1' and tracker['2'] == 1 and tracker['1'] == 0 and tracker['cancel'] == 1:
            widgets.append({
                'textParagraph': {
                    'text': ' You have selected option 1. Unique configuration item identifier.  To cancel and make a new selection, type CANCEL. Otherwise, please enter the CI identifier.'
                }
            })
            tracker['1'] += 1  # 1 == 1
            tracker['cancel'] += 1  # cancel == 2
        elif bot_function.validate_CI(word) == True and tracker['1'] == 1 and tracker['2'] ==1 : # this is right
            widgets.append({
                'textParagraph':{
                    'text':'Congrats!! I found a match for your CI. <br> Please indicates field on CI you want to update. <br> a. Owner <br> b.Service(s) <br> c.Status <br> d.Compliance category (PC11,PCI2, SOX, and/or SSAE) <br>e.Description'
                }
            })
            CI = word
            tracker['1'] +=1 # 1 ==2
            tracker['cancel'] +=1 # cancel == 3
        elif bot_function.validate_CI(word) == False and tracker['1'] == 1 and tracker['2'] ==1:
            widgets.append({
                'textParagraph': {
                    'text': 'Ops, something went wrong with your CI ' + word + 'Please check this CI and re-enter and value'
                }
            })
        elif word == 'a' and tracker['1'] == 2 and tracker['2'] == 1: # incomplete
            widgets.append({
                'textParagraph': {
                    'text': 'Please type the email address you want to update '
                }
            })
        elif word == 'b' and tracker['1'] == 2 and tracker['2'] == 1:  # incomplete
            widgets.append({
                'textParagraph': {
                    'text': 'Ops, something went wrong with your CI ' + word + 'Please check this CI and re-enter and value'
                }
            })
        elif word == 'c' and tracker['1'] == 2 and tracker['2'] == 1:  # incomplete let's say user choose c
            widgets.append({
                'textParagraph': {
                    'text': 'Select one to update:<br>a.open <br>b.Discovered<br>c.Received<br>d.In Stock<br>e.Reserved<br>f. In Use<br>g.Maintenance<br>h.Retired/Consumed<br>i.Disposed'
                }
            })
            tracker['1'] += 1 # 1==3
            tracker['cancel'] +=1 # cancel ==3
        elif word == 'd' and tracker['1'] == 2 and tracker['2'] == 1:  # incomplete
            widgets.append({
                'textParagraph': {
                    'text': 'Ops, something went wrong with your CI ' + word + 'Please check this CI and re-enter and value'
                }
            })
        elif word == 'e' and tracker['1'] == 2 and tracker['2'] == 1:  # incomplete
            widgets.append({
                'textParagraph': {
                    'text': 'Ops, something went wrong with your CI ' + word + 'Please check this CI and re-enter and value'
                }
            })
        elif word =='a' and tracker['1'] == 3 and tracker['2'] == 1:
            widgets.append({
                'textParagraph': {
                    'text': bot_function.create_ticket(CI, 'open')
                }

            })
        elif word == '2' and tracker['2'] == 1:
            widgets.append({
                 'textParagraph': {
                    'text':' You have selected option 2, IP address. To cancel and make a new selection, type CANCEL. Otherwise, please enter the IP address of the CI you want to update.'
                }
            })
            tracker['2'] += 1 # 2 == 2
            tracker['cancel'] += 1 # cancel == 2
        elif word == 'cancel' and tracker['2'] == 2 and tracker['cancel'] ==2:
            widgets.append({
                'textParagraph': {
                    'text': 'You have selected option2, open a ticket to update a configuration item. Please indicate the CI you wanto update <br>1.Unique configuration item identifier<br>2.IP address<br>3.Hostname<br>Cancel<br>Please select one of these options'
                }
            })
            tracker['2'] -= 1  # 2== 1
            tracker['cancel'] -= 1  # cancel == 1
        elif bot_function.validate_IP_address(word) == True and tracker['2'] == 2 and tracker['cancel'] == 2:
            ip_address = word
            widgets.append({
                 'textParagraph': {
                    'text':' You have entered ' + ip_address + '<br>Is this the IP address you want to lookup? Plese incidate yes or no'
                }
            })
            tracker['2'] += 1
            tracker['cancel'] +=1 # cancel == 3
        elif bot_function.validate_IP_address(word) == False and tracker['2'] == 2 and tracker['cancel'] == 2:
            ip_address = word
            widgets.append({
                'textParagraph': {
                    'text': ' You have entered a wrong IP address. Please re-enter the IP address you want to lookup. Or type "finish" to end the conversation'
                }
            })
        elif word == 'yes' and tracker['2'] == 3 and tracker['cancel'] == 3 and check_IP_address(ip_address) == True:
            widgets.append({
                 'textParagraph': {
                    'text':'You IP address matched with the following configuration item <br>CID01234567890<br>G1nwwhatever991<br>127.0.0.1<br> Is this the configuration Item you want to update? Please type yes or no'
                }
            })
            tracker['2'] += 1
            tracker['yes'] += 1 # yes == 1
            tracker['cancel'] +=1 # cancel == 4
        elif word == 'no' and tracker['2'] == 3 and tracker['cancel'] ==3:
            widgets.append({
                'textParagraph': {
                    'text': 'Please re-enter the IP address of the CI you want to update.'
                }
            })
            tracker['2'] -=1
            tracker['cancel'] -=1
        elif word == 'yes' and tracker['2'] == 3 and tracker['cancel'] == 3 and check_IP_address(ip_address) == False:
            widgets.append({
                'textParagraph': {
                    'text': 'Sorry, I did not find any matched IP address in the system. Or you entered an invalid IP address. Please type the IP address again or type "finish" to quit the conversation'
                }
            })
            tracker['2'] -=1
            tracker['cancel'] -=1
        elif word == 'yes' and tracker['2'] == 4 and tracker['cancel'] == 4 : # the unique identifier will help to keep track of the progress of the conversation.
            widgets.append({
                 'textParagraph': {
                    'text':'What data do you want to update for this CI? Please select one of the following options:<br>a.Owner<br>b.Service(s)<br>c.Status<br>d.Compliance category(PCI1,PCI2,SOX,and/or SSAE)<br>e.Description'
                }
            })
            tracker['2'] += 1
            tracker['yes'] +=1 # yes == 2
            tracker['cancel'] +=1 # cancel ==5
        elif word == 'no' and tracker['2'] == 4 and tracker['cancel'] == 4:
            widgets.append({
                'textParagraph': {
                    'text': 'This is still in development.' # currently, using IP address to update the information are not viable now.
                }
            })
        elif word == 'a' and tracker['2'] == 5 and tracker['cancel'] == 5:
            widgets.append({
                 'textParagraph': {
                    'text':'You have chosen to update the owner of this configuration item. Is that correct? Please enter yes or no'
                }
            })
            tracker['2'] += 1 # 2 == 6
            tracker['cancel'] +=1 # cancel == 6
        elif word == 'yes' and tracker['2'] == 6 and tracker['cancel'] == 6:
            widgets.append({
                 'textParagraph': {
                    'text':'Please enter the valid email address of the new owner you want to assign to this configuration item'
                }
            })
            tracker['2'] += 1 # 2== 7
            tracker['cancel'] += 1 # cancel == 7
            tracker['yes'] += 1 # yes == 3
        elif word == 'no' and tracker['2'] == 6 and tracker['cancel'] == 6:
            widgets.append({
                'textParagraph': {
                    'text': 'What data do you want to update for this CI? Please select one of the following options:<br>a.Owner<br>b.Service(s)<br>c.Status<br>d.Compliance category(PCI1,PCI2,SOX,and/or SSAE)<br>e.Description'
                }
            })
            tracker['2'] -= 2
            tracker['cancel'] -= 2
        elif tracker['2'] == 7 and tracker['cancel'] == 7: # validate_email_address(word) == True and
            widgets.append({
                 'textParagraph': {
                    'text':'You entered ' + word + '<br>Is this the update you wish to request?'
                }
            })
            tracker['2'] += 1 # 2 == 8
            tracker['cancel'] += 1 # cancel == 8
        elif word == 'yes'and tracker['2'] == 8 and tracker['cancel'] == 8:
            widgets.append({
                 'textParagraph': {
                    'text':'Please stand by while I open you ticket. <br> You ticket number is RF9876543. Type "finish" to end the conversation'
                }
            })
            tracker['yes'] += 1
        elif word == 'finish':
            tracker = {key: 0 for key in tracker} # clear all the data in case the next user will be using the same result.
            widgets.append({
                'textParagraph': {
                    'text': 'Feel free to start another task by type "start"'
                }
            })
        elif word == 'cancel': # the number will used to track the stage of the conversation
            if tracker['1'] != 0:
                widgets.append({
                    'textParagraph': {
                        'text': send_cancel_message(1, tracker['cancel'])
                    }
                })
            elif tracker['2'] != 0:
                widgets.append({
                    'textParagraph': {
                        'text': send_cancel_message(2, tracker['cancel'])
                    }
                })
            elif tracker['3'] != 0:
                widgets.append({
                    'textParagraph': {
                        'text': send_cancel_message(3, tracker['cancel'])
                    }
                })
        elif word == 'debug':
            widgets.append({
                'textParagraph': {
                    'text': 'Debug - Current bot status: <br>' + str(tracker) + '<br> Current length of the message is ' + str(len(words)) + '<br> Words test ' + event_message + '<br>IP address' + ip_address + '<br> error message = ' + str(error_message)
                }
            })
        elif word =='help':
            widgets.append({
                'textParagraph':{
                    'text':'Please type "start" to get started.'
                }


            })
        else:
            error_message +=1



    if error_message > 0:
        widgets.append({
            'textParagraph': {
                'text': "Sorry, I don't think I got that. Type 'start' to get started:)"
            }
        })
        error_message = 0

    if header != None:
        cards.append(header)

    cards.append({  'header': {
                    'title': 'Service Manager Support',
                    'subtitle': 'Connecting with SM faster than ever',
                    'imageUrl': 'https://goo.gl/aeDtrS',
                    'imageStyle': 'IMAGE'
                  },
                    'sections': [{'widgets': widgets }]})
    response['cards'] = cards

    return response

#c_stage means the stage of the cancel
#c_message means the message that we will send back
#we need more information to check the coordinates
def send_cancel_message(num, c_stage):
    global tracker
    if num == 2:
        if c_stage == 1:
            c_message = 'How can I help you today? <br>1.Open a ticket<br>2.Open a ticket to update a CI'
            tracker['cancel'] -= 1
            tracker['2'] -= 1
            return c_message
        elif c_stage == 2:
            c_message = 'You have selected option2, open a ticket to update a configuration item. Please indicate the CI you wanto update <br>1.Unique configuration item identifier<br>2.IP address<br>3.Hostname<br>4.Cancel<br>Please select one of these options'
            tracker['cancel'] -= 1
            tracker['2'] -= 1
            return c_message
        elif c_stage == 3:
            c_message = ' You have selected option 2, IP address. To cancel and make a new selection, type CANCEL. Otherwise, please enter the IP address of the CI you want to update.'
            tracker['cancel'] -= 1
            tracker['2'] -= 1
            return c_message
        elif c_stage == 4:
            c_message = ' You have entered ' + ip_address + '<br>Is this the IP address you want to lookup? Plese incidate yes or no'
            tracker['cancel'] -= 1
            tracker['2'] -= 1
            tracker['yes'] -=1
            return c_message
        elif c_stage == 5:
            c_message ='You IP address matched with the following configuration item <br>CID01234567890<br>G1nwwhatever991<br>127.0.0.1<br> Is this the configuration Item you want to update? Please type yes or no'
            tracker['cancel'] -= 1
            tracker['2'] -= 1
            tracker['yes'] -=1
            return c_message
        elif c_stage == 6:
            c_message ='What data do you want to update for this CI? Please select one of the following options:<br>a.Owner<br>b.Service(s)<br>c.Status<br>d.Compliance category(PCI1,PCI2,SOX,and/or SSAE)<br>e.Description'
            tracker['cancel'] -= 1
            tracker['2'] -= 1
            return c_message
        elif c_stage == 7:
            c_message = 'You have chosen to update the owner of this configuration item. Is that correct? Please enter yes or no'
            tracker['cancel'] -= 1
            tracker['2'] -= 1
            tracker['yes']-=1
            return c_message
        elif c_stage == 8:
            c_message = 'You entered ??? (still in progress) <br>Is this the update you wish to request?'
            tracker['cancel'] -= 1
            tracker['2'] -= 1
            return c_message






















