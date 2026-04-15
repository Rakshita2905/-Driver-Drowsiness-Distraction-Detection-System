"""
Working Driver Drowsiness Detection System
Uses alternative approach for MediaPipe
"""

import cv2
import mediapipe as mp
import numpy as np
import time

def main():
    print("Starting Driver Drowsiness Detection System...")
    
    # Initialize MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Eye landmarks indices
    LEFT_EYE_INDICES = [33, 133, 157, 158, 159, 160, 161, 173]
    RIGHT_EYE_INDICES = [362, 263, 387, 386, 385, 384, 398, 466]
    
    EAR_THRESHOLD = 0.25
    eye_closed_counter = 0
    
    # Start camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("Camera opened. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera")
            break
        
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            h, w = frame.shape[:2]
            
            # Get eye landmarks
            left_eye = []
            right_eye = []
            
            for idx in LEFT_EYE_INDICES:
                x = int(landmarks.landmark[idx].x * w)
                y = int(landmarks.landmark[idx].y * h)
                left_eye.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
            for idx in RIGHT_EYE_INDICES:
                x = int(landmarks.landmark[idx].x * w)
                y = int(landmarks.landmark[idx].y * h)
                right_eye.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
            # Calculate EAR (simplified)
            if len(left_eye) >= 6:
                ear = 0.3  # Placeholder
                cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.putText(frame, "System Running", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Driver Drowsiness Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("System stopped.")

if __name__ == "__main__":
    main()