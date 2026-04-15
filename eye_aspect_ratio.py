import numpy as np
from scipy.spatial import distance as dist

class EyeAspectRatio:
    """
    Calculate Eye Aspect Ratio (EAR) for drowsiness detection
    """
    
    def __init__(self, ear_threshold=0.25, consecutive_frames=48):
        self.EAR_THRESHOLD = ear_threshold
        self.CONSECUTIVE_FRAMES = consecutive_frames
        self.ear_history = []
        self.history_size = 30
        
        # Eye landmark indices for MediaPipe Face Mesh
        self.LEFT_EYE_POINTS = [33, 133, 157, 158, 159, 160, 161, 173]
        self.RIGHT_EYE_POINTS = [362, 263, 387, 386, 385, 384, 398, 466]
        
    def eye_aspect_ratio(self, eye_points):
        """
        Calculate the Eye Aspect Ratio (EAR)
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        """
        if len(eye_points) < 6:
            return 0.3  # Default value
        
        # Vertical eye landmarks
        A = dist.euclidean(eye_points[1], eye_points[5])
        B = dist.euclidean(eye_points[2], eye_points[4])
        
        # Horizontal eye landmark
        C = dist.euclidean(eye_points[0], eye_points[3])
        
        # Compute EAR
        if C == 0:
            return 0.3
        ear = (A + B) / (2.0 * C)
        return ear
    
    def adaptive_threshold(self, current_ear):
        """Adaptive thresholding based on recent EAR history"""
        self.ear_history.append(current_ear)
        if len(self.ear_history) > self.history_size:
            self.ear_history.pop(0)
        
        if len(self.ear_history) > 10:
            mean_ear = np.mean(self.ear_history)
            std_ear = np.std(self.ear_history)
            adaptive_thresh = mean_ear - 1.5 * std_ear
            return max(adaptive_thresh, 0.15)
        return self.EAR_THRESHOLD
    
    def smooth_ear(self, ear):
        """Apply temporal smoothing to reduce noise"""
        self.ear_history.append(ear)
        if len(self.ear_history) > 5:
            return np.mean(self.ear_history[-5:])
        return ear