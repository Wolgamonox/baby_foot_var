import json

import PySimpleGUI as sg

from core.utils import constants


class Settings_dialog:
    """
    Simple dialog to change settings
    """

    def __init__(self):
        # Load default settings
        with open(constants.DEFAULT_SETTINGS_PATH, "r") as content:
            self.default_settings = json.load(content)

        # Load current settings
        try:
            with open(constants.SETTINGS_PATH, "r") as content:
                self.settings = json.load(content)
        except FileNotFoundError:
            self.settings = self.default_settings
            self.save()

        self.window = sg.Window("Settings",
                                self.setup_layout(),
                                finalize=True,
                                keep_on_top=True,
                                element_justification='right')

    def setup_layout(self):
        """
        Setup layout for settings dialog
        """
        replay_settings = [sg.Frame("Replay", [
            [sg.Text('Speed factor', size=(15, 1), tooltip='How much the video is slowed'),
             sg.Input(self.settings['speed_factor'], key='speed_factor')],
            [sg.Text('Replay duration', size=(15, 1), tooltip='How long the replay will be'),
             sg.Input(self.settings['replay_duration'], key='replay_duration')],
            [sg.Text('Replay delay', size=(15, 1), tooltip='Time between the goal detection and the replay'),
             sg.Input(self.settings['replay_delay'], key='replay_delay')],
        ])]

        serial_settings = [sg.Frame("Serial", [
            [sg.Text('Baudrate', size=(15, 1), tooltip='Serial Baudrate'),
             sg.Input(self.settings['baudrate'], key='baudrate')],
            [sg.Text('Port (Optional)', size=(15, 1), tooltip='Leave empty for automatic detection'),
             sg.Input(self.settings['port'], key='port')],
            [sg.Text('Detector Sample Rate', size=(15, 1), tooltip='IR detector sample rate'),
             sg.Input(self.settings['detector_sample_rate'], key='detector_sample_rate')],
        ])]

        buttons = [sg.Button("Save", pad=(0, 2)), sg.Button("Reset to defaults")]

        return [replay_settings, serial_settings, buttons]

    def save(self):
        """
        Saves the current settings in the settings file
        """
        with open(constants.SETTINGS_PATH, "w") as out_file:
            json.dump(self.settings, out_file, indent=4)

    def run(self):
        """
        Runs the settings dialog
        """

        while True:
            event, values = self.window.read()
            if event in ("Exit", sg.WIN_CLOSED):
                break

            # Save new settings
            elif event == "Save":
                for key in self.settings:
                    self.settings[key] = self.window[key].get()
                self.save()
                break

            # Reset to defaults
            elif event == "Reset to defaults":
                self.settings = self.default_settings

                for key in self.settings:
                    self.window[key].update(self.settings[key])
                self.save()

        self.window.close()
