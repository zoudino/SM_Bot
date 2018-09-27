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
        resp = create_card_response(event_data['message']['text'])
  
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
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'service-acct.json', scopes)
    http_auth = credentials.authorize(Http())

    chat = build('chat', 'v1', http=http_auth)
    chat.spaces().messages().create(
        parent=space_name,
        body=response).execute()

def create_card_response(event_message):
    """Creates a card response based on the message sent in Hangouts Chat.
    See the reference for JSON keys and format for cards:
    https://developers.google.com/hangouts/chat/reference/message-formats/cards
    Args:
        eventMessage: the user's message to the bot
    """

    response = dict() # 
    cards = list()
    widgets = list()
    header = None

    words = event_message.lower().split()
    
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

        elif word =='start':
            widgets.append({
                'textParagraph' : {
                    'text':'How can I help you today? <br>1.Open a ticket<br>2.Open a ticket to update a CI'
                } 
            })
        elif word == '2':
            widgets.append({
            	'textParagraph' : {
                    'text':'you have selected option2, open a ticket to update a configuration item. To cancal and make a new selection, type cancel and make a new selection, type CANCEL. Otherwise, please indicate the CI you wanto update <br>1.Unique configuration item identifier<br>2.IP address<br>3.Hostname<br>Please select one of these options'
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

# [START async-bot]

# understand the logic in this python file
import logging # This can help to implement a flexible event logging system for application and libraries.
from apiclient.discovery import build, build_from_document # using google api discovery to use the hangout api
from flask import Flask, render_template, request, json, make_response # flask is a web framework for developing web application
from httplib2 import Http # supporting access to the internet.
from oauth2client.service_account import ServiceAccountCredentials # the GCP service account authentication

"""
   The whole logic of async bot, in my current understanding, is from client - hangout - flask 
"""
app = Flask(__name__) # Define web app. This is a required step for using web app.
@app.route('/', methods=['POST'])
def home_post():
    """Respond to POST requests to this endpoint.
    All requests sent to this endpoint from Hangouts Chat are POST
    requests.
    """

    event_data = request.get_json() # the google hangout api calls the flask app. Flask will capture a json file sending from google app

    resp = None # variable for response

    # If the bot is removed from the space, it doesn't post a message
    # to the space. Instead, log a message showing that the bot was removed.
    if event_data['type'] == 'REMOVED_FROM_SPACE':
        logging.info('Bot removed from  %s' % event_data['space']['name'])
        return 'OK'
    else:
        resp = format_response(event_data) # This will define what kind of data should be return to the client side.

    spaceName = event_data['space']['name']

    send_async_response(resp, spaceName) # calling send_async_response, processing the message, and sending back the message.


    # Need to return a response to avoid an error in the Flask app.
    return 'OK'

# [START async-response]

def send_async_response(response, spaceName):
    """Sends a response back to the Hangouts Chat room asynchronously.
    Args:
      response: the response payload
      spaceName: The URL of the Hangouts Chat room
    """
    # connecting with the google hangout api
    scopes = ['https://www.googleapis.com/auth/chat.bot']  # this part is to use Google oauth2.0 to access google APIs
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'service-acct.json', scopes)
    http_auth = credentials.authorize(Http())

    # the below part is sending back the message through google hangout api.
    chat = build('chat', 'v1', http=http_auth)
    chat.spaces().messages().create(
        parent=spaceName,
        body=response).execute()

# [END async-response]

def format_response(event):
    """Determine what response to provide based upon event data.
    Args:
      event: A dictionary with the event data.
    """

    eventType = event['type']

    logging.info(eventType)

    text = ""
    senderName = event['user']['displayName']

    # Case 1: The bot was added to a room
    if eventType == 'ADDED_TO_SPACE' and event['space']['type'] == 'ROOM':
        text = 'Thanks for adding me to {}!'.format(event['space']['displayName'])

    # Case 2: The bot was added to a DM
    elif eventType == 'ADDED_TO_SPACE' and event['space']['type'] == 'DM':
        text = 'Thanks for adding me to a DM, {}!'.format(senderName)

    elif eventType == 'MESSAGE':
        text = 'Your message, {}: "{}"'.format(senderName, event['message']['text'])

    response = { 'text': text }

    # The following three lines of code update the thread that raised the event.
    # Delete them if you want to send the message in a new thread.
    if eventType == 'MESSAGE' and event['message']['thread'] is not None:
        threadId = event['message']['thread']
        response['thread'] = threadId

    return response
# [END async-bot]

@app.route('/', methods=['GET'])
def home_get():
    """Respond to GET requests to this endpoint.
    This function responds to requests with a simple HTML landing page for this
    App Engine instance.
    """
    return render_template('home.html')


