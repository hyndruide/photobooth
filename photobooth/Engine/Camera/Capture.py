import threading
import cv2
import os
import json

class VideoCaptureThreading:
    def __init__(self):
        self.settings_camera = self.load_setting()
        self.cap = cv2.VideoCapture(self.settings_camera["camera_device"],eval(self.settings_camera["camera_backend"]))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings_camera["camera_res"][0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings_camera["camera_res"][1])
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def load_setting(self):
        if os.path.isfile('./photobooth/json/settings.json'):
            with open('./photobooth/json/settings.json', 'r') as f1:
                data = json.load(f1)
            return data['camera']


    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()