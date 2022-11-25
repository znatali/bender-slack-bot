import logging
import os

import uvicorn
from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SIGNING_SECRET = os.environ.get('SIGNING_SECRET')

logging.basicConfig(level=logging.DEBUG)

app = AsyncApp(token=SLACK_TOKEN, signing_secret=SIGNING_SECRET)
app_handler = AsyncSlackRequestHandler(app)


@app.event("app_mention")
async def handle_app_mentions(body, say, logger):
    logger.info(body)
    await say("What's up?")


@app.event("message")
async def handle_message(message, say):
    print(message)
    await say("Bender is here")


api = FastAPI()


@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)


@api.get('/ping')
def ping():
    return {'message': 'pong'}


if __name__ == "__main__":
    uvicorn.run('app:api', host='0.0.0.0', reload=True)
