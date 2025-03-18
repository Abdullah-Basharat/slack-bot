import os
from dotenv import load_dotenv
import slack
from flask import Flask
from slackeventsapi import SlackEventAdapter

load_dotenv()

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
        client.chat_postMessage(channel=channel_id,text=text)


    
if __name__ == "__main__":
    app.run(debug=True)