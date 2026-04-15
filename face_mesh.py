import cv2
import mediapipe as mp
import numpy as np

class FaceMeshDetector:
    """
    3D Facial Landmark Detection using MediaPipe
    """
    
    def __init__(self, static_image_mode=False, max_faces=1, 
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Eye landmark indices
        self.LEFT_EYE_INDICES = [33, 133, 157, 158, 159, 160, 161, 173]
        self.RIGHT_EYE_INDICES = [362, 263, 387, 386, 385, 384, 398, 466]
        
        # Head pose landmarks
        self.HEAD_POSE_INDICES = [1, 33, 61, 199, 263, 397]
        
    def find_faces(self, img, draw=True):
        """Detect faces and return landmarks"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.face_mesh.process(img_rgb)
        
        landmarks = []
        if self.results.multi_face_landmarks:
            for face_landmarks in self.results.multi_face_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS)
                
                face_points = []
                h, w, c = img.shape
                for lm in face_landmarks.landmark:
                    x, y = int(lm.x * w), int(lm.y * h)
                    face_points.append([x, y])
                landmarks.append(face_points)
        
        return img, landmarks
    
    def get_eye_landmarks(self, landmarks):
        """Extract eye landmarks"""
        if not landmarks or len(landmarks) == 0:
            return None, None
        
        left_eye = []
        right_eye = []
        
        for idx in self.LEFT_EYE_INDICES:
            if idx < len(landmarks[0]):
                left_eye.append(landmarks[0][idx])
        
        for idx in self.RIGHT_EYE_INDICES:
            if idx < len(landmarks[0]):
                right_eye.append(landmarks[0][idx])
        
        return left_eye, right_eye
    
    def get_head_pose_landmarks(self, landmarks):
        """Get landmarks for head pose estimation"""
        if not landmarks or len(landmarks) == 0:
            return None
        
        head_points = []
        for idx in self.HEAD_POSE_INDICES:
            if idx < len(landmarks[0]):
                head_points.append(landmarks[0][idx])
        
        return np.array(head_points) if head_points else None