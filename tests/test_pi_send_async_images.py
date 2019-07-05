import sys
sys.path.insert(0, '../')  # imagezmq.py is in ../imagezmq
import time
from imagezmq.asyncimagesender import AsyncImageSender
from imutils.video import VideoStream
import imutils as imutils
import socket
import argparse


"""
Test file that will create 2 AsyncImageSender classes and send an image to the specified server and port

"""

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=False, default='192.168.1.208',
                help="ip address of the server to which the client will connect")

args = vars(ap.parse_args())
server_ip = args['server_ip']

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()

video_stream = VideoStream(usePiCamera=True).start()

async_image_sender1 = AsyncImageSender(server_name=rpiName, server_ip=server_ip, port=5555, send_timeout=10, recv_timeout=10, show_frame_rate=10)
async_image_sender1.run_in_background()

image_count = 0

print("Press ctrl-c to stop async image sending")
while True:
    frame = video_stream.read()
    if frame is not None:
        frame = imutils.rotate(frame, 90)

        async_image_sender1.send_frame_async(frame)

        image_count += 1

        print(".", end="", flush=True)
        if image_count > 0 and image_count % 25 == 0:
            print("")

    time.sleep(0.25)


