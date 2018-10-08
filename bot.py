# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import random
from apiclient.discovery import build, build_from_document
from flask import Flask, render_template, request, json, make_response
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)

INTERACTIVE_TEXT_BUTTON_ACTION = "doTextButtonAction"
INTERACTIVE_IMAGE_BUTTON_ACTION = "doImageButtonAction"
INTERACTIVE_BUTTON_PARAMETER_KEY = "param_key"
BOT_HEADER = 'Card Bot Python'

@app.route('/', methods=['POST'])
def home_post():
    """Respond to POST requests to this endpoint.
    All requests sent to this endpoint from Hangouts Chat are POST
    requests.
    """
    event_data = request.get_json()
    resp = None
    # If the bot is removed from the space, it doesn't post a message
    # to the space. Instead, log a message showing that the bot was removed.
    if event_data['type'] == 'REMOVED_FROM_SPACE':
        logging.info('Bot removed from  %s' % event_data['space']['name'])
        return 'OK'

    elif event_data['type']  == 'ADDED_TO_SPACE' and event_data['space']['type'] == 'ROOM':
        resp = { 'text': ('Thanks for adding me to {}!'
            .format(event_data['space']['name'])) }

    elif event_data['type']  == 'ADDED_TO_SPACE' and event_data['space']['type'] == 'DM':
        resp = { 'text': ('Thanks for adding me to a DM, {}!'
            .format(event_data['user']['displayName'])) }

    elif event_data['type'] == 'MESSAGE':
        resp = create_card_response(event_data['message']['text']) # changed
  
    elif event_data['type'] == 'CARD_CLICKED':
        action_name = event_data['action']['actionMethodName']
        parameters = event_data['action']['parameters']
        resp = respond_to_interactive_card_click(action_name, parameters)

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
    """Respond to GET requests to this endpoint.
    This function responds to requests with a simple HTML landing page for this
    App Engine instance.
    """
    
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

"""This is coodinate to track the progress of the conversation"""
tracker = {
        "start":0,
            "1":0,
            "2":0,
            "3":0,
          "yes":0,
           "no":0,
       "cancel":0
    }

def create_card_response(event_message):
    """Creates a card response based on the message sent in Hangouts Chat.
    See the reference for JSON keys and format for cards:
    https://developers.google.com/hangouts/chat/reference/message-formats/cards
    Args:
        eventMessage: the user's message to the bot
    """

    response = dict()  
    cards = list()
    widgets = list()
    header = None

    words = event_message.lower().split()
    # Event message = @"Service Manager bot"  debug
    words = words[3:]

    # let's add some conversation into the bot. So, we can add some flexability into our chat.
    GREETING_KEYWORDS = ("hello", "hi","sup","what's up")
    GREETING_RESPONSES = ["'sup bro","hey","hi","hey you get my snap"]

    tracker['start'] = 0
    tracker['1'] = 0
    tracker['2'] = 0
    tracker['3'] = 0
    tracker['yes'] = 0
    tracker['cancel'] = 0
    tracker['no'] = 0

    for word in words:
        if word == 'header':
            header = {
                'header': {
                    'title': 'Service Manager Ticket Support',
                    'subtitle': 'This bot is designed to help you quickly upadte the information of a ticket',
                    'imageUrl': 'https://goo.gl/5obRKj', # This picture is not working and will be replaced soon.
                    'imageStyle': 'IMAGE'
                }
            }
        elif word in GREETING_KEYWORDS:
            widgets.append({
                'textParagraph': {
                    'text': random.choice(GREETING_RESPONSES)
                }
            })
        elif word =='start':
            tracker['start']
            widgets.append({
                'textParagraph' : {
                    'text':'How can I help you today? <br>1.Open a ticket<br>2.Open a ticket to update a CI'
                }
             })
            tracker['start'] = tracker['start'] + 1
        elif word == 'start' and tracker['start'] == 1:
            tracker = {key:0 for key in tracker}
            widgets.append({
                'textParagraph': {
                    'text': 'How can I help you today? <br>1.Open a ticket<br>2.Open a ticket to update a CI'
                }
            })
        elif word == '1':
            widgets.append({
                'textParagraph': {
                    'text': 'Sorry, this feature is still in progress. Please type "cancel" for returning the previous window'
                }
            })
        elif word == '2' and tracker['2'] == 0:
            widgets.append({
                 'textParagraph' : {
                    'text':'You have selected option2, open a ticket to update a configuration item. Please indicate the CI you wanto update <br>1.Unique configuration item identifier<br>2.IP address<br>3.Hostname<br>Cancel<br>Please select one of these options'
                }
            })
            tracker['2'] += 1
            tracker['cancel'] += 1

        elif word == '2' and tracker['2'] == 1:
            widgets.append({
                 'textParagraph': {
                    'text':' You have selected option 2, IP address. To cancel and make a new selection, type CANCEL. Otherwise, please enter the IP address of the CI you want to update.'
                }
            })
            tracker['2'] += 1
            tracker['cancel'] += 1

        elif tracker['2'] == 2 and tracker['cancel'] == 2:
            ip_address = word
            widgets.append({
                 'textParagraph': {
                    'text':' You have entered ' + word + '<br>Is this the IP address you want to lookup? Plese incidate yes or no'
                }
            })
            tracker['2'] += 1
            tracker['cancel'] += 1
        elif word == 'yes' and tracker['2'] == 3 and tracker['cancel'] == 3 and check_IP_address(ip_address) == True:
            widgets.append({
                 'textParagraph': {
                    'text':'You IP address matched with the following configuration item <br>CID01234567890<br>G1nwwhatever991<br>127.0.0.1<br> Is this the configuration Item you want to update? Please type yes or no'
                }
            })
            tracker['2'] += 1
            tracker['cancel'] += 1
        elif word == 'yes' and tracker['2'] == 3 and tracker['cancel'] == 3 and check_IP_address(ip_address) == False:
            widgets.append({
                'textParagraph': {
                    'text': 'Sorry, I did not find any matched IP address in the system. Or you entered an invalid IP address.'
                }
            })
        elif word == 'yes' and tracker['2'] == 4 and tracker['cancel'] == 4: # the unique identifier will help to keep track of the progress of the conversation.
            widgets.append({
                 'textParagraph': {
                    'text':'What data do you want to update for this CI? Please select one of the following options:<br>a.Owner<br>b.Service(s)<br>c.Status<br>d.Compliance category(PCI1,PCI2,SOX,and/or SSAE)<br>e.Description'
                }
            })
            tracker['2'] += 1
            tracker['cancel'] += 1
        elif word == 'a' and tracker['2'] == 5 and tracker['cancel'] == 5:
            widgets.append({
                 'textParagraph': {
                    'text':'You have chosen to update the owner of this configuration item. Is that correct? Please enter yes or no'
                }
            })
            tracker['2'] += 1
            tracker['cancel'] += 1
        elif word == 'yes' and tracker['2'] == 6 and tracker['cancel'] == 6:
            widgets.append({
                 'textParagraph': {
                    'text':'Please enter the valid email address of the new owner you want to assign to this configuration item'
                }
            })
            tracker['2'] += 1
            tracker['cancel'] += 1
        elif tracker['2'] == 7 and tracker['cancel'] == 7:
            widgets.append({
                 'textParagraph': {
                    'text':'You entered' + 'Darren.Kroll@global.com' + '<br>Is this the update you wish to request?'
                }
            })
            tracker['2'] += 1
            tracker['cancel'] += 1
        elif word == 'yes'and tracker['2'] == 8 and tracker['cancel'] == 8:
            widgets.append({
                 'textParagraph': {
                    'text':'Please stand by while I open you ticket. <br> You ticket number is RF9876543. Type "finish" to end the conversation'
                }
            })
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
                        'text': send_cancel_message(tracker['1'], tracker['cancel'])
                    }
                })
                tracker['cancel'] -=1
            elif tracker['2'] != 0:
                widgets.append({
                    'textParagraph': {
                        'text': send_cancel_message(tracker['2'], tracker['cancel'])
                    }
                })
                tracker['cancel'] -=1
            elif tracker['3'] != 0:
                widgets.append({
                    'textParagraph': {
                        'text': send_cancel_message(tracker['3'], tracker['cancel'])
                    }
                })
                tracker['cancel'] -=1


        elif word == 'debug':
            widgets.append({
                'textParagraph': {
                    'text': 'Debug - Current bot status: <br>' + str(tracker) + '<br> Current length of the message is ' + str(len(words)) + '<br> Words test ' + event_message
                }
            })
        else:
            widgets.append({
                'textParagraph': {
                    'text': "Sorry, I don't think I got that. Type 'start' to get started:)"
                }
            })
    if header != None:
        cards.append(header)

    cards.append({  'header': {
                    'title': 'Service Manager Support',
                    'subtitle': 'Connecting with SM faster than ever',
                    'imageUrl': 'https://ibb.co/cAtewp',
                    'imageStyle': 'IMAGE'
                  },
                    'sections': [{'widgets': widgets }]})
    response['cards'] = cards

    return response

#c_stage means the stage of the cancel
#c_message means the message that we will send back
#we need more information to check the coordinates
def send_cancel_message(num, c_stage):
    if num != 0 and c_stage == 1:
        c_message = 'How can I help you today? <br>1.Open a ticket<br>2.Open a ticket to update a CI'
        return c_message
    elif num !=0 and c_stage == 2:
        c_message = 'You have selected option2, open a ticket to update a configuration item. Please indicate the CI you wanto update <br>1.Unique configuration item identifier<br>2.IP address<br>3.Hostname<br>4.Cancel<br>Please select one of these options'

def check_IP_address(ip):
    fake_data = ['127.0.0.1']
    if ip == fake_data[0]:
        return True
    else:
        return False

"""
   Later will be deleted if we no longer use it. 

        elif word == 'keyvalue':
            widgets.append({
                'keyValue': {
                    'topLabel': 'KeyValue Widget',
                    'content': 'This is a KeyValue widget',
                    'bottomLabel': 'The bottom label',
                    'icon': 'STAR'
                }
            })
        elif word == 'interactivetextbutton':
            widgets.append({
                'buttons': [
                    {
                        'textButton': {
                            'text': 'INTERACTIVE BUTTON',
                            'onClick': {
                                'action': {
                                    'actionMethodName': INTERACTIVE_TEXT_BUTTON_ACTION,
                                    'parameters': [{
                                        'key': INTERACTIVE_BUTTON_PARAMETER_KEY,
                                        'value': event_message
                                    }]
                                }
                            }
                        }
                    }
                ]
            })
        elif word == 'interactiveimagebutton':
            widgets.append({
                'buttons': [
                    {
                        'imageButton': {
                            'icon': 'EVENT_SEAT',
                            'onClick': {
                                'action': {
                                    'actionMethodName': INTERACTIVE_IMAGE_BUTTON_ACTION,
                                    'parameters': [{
                                        'key': INTERACTIVE_BUTTON_PARAMETER_KEY,
                                        'value': event_message
                                    }]
                                }
                            }
                        }
                    }
                ]
            })
        elif word == 'textbutton':
            widgets.append({
                'buttons': [
                    {
                        'textButton': {
                            'text': 'TEXT BUTTON',
                            'onClick': {
                                'openLink': {
                                    'url': 'https://developers.google.com',
                                }
                            }
                        }
                    }
                ]
            })
        elif word == 'imagebutton':
            widgets.append({
                'buttons': [
                    {
                        'imageButton': {
                            'icon': 'EVENT_SEAT',
                            'onClick': {
                                'openLink': {
                                    'url': 'https://developers.google.com',
                                }
                            }
                        }
                    }
                ]
            })
        elif word == 'image':
            widgets.append({
                'image': {
                    'imageUrl': 'https://goo.gl/Bpa3Y5',
                    'onClick': {
                        'openLink': {
                            'url': 'https://developers.google.com'
                        }
                    }
                }
            })




"""





















