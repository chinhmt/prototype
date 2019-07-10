# Simple server for one http-client serving

import cv2
import zmq
import base64
import numpy as np
from flask import Flask, render_template, Response

app = Flask(__name__)
ret, jpeg = cv2.imencode('.jpg', np.zeros([480, 640, 3], dtype=np.uint8))
default_frame = jpeg.tobytes()

context = zmq.Context()
zmq_socket = context.socket(zmq.SUB)
zmq_socket.connect('tcp://localhost:5555')
zmq_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

@app.route('/')
def index():
    return render_template('index.html')

def getFrame():
    global default_frame

    while True:
        try:
            frame = zmq_socket.recv_string(zmq.NOBLOCK)
            if frame is None:
                raise Exception
            img = base64.b64decode(frame)
            npimg = np.frombuffer(img, dtype=np.uint8)
            ret, jpeg = cv2.imencode('.jpg', cv2.imdecode(npimg, 1))
            source = jpeg.tobytes()
            default_frame = source
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + source + b'\r\n\r\n')
        except:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + default_frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(getFrame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
