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
        resp = create_card_response(event_data['message']['text'],event_data['message']['createTime']) # changed
  
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

message_time = [] # changed
def create_card_response(event_message, create_time): #changed
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
    error_message = 0;

    words = event_message.lower().split()

    # let's add some conversation into the bot
    GREETING_KEYWORDS = ("hello", "hi","sup","what's up")
    GREETING_RESPONSES = ["'sup bro","hey","hi","hey you get my snap"]


    # using dictionary to track the phases of the conversation.
    # More explaination: this dictionary is simulated to coordinate. People always can find their specific location by coordinate
    tracker = {
        "start":0,
            "1":0,
            "2":0,
            "3":0,
          "yes":0,
           "no":0,
       "cancel":0
    }
    # when the cancel equals to  1. It means we are in phase 1. And use can have one opportunity to cancel back.

    for word in words:
        if word == 'header':
            header = {
                'header': {
                    'title': 'Service Manager Ticket Support',
                    'subtitle': 'This bot is designed to help you quickly upadte the information of a ticket',
                    'imageUrl': 'https://goo.gl/5obRKj',
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
            widgets.append({
                'textParagraph' : {
                    'text':'How can I help you today? <br>1.Open a ticket<br>2.Open a ticket to update a CI' + str(len(words))
                }
             })
        elif word == '2' and tracker['2'] == 0:
            tracker['2'] +=1
            widgets.append({
                 'textParagraph' : {
                    'text':'You have selected option2, open a ticket to update a configuration item. Please indicate the CI you wanto update <br>1.Unique configuration item identifier<br>2.IP address<br>3.Hostname<br>4.Cancel<br>Please select one of these options'
                }
            })
        elif word == '2' and tracker['2'] == 1:
            tracker['2'] += 1
            widgets.append({
                 'textParagraph': {
                    'text':' You have selected option 2, IP address. To cancel and make a new selection, type CANCEL. Otherwise, please enter the IP address of the CI you want to update.'
                }
            })
        elif word == '127.0.0.1':
            widgets.append({
                 'textParagraph': {
                    'text':' You have entered 127.0.0.1. Is this the IP address you want to lookup? Plese incidate yes or no'
                }
            })
        elif word == 'yes':
            widgets.append({
                 'textParagraph': {
                    'text':'You IP address matched with the following configuration item <br>CID01234567890<br>G1nwwhatever991<br>127.0.0.1<br> Is this the configuration Item you want to update? Please type yes or no'
                }
            })
        elif word == 'yes1':
            widgets.append({
                 'textParagraph': {
                    'text':'What data do you want to update for this CI? Please select one of the following options:<br>a.Owner<br>b.Service(s)<br>c.Status<br>d.Compliance category(PCI1,PCI2,SOX,and/or SSAE)<br>e.Description'
                }
            })
        elif word == 'a':
            widgets.append({
                 'textParagraph': {
                    'text':'You have chosen to update the owner of this configuration item. Is that correct? Please enter yes or no'
                }
            })
        elif word == 'yes2':
            widgets.append({
                 'textParagraph': {
                    'text':'Please enter the valid email address of the new owner you want to assign to this configuration item'
                }
            })
        elif word == 'darren.kroll@globalpay.com':
            widgets.append({
                 'textParagraph': {
                    'text':'You entered Darren.Kroll@global.com. Is this the update you wish to request?'
                }
            })
        elif word == 'yes3':
            widgets.append({
                 'textParagraph': {
                    'text':'Please stand by while I open you ticket. <br> You ticket number is RF9876543'
                }
            })
        elif word == 'cancel':
           widgets.append({
                 'textParagraph':{
                    'text':'Nothing happen! Need More Discussion'
               }
           })
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
        else:
            widgets.append({
                'textParagraph': {
                    'text': "I don't understand it. Please type '@service manager bot start' to get started with the bot:) Otherwise, the bot will not work approriately."
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

def respond_to_interactive_card_click(action_name, custom_params):
    """Creates a response for when the user clicks on an interactive card.
    See the guide for creating interactive cards
    https://developers.google.com/hangouts/chat/how-tos/cards-onclick
    Args:
        action_name: the name of the custom action defined in the original bot response
        custom_params: the parameters defined in the original bot response
    """
    message = 'You clicked {}'.format(
        'a text button' if action_name == INTERACTIVE_TEXT_BUTTON_ACTION
            else 'an image button')

    original_message = ""

    if custom_params[0]['key'] == INTERACTIVE_BUTTON_PARAMETER_KEY:
        original_message = custom_params[0]['value']
    else:
        original_message = '<i>Cannot determine original message</i>'

    # If you want to respond to the same room but with a new message,
    # change the following value to NEW_MESSAGE.
    action_response = 'UPDATE_MESSAGE'

    return {
        'actionResponse': {
            'type': action_response
        },
        'cards': [
            {
                'header': {
                    'title': BOT_HEADER,
                    'subtitle': 'Interactive card clicked',
                    'imageUrl': 'https://goo.gl/5obRKj',
                    'imageStyle': 'IMAGE'
                }
            },
            {
                'sections': [
                    {
                        'widgets': [
                            {
                                'textParagraph': {
                                    'text': message
                                }
                            },
                            {
                                'keyValue': {
                                    'topLabel': 'Original message',
                                    'content': original_message
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
























