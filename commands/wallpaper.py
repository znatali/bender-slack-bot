import os.path

import aiohttp
from bs4 import BeautifulSoup
import random

RANDOM_URL_PROVIDER = 'https://wallhaven.cc/random'


async def wallpaper_command_handler():
    session = aiohttp.ClientSession()
    response = await session.get(RANDOM_URL_PROVIDER)
    html = await response.text()
    bs = BeautifulSoup(html)
    pictures = bs.find_all('a', {'class': 'preview'})
    picture_url = pictures[random.randint(0, len(pictures) - 1)].get('href')

    response = await session.get(picture_url)
    html = await response.text()
    bs = BeautifulSoup(html)

    result_picture_url = bs.find('img', {'id': 'wallpaper'}).get('src')
    return result_picture_url
