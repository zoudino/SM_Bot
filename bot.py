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


