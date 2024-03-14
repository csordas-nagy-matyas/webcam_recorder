import cv2
import glob
import os
from ultralytics import YOLO

def read_video_file_by_frames(file_path):
    video = cv2.VideoCapture(file_path)
    
    if not os.path.exists('./annotations'):
            os.mkdir('./annotations')
    output_txt = open(os.path.join("./annotations", os.path.basename(file_path).replace(".mp4", ".txt")), "w")

    while True:
        ret, frame = video.read()
        if not ret:
            break
        results = model(frame, stream=True, verbose=False)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = classNames[int(box.cls[0])]
                if cls == "person":
                    time_stamp = video.get(cv2.CAP_PROP_POS_MSEC)
                    output_txt.write(f"Time: {time_stamp/1000:.2f} sec: Person\n")
    output_txt.close()
    video.release()


model = YOLO("yolo-Weights/yolov8n.pt")
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
            "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
            "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
            "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
            "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
            "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
            "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
            "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
            "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
            "teddy bear", "hair drier", "toothbrush"
            ]

videos = glob.glob("./recorded_videos/*.mp4")
for video in videos:
    read_video_file_by_frames(video)