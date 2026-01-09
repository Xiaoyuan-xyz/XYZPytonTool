import cv2
import numpy as np

# === 参数配置 ===
video_path = "./png_transparent/out.mp4"
output_path = "./png_transparent/transition_map.png"

# === 打开视频 ===
cap = cv2.VideoCapture(video_path)
n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

ret, first_frame = cap.read()
if not ret:
    raise RuntimeError("无法读取视频第一帧")

# 转为灰度并归一化到 [0,1]
prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
h, w = prev_gray.shape

# 初始化"首次变化帧索引"，-1 表示未变化
change_frame = np.full((h, w), -1, dtype=np.int32)

# === 逐帧处理 ===
for i in range(1, n_frames):
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

    # 计算像素变化
    diff = np.abs(gray - prev_gray)

    # 找出"由白变黑"的像素（或亮度下降明显）
    changed = (diff > 0.1) & (gray < prev_gray)

    # 只记录第一次变化的帧索引
    newly_changed = (change_frame == -1) & changed
    change_frame[newly_changed] = i

    prev_gray = gray

cap.release()

# === 将帧索引映射到灰度 ===
# 未变化的像素设为0（纯黑色），已变化的像素根据帧索引映射
transition_map = np.zeros((h, w), dtype=np.uint8)

# 将有变化的像素映射到对应的灰度值
changed_pixels = change_frame != -1
if np.any(changed_pixels):
    # 将帧索引归一化到 [1, 255] 范围，确保第一帧是纯黑色(0)
    min_frame = np.min(change_frame[changed_pixels])
    max_frame = np.max(change_frame[changed_pixels])
    
    if max_frame > min_frame:  # 避免除零
        normalized = (change_frame[changed_pixels] - min_frame) / (max_frame - min_frame)
        transition_map[changed_pixels] = (normalized * 254 + 1).astype(np.uint8)
    else:
        # 如果所有变化都在同一帧，设为中间灰度
        transition_map[changed_pixels] = 128

cv2.imwrite(output_path, transition_map)
print(f"转场图已生成：{output_path}")