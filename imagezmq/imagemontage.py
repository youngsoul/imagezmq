import sys
sys.path.insert(0, '../')  # imagezmq.py is in ../imagezmq
from imutils import build_montages
import imutils
from imagezmq.imagezmq import ImageHub
import cv2
import threading


class ImageMontage(object):

    def __init__(self, number_of_rows=1, number_of_columns=1, image_width=400):
        self.number_of_rows = number_of_rows
        self.number_of_columns = number_of_columns
        self.image_width = image_width

    def disply_montage(self):
        # initialize the ImageHub object
        imageHub = ImageHub()
        frameDict = {}

        # 1 row (mH) and 2 columns (mW)
        mW = self.number_of_columns
        mH = self.number_of_rows
        while True:
            (serverName, frame) = imageHub.recv_image()
            imageHub.send_reply(b'OK')

            frame = imutils.resize(frame, width=self.image_width)
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

    def run_in_background(self):
        self.background_thread = threading.Thread(target=self.disply_montage, args=())
        self.background_thread.daemon = True
        self.background_thread.start()




