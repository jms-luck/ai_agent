import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Cannot access the webcam.")
else:
    print("Webcam accessed. Checking for video feed...")

    time.sleep(1)

    ret, frame = cap.read()
    if not ret or frame is None:
        print("⚠️ WARNING: No video feed available.")
    else:
        # Check if the frame is mostly dark
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_intensity = np.mean(gray)

        if mean_intensity < 10:  # You can adjust this threshold
            print("🕶️ Frame is too dark. Webcam might be covered or shutter closed.")
        else:
            print("📷 Webcam is working and providing visible video feed.")
    cap.release()
    print("✅ Webcam closed after check.")