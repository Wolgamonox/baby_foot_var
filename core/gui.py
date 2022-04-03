import os
import shutil
from datetime import datetime
from time import sleep

import PySimpleGUI as sg

from core.dialogs.replay_dialog import Replay_dialog
from core.dialogs.settings_dialog import Settings_dialog
from core.game_logic.game import Game
from core.utils import constants
from core.utils.serial_bridge import IR_Goal_Detector
from core.utils.utils import parse_IPs
from core.utils.webcam import Webcam


class Gui:
    """
    Graphical User Interface for a baby soccer/foosbal
    highlight record software.
    """
    def __init__(self, nb_camera):
        sg.theme('DarkGrey12')

        # Create initial settings file with the default settings
        if not os.path.exists(constants.SETTINGS_PATH):
            shutil.copyfile(constants.DEFAULT_SETTINGS_PATH, constants.SETTINGS_PATH)

        # Load settings
        sg.user_settings_filename(filename='settings.json', path='core\settings')

        self.nb_camera = nb_camera
        self.webcams = []

        # creating game
        self.game = Game()

        self.streaming = False

        # creating IR detector
        baudrate = int(sg.user_settings_get_entry('baudrate'))
        detector_sample_rate = int(sg.user_settings_get_entry('detector_sample_rate'))
        self.detector = IR_Goal_Detector(baudrate, detector_sample_rate)

        # creating main window
        self.camera_keys = ['k_cam_%d' % i for i in range(nb_camera)]
        layout = self.setup_layout()
        self.window = sg.Window("Table soccer",
                                layout,
                                return_keyboard_events=True,
                                finalize=True,
                                use_default_focus=False)

        # define callback to be called when a goal is detected
        self.goal_callback = self.window.write_event_value

        self.setup_replay_folders()

    def setup_layout(self):
        """
        Setup the layout for the main window.
        """

        # Menu bar
        menu_row = [sg.Menu([
            ["Settings", [
                "Edit settings",
                "&About"
            ]],
        ])]

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
                                       size=constants.CAM_RESOLUTION_BIG,
                                       key=key) for key in self.camera_keys]
        else:
            cameras_layout = [sg.Image('',
                                       size=constants.CAM_RESOLUTION_SMALL,
                                       key=key) for key in self.camera_keys]

        cameras_row = [
            sg.Frame("Cameras", [cameras_layout])
        ]

        # Controls
        controls_row = [
            sg.Frame("Controls", [[
                sg.Image(filename=constants.RED_LIGHT_ICON,
                         key="k_serial_port_status"),
                sg.Text("Detector connection status",
                          tooltip="Click to refresh",
                          enable_events=True),
                sg.Push(),
                sg.Checkbox("Delete replays",
                            default=True,
                            key='k_delete_replays'),
                sg.Button("New Game"),
                sg.Button("Connect camera(s)"),
            ]], expand_x=True)
        ]

        # Main layout
        layout = [
            menu_row,
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
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        goal_videos_path = os.path.join(dir_path, time_str)
        try:
            os.mkdir(goal_videos_path)
        except FileExistsError:
            pass # just override old file

        # add path to the constants
        constants.GOAL_VIDEOS_PATH = goal_videos_path

    def connect_webcams(self, ips):
        """
        Connect to the webcams and start the livestream.
        """

        # disconnect potential existing webcams
        self.disconnect_webcams()

        # Load variables from settings
        replay_duration = int(sg.user_settings_get_entry('replay_duration'))

        # creating webcams
        self.webcams = []
        for ip in ips:
            try:
                webcam = Webcam(ip, replay_duration)
                webcam.connect()
            except Exception as e:
                print("Error : %s" % e)
                return
            
            self.webcams.append(webcam)

        # start listening for goals
        self.detector.start(self.goal_callback)
        if self.detector.connected:
            self.window['k_serial_port_status'].update(filename=constants.GREEN_LIGHT_ICON)
        else:
            self.window['k_serial_port_status'].update(filename=constants.RED_LIGHT_ICON)
            print("Could not connect to the serial port. Please check the wiring or the settings")

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
        replay_dialog = Replay_dialog(self.camera_keys)

        goal_number = self.game.player_blue.score + self.game.player_red.score
        replay_dialog.play(goal_number)

        
    def save_goal_replay(self):
        """
        Save goal replays in a folder named 'goal_<goal_number>'
        """
        goal_number = self.game.player_blue.score + self.game.player_red.score
        folder_path = os.path.join(constants.GOAL_VIDEOS_PATH,
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

            # Closing the window
            if event in ("Exit", sg.WIN_CLOSED):
                # if checked, delete goal replays
                if self.window['k_delete_replays'].get():
                    shutil.rmtree(constants.GOAL_VIDEOS_PATH)
                    print("Replays deleted.")
                break

            # Goal detected
            elif event in ('r', 'b'):
                if event == 'b':
                    # update score
                    self.game.goal(self.game.player_blue)
                    self.window["k_blue_score"].update(value=self.game.player_blue.score)


                elif event == 'r':
                    self.game.goal(self.game.player_red)
                    self.window["k_red_score"].update(value=self.game.player_red.score)

                if len(self.webcams) > 0:
                    self.save_goal_replay()
                    sleep(int(sg.user_settings_get_entry('replay_delay')))
                    self.play_goal_replay()
                    # restart the listening after the replay
                    self.detector.start(self.goal_callback)

            # Update score when the spinner is changed
            elif event == 'k_blue_score':
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
            elif event == "Connect camera(s)":
                ips_raw = sg.popup_get_text("Please enter the IPs (max 3) separated by a ','")

                # check if input is not empty
                if ips_raw:
                    self.connect_webcams(parse_IPs(ips_raw))
                    if len(self.webcams) > 0:
                        self.streaming = True

            # Check if Serial port status
            elif event == "Detector connection status":
                self.detector.start(self.goal_callback)
                if self.detector.connected:
                    self.window['k_serial_port_status'].update(filename=constants.GREEN_LIGHT_ICON)
                else:
                    self.window['k_serial_port_status'].update(filename=constants.RED_LIGHT_ICON)
                    print("Could not connect to the serial port. Please check the wiring or the settings")

            # Resets the score for a new game
            elif event == "New Game":
                self.game.reset()
                self.window['k_blue_score'].update(self.game.player_blue.score)
                self.window['k_red_score'].update(self.game.player_red.score)

                # if checked, delete goal replays
                if self.window['k_delete_replays'].get():
                    try:
                        shutil.rmtree(constants.GOAL_VIDEOS_PATH)
                        print("Replays deleted.")
                    except PermissionError:
                        print("Could not delete the files, another process was using them. Try closing the replay window.")

                self.setup_replay_folders()

            # Open Settings dialog
            elif event == "Edit settings":
                settings_dialog = Settings_dialog()
                settings_dialog.run()
                # maybe not useful ? need to test
                sg.user_settings_load(filename='settings.json', path='core\settings')

            # Stream the webcam output to the main window screen
            if self.streaming:
                for key, webcam in zip(self.camera_keys, self.webcams):
                    self.window[key].update(data=webcam.current_frame())

        # cleaning up
        self.detector.stop()
        self.disconnect_webcams()
        self.window.close()
