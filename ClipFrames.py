import sys
import os
import numpy as np
import cv2

cap = None
file_path: str # 開く動画ファイルのパス
durations = [] # 保存するフレームの位置を記録するクラスを格納
from_frame = -1 # 開始に選ばれたフレーム


if __name__ == "__main__":
    if(len(sys.argv)<2):
        file_path = input('動画ファイルを指定してください: ')
    else:
        file_path = sys.argv[1]
    
    cap = cv2.VideoCapture(file_path)

    if(cap.isOpened()):
        print('{} is loaded'.format(file_path))
    else:
        print('{} is not found'.format(file_path))
        sys.exit()

    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # 総フレーム数の取得
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)

    while(cap.isOpened()):
        ret, frame = cap.read()
        
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) # 現在の再生位置（フレーム位置）の取得
        
        cv2.putText(frame, 'frame: {}'.format(current_frame), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), thickness=2)
        
        cv2.imshow('frame',frame)
        
        key = cv2.waitKey(1) & 0xFF # get pressed key

        if key == ord('q'):
            break
        elif key == 32: # space
            if(from_frame == -1):
                from_frame = current_frame
            else:
                durations.append(from_frame, current_frame, os.path.basename(file_path))
                from_frame = -1

    print('start saving')

    for duration in durations:
        duration.save_file()

    print('done saving')


    cap.release()
    cv2.destroyAllWindows()


# ref: https://note.nkmk.me/python-opencv-video-to-still-image/
def save_frame_range(start_frame, stop_frame, step_frame, dir_path, basename, ext='jpg'):
    if not cap.isOpened():
        return

    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)

    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))

    for n in range(start_frame, stop_frame, step_frame):
        cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = cap.read()
        if ret:
            save_path = '{}_{}.{}'.format(base_path, str(n).zfill(digit), ext)
            cv2.imwrite(save_path, frame)
            print('{} saved'.format(save_path))
        else:
            return


class SaveDuration:
    def __init__(self, frame_from, frame_to, basename, step_frame=10):
        self.frame_from = frame_from
        self.frame_to = frame_to
        self.step_frame = step_frame
        self.basename = basename

    def save_file(self):
        save_frame_range(self.frame_from, self.frame_to, self.step_frame, "./save_images/", self.basename)