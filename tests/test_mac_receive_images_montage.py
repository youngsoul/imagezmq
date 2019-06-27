import sys
sys.path.insert(0, '../')  # imagezmq.py is in ../imagezmq
from imutils import build_montages
import imutils
from imagezmq.imagezmq import ImageHub
import cv2

# initialize the ImageHub object
imageHub = ImageHub()
frameDict = {}

# 1 row (mH) and 2 columns (mW)
mW = 2
mH = 1
image_count = 0
while True:
    (serverName, frame) = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    image_count += 1
    print(".", end="", flush=True)
    if image_count > 0 and image_count % 25 == 0:
        print("")


    frame = imutils.resize(frame, width=400)
    (h, w) = frame.shape[:2]

    # draw the sending device name on the frame
    cv2.putText(frame, serverName, (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


    # update the new frame in the frame dictionary
    frameDict[serverName] = frame

    # build a montage using images in the frame dictionary
    montages = build_montages(frameDict.values(), (w, h), (mW, mH))

    # display the montage(s) on the screen
    for (i, montage) in enumerate(montages):
        cv2.imshow("Monitor Dashboard ({})".format(i),
                   montage)


    # detect any kepresses
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()

