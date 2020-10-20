import sys
import os
import numpy as np
import cv2


cap = None
file_path: str # 開く動画ファイルのパス
durations = [] # 保存するフレームの位置を記録するクラスを格納
from_frame = -1 # 開始に選ばれたフレーム
step_frame = 10 # 何フレーム間隔で保存するか
is_playing = False # 再生中かどうか
paused = False # ポーズしてるとTrue


def nothing(x):
    pass


def on_stepframe_bar_change(new_step):
    global step_frame
    print('step change: {}'.format(new_step))
    step_frame = new_step

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


def set_from_frame(frame):
    global from_frame
    from_frame = frame
    print('from_frame: {}'.format(from_frame))


def pause():
    global paused
    paused = True
    print('pause')

def resume():
    global paused
    paused = False
    print('resume')

def toggle_pause():
    if(paused):
        resume()
    else:
        pause()


def set_playback_frame(new_frame):
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame) # 再生開始位置指定


def skipback(back_frame):
    if cap.isOpened():
        new_frame = current_frame - back_frame
        if new_frame < 0:
            new_frame = 0
        print('frame skipped: {} -> {}'.format(current_frame, new_frame))
        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame) # 再生開始位置指定

def skipforward(forward_frame):
    if cap.isOpened():
        new_frame = current_frame + forward_frame
        if new_frame > cap_allframes:
            new_frame = cap_allframes
        print('frame skipped: {} -> {}'.format(current_frame, new_frame))
        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame) # 再生開始位置指定


def sec2frame(second):
    if cap.isOpened() and cap_fps:
        return int(second * cap_fps)
    return None


def frame2sec(frame):
    if cap.isOpened():
        return int(frame / cap_fps)
    return None


def print_usage():
    print('Q = save images and exit')
    print('Space=create start/stop frame')
    print('W = pause/resume')
    print('A = back 5 seconds')
    print('D = skip 5 seconds')
    # print('W = 2x speed')
    # print('S = 0.5x speed')


class SaveDuration:
    def __init__(self, frame_from, frame_to, step_frame=10, dirname=None, basename=""):
        self.frame_from = frame_from
        self.frame_to = frame_to
        self.step_frame = step_frame
        self.dirname = dirname
        self.basename = basename

    def save_file(self):
        save_frame_range(self.frame_from, self.frame_to, self.step_frame, "./saved_images/"+self.dirname, self.basename)



if __name__ == "__main__":
    if(len(sys.argv) < 2):
        file_path = input('動画ファイルのパスを入力してください: ')
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
    set_playback_frame(0)


    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2) # サイズ基本デカすぎるので半分に(ツールバーでいじりたい)
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)

    print('fps: {}'.format(cap_fps))
    print('resolution: {}x{}'.format(cap_width, cap_height))

    cv2.namedWindow("frame", cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    # フレーム間隔をいじれるトラックバーの作成
    cv2.createTrackbar('step', 'frame', step_frame, 50, on_stepframe_bar_change)
    cv2.setTrackbarMin('step', 'frame', 1)

    print_usage()

    while(cap.isOpened()):
        ret, frame = cap.read()

        if(not paused and ret):
            is_playing = True
            
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) # 現在の再生位置（フレーム位置）の取得
            current_sec = int(frame2sec(current_frame))
            
            cv2.putText(frame, 'frame: {}/{}'.format(current_frame, cap_allframes), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), thickness=2)

            # フレームサイズの変更
            frame = cv2.resize(frame, dsize=(cap_width, cap_height))
            
            cv2.imshow('frame',frame)

        else:
            is_playing = False

        key = cv2.waitKey(1) & 0xFF # get pressed key
        if key == ord('q'):
            break
        elif key == ord('w'):
            # pause/resume
            toggle_pause()
        elif key == ord('a'):
            # back 5s
            skipback(5*cap_fps)
        elif key == ord('d'):
            # skip 5s
            skipforward(5*cap_fps)
        elif key == 32: # space
            if from_frame > current_frame: # 開始フレームが現在フレームより後(未来)なら
                print('from_frame({}) is bigger than current_frame({})'.format(from_frame, current_frame))
                set_from_frame(current_frame)
            elif from_frame == -1:
                set_from_frame(current_frame)
            else:
                duration = SaveDuration(from_frame, current_frame, step_frame, os.path.splitext(os.path.basename(file_path))[0])
                durations.append(duration)
                print('add duration: {} -> {}'.format(duration.frame_from, duration.frame_to))
                set_from_frame(-1)



    for duration in durations:
        duration.save_file()


    cap.release()
    cv2.destroyAllWindows()