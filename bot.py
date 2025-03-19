import os
from dotenv import load_dotenv
import slack
from flask import Flask,request,Response
from slackeventsapi import SlackEventAdapter
import sqlite3
from database_interactions import upsert_user,get_message_count
load_dotenv()

welcome_messages = {}
class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to this awesome channel! \n\n'
                '*Get started by completing the tasks!*'
            )
        }
    }

    DIVIDER = {'type': 'divider'}

    def __init__(self, channel):
        self.channel = channel
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False

    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome Robot!',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'

        text = f'{checkmark} *React to this message!*'

        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}


def send_welcome_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    if user in welcome_messages[channel]:
        return

    welcome = WelcomeMessage(channel)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    welcome_messages[channel][user] = welcome


app = Flask(__name__)
slack_event_adaptor = SlackEventAdapter(os.getenv("SIGNING_SECRET"),'/slack/events',app)
client = slack.WebClient(token=os.getenv("SLACK_TOKEN"))

print(client.api_call("auth.test"))


BOT_ID = client.api_call("auth.test")['user_id']

@slack_event_adaptor.on('message')
def message(payload):
    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    
    if BOT_ID != user_id:
        upsert_user(user_id)   
        # client.chat_postMessage(channel=channel_id,text=text)
        # send_welcome_message(f'@{user_id}', user_id) #send's to the client
        
        send_welcome_message(channel_id, user_id)
 
@app.route("/message-count",methods=['POST'])       
def message_count():
    data = request.form
    
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    msg_count = get_message_count(user_id)
    client.chat_postMessage(channel=channel_id,text=f"Message-Count: {msg_count}")
    return Response(),200


    
if __name__ == "__main__":
    app.run(debug=True)