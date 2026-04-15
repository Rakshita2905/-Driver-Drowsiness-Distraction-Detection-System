"""
Driver Drowsiness Detection - Complete Version
With Sound Alerts, Logging, and Adjustable Sensitivity
"""

import cv2
import numpy as np
import time
from datetime import datetime
import winsound  # For sound alerts
import os

class DrowsinessDetector:
    def __init__(self):
        # Load face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Load eye detector
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        # ========== ADJUST SENSITIVITY HERE ==========
        # Lower number = MORE sensitive (alerts faster)
        # Higher number = LESS sensitive (alerts slower)
        self.EYE_CLOSED_THRESHOLD = 3  # Default: 5 frames (~0.2 seconds)
        # Try these values:
        # 3 = Very Sensitive (alerts quickly)
        # 5 = Normal (recommended)
        # 10 = Less Sensitive (alerts after longer eye closure)
        # ============================================
        
        self.eye_closed_counter = 0
        self.drowsy_events = 0
        
        # For sound alert cooldown (prevents continuous beeping)
        self.last_alert_time = 0
        self.alert_cooldown = 3  # Seconds between alerts
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Initialize log file
        self.log_file = f"logs/drowsiness_log_{datetime.now().strftime('%Y%m%d')}.csv"
        self.init_log_file()
        
    def init_log_file(self):
        """Create log file with headers"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("timestamp,eyes_detected,drowsiness_score,drowsy_event,event_count\n")
    
    def log_event(self, eyes_detected, drowsiness_score, is_drowsy, event_count):
        """Log detection data to CSV file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(self.log_file, 'a') as f:
            f.write(f"{timestamp},{eyes_detected},{drowsiness_score:.2f},{is_drowsy},{event_count}\n")
    
    def play_alert_sound(self):
        """Play beep sound when drowsy detected"""
        try:
            # Different beep patterns based on severity
            current_time = time.time()
            
            # Check cooldown to avoid continuous beeping
            if current_time - self.last_alert_time >= self.alert_cooldown:
                # Play 3 beeps for drowsy alert
                for i in range(3):
                    winsound.Beep(1000, 500)  # 1000Hz for 500ms
                    time.sleep(0.2)
                self.last_alert_time = current_time
                print("\n🔔 ALERT: Drowsiness Detected! Take a break!\n")
        except:
            pass  # Silently fail if sound doesn't work
    
    def detect_eyes(self, face_roi):
        """Detect eyes in face region"""
        eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 5)
        return eyes
    
    def run(self):
        """Main detection loop"""
        print("="*60)
        print("🚗 Driver Drowsiness Detection System")
        print("="*60)
        print("✅ System Started!")
        print(f"⚙️  Sensitivity: {self.EYE_CLOSED_THRESHOLD} frames")
        print("🔊 Sound Alerts: ENABLED")
        print("📝 Logging: ENABLED")
        print("📌 Press 'q' to quit")
        print("📌 Press 's' to save screenshot")
        print("="*60)
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera not found!")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        frame_count = 0
        start_time = time.time()
        is_drowsy = False  # Track drowsy state for logging
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            # Calculate FPS
            frame_count += 1
            if time.time() - start_time > 1:
                fps = frame_count
                frame_count = 0
                start_time = time.time()
            else:
                fps = frame_count
            
            eyes_detected = 0
            
            for (x, y, w, h) in faces:
                # Draw face rectangle
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Face region of interest
                face_roi = gray[y:y+h, x:x+w]
                
                # Detect eyes in face region
                eyes = self.eye_cascade.detectMultiScale(face_roi, 1.05, 5)
                eyes_detected = len(eyes)
                
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 0, 0), 2)
            
            # Drowsiness detection logic
            previous_drowsy = is_drowsy
            
            if eyes_detected < 2:
                self.eye_closed_counter += 1
                eye_status = "NOT VISIBLE"
            else:
                self.eye_closed_counter = max(0, self.eye_closed_counter - 1)
                eye_status = "OPEN"
            
            # Check for drowsiness
            is_drowsy = self.eye_closed_counter >= self.EYE_CLOSED_THRESHOLD
            drowsiness_score = min(1.0, self.eye_closed_counter / self.EYE_CLOSED_THRESHOLD)
            
            # ========== SOUND ALERT ==========
            if is_drowsy:
                self.play_alert_sound()  # Play beep sound when drowsy
            # ================================
            
            # Count drowsy events (only when newly drowsy)
            if is_drowsy and not previous_drowsy:
                self.drowsy_events += 1
                print(f"⚠️  DROWSY EVENT #{self.drowsy_events} DETECTED at {datetime.now().strftime('%H:%M:%S')}")
            
            # ========== LOGGING ==========
            # Log data every frame
            self.log_event(eyes_detected, drowsiness_score, is_drowsy, self.drowsy_events)
            # =============================
            
            # Visual alert for drowsy state
            if is_drowsy:
                # Red alert border
                cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), 10)
                cv2.putText(frame, "!!! DROWSY ALERT !!!", (frame.shape[1]//2 - 150, frame.shape[0]//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            
            # Display info
            self.display_info(frame, eyes_detected, eye_status, drowsiness_score, fps, self.drowsy_events, is_drowsy)
            
            cv2.imshow("Driver Drowsiness Detection", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"screenshots/driver_{timestamp}.jpg", frame)
                print(f"📸 Screenshot saved: screenshots/driver_{timestamp}.jpg")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Print session summary
        print("\n" + "="*60)
        print("📊 SESSION SUMMARY")
        print("="*60)
        print(f"🛑 System Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Total Drowsy Events: {self.drowsy_events}")
        print(f"📝 Log file saved: {self.log_file}")
        print("="*60)
    
    def display_info(self, frame, eyes_detected, eye_status, drowsiness_score, fps, drowsy_events, is_drowsy):
        """Display information on frame"""
        h, w = frame.shape[:2]
        
        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 150), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        # Sensitivity info
        cv2.putText(frame, f"Sensitivity: {self.EYE_CLOSED_THRESHOLD} frames", (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Info
        cv2.putText(frame, f"Eyes Detected: {eyes_detected}", (10, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        color = (0, 0, 255) if eye_status == "NOT VISIBLE" else (0, 255, 0)
        cv2.putText(frame, f"Eye Status: {eye_status}", (10, 75), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        cv2.putText(frame, f"FPS: {fps}", (w-100, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Drowsy Events: {drowsy_events}", (w-180, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Drowsiness bar
        bar_width = int(drowsiness_score * 400)
        cv2.rectangle(frame, (10, 95), (410, 115), (100, 100, 100), -1)
        
        if drowsiness_score < 0.3:
            bar_color = (0, 255, 0)  # Green
        elif drowsiness_score < 0.7:
            bar_color = (0, 255, 255)  # Yellow
        else:
            bar_color = (0, 0, 255)  # Red
        
        cv2.rectangle(frame, (10, 95), (10 + bar_width, 115), bar_color, -1)
        cv2.putText(frame, f"Drowsiness: {drowsiness_score:.0%}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Sound alert indicator
        cv2.putText(frame, "🔊 Sound Alerts: ON", (w-130, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Instructions
        cv2.putText(frame, "Press 'q' to quit | 's' for screenshot", (10, h - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

if __name__ == "__main__":
    detector = DrowsinessDetector()
    detector.run()