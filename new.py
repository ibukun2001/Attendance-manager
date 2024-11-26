import cv2
import time

# Open the video file or webcam (0 for default webcam)
cap = cv2.VideoCapture(0)  # Change to 'video.mp4' for a video file

# Get the frame rate (fps) for video files
fps = cap.get(cv2.CAP_PROP_FPS)
interval_frames = None
if fps > 0:
    interval_frames = int(fps * 0.5)  # For videos, process every 0.5 seconds based on frames

# For webcams, use a time-based interval
interval_time = 0.5  # Process every 0.5 seconds
last_processed_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # For videos, process frames based on frame intervals
    if interval_frames:
        frame_position = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        if frame_position % interval_frames == 0:
            cv2.imshow('Frame', frame)
            # Add your processing code here
            unique_encoded,unique_faces,today,init_len = process(img, unique_encoded, unique_faces, today, init_len)

    # For webcams, process frames based on time intervals
    else:
        current_time = time.time()
        if current_time - last_processed_time >= interval_time:
            last_processed_time = current_time
            cv2.imshow('Frame', frame)
            # Add your processing code here
            unique_encoded, unique_faces, today, init_len = process(img, unique_encoded, unique_faces, today, init_len)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
