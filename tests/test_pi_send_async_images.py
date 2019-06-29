import sys
sys.path.insert(0, '../')  # imagezmq.py is in ../imagezmq
import time
from imagezmq.asyncimagesender import AsyncImageSender
from imutils.video import VideoStream

"""
Test file that will create 2 AsyncImageSender classes and send an image to the specified server and port

"""

video_stream = VideoStream(usePiCamera=True).start()

async_image_sender1 = AsyncImageSender(server_name='test image sender 1', server_ip='192.168.1.208', port=5555, send_timeout=10, recv_timeout=10)
async_image_sender1.run_in_background()

image_count = 0

print("Press ctrl-c to stop async image sending")
while True:
    frame = video_stream.read()

    async_image_sender1.send_frame_async(frame)

    image_count += 1

    print(".", end="", flush=True)
    if image_count > 0 and image_count % 25 == 0:
        print("")

    time.sleep(0.25)


