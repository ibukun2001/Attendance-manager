
import cv2 as cv
import dlib
import matplotlib.pyplot as plt
import numpy as np
import face_recognition
import os
import time
import module
import pandas as pd
import process


db_record = module.retrieve_from_db()
unique_encoded = db_record['face_encode']
unique_faces = db_record['face']
init_len = len(unique_encoded)
date = '25_10_2024'
today = [False] * len(unique_faces)

i = 1

# Open a video file or capture device
path = 'vid.mp4'
cap = cv.VideoCapture(path)

while cap.isOpened():
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to retrieve frame. Exiting loop.")
        break

    # Check if the frame was read successfully
    img = frame
    # Display the frame
    cv.imshow('VID', img)



    # Press 'q' to exit the loop
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv.destroyAllWindows()

#print(f"Done. {len(unique_encoded) - init_len} new faces")
#module.update_database(unique_encoded,unique_faces,today,date,init_len)