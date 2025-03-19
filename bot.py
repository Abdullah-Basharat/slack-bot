import os
from dotenv import load_dotenv
import slack
from flask import Flask,request,Response
from slackeventsapi import SlackEventAdapter
import sqlite3
from database_interactions import upsert_user,get_message_count
load_dotenv()
import string
from datetime import datetime,timedelta

BAD_WORDS = ['hmm', 'no', 'haha']
SCHEDULED_MESSAGES = [
    {'text': 'First message', 'post_at': int((
        datetime.now() + timedelta(seconds=20)).timestamp()), 'channel': 'C08J1R620UA'},
    {'text': 'Second Message!', 'post_at': int((
        datetime.now() + timedelta(seconds=30)).timestamp()), 'channel': 'C08J1R620UA'}
]

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
            # 'username': 'Welcome Robot!',
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

def list_scheduled_messages(channel):
    response = client.chat_scheduledMessages_list(channel=channel)
    messages = response.data.get('scheduled_messages')
    ids = []
    for msg in messages:
        ids.append(msg.get('id'))

    return ids


def schedule_messages(messages):
    ids = []
    for msg in messages:
        response = client.chat_scheduleMessage(
            channel=msg['channel'], text=msg['text'], post_at=msg['post_at'])
        id_ = response.get('scheduled_message_id')
        ids.append(id_)

    return ids


def delete_scheduled_messages(ids, channel):
    for _id in ids:
        try:
            client.chat_deleteScheduledMessage(
                channel=channel, scheduled_message_id=_id)
        except Exception as e:
            print(e)



def check_if_bad_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))

    return any(word in msg for word in BAD_WORDS)


@slack_event_adaptor.on('message')
def message(payload):
    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    
    if user_id != None and BOT_ID != user_id:
        upsert_user(user_id)   
        # client.chat_postMessage(channel=channel_id,text=text)
        # send_welcome_message(f'@{user_id}', user_id) #send's to the client
        if text.lower() == "start":
            send_welcome_message(channel_id, user_id)
        elif check_if_bad_words(text):
            ts = event.get('ts')
            client.chat_postMessage(
                channel=channel_id, thread_ts=ts, text="THAT IS A BAD WORD!")
        
@slack_event_adaptor.on('reaction_added')
def reaction(payload):
    event = payload.get('event', {})
    channel_id = event.get('item', {}).get('channel')
    user_id = event.get('user')

    if channel_id not in welcome_messages:
        return

    welcome = welcome_messages[channel_id][user_id]
    welcome.completed = True
    # welcome.channel = channel_id
    message = welcome.get_message()
    updated_message = client.chat_update(**message)
    welcome.timestamp = updated_message['ts']
 
@app.route("/message-count",methods=['POST'])       
def message_count():
    data = request.form
    
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    msg_count = get_message_count(user_id)
    client.chat_postMessage(channel=channel_id,text=f"Message-Count: {msg_count}")
    return Response(),200


    
if __name__ == "__main__":
    schedule_messages(SCHEDULED_MESSAGES)
    ids = list_scheduled_messages('C08J1R620UA')
    # delete_scheduled_messages(ids, 'C08J1R620UA')
    app.run(debug=True)