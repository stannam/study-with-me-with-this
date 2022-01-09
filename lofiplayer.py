import asyncio
from os import listdir
from os.path import join
from random import choice
import pyglet


async def player_wrapper(session_length):
    # session_length in seconds
    task_playingmusic = asyncio.create_task(player())
    await asyncio.sleep(session_length-1)
    task_playingmusic.cancel()


async def player():
    lofipath = 'resource/sound/lofi/'
    songlist = [f for f in listdir(lofipath) if join(lofipath, f).endswith('mp3')]
    while True:
        to_play = choice(songlist)
        msg_current_lofi = f'{to_play[:-4]}     :::     Music provided by Lofi Girl.   ' \
                           f'Listen to Lofi Girl at bit.ly/lofigirI-playlists' \
                           f'                 '
        with open('log/current_lofi.txt', 'w+', encoding="utf-8") as f:
            f.write(msg_current_lofi)
        pl = pyglet.media.Player()
        x = pyglet.media.load(f'{lofipath}{to_play}', streaming=False)
        pl.queue(x)
        pl.volume = 0.2
        pl.play()
        await asyncio.sleep(x.duration+5)
