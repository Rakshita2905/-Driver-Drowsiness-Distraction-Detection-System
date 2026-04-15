import cv2
import numpy as np

class HeadPoseEstimator:
    """
    3D Head Pose Estimation
    """
    
    def __init__(self):
        # 3D model points
        self.model_points = np.array([
            (0.0, 0.0, 0.0),           # Nose tip
            (0.0, -330.0, -65.0),       # Chin
            (-225.0, 170.0, -135.0),    # Left eye left corner
            (225.0, 170.0, -135.0),     # Right eye right corner
            (-150.0, -150.0, -125.0),   # Left Mouth corner
            (150.0, -150.0, -125.0)     # Right mouth corner
        ])
        
        # Camera matrix
        self.focal_length = 640
        self.center = (320, 240)
        self.camera_matrix = np.array([
            [self.focal_length, 0, self.center[0]],
            [0, self.focal_length, self.center[1]],
            [0, 0, 1]
        ], dtype="double")
        
        self.dist_coeffs = np.zeros((4, 1))
        
        # Thresholds
        self.PITCH_THRESH = 15
        self.YAW_THRESH = 20
        self.ROLL_THRESH = 15
        
        # Smoothing
        self.pose_history = []
        self.history_size = 10
    
    def estimate_pose(self, image_points):
        """Estimate head pose from 2D image points"""
        if image_points is None or len(image_points) < 6:
            return None
        
        try:
            success, rotation_vector, translation_vector = cv2.solvePnP(
                self.model_points, image_points.astype(np.float32), 
                self.camera_matrix, self.dist_coeffs, 
                flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if not success:
                return None
            
            # Get Euler angles
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            pitch, yaw, roll = self.get_euler_angles(rotation_matrix)
            
            return pitch, yaw, roll
        except:
            return None
    
    def get_euler_angles(self, rotation_matrix):
        """Extract pitch, yaw, roll from rotation matrix"""
        sy = np.sqrt(rotation_matrix[0,0] ** 2 + rotation_matrix[1,0] ** 2)
        singular = sy < 1e-6
        
        if not singular:
            pitch = np.arctan2(rotation_matrix[2,1], rotation_matrix[2,2]) * 180 / np.pi
            yaw = np.arctan2(-rotation_matrix[2,0], sy) * 180 / np.pi
            roll = np.arctan2(rotation_matrix[1,0], rotation_matrix[0,0]) * 180 / np.pi
        else:
            pitch = np.arctan2(-rotation_matrix[1,2], rotation_matrix[1,1]) * 180 / np.pi
            yaw = np.arctan2(-rotation_matrix[2,0], sy) * 180 / np.pi
            roll = 0
        
        return pitch, yaw, roll
    
    def is_looking_away(self, yaw, pitch):
        """Check if driver is looking away"""
        return abs(yaw) > self.YAW_THRESH or abs(pitch) > self.PITCH_THRESH