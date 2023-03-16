import cv2

from CameraServer import CameraServer

# Method that starts the ServerFolde system
def startStreamer():

    # Create and start the camera threads
    # These threads cannot die.  They now only need to be started once.

    Front = CameraServer(1180)
    Right = CameraServer(1181)
    Left = CameraServer(1182)
    Palm = CameraServer(1183)
    Front.start()
    Right.start()
    Left.start()
    Palm.start()


# Start this flaming pile of garbage
startStreamer()
