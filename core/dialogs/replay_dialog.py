import json
import os

import PySimpleGUI as sg
import vlc

from core.utils import constants


class Replay_dialog:
    """
    Small window that show the replay and then exits
    """
    def __init__(self, camera_keys):
        self.camera_keys = camera_keys
        self.nb_camera = len(camera_keys)

        # load settings
        with open(constants.SETTINGS_PATH, "r") as content:
                self.settings = json.load(content)
        
        # create the window
        if self.nb_camera < 3:
            replay_row = [sg.Image('',
                                   size=constants.CAM_RESOLUTION_BIG,
                                   key=key) for key in self.camera_keys]
        else:
            replay_row = [sg.Image('',
                                   size=constants.CAM_RESOLUTION_SMALL,
                                   key=key) for key in self.camera_keys]

        self.replay_window = sg.Window("Replay", [replay_row], finalize=True)

        # create media players
        self.vlc_instance = vlc.Instance()
        self.media_players = []
        for key in self.camera_keys:
            self.media_players.append(self.vlc_instance.media_player_new())
            self.replay_window[key].expand(True, True)
            self.media_players[-1].set_hwnd(self.replay_window[key].Widget.winfo_id())

    def play(self, goal_number):
        i = 1
        for media_player in self.media_players:
            source = os.path.join(constants.GOAL_VIDEOS_PATH,
                                  'goal_%d' % goal_number,
                                  'cam%d.avi' % i)
            i += 1

            media = self.vlc_instance.media_new(source)
            media_player.set_media(media)
            media_player.set_rate(float(self.settings['speed_factor']))
            media_player.play()
        

        while True:
            event, values = self.replay_window.read(timeout=200)

            if not self.media_players[-1].is_playing():
                break
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

        # cleanup after replay
        for media_player in self.media_players:
            media_player.release()
        self.replay_window.close()