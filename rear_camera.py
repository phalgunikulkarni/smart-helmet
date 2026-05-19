# rear_camera.py
# Detects obstacles behind the rider using Pi Camera Module V2
# On Windows: uses laptop webcam or a test image for simulation
# On Raspberry Pi: uses Pi Camera via OpenCV

import cv2
import platform
import time

SIMULATED = platform.system() != "Linux"

# ── Settings ──────────────────────────────────────────────
CAMERA_INDEX    = 0      # 0 = default webcam on laptop
FRAME_WIDTH     = 640
FRAME_HEIGHT    = 480
OBSTACLE_AREA   = 8000   # minimum contour area to count as obstacle
DETECTION_DELAY = 0.1    # seconds between frames

def initialize_camera():
    """Start the camera feed"""
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("[ERROR] Could not open camera.")
        return None

    print("[INFO] Camera initialized successfully")
    return cap

def detect_obstacles(frame, prev_frame):
    """
    Compare current frame to previous frame.
    Moving objects show up as bright regions in the diff.
    """
    # Convert to grayscale
    gray_curr = cv2.cvtColor(frame,      cv2.COLOR_BGR2GRAY)
    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Blur to reduce noise
    gray_curr = cv2.GaussianBlur(gray_curr, (21, 21), 0)
    gray_prev = cv2.GaussianBlur(gray_prev, (21, 21), 0)

    # Find difference between frames
    diff = cv2.absdiff(gray_prev, gray_curr)

    # Threshold — only keep significant changes
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find contours (moving regions)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    obstacles = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > OBSTACLE_AREA:
            x, y, w, h = cv2.boundingRect(contour)
            obstacles.append((x, y, w, h, area))

    return obstacles, thresh

def draw_detections(frame, obstacles):
    """Draw boxes around detected obstacles"""
    for (x, y, w, h, area) in obstacles:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.putText(
            frame, f"OBSTACLE ({int(area)})",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2
        )
    return frame

# ── Main loop ──────────────────────────────────────────────
if __name__ == "__main__":
    print("[INFO] Rear Camera Obstacle Detection started...")
    print("[INFO] Press Q to quit\n")

    cap = initialize_camera()
    if cap is None:
        exit()

    # Read first frame as reference
    ret, prev_frame = cap.read()
    if not ret:
        print("[ERROR] Could not read from camera.")
        cap.release()
        exit()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Lost camera feed.")
                break

            obstacles, thresh = detect_obstacles(frame, prev_frame)

            # Draw detections on frame
            annotated = draw_detections(frame.copy(), obstacles)

            # Print to terminal
            if obstacles:
                print(f"🚨 OBSTACLE DETECTED — {len(obstacles)} object(s) in view!")
            else:
                print("   Clear — no obstacles")

            # Show live video windows
            cv2.imshow("Rear Camera Feed", annotated)
            cv2.imshow("Motion Mask",      thresh)

            # Update previous frame
            prev_frame = frame.copy()

            # Q to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(DETECTION_DELAY)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped.")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Camera released.")