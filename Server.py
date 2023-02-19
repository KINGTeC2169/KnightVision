import cv2

from CameraServer import CameraServer

# Method that starts the ServerFolde system
def startStreamer():

    # Create and start the camera threads
    # These threads cannot die.  They now only need to be started once.

    Front = CameraServer(5800)
    Right = CameraServer(5802)
    Left = CameraServer(5801)
    Palm = CameraServer(5803)
    Front.start()
    Right.start()
    Left.start()
    Palm.start()


# Start this flaming pile of garbage
startStreamer()
