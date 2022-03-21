import os
import shutil
from datetime import datetime
from threading import Thread
from time import sleep

import PySimpleGUI as sg
from numpy import size
import vlc
from serial import Serial

from core.utils.serial_bridge import IR_Goal_Detector
from core.utils.utils import parse_IPs
from core.utils.webcam import Webcam

from .game_logic.game import Game

# Resolution settings
CAM_RESOLUTION_BIG = (640, 480)
CAM_RESOLUTION_SMALL = (480, 360)

# Replay settings
REPLAY_DELAY = 2        # s
SLOWING_FACTOR = 2      # s
REPLAY_DURATION = 5     # s

# Serial port settings
COM_PORT = 'COM7'
BAUDRATE = 9600

# Detector settings
SAMPLE_RATE = 100       # Hz


class Gui:
    """
    Graphical User Interface for a baby soccer/foosbal
    highlight record software.
    """
    def __init__(self, nb_camera):
        sg.theme('DarkAmber')

        # Change video preferences :
        self.slowing_factor = SLOWING_FACTOR
        self.replay_duration = REPLAY_DURATION
        self.nb_camera = nb_camera

        # creating game
        self.game = Game()

        # init vlc player for replays
        self.vlc_instance = vlc.Instance()

        self.streaming = False

        # creating IR detector
        self.detector = IR_Goal_Detector(COM_PORT,
                                         BAUDRATE,
                                         SAMPLE_RATE)

        # creating main window
        self.camera_keys = ['k_cam_%d' % i for i in range(nb_camera)]
        layout = self.setup_layout()
        self.window = sg.Window("Table soccer",
                                layout,
                                return_keyboard_events=True,
                                finalize=True,
                                use_default_focus=False)

        self.setup_replay_folders()

    def setup_layout(self):
        """
        Setup the layout for the main window.
        """

        # Scores
        scores_row = [
            sg.Frame("Scores", [[
                sg.Push(),
                sg.Text("Blue",
                        font=('Helvetica bold', 30),
                        text_color='dark turquoise'),
                sg.Spin([i for i in range(0, self.game.max_points+1)],
                        font=('bold', 30),
                        initial_value=0,
                        enable_events=True,
                        key='k_blue_score'),
                sg.Spin([i for i in range(0, self.game.max_points+1)],
                        font=('bold', 30),
                        initial_value=0,
                        enable_events=True,
                        key='k_red_score'),
                sg.Text("Red", font=('Helvetica bold', 30), text_color='red3'),
                sg.Push(),
            ]], expand_x=True)
        ]

        # Cameras [1-3]
        if self.nb_camera < 3:
            cameras_layout = [sg.Image('',
                                       size=CAM_RESOLUTION_BIG,
                                       key=key) for key in self.camera_keys]
        else:
            cameras_layout = [sg.Image('',
                                       size=CAM_RESOLUTION_SMALL,
                                       key=key) for key in self.camera_keys]

        cameras_row = [
            sg.Frame("Cameras", [cameras_layout])
        ]

        # Controls
        controls_row = [
            sg.Frame("Controls", [[
                sg.Image(filename='core/icons/Green_Light_Icon.png'),
                sg.Push(),
                sg.Checkbox("Delete replays",
                            default=False,
                            key='k_delete_replays'),
                sg.Button("New Game"),
                sg.Button("Connect camera(s)"),
            ]], expand_x=True, element_justification='right')
        ]

        # Main layout
        layout = [
            scores_row,
            cameras_row,
            controls_row,
        ]

        return layout

    def setup_replay_folders(self):
        # create path for goal videos
        now = datetime.now()
        time_str = now.strftime("%d.%m.%Y_%Hh%Mm%S")

        dir_path = os.path.join(os.getcwd(), 'goal_videos')
        self.game_videos_path = os.path.join(dir_path, time_str)

        try:
            os.mkdir(self.game_videos_path)
        except FileExistsError:
            pass

    def connect_webcams(self, ips):
        """
        Connect to the webcams and start the livestream.
        """

        # disconnect potential existing webcams
        self.disconnect_webcams()

        # creating webcams
        self.webcams = []
        for ip in ips:
            self.webcams.append(Webcam(ip, self.replay_duration))
            self.webcams[-1].connect()

        # start listening for goals
        self.detector.start(self.window.write_event_value)

    def disconnect_webcams(self):
        """
        Disonnect the webcams.
        """
        try:
            for webcam in self.webcams:
                webcam.disconnect()
        except AttributeError:
            # No webcam to disconnect
            pass

    def play_goal_replay(self):
        if self.nb_camera < 3:
            replay_row = [sg.Image('',
                                   size=CAM_RESOLUTION_BIG,
                                   key=key) for key in self.camera_keys]
        else:
            replay_row = [sg.Image('',
                                   size=CAM_RESOLUTION_SMALL,
                                   key=key) for key in self.camera_keys]

        replay_window = sg.Window("Replay", [replay_row], finalize=True)

        # create media players
        media_players = []
        for key in self.camera_keys:
            media_players.append(self.vlc_instance.media_player_new())
            self.window[key].expand(True, True)
            media_players[-1].set_hwnd(replay_window[key].Widget.winfo_id())

        # play the last goal
        i = 1
        for media_player in media_players:
            goal_number = self.game.player_blue.score + self.game.player_red.score
            source = os.path.join(self.game_videos_path,
                                  'goal_%d' % goal_number,
                                  'cam%d.avi' % i)
            i += 1

            media = self.vlc_instance.media_new(source)
            media_player.set_media(media)
            media_player.play()

        event, values = replay_window.read()
        replay_window.close()

    def save_goal_replay(self):
        """
        Save goal replays in a folder named 'goal_<goal_number>'
        """
        goal_number = self.game.player_blue.score + self.game.player_red.score
        folder_path = os.path.join(self.game_videos_path,
                                   'goal_%d' % goal_number)

        # if the folder already exists, it means that a goal was false
        # registered and was deleted. This means we just override the replays
        try:
            os.mkdir(folder_path)
        except FileExistsError:
            pass

        i = 1
        for webcam in self.webcams:
            filename = os.path.join(folder_path, 'cam%d.avi' % i)
            i += 1
            webcam.save_buffer(filename)

    def run(self):
        """
        Runs the GUI by running the event loop.
        """
        while True:
            event, values = self.window.read(timeout=20)

            # To avoid errors
            if event is None:
                break

            if len(event) == 1:
                # Blue goal
                if event == 'b':
                    # update score
                    self.game.goal(self.game.player_blue)
                    self.window["k_blue_score"].update(value=self.game.player_blue.score)

                    self.save_goal_replay()
                    sleep(REPLAY_DELAY)
                    self.play_goal_replay()

                    # restart the listening after the replay
                    self.detector.start(self.window.write_event_value)

                # Red goal
                elif event == 'r':
                    self.game.goal(self.game.player_red)
                    self.window["k_red_score"].update(value=self.game.player_red.score)

                    self.save_goal_replay()
                    sleep(REPLAY_DELAY)
                    self.play_goal_replay()

                    # restart the listening after the replay
                    self.detector.start(self.window.write_event_value)

            # Update score when the spinner is changed
            if event == 'k_blue_score':
                if self.window['k_blue_score'].get() > self.game.player_blue.score:
                    self.game.goal(self.game.player_blue)
                elif self.game.player_blue.score > 0:
                    self.game.player_blue.score -= 1

            elif event == 'k_red_score':
                if self.window['k_red_score'].get() > self.game.player_red.score:
                    self.game.goal(self.game.player_red)
                elif self.game.player_red.score > 0:
                    self.game.player_red.score -= 1

            # Connect to the webcam
            if event == "Connect camera(s)":
                ips_raw = sg.popup_get_text("Please enter the IPs (max 3) separated by a ','")

                # check if input is not empty
                if ips_raw:
                    self.connect_webcams(parse_IPs(ips_raw))
                    self.streaming = True

            # Resets the score for a new game
            if event == "New Game":
                self.game.reset()
                self.window['k_blue_score'].update(self.game.player_blue.score)
                self.window['k_red_score'].update(self.game.player_red.score)

                # if checked, delete goal replays
                if self.window['k_delete_replays'].get():
                    shutil.rmtree(self.game_videos_path)
                    print("Replays deleted.")

                self.setup_replay_folders()

            # Stream the webcam output to the main window screen
            if self.streaming:
                for key, webcam in zip(self.camera_keys, self.webcams):
                    self.window[key].update(data=webcam.current_frame())

            # Closing the window
            if event == "Exit" or event == sg.WIN_CLOSED:
                self.detector.stop()
                # if checked, delete goal replays
                if self.window['k_delete_replays'].get():
                    shutil.rmtree(self.game_videos_path)
                    print("Replays deleted.")
                break

        # cleaning up
        self.disconnect_webcams()
        self.window.close()
