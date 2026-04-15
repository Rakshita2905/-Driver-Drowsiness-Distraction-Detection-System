"""
Unit tests for Driver Drowsiness Detection System
Run with: python -m pytest tests/test_detector.py
"""

import unittest
import sys
import os
import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.eye_aspect_ratio import EyeAspectRatio
from src.face_mesh import FaceMeshDetector
from src.head_pose import HeadPoseEstimator
from src.drowsiness_detector import DrowsinessDetector
from src.alert_system import AlertSystem
from src.data_logger import DataLogger

class TestEyeAspectRatio(unittest.TestCase):
    """Test Eye Aspect Ratio calculations"""
    
    def setUp(self):
        self.ear_calc = EyeAspectRatio(ear_threshold=0.25, consecutive_frames=48)
    
    def test_ear_calculation_normal(self):
        """Test EAR calculation with normal eye points"""
        # Simulated eye points for open eye
        eye_points = [
            (10, 20),   # p1
            (12, 18),   # p2
            (14, 18),   # p3
            (20, 20),   # p4
            (14, 22),   # p5
            (12, 22)    # p6
        ]
        ear = self.ear_calc.eye_aspect_ratio(eye_points)
        self.assertGreater(ear, 0.2)
        self.assertLess(ear, 0.5)
    
    def test_ear_calculation_closed(self):
        """Test EAR calculation with closed eye points"""
        # Simulated eye points for closed eye
        eye_points = [
            (10, 20),   # p1
            (12, 20),   # p2
            (14, 20),   # p3
            (20, 20),   # p4
            (14, 20),   # p5
            (12, 20)    # p6
        ]
        ear = self.ear_calc.eye_aspect_ratio(eye_points)
        self.assertLess(ear, 0.15)
    
    def test_adaptive_threshold(self):
        """Test adaptive threshold calculation"""
        ear_values = [0.3, 0.28, 0.26, 0.24, 0.22, 0.20, 0.18]
        for ear in ear_values:
            threshold = self.ear_calc.adaptive_threshold(ear)
            self.assertGreater(threshold, 0.15)
            self.assertLess(threshold, 0.35)
    
    def test_smooth_ear(self):
        """Test EAR smoothing"""
        ear = 0.25
        smoothed = self.ear_calc.smooth_ear(ear)
        self.assertEqual(smoothed, ear)
        
        # Test with multiple values
        for i in range(10):
            self.ear_calc.smooth_ear(0.3)
        self.assertEqual(len(self.ear_calc.ear_history), 10)

class TestFaceMeshDetector(unittest.TestCase):
    """Test Face Mesh Detector"""
    
    def setUp(self):
        self.detector = FaceMeshDetector()
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector.face_mesh)
        self.assertIsNotNone(self.detector.mp_face_mesh)
    
    def test_eye_landmark_indices(self):
        """Test eye landmark indices are correct"""
        self.assertEqual(len(self.detector.LEFT_EYE_INDICES), 8)
        self.assertEqual(len(self.detector.RIGHT_EYE_INDICES), 8)
        self.assertEqual(self.detector.LEFT_EYE_INDICES[0], 33)
        self.assertEqual(self.detector.RIGHT_EYE_INDICES[0], 362)

class TestHeadPoseEstimator(unittest.TestCase):
    """Test Head Pose Estimation"""
    
    def setUp(self):
        self.pose_estimator = HeadPoseEstimator()
    
    def test_initialization(self):
        """Test head pose estimator initialization"""
        self.assertIsNotNone(self.pose_estimator.model_points)
        self.assertEqual(len(self.pose_estimator.model_points), 6)
    
    def test_euler_angles(self):
        """Test Euler angle calculation"""
        # Create a simple rotation matrix (identity)
        rotation_matrix = np.eye(3)
        pitch, yaw, roll = self.pose_estimator.get_euler_angles(rotation_matrix)
        self.assertAlmostEqual(pitch, 0, places=5)
        self.assertAlmostEqual(yaw, 0, places=5)
        self.assertAlmostEqual(roll, 0, places=5)
    
    def test_looking_away_detection(self):
        """Test looking away detection"""
        # Normal looking
        self.assertFalse(self.pose_estimator.is_looking_away(0, 0))
        # Looking away
        self.assertTrue(self.pose_estimator.is_looking_away(30, 0))
        self.assertTrue(self.pose_estimator.is_looking_away(0, 20))

class TestDrowsinessDetector(unittest.TestCase):
    """Test Drowsiness Detector"""
    
    def setUp(self):
        config = {
            'ear': {'threshold': 0.25, 'consecutive_frames': 48},
            'head_pose': {'pitch_threshold': 15, 'yaw_threshold': 20, 'roll_threshold': 15},
            'distraction': {'face_not_visible_time': 2.0, 'looking_away_time': 2.0},
            'alerts': {'cooldown_time': 5},
            'logging': {'enabled': True, 'log_file': 'logs/test_log.csv', 'save_video': False}
        }
        self.detector = DrowsinessDetector(config)
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector.ear_calculator)
        self.assertIsNotNone(self.detector.face_detector)
        self.assertEqual(self.detector.eye_closed_counter, 0)
        self.assertFalse(self.detector.drowsy_state)

class TestAlertSystem(unittest.TestCase):
    """Test Alert System"""
    
    def setUp(self):
        config = {'alerts': {'cooldown_time': 5, 'volume': 0.8}}
        self.alert_system = AlertSystem(config)
    
    def test_initialization(self):
        """Test alert system initialization"""
        self.assertIsNotNone(self.alert_system.messages)
        self.assertEqual(len(self.alert_system.messages), 3)
    
    def test_alert_messages(self):
        """Test alert messages exist"""
        self.assertIn('drowsy', self.alert_system.messages)
        self.assertIn('microsleep', self.alert_system.messages)
        self.assertIn('distracted', self.alert_system.messages)

class TestDataLogger(unittest.TestCase):
    """Test Data Logger"""
    
    def setUp(self):
        config = {'logging': {'enabled': True, 'log_file': 'logs/test_log.csv'}}
        self.logger = DataLogger(config)
    
    def test_initialization(self):
        """Test logger initialization"""
        self.assertTrue(self.logger.enabled)
        self.assertIsNotNone(self.logger.stats)
    
    def test_log_frame(self):
        """Test frame logging"""
        try:
            self.logger.log_frame(0.5, 0.3, 0.5, "OPEN", "none")
            self.assertEqual(self.logger.stats['total_frames'], 1)
        except Exception as e:
            self.fail(f"Logging failed: {e}")

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEyeAspectRatio))
    suite.addTests(loader.loadTestsFromTestCase(TestFaceMeshDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestHeadPoseEstimator))
    suite.addTests(loader.loadTestsFromTestCase(TestDrowsinessDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLogger))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("="*60)
    print("Running Driver Monitoring System Tests")
    print("="*60)
    success = run_tests()
    print("="*60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("="*60)