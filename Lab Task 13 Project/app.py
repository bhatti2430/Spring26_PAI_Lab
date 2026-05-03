import os
import time
import threading
from io import BytesIO

import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template, request
import cvzone

try:
    from rembg import remove
    HAVE_REMBG = True
except ImportError:
    HAVE_REMBG = False

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "img")
WIDTH, HEIGHT = 640, 480

# Background frame processing
latest_frame_output = None
frame_lock = threading.Lock()
processor_running = True


def open_camera():
    indices = [0, 1, 2]
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    for index in indices:
        for backend in backends:
            cap = cv2.VideoCapture(index, backend)
            if not cap.isOpened():
                cap.release()
                continue

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
            cap.set(cv2.CAP_PROP_FPS, 60)
            time.sleep(0.2)

            success, frame = cap.read()
            if not success or frame is None:
                print(f"Camera opened but no frame from index {index}, backend {backend}")
                cap.release()
                continue

            print(f"Camera opened on index {index} with backend {backend}")
            return cap
    return None


cap = open_camera()
if cap is None or not cap.isOpened():
    print("Camera not accessible on indexes 0-2. Try changing the index or closing other apps using the camera.")
    exit(1)

backgrounds = []
current_index = 0

# Check camera
if not cap.isOpened():
    print("Camera not accessible!")
    exit(1)
else:
    print("Camera opened successfully")
    if HAVE_REMBG:
        print("Using rembg person segmentation for live background replacement.")
    else:
        print("rembg not available; falling back to green/blue screen chroma-key.")



def load_backgrounds():
    global backgrounds
    backgrounds = []
    if not os.path.isdir(IMG_DIR):
        return
    for filename in sorted(os.listdir(IMG_DIR)):
        path = os.path.join(IMG_DIR, filename)
        if not os.path.isfile(path):
            continue
        img = cv2.imread(path)
        if img is None:
            continue
        img = cv2.resize(img, (WIDTH, HEIGHT))
        backgrounds.append({"name": filename, "image": img})


def merge_frame(frame, bg_img):
    if HAVE_REMBG:
        try:
            frame_rgba = remove(frame)
            alpha = frame_rgba[:, :, 3] / 255.0
            alpha = np.stack([alpha, alpha, alpha], axis=-1)
            fg = frame_rgba[:, :, :3].astype(np.float32)
            bg = bg_img.astype(np.float32)
            output = fg * alpha + bg * (1.0 - alpha)
            return np.clip(output, 0, 255).astype(np.uint8)
        except Exception as e:
            print('rembg error:', e)
            # fallback to chroma-key if rembg fails

    # Fallback chroma-key replacement
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([100, 255, 255])

    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask = cv2.bitwise_or(mask_green, mask_blue)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    mask_inv = cv2.bitwise_not(mask)
    fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    bg = cv2.bitwise_and(bg_img, bg_img, mask=mask)
    output = cv2.add(fg, bg)
    return output


def frame_processor_thread():
    global latest_frame_output, processor_running
    print("Frame processor thread started")
    frame_count = 0
    skip_frames = 2
    
    while processor_running:
        try:
            if not backgrounds:
                time.sleep(0.01)
                continue
            
            success, frame = cap.read()
            if not success or frame is None:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            if frame_count % (skip_frames + 1) != 0:
                time.sleep(0.01)
                continue
            
            frame = cv2.flip(frame, 1)
            
            try:
                output = merge_frame(frame, backgrounds[current_index]["image"])
            except Exception as e:
                print('Background processing error:', e)
                output = frame
            
            ret, buffer = cv2.imencode(".jpg", output, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret and buffer is not None:
                with frame_lock:
                    latest_frame_output = buffer.tobytes()
            
            time.sleep(0.01)
        except Exception as e:
            print(f"Frame processor error: {e}")
            time.sleep(0.01)


@app.route("/")
def index():
    load_backgrounds()
    return render_template("index.html", backgrounds=backgrounds, current=current_index)


@app.route("/video_feed")
def video_feed():
    global latest_frame_output
    if latest_frame_output is None:
        blank = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        ret, buffer = cv2.imencode(".jpg", blank)
        frame_bytes = buffer.tobytes()
    else:
        with frame_lock:
            frame_bytes = latest_frame_output
    
    return Response(
        frame_bytes,
        mimetype="image/jpeg",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.route("/api/backgrounds")
def api_backgrounds():
    load_backgrounds()
    return jsonify([{"index": idx, "name": bg["name"]} for idx, bg in enumerate(backgrounds)])


@app.route("/api/set_background")
def api_set_background():
    global current_index
    index = request.args.get("index", type=int)
    load_backgrounds()
    if index is None or index < 0 or index >= len(backgrounds):
        return jsonify({"success": False, "error": "Invalid background index."}), 400
    current_index = index
    return jsonify({"success": True, "background": backgrounds[current_index]["name"], "index": current_index})


@app.route("/api/process", methods=["POST"])
def api_process():
    load_backgrounds()
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file provided."}), 400
    file = request.files["image"]
    index = request.form.get("index", type=int, default=current_index)
    if index < 0 or index >= len(backgrounds):
        return jsonify({"success": False, "error": "Invalid background index."}), 400
    np_img = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({"success": False, "error": "Unable to decode image."}), 400
    output = merge_frame(frame, backgrounds[index]["image"])
    ret, buffer = cv2.imencode(".jpg", output)
    return Response(buffer.tobytes(), mimetype="image/jpeg")


@app.route("/test")
def test():
    return "App is running! Camera status: " + ("Open" if cap.isOpened() else "Closed")


if __name__ == "__main__":
    load_backgrounds()
    
    # Start background frame processor thread
    processor_thread = threading.Thread(target=frame_processor_thread, daemon=True)
    processor_thread.start()
    print("Started background frame processor")
    
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
