from threading import Thread
from time import sleep

from serial import Serial


class IR_Goal_Detector:
    """
    A communication bridge between the arduino IR detection system
    and the replay GUI.
    """
    def __init__(self, port, baudrate, sample_rate):
        self.sample_rate = sample_rate

        self.ser = Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate

        self.listening_thread = None
        self.listening = False

    def start(self, callback):
        """
        Starts to detect goals and executes the function given
        in the call back. The values given by detection are 'r'
        for red goal and 'b for blue goal.
        """
        self.listening_thread = Thread(target=self.thread, args=[callback])
        self.listening_thread.start()

    def thread(self, callback):
        """
        Thread to check the serial port.
        """
        if not self.listening:
            self.listening = True
            if not self.ser.is_open:
                self.ser.open()

            while self.ser.is_open and self.listening:
                val = self.ser.readline(1).decode()
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
