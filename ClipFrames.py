import sys
import os
import numpy as np
import cv2

cap = None
file_path: str # 開く動画ファイルのパス
durations = [] # 保存するフレームの位置を記録するクラスを格納
from_frame = -1 # 開始に選ばれたフレーム
is_playing = False # 再生中かどうか


def nothing(x):
    pass


def on_seekbar_change(pos):
    print('seekbar pos: {}'.format(pos))
    set_cap_sec(pos)

# ref: https://note.nkmk.me/python-opencv-video-to-still-image/
def save_frame_range(start_frame, stop_frame, step_frame, dir_path, basename="", ext='jpg'):
    if not cap.isOpened():
        return 0

    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)

    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))

    for n in range(start_frame, stop_frame, step_frame):
        cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = cap.read()
        if ret:
            if(basename):
                save_path = '{}_{}.{}'.format(base_path, str(n).zfill(digit), ext)
            else:
                save_path = '{}{}.{}'.format(base_path, str(n).zfill(digit), ext)
            cv2.imwrite(save_path, frame)
            print('{} saved'.format(save_path))
        else:
            return 0

    return 1


def sec2frame(second):
    if cap.isOpened() and cap_fps:
        return int(second * cap_fps)
    return None


def frame2sec(frame):
    if cap.isOpened():
        return int(frame / cap_fps)
    return None


def set_cap_sec(second):
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, sec2frame(second)) # 再生開始位置指定
        set_seekbar_pos(second)

def set_seekbar_pos(second):
    if cap.isOpened():
        cv2.setTrackbarPos('second', 'frame', second)

def get_seekbar_pos():
    if cap.isOpened():
        return cv2.getTrackbarPos('second', 'frame')
    return None

class SaveDuration:
    def __init__(self, frame_from, frame_to, dirname, basename="", step_frame=10):
        self.frame_from = frame_from
        self.frame_to = frame_to
        self.dirname = dirname
        self.basename = basename
        self.step_frame = step_frame

    def save_file(self):
        save_frame_range(self.frame_from, self.frame_to, self.step_frame, "./saved_images/"+self.dirname, self.basename)



if __name__ == "__main__":
    if(len(sys.argv) < 2):
        file_path = input('動画ファイルを指定してください: ')
    else:
        file_path = sys.argv[1]
    
    cap = cv2.VideoCapture(file_path)

    if(cap.isOpened()):
        print('{} is loaded'.format(file_path))
    else:
        print('{} is not found'.format(file_path))
        sys.exit()

    cap_allframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # 総フレーム数の取得
    cap_fps = int(cap.get(cv2.CAP_PROP_FPS))
    cap_allsec = frame2sec(cap_allframes)
    print('sec', cap_allsec)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # 再生開始位置指定


    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2) # サイズ基本デカすぎるので半分に(ツールバーでいじりたい)
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)

    print('fps: {}'.format(cap_fps))
    print('resolution: {}x{}'.format(cap_width, cap_height))

    cv2.namedWindow("frame", cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    # シークバーなどの作成
    cv2.createTrackbar('second', 'frame', 0, frame2sec(cap_allframes), on_seekbar_change)

    while(cap.isOpened()):
        ret, frame = cap.read()

        if(ret):
            is_playing = True
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) # 現在の再生位置（フレーム位置）の取得
            current_sec = int(frame2sec(current_frame))
            
            cv2.putText(frame, 'frame: {}'.format(current_frame), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), thickness=2)

            # フレームサイズの変更
            frame = cv2.resize(frame, dsize=(cap_width, cap_height))
            
            cv2.imshow('frame',frame)
            
            set_seekbar_pos(frame2sec(current_frame)) # change tracker pos
            key = cv2.waitKey(1) & 0xFF # get pressed key

            if key == ord('q'):
                break
            elif key == 32: # space
                if(from_frame == -1):
                    from_frame = current_frame
                else:
                    duration = SaveDuration(from_frame, current_frame, os.path.splitext(os.path.basename(file_path))[0])
                    durations.append(duration)
                    from_frame = -1

        else:
            is_playing = False

            while(True):
                key = cv2.waitKey(1) & 0xFF # wait for key
                current_sec = int(frame2sec(current_frame))
                print('current' + current_sec)
                if cap_allsec > current_sec:
                    print('break')
                    break

            



    for duration in durations:
        duration.save_file()


    cap.release()
    cv2.destroyAllWindows()