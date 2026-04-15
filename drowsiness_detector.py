import cv2
import numpy as np
from collections import deque
import time
from .eye_aspect_ratio import EyeAspectRatio
from .face_mesh import FaceMeshDetector
from .head_pose import HeadPoseEstimator

class DrowsinessDetector:
    """
    Main Drowsiness Detection Class
    """
    
    def __init__(self, config):
        self.config = config
        self.ear_calculator = EyeAspectRatio(
            ear_threshold=config['ear']['threshold'],
            consecutive_frames=config['ear']['consecutive_frames']
        )
        self.face_detector = FaceMeshDetector()
        self.head_pose = HeadPoseEstimator()
        
        self.eye_closed_counter = 0
        self.drowsy_state = False
        self.ear_history = deque(maxlen=100)
        
    def detect_drowsiness(self, frame):
        """
        Main detection pipeline
        Returns: (frame_with_annotations, drowsiness_score, is_drowsy, eye_status)
        """
        # Detect face and landmarks
        frame, landmarks = self.face_detector.find_faces(frame)
        
        if not landmarks:
            return frame, 0, False, "No Face Detected"
        
        # Get eye landmarks
        left_eye, right_eye = self.face_detector.get_eye_landmarks(landmarks)
        
        if left_eye and right_eye and len(left_eye) >= 6 and len(right_eye) >= 6:
            # Calculate EAR
            left_ear = self.ear_calculator.eye_aspect_ratio(left_eye)
            right_ear = self.ear_calculator.eye_aspect_ratio(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Apply smoothing
            smoothed_ear = self.ear_calculator.smooth_ear(avg_ear)
            self.ear_history.append(smoothed_ear)
            
            # Get adaptive threshold
            adaptive_thresh = self.ear_calculator.adaptive_threshold(smoothed_ear)
            
            # Detect eye closure
            if smoothed_ear < adaptive_thresh:
                self.eye_closed_counter += 1
                eye_status = "CLOSED"
            else:
                self.eye_closed_counter = max(0, self.eye_closed_counter - 1)
                eye_status = "OPEN"
            
            # Check for drowsiness
            drowsiness_score = min(1.0, self.eye_closed_counter / self.ear_calculator.CONSECUTIVE_FRAMES)
            is_drowsy = self.eye_closed_counter >= self.ear_calculator.CONSECUTIVE_FRAMES
            
            # Draw annotations
            frame = self.draw_annotations(frame, smoothed_ear, adaptive_thresh, 
                                         eye_status, drowsiness_score)
            
            return frame, drowsiness_score, is_drowsy, eye_status
        
        return frame, 0, False, "Eyes Not Visible"
    
    def draw_annotations(self, frame, ear, threshold, eye_status, drowsiness_score):
        """Draw real-time annotations"""
        h, w = frame.shape[:2]
        
        # Background overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
        
        # EAR value
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Eye status
        color = (0, 0, 255) if eye_status == "CLOSED" else (0, 255, 0)
        cv2.putText(frame, f"Eyes: {eye_status}", (250, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Drowsiness bar
        bar_width = int(drowsiness_score * 300)
        cv2.rectangle(frame, (250, 50), (550, 70), (100, 100, 100), -1)
        cv2.rectangle(frame, (250, 50), (250 + bar_width, 70), (0, 0, 255), -1)
        cv2.putText(frame, f"Drowsiness: {drowsiness_score:.0%}", (250, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Alert
        if drowsiness_score > 0.7:
            cv2.putText(frame, "DROWSY! PLEASE REST!", (w//2 - 150, h - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        return frame