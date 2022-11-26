import asyncio
import base64
import hashlib
import json
import os

import climage
import torch
import websockets
from diffusers import StableDiffusionPipeline
from websockets.client import WebSocketClientProtocol

HOSTNAME = os.environ.get("SLACK_HOSTNAME")

model_id = "prompthero/openjourney"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
# pipe.safety_checker = lambda images, clip_input: (images, False)  # disables NSFW exception
pipe = pipe.to("cuda")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pictures_folder = os.path.join(BASE_DIR, 'pictures')

exception_counter = 0


def generate_picture(query):
    image = pipe(query).images[0]
    filename = hashlib.md5(query.encode()).hexdigest()
    i_file = os.path.join(f"{filename}.png")
    image.save(i_file)
    print(climage.convert(i_file))
    return i_file


async def main_loop():
    if not os.path.exists(pictures_folder):
        os.mkdir(pictures_folder)
    while True:
        try:
            async with websockets.connect(f"wss://{HOSTNAME}/ws/picture_service") as websocket:
                websocket: WebSocketClientProtocol
                await websocket.send(json.dumps({'service_name': 'picture_generator', 'event': 'request_picture'}))
                data = json.loads(await websocket.recv())
                print(data)

                query = data.get('query')
                if not query:
                    continue
                file_path = generate_picture(query)
                # await asyncio.sleep(20)  # imitating picture generation

                await websocket.send(json.dumps({'service_name': 'picture_generator',
                                                 'event': 'response_picture',
                                                 'picture_data': {
                                                     'picture_base64': base64.b64encode(
                                                         open(file_path, 'rb').read()).decode(),
                                                     'picture_name': os.path.basename(file_path)
                                                 }})
                                     )
                os.remove(file_path)
                print(await websocket.recv())
                # await websocket.close()
        except Exception as e:
            print(e)
            await asyncio.sleep(1)


asyncio.run(main_loop())
