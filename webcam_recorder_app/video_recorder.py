import cv2
import datetime
import argparse
import time
import os

from ultralytics import YOLO

class VideoRecorder:
    def __init__(self):
        self.video_files, self.annotation_files = self.generate_video_files()
        self.video_start_times = list(self.video_files.keys())
        self.previous_video_file = self.video_start_times[0]

    @staticmethod
    def generate_video_files() -> dict:
        time_delta = END_TIME - START_TIME
        num_intervals = time_delta.seconds // (args.slice_interval * 60)
        TIME_STAMPS = [START_TIME + datetime.timedelta(minutes=args.slice_interval*i) for i in range(num_intervals+1)]

        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        if not os.path.exists('./recorded_videos'):
            os.mkdir('./recorded_videos')
        if not os.path.exists('./annotations'):
            os.mkdir('./annotations')

        video_files = {time_stamp: cv2.VideoWriter(f"./recorded_videos/{time_stamp.strftime('%Y.%m.%d.%H.%M')}.mp4", fourcc, 25.0, (args.width, args.height)) for time_stamp in TIME_STAMPS}
        annotation_files = {time_stamp: open(os.path.join("./annotations", f"{time_stamp.strftime('%Y.%m.%d.%H.%M')}.txt"), "w") for time_stamp in TIME_STAMPS}
        return video_files, annotation_files

    def select_recorder(self) -> None:
        closest_timestamp = [time for time in self.video_start_times if time < self.current_time][-1]
        self.video_files[closest_timestamp].write(self.frame)

        results = model(self.frame, stream=True, verbose=False)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = classNames[int(box.cls[0])]
                if cls == "person":
                    self.annotation_files[closest_timestamp].write(f"{self.current_time}: Person\n")

        if self.previous_video_file != closest_timestamp:
            self.video_files[self.previous_video_file].release()
            self.annotation_files[self.previous_video_file].close()
            self.previous_video_file = closest_timestamp
            print(f"Recording finished at {self.current_time}")
            print(f"Recording started at {self.current_time}")

    def record_video(self):
        is_recording = False
        is_camera_initialized = False
        sleep_before_recording = args.sleep_before_recording #in minutes
        sleep_interval = args.sleep_interval #in seconds

        while True:
            self.current_time = datetime.datetime.now()

            if self.video_start_times[0] - self.current_time > datetime.timedelta(minutes=sleep_before_recording):
                if self.current_time + datetime.timedelta(seconds=sleep_interval) < self.video_start_times[0]:
                    time.sleep(sleep_interval)
            else:
                if not is_camera_initialized:
                    #Camera initialization
                    self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
                    is_camera_initialized = True

                ret, self.frame = self.cap.read()

                # # coordinates
                # for r in results:
                #     boxes = r.boxes

                #     for box in boxes:
                #         # bounding box
                #         x1, y1, x2, y2 = box.xyxy[0]
                #         x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

                #         # put box in cam
                #         cv2.rectangle(self.frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                #         # confidence
                #         confidence = math.ceil((box.conf[0]*100))/100
        
                #         # class name
                #         cls = int(box.cls[0])

                #         # object details
                #         org = [x1, y1 - 10]
                #         font = cv2.FONT_HERSHEY_SIMPLEX
                #         fontScale = 1
                #         color = (255, 242, 3)
                #         thickness = 2

                #         cv2.putText(self.frame, f"{classNames[cls]} {confidence}", org, font, fontScale, color, thickness)

                if ret and START_TIME <= self.current_time <= END_TIME:
                    if not is_recording:
                        is_recording = True
                        print(f"Recording started at {self.current_time}")
                    cv2.putText(self.frame, str(self.current_time), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    #cv2.imshow("Video", self.frame)
                    self.select_recorder()
                    
                    if cv2.waitKey(1) & 0xFF == 27: break
                elif self.current_time > END_TIME:
                    print(f"Recording finished at {self.current_time}")
                    break

        cv2.destroyAllWindows()
        self.cap.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Video recorder',
                    description='Webcam video recorder')
    parser.add_argument("-start", "--start_time", help="Start time", type=str)
    parser.add_argument("-end", "--end_time", help="End time", type=str)
    parser.add_argument("-slice_interval", help="Video slice interval in minutes", type=int, default=15)
    parser.add_argument("-sleep_before_recording", help="Sleep before recording in minutes", type=int, default=1)
    parser.add_argument("-sleep_interval", help="Sleep interval in seconds", type=int, default=15)
    parser.add_argument("--width", help="Video width", type=int, default=1920)
    parser.add_argument("--height", help="Video height", type=int, default=1080)

    args = parser.parse_args()

    START_TIME = datetime.datetime.strptime(args.start_time, '%Y.%m.%d.%H:%M')
    END_TIME = datetime.datetime.strptime(args.end_time, '%Y.%m.%d.%H:%M')

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

    video_recorder = VideoRecorder()
    video_recorder.record_video()
