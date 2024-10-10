import torch
import numpy as np
from .post_process import Preprocessing, interpolate_or_pad
from .extract_landmark import POINT_LANDMARKS
from .transformer import M

# Khởi tạo mô hình AI
def load_model():
    model = M(num_block=3)
    checkpoint = torch.load('modelAI/checkpoint_last_seed-1.pth', map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model'])
    model.eval()
    return model

# Hàm xử lý dự đoán bằng PyTorch
def predict_pytorch(input_data, model, label_map, threshold=0.6):
    input_data = torch.tensor(input_data).unsqueeze(0).float()  # (1, L, num_landmark)
    with torch.no_grad():
        output = model(input_data)  # output có kích thước (1, num_class)
    probabilities = torch.softmax(output, dim=-1)
    confidence, predictions = torch.max(probabilities, dim=-1)
    predicted_label = list(label_map.keys())[predictions.item()]
    if confidence.item() < threshold:
        return "Uncertain"
    else:
        return predicted_label

# Hàm trích xuất keypoints từ Mediapipe
def extract_keypoints(results):
    face_x  = np.array([res.x for res in results.face_landmarks.landmark],dtype=np.float32) if results.face_landmarks else np.zeros(468)
    face_y  = np.array([res.y for res in results.face_landmarks.landmark],dtype=np.float32) if results.face_landmarks else np.zeros(468)
    face_z  = np.array([res.z for res in results.face_landmarks.landmark],dtype=np.float32) if results.face_landmarks else np.zeros(468)

    lh_x  = np.array([res.x for res in results.left_hand_landmarks.landmark],dtype=np.float32) if results.left_hand_landmarks else np.zeros(21)
    lh_y  = np.array([res.y for res in results.left_hand_landmarks.landmark],dtype=np.float32) if results.left_hand_landmarks else np.zeros(21)
    lh_z  = np.array([res.z for res in results.left_hand_landmarks.landmark],dtype=np.float32) if results.left_hand_landmarks else np.zeros(21)

    pose_x  = np.array([res.x for res in results.pose_landmarks.landmark],dtype=np.float32) if results.pose_landmarks else np.zeros(33)
    pose_y  = np.array([res.y for res in results.pose_landmarks.landmark],dtype=np.float32) if results.pose_landmarks else np.zeros(33)
    pose_z  = np.array([res.z for res in results.pose_landmarks.landmark],dtype=np.float32) if results.pose_landmarks else np.zeros(33)

    rh_x  = np.array([res.x for res in results.right_hand_landmarks.landmark],dtype=np.float32) if results.right_hand_landmarks else np.zeros(21)
    rh_y  = np.array([res.y for res in results.right_hand_landmarks.landmark],dtype=np.float32) if results.right_hand_landmarks else np.zeros(21)
    rh_z  = np.array([res.z for res in results.right_hand_landmarks.landmark],dtype=np.float32) if results.right_hand_landmarks else np.zeros(21)

    x_cor = np.concatenate([face_x, lh_x, pose_x, rh_x])
    y_cor = np.concatenate([face_y, lh_y, pose_y, rh_y])
    z_cor = np.concatenate([face_z, lh_z, pose_z, rh_z])
    POINT_LANDMARKS_array = np.array(POINT_LANDMARKS)
    result = np.concatenate((x_cor[POINT_LANDMARKS_array], y_cor[POINT_LANDMARKS_array], z_cor[POINT_LANDMARKS_array]))
    return result