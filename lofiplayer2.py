import asyncio
from os import path, listdir
from pyglet import media
from random import choice

import state


base_dir = path.normpath(path.expanduser('~/Documents/Study-with-me'))  # base resource directory.


class MusicPlayer:
    def __init__(self):
        self.music_files = self.get_music_files()
        self.current_index = 0
        self.player = None
        self.is_playing = False
        self.is_muted = False
        self.volume = 0.6  # Default volume set to 0.6

    def get_music_files(self):
        folder_path = path.join(base_dir, "resource", "sound", "lofi")
        music_files = [f for f in listdir(folder_path) if f.endswith(".mp3")]
        return music_files

    async def player_wrapper(self, session_length):
        # session_length in seconds
        try:
            # run the task play_music() with session_length as timeout
            await asyncio.wait_for(self.play_music(), timeout=session_length - 1)
        except asyncio.TimeoutError:
            print('killed music_player')
        else:
            pass

        # In case the player does not end after a study session, double_kill with stop_music()
        try:
            music_player.stop_music()
        except NameError:
            pass

    async def play_music(self):
        played_songs = []
        played_songs_path = path.join(base_dir, 'log', 'played_lofi.txt')
        with open(played_songs_path, 'r', encoding='utf-8') as f:
            n_lofi = len(self.music_files)  # number of lofi songs
            if n_lofi == 0:
                raise FileNotFoundError('No lofi music found. Please download music files.')
            lines = f.readlines()[-(int(n_lofi * 0.8)):]
            for l in lines:
                played_songs.append(l.strip())
        if not self.is_playing:
            if state.study_or_rest == 'r':
                return
            while True:
                music_file = choice(self.music_files)
                print(music_file)
                if music_file in played_songs:
                    continue
                msg_current_lofi = f'{music_file[:-4]}   :::   Music provided by Lofi Girl. ' \
                                   f'Listen to Lofi Girl at bit.ly/lofigirI-playlists' \
                                   f'                 '
                state.currently['lofi'] = msg_current_lofi
                with open(played_songs_path, 'a', encoding='utf-8') as f:
                    f.write(music_file + '\n')
                played_songs.append(music_file)
                self.player = media.Player()
                source = media.load(path.join(base_dir, "resource", "sound", "lofi", music_file))
                self.player.queue(source)
                self.player.volume = self.volume if not self.is_muted else 0
                self.player.play()
                await asyncio.sleep(source.duration + 2)

    def stop_music(self):
        if self.player is not None and self.player.playing:
            self.player.pause()
            self.is_playing = False

    def toggle_mute(self):
        if self.player is not None:
            self.player.volume = 0 if not self.is_muted else self.volume
            self.is_muted = not self.is_muted

    def volume_up(self):
        if self.player is not None:
            self.volume = min(self.volume * 1.1, 1.0)  # Volume increase 10%
            self.player.volume = self.volume
            self.is_muted = False

    def volume_down(self):
        if self.player is not None:
            self.volume = max(self.volume * 0.9, 0.05)  # Volume decrease 10%
            self.player.volume = self.volume
            self.is_muted = False

    def get_volume(self):
        return self.volume if self.player is None else self.player.volume

    def current_track_info(self):
        if self.is_playing and self.player is not None:
            music_file = self.music_files[self.current_index]
            return music_file, self.volume
        return None, None
