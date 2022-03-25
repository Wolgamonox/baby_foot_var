from threading import Thread
from time import sleep
from types import NoneType

import cv2
import numpy as np

from core.utils.utils import Queue

SLOWING_FACTOR = 2    


class Webcam:
    """
    Webcam class for a droidcam using opencv
    """

    def __init__(self, ip, buffer_duration=5):
        self.ip = ip
        self.stream_url = 'http://' + self.ip + ':4747/video'
        self.fps = None


        self.is_buffering = False
        self.buffer = Queue()
        self.buffer_duration = buffer_duration

        self.cam_thread = None

    def connect(self):
        """
        Connect to a distant webcam using IP address and droidcam.
        """
        print('Connecting to %s ...' % self.ip)
        self.cap = cv2.VideoCapture(self.stream_url)

        if self.cap.isOpened():
            print('Succefully connected to %s!' % self.ip)
            self.fps = self.cap.get(5)

            # begin thread
            self.cam_thread = Thread(target=self.start_buffering,
                                     args=(self.cap, self.buffer_duration),
                                     daemon=True)
            self.cam_thread.start()

        else:
            print('Error: Could not connect %s.' % self.ip)

    def disconnect(self):
        """
        Disconnects the webcam
        """
        self.stop_buffering()
        self.cap.release()

        sleep(1)

        print('%s disconnected' % self.ip)

    def start_buffering(self, cap, duration):
        """
        Starts to buffer images from the camera
        for a certain duration (in seconds).
        """
        if not self.is_buffering:
            self.is_buffering = True

            nb_frames = self.fps * duration

            self.buffer = Queue(nb_frames)

            while self.is_buffering:
                ret, frame = cap.read()
                if ret:
                    self.buffer.put(frame)

    def stop_buffering(self):
        """
        Stops the buffering process.
        """
        if self.is_buffering:
            self.is_buffering = False
            self.cam_thread.join()

    def save_buffer(self, filename, slowing_factor=SLOWING_FACTOR, codec='MJPG'):
        """
        Saves the buffer to the filename provided (only tested for .avi files)
        Increase the slowing_factor to have a slow motion effect.
        """
        fourcc = cv2.VideoWriter_fourcc(*codec)
        frames = self.buffer.dump()

        (w, h) = (len(frames[0][0]), len(frames[0]))
        writer = cv2.VideoWriter(filename,
                                 fourcc,
                                 self.fps/float(slowing_factor),
                                 (w, h),
                                 True)

        for frame in frames:
            writer.write(frame)
        writer.release()

    def current_frame(self):
        """
        Returns the current frame to display the live video stream.
        """
        frame = self.buffer.last()
        if type(frame) == NoneType:
            frame = np.full((480, 640), 200)

        imgbytes = cv2.imencode('.png', frame)[1].tobytes()
        return imgbytes
