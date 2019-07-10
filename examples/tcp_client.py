import cv2
import zmq
import base64
import numpy as np

context = zmq.Context()
zmq_socket = context.socket(zmq.SUB)
zmq_socket.connect('tcp://localhost:5555')
zmq_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

while True:
    try:
        frame = zmq_socket.recv_string(zmq.NOBLOCK)
        img = base64.b64decode(frame)
        npimg = np.frombuffer(img, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        cv2.imshow("Stream", source)
        cv2.waitKey(1)

    except zmq.ZMQError:
        continue
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break
