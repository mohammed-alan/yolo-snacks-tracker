# backend.py
import os
import sys
import cv2
import numpy as np
from ultralytics import YOLO
import socketio
import argparse
import base64
import time
import eventlet

# ------------------ PARSE ARGUMENTS ------------------
parser = argparse.ArgumentParser()
parser.add_argument('--model', required=True, help='Path to YOLO model file')
parser.add_argument('--source', required=True, help='Camera index, video file, IP camera URL, or image folder')
parser.add_argument('--thresh', default=0.5, type=float, help='Confidence threshold')
parser.add_argument('--resolution', default=None, help='Resolution WxH (e.g., 640x480)')
args = parser.parse_args()

MODEL_PATH = args.model
SOURCE = args.source
CONF_THRESH = args.thresh
RESOLUTION = args.resolution

# ------------------ LOAD YOLO MODEL ------------------
if not os.path.exists(MODEL_PATH):
    print(f"Model not found at {MODEL_PATH}")
    sys.exit(1)

print("Loading YOLO model...")
model = YOLO(MODEL_PATH, task='detect')
labels = model.names
print("Model loaded successfully.")

# ------------------ SETUP CAMERA / VIDEO ------------------
if os.path.isdir(SOURCE):
    # image folder
    imgs_list = [os.path.join(SOURCE, f) for f in os.listdir(SOURCE)
                 if f.lower().endswith(('.jpg','.jpeg','.png','.bmp'))]
    source_type = 'folder'
    img_count = 0
else:
    # treat everything else as a video / camera source (USB index, video file, or IP camera URL)
    try:
        cap_idx = int(SOURCE)
        cap = cv2.VideoCapture(cap_idx)
    except ValueError:
        cap = cv2.VideoCapture(SOURCE)  # IP webcam URL or video file
    if not cap.isOpened():
        print(f"ERROR: Unable to open camera or video source: {SOURCE}")
        sys.exit(1)
    source_type = 'video'  # covers USB, video file, and IP webcam

if RESOLUTION and source_type in ['video','usb']:
    w,h = map(int, RESOLUTION.split('x'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    resize = True
else:
    resize = False

# ------------------ SOCKET.IO SERVER ------------------
sio = socketio.Server(cors_allowed_origins="*", async_mode='eventlet')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

# ------------------ DETECTION LOOP ------------------
def detection_loop():
    bbox_colors = [
        (164,120,87), (68,148,228), (93,97,209), (178,182,133),
        (88,159,106), (96,202,231), (159,124,168), (169,162,241),
        (98,118,150), (172,176,184)
    ]

    frame_rate_buffer = []
    fps_avg_len = 200
    global img_count

    while True:
        try:
            # Load frame
            if source_type == 'folder':
                if img_count >= len(imgs_list):
                    print("All images processed. Exiting...")
                    sys.exit(0)
                frame = cv2.imread(imgs_list[img_count])
                img_count += 1
            else:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame or end of video. Exiting...")
                    break

            if frame is None:
                continue

            # Resize frame if requested
            if resize:
                frame = cv2.resize(frame, (w,h))

            t_start = time.perf_counter()

            # Run inference (same as app)
            
            results = model(frame, verbose=False)
            detections_list = []
            detections = results[0].boxes

            object_count = 0
            for i in range(len(detections)):
                conf = float(detections[i].conf.item())
                if conf < CONF_THRESH:
                    continue
                cls_id = int(detections[i].cls.item())
                xyxy = detections[i].xyxy.cpu().numpy().squeeze()
                xmin, ymin, xmax, ymax = xyxy.astype(int)
                detections_list.append({
                    "class": labels[cls_id],
                    "confidence": conf,
                    "bbox": xyxy.tolist()
                })

                color = bbox_colors[cls_id % len(bbox_colors)]
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                label = f"{labels[cls_id]}: {int(conf*100)}%"
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                label_ymin = max(ymin, labelSize[1]+10)
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), color, cv2.FILLED)
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

                object_count += 1

            # Calculate FPS
            t_stop = time.perf_counter()
            frame_rate = 1/(t_stop - t_start)
            frame_rate_buffer.append(frame_rate)
            if len(frame_rate_buffer) > fps_avg_len:
                frame_rate_buffer.pop(0)
            avg_frame_rate = np.mean(frame_rate_buffer)

            # Draw FPS and object count
            if source_type in ['video','usb','folder']:
                cv2.putText(frame, f"FPS: {avg_frame_rate:.2f}", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                cv2.putText(frame, f"Objects: {object_count}", (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

            # Encode and emit
            success, buffer = cv2.imencode('.jpg', frame)
            if success:
                frame_b64 = base64.b64encode(buffer).decode('utf-8')
                sio.emit("detections", {"detections": detections_list, "frame": frame_b64})

            # Small sleep to avoid blocking
            eventlet.sleep(0.001)

        except Exception as e:
            print(f"Error in detection loop: {e}")
            eventlet.sleep(1)

# ------------------ START DETECTION LOOP ------------------
eventlet.spawn(detection_loop)

# ------------------ START SERVER ------------------
if __name__ == "__main__":
    print("Starting YOLO backend on http://0.0.0.0:8000")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8000)), app)
