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
ap.add_argument("-r", "--rotate", required=False, type=float, default=0, help="Rotate the image by the provided degrees")
ap.add_argument("-b", "--backlog", required=False, type=int, default=0, help="Maximum number of messages in the queue before waiting for room")


args = vars(ap.parse_args())
server_ip = args['server_ip']
rotation = float(args['rotate'])
backlog = int(args['backlog'])
print(f"Backlog: {backlog}")

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()

video_stream = VideoStream(usePiCamera=True).start()

async_image_sender1 = AsyncImageSender(server_name=rpiName, server_ip=server_ip, port=5555, send_timeout=10, recv_timeout=10, show_frame_rate=0, backlog=backlog)
async_image_sender1.run_in_background()

image_count = 0

print("Press ctrl-c to stop async image sending")
sleep_time = 0.25
show_info = False
while True:
    frame = video_stream.read()
    if frame is not None:
        if rotation != 0:
            frame = imutils.rotate(frame, rotation)

        async_image_sender1.send_frame_async(frame)

        image_count += 1

        # print(".", end="", flush=True)

        if show_info:
            if image_count > 0 and image_count % 25 == 0:
                qsize = async_image_sender1.queue_size()
                if backlog > 0:
                    # then the user specified a backlog, check to see if we are under the backlog number
                    # and if we are - try to decrease the sleep_time for better frame rate.  if we are at
                    # the limit - then increase the sleep_time
                    if qsize < backlog:
                        if sleep_time > 0.05: # dont go to zero
                            sleep_time = sleep_time - 0.05
                    else:
                        if sleep_time < 0.25:
                            sleep_time = sleep_time + 0.05
                    print(f"frame pooling time: {sleep_time}")
                print(f"Queue Size: {qsize}")

    time.sleep(sleep_time)


