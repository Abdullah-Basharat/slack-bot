import os
from dotenv import load_dotenv
import slack
from flask import Flask,request,Response
from slackeventsapi import SlackEventAdapter
import sqlite3
from database_interactions import upsert_user,get_message_count

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
    print(user_id)
    text = event.get('text')
    
    if BOT_ID != user_id:
        upsert_user(user_id)   
        client.chat_postMessage(channel=channel_id,text=text)
 
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