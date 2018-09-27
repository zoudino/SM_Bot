# proj-chatbot-og
Hangouts Chat card bot
This code sample creates a simple Hangouts Chat bot that responds to events and messages from a room synchronously. The bot formats the response using cards, inserting widgets based upon the user's original input

The sample is built using Python on Google App Engine, Standard Environment.

Run the sample in Hangouts Chat
Create a new project in the Google Cloud Console
Create a service account for the bot, as documented here. Replace the contents of the service-acct.json file with the service account secrets that you download.
Download the Google App Engine Python SDK.
Start a virtual environment
virtualenv env
source env/bin/activate
Install any extra libraries using pip.
pip install -t lib -r requirements.txt
pip install --upgrade -t lib oauth2client
pip install --upgrade -t lib google-api-python-client
pip install --upgrade -t lib httplib2
Create an App Engine instance for the bot.
gcloud app create --region <REGION>
Deploy the sample to Google App Engine.
gcloud app deploy
To configure the bot to respond to @ mentions in Hangouts Chat, follow the steps to enable the API in Publishing bots.
When configuring the bot on the Configuration tab on the Hangouts Chat API page, enter the URL for the deployed version of the bot into the Bot URL text box.
Add the bot to a room or direct message.
Send the message to the bot with an @-message or directly in a DM.
In the message to the bot, send a list of the widgets for the bot to send back. For example, if you want the bot to send a header and a text paragraph widget, type 'header textparagraph'.

The bot responds to the following user input:

header
textparagraph
image
textbutton
imagebutton
keyvalue
interactivetextbutton
interactiveimagebutton
Note: When running this sample, you may receive an error about SpooledTemporaryFile class missing from the werkzeug package. To fix this, after you've downloaded all of the support libraries to lib/ open up lib/werkzeug/formparser.py and change the following line

from tempfile import SpooledTemporaryFile
to

from tempfile import TemporaryFile
Shut down the local environment
virtualenv deactivate

