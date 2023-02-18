import cv2

from CameraServer import CameraServer

# Method that starts the ServerFolde system
def startStreamer():

    # Create and start the camera threads
    # These threads cannot die.  They now only need to be started once.

    c1 = CameraServer(5800)
    c1.start()


# Start this flaming pile of garbage
startStreamer()
