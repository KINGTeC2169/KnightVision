#!/usr/bin/python
import socket
import sys
import time
import traceback

import cv2
import numpy


def runClient(sock, img):


    # Grab a frame from the webcam
    frame = img

    # C R O N C H   that image down to half size
    newX, newY = frame.shape[1] * .5, frame.shape[0] * .5
    frame = cv2.resize(frame, (int(newX), int(newY)))

    # C R O N C H   that image down to extremely compressed JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 7]
    result, imgencode = cv2.imencode('.jpg', frame, encode_param)

    # Encode that JPEG string into a NumPy array for compatibility on the other side
    data = numpy.array(imgencode)

    # Turn NumPy array into a string so we can ship er' on over the information superhighway
    stringData = data.tostring()

    print(sys.getsizeof(stringData))

    # Send the size of the data for efficient unpacking
    sock.send(str(len(stringData)).ljust(16).encode())

    # Might as well send the actual data while we're sending things
    sock.send(stringData)

    # Arbitrary OpenCV wait statement that I still don't understand the purpose of but when I take it out it
    # doesn't work so here it will stay.
      


# This horrific piece of garbage just verifies that even if it crashes it gets up and tries again.  Please don't throw
# things at me.

