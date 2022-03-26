from threading import Thread
from time import sleep

import serial
from serial.tools import list_ports


class IR_Goal_Detector:
    """
    A communication bridge between the arduino IR detection system
    and the replay GUI.
    """
    def __init__(self, baudrate, sample_rate, port=None):
        self.sample_rate = sample_rate

        self.ser = serial.Serial()
        self.ser.baudrate = baudrate
        if port is None:
            self.ser.port = self.find_available_port()
        else:
            self.ser.port = port

        self.listening_thread = None
        self.listening = False

        self.connected = False

    def find_available_port(self):
        """
        Finds the first available COM port
        """
        ports = list(list_ports.comports())
        return ports[0].name

    def start(self, callback):
        """
        Starts to detect goals and executes the function given
        in the call back. The values given by detection are 'r'
        for red goal and 'b for blue goal.
        """
        if self.ser.is_open:
            self.connected = True
        else:
            try:
                self.ser.open()
            except serial.serialutil.SerialException:
                self.connected =  False

            self.connected = True

        # clean serial before starting to read
        self.ser.flushInput()

        self.listening_thread = Thread(target=self.thread, args=[callback])
        self.listening_thread.start()

    def thread(self, callback):
        """
        Thread to check the serial port.
        """
        if not self.listening:
            self.listening = True

            while self.listening:
                try:
                    val = self.ser.readline(1).decode()
                except serial.serialutil.SerialException:
                    self.connected = False
                    self.listening = False
                    break
                
                if val in ('b', 'r'):
                    callback(val, '')
                    self.listening = False

                sleep(1/self.sample_rate)
                self.ser.reset_input_buffer()

    def stop(self):
        """
        Stops the goal detection system.
        """
        self.listening = False
        self.listening_thread.join()
        self.ser.close()
