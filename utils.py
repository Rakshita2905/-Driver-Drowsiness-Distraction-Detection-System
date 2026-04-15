import cv2
import numpy as np
from datetime import datetime

class Utils:
    """Utility functions"""
    
    @staticmethod
    def resize_frame(frame, width=None, height=None):
        """Resize frame"""
        if width is None and height is None:
            return frame
        
        h, w = frame.shape[:2]
        if width is not None:
            ratio = width / w
            height = int(h * ratio)
        else:
            ratio = height / h
            width = int(w * ratio)
        
        return cv2.resize(frame, (width, height))
    
    @staticmethod
    def enhance_low_light(frame):
        """Enhance low light images"""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        return enhanced