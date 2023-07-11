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
    played_songs = []
    played_songs_path = 'log/played_lofi.txt'
    with open(played_songs_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()[-50:]
        for l in lines:
            played_songs.append(l.strip())
    while True:

        to_play = choice(songlist)
        if to_play in played_songs:
            continue
        msg_current_lofi = f'{to_play[:-4]}     :::     Music provided by Lofi Girl.   ' \
                           f'Listen to Lofi Girl at bit.ly/lofigirI-playlists' \
                           f'                 '
        with open('log/current_lofi.txt', 'w+', encoding="utf-8") as f:
            f.write(msg_current_lofi)
        with open(played_songs_path, 'a', encoding='utf-8') as f:
            f.write(to_play + '\n')
        played_songs.append(to_play)

        pl = pyglet.media.Player()
        x = pyglet.media.load(f'{lofipath}{to_play}', streaming=False)
        pl.queue(x)
        pl.volume = 0.6
        pl.play()
        await asyncio.sleep(x.duration+2)
