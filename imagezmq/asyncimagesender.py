from imagezmq.imagezmq import ImageSender
from queue import Queue
import time
import threading
from logging import getLogger

"""
Class used to simplify the sending of images in an asychronous fashion.

See tests/test_send_async_images.py for an example usage
See test/test_mac_receive_images_montage.py for an example of how to setup a montage window for
each of the test ImageSenders

NOTE: the tests ( but not this class ) assume you have OpenCV and imutils installed.

"""
class AsyncImageSender(object):

    def __init__(self, server_name="server", server_ip='127.0.0.1', port=5555,  send_timeout=0, recv_timeout=0, show_frame_rate=0, backlog=0):
        self.server_name = server_name
        self.server_ip = server_ip
        self.port = port
        self.send_timeout = send_timeout
        self.recv_timeout = recv_timeout
        self.frame_queue = Queue()
        self.background_thread = None
        self.show_frame_rate = show_frame_rate
        self.sender = None
        self.backlog = backlog

    def _create_sender(self):
        connect_to = f'tcp://{self.server_ip}:{self.port}'
        sender = ImageSender(connect_to=connect_to, send_timeout=self.send_timeout, recv_timeout=self.recv_timeout)
        return sender

    def _send_immediate(self, frame):
        start = time.time()
        frame_count = 0

        try:

            if self.show_frame_rate > 0:
                frame_count += 1
                delta = time.time() - start
                if delta > self.show_frame_rate:
                    print(f"Sending {(frame_count / delta)} frames/sec")
                    start = time.time()
                    frame_count = 0

            try:
                hub_reply = self.sender.send_image(self.server_name, frame)
            except Exception as exc:
                getLogger("AsyncImageSender").error("send_image exception")
                getLogger("AsyncImageSender").error(f"Exception msg: {exc}")
                print(exc)
                time.sleep(6)  # something happened, force a timeout
                raise TimeoutError
        except TimeoutError:
            getLogger("AsyncImageSender").error("Sending timeout.. reconnect to server")
            self.sender = self._create_sender()

    def _send_frame_background_function(self):
        self.sender = self._create_sender()

        while True:
            frame = self.frame_queue.get()
            self._send_immediate(frame)


    def run_in_background(self):
        self.background_thread = threading.Thread(target=self._send_frame_background_function, args=())
        self.background_thread.daemon = True
        self.background_thread.start()

    def send_frame_async(self, frame):
        if self.backlog > 0 and self.frame_queue.qsize() > self.backlog:
            print("no put")
            return
        print(f"Put frame: {self.frame_queue.qsize()}")
        self.frame_queue.put_nowait(frame)
        return

    def send_frame_immediate(self, frame):
        if self.background_thread is not None:
            raise Exception("Cannot send a frame immediately if there is a background thread running")

        if self.sender is None:
            self.sender = self._create_sender()

        self._send_immediate(frame)
        return

    def queue_size(self):
        return self.frame_queue.qsize()
