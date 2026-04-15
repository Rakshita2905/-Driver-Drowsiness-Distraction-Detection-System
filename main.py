import cv2
import yaml
import time
from datetime import datetime
from src.drowsiness_detector import DrowsinessDetector
from src.distraction_detector import DistractionDetector
from src.alert_system_simple import AlertSystem
from src.data_logger import DataLogger

class DriverMonitoringSystem:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.drowsiness_detector = DrowsinessDetector(self.config)
        self.distraction_detector = DistractionDetector(self.config)
        self.alert_system = AlertSystem(self.config)
        self.data_logger = DataLogger(self.config)
        
        self.cap = cv2.VideoCapture(self.config['system']['camera_id'])
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['system']['frame_width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['system']['frame_height'])
        
        self.running = True
        self.drowsiness_events = 0
        self.distraction_events = 0
        self.frame_count = 0
        self.start_time = time.time()
    
    def run(self):
        print("="*60)
        print("🚗 Driver Drowsiness & Distraction Detection System")
        print("="*60)
        print("✅ System Started!")
        print("📌 Press 'q' to quit")
        print("📌 Press 's' to save screenshot")
        print("📌 Press 'r' to reset statistics")
        print("="*60)
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to grab frame")
                break
            
            frame = cv2.flip(frame, 1)
            
            # Detect drowsiness
            frame, drowsiness_score, is_drowsy, eye_status = \
                self.drowsiness_detector.detect_drowsiness(frame)
            
            # Detect distraction
            frame, distraction_score, is_distracted, distraction_type = \
                self.distraction_detector.detect_distraction(frame)
            
            # Combined risk score
            risk_score = max(drowsiness_score, distraction_score)
            
            # Trigger alerts
            if is_drowsy:
                self.alert_system.trigger_alert('drowsy', 2)
                self.drowsiness_events += 1
                self.data_logger.log_event('drowsy', 2, f'Score: {drowsiness_score}')
            elif is_distracted:
                self.alert_system.trigger_alert('distracted', 2)
                self.distraction_events += 1
                self.data_logger.log_event('distraction', 2, distraction_type)
            
            # Calculate FPS
            self.frame_count += 1
            if time.time() - self.start_time > 1:
                fps = self.frame_count
                self.frame_count = 0
                self.start_time = time.time()
            else:
                fps = self.frame_count
            
            # Display info
            self.display_info(frame, risk_score, fps, drowsiness_score, distraction_score)
            
            # Log data
            self.data_logger.log_frame(drowsiness_score, distraction_score, 
                                      risk_score, eye_status, distraction_type)
            
            cv2.imshow("Driver Monitoring System", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"screenshots/driver_{timestamp}.jpg", frame)
                print(f"📸 Screenshot saved: screenshots/driver_{timestamp}.jpg")
            elif key == ord('r'):
                self.drowsiness_events = 0
                self.distraction_events = 0
                print("🔄 Statistics reset")
        
        self.cleanup()
    
    def display_info(self, frame, risk_score, fps, drowsiness_score, distraction_score):
        """Display system information"""
        h, w = frame.shape[:2]
        
        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h-100), (w, h), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        # FPS
        cv2.putText(frame, f"FPS: {fps}", (10, h-70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Risk score
        if risk_score < 0.3:
            color = (0, 255, 0)
            status = "LOW"
        elif risk_score < 0.7:
            color = (0, 255, 255)
            status = "MEDIUM"
        else:
            color = (0, 0, 255)
            status = "HIGH"
        
        cv2.putText(frame, f"RISK: {status}", (w-150, h-70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Events
        cv2.putText(frame, f"Drowsy: {self.drowsiness_events}", (10, h-40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Distraction: {self.distraction_events}", (10, h-15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Scores
        cv2.putText(frame, f"D: {drowsiness_score:.0%}", (w-150, h-40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        cv2.putText(frame, f"Dist: {distraction_score:.0%}", (w-150, h-15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.data_logger.close()
        print("\n" + "="*60)
        print("🛑 System Shutdown Complete")
        print("📊 Check logs folder for session reports")
        print("="*60)

if __name__ == "__main__":
    system = DriverMonitoringSystem()
    system.run()