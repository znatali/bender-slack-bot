import slack
from flask import Flask
from slackeventsapi import SlackEventAdapter
import os

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
SIGNING_SECRET = os.environ.get("SIGNING_SECRET")

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)


@slack_event_adapter.on('message')
def message(payload):
    print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if text == "hi":
        client.chat_postMessage(channel=channel_id, text="Hello")


if __name__ == "__main__":
    app.run(debug=True)
