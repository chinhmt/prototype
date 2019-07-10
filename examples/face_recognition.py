# This example from https://github.com/ageitgey/face_recognition with some modifications for jupyter

import zmq
import cv2
import base64
import numpy as np
import face_recognition

from IPython import display
import matplotlib.pyplot as py

%matplotlib inline

# Use PUB-SUB model for images streaming
zmq_context = zmq.Context()
stream_socket = zmq_context.socket(zmq.PUB)
stream_socket.bind('tcp://*:5555')

video_capture = cv2.VideoCapture(0)
detecting_image = face_recognition.load_image_file("photo.jpg")
detecting_face_encoding = face_recognition.face_encodings(detecting_image)[0]

known_face_encodings = [
    detecting_face_encoding
]
known_face_names = [
    "Donald Trump"
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    ret, frame = video_capture.read()

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 1)

    encoded, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)
    stream_socket.send(jpg_as_text)

    py.title("Input Stream")
    py.imshow(frame[:, :, ::-1])
    py.show()
    display.clear_output(wait=True)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
