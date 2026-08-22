import cv2
import numpy as np
import base64
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True
)

def analyze_frame(base64_image: str) -> dict:
    try:
        header, data = base64_image.split(",", 1)
        img_bytes = base64.b64decode(data)

        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return {"eye_contact": "Unknown", "blink": False}

        img_h, img_w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {"eye_contact": "No Face Detected", "blink": False}

        landmarks = results.multi_face_landmarks[0].landmark

        LEFT_EYE  = [362, 385, 387, 263, 373, 380]
        RIGHT_EYE = [33, 160, 158, 133, 153, 144]

        def ear(indices):
            pts = [(int(landmarks[i].x * img_w), int(landmarks[i].y * img_h)) for i in indices]
            v1 = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
            v2 = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
            h  = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
            return (v1 + v2) / (2.0 * h) if h != 0 else 0

        avg_ear = (ear(LEFT_EYE) + ear(RIGHT_EYE)) / 2.0
        blink = avg_ear < 0.2

        nose = landmarks[1]
        left_temple = landmarks[234]
        right_temple = landmarks[454]

        face_center_x = (left_temple.x + right_temple.x) / 2
        offset = abs(nose.x - face_center_x)

        if offset < 0.05:
            eye_contact = "Looking at screen"
        elif nose.x < face_center_x:
            eye_contact = "Looking left"
        else:
            eye_contact = "Looking right"

        return {"eye_contact": eye_contact, "blink": blink}

    except Exception as e:
        print("Vision error:", repr(e))   #  IMPORTANT FIX
        return {"eye_contact": "Unknown", "blink": False}