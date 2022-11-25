import os

import slack
import uvicorn
from fastapi import FastAPI
from fastapi_slackeventsapi import SlackEventManager

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
SIGNING_SECRET = os.environ.get("SIGNING_SECRET")

app = FastAPI()
slack_event_manger = SlackEventManager(singing_secret=SIGNING_SECRET,
                                       endpoint='/slack/events',
                                       app=app)

client = slack.WebClient(token=SLACK_TOKEN)


@slack_event_manger.on('message')
def message(payload):
    print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if text == "hi":
        client.chat_postMessage(channel=channel_id, text="Hello")


@slack_event_manger.on('reaction_added')
async def reaction_added(event_data):
    emoji = event_data['event']['reaction']
    print(emoji)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0')
