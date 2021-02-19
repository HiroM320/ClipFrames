import sys
import argparse
import os
import time
import numpy as np
import cv2

cap = None
file_path: str # 開く動画ファイルのパス
durations = [] # 保存するフレームの位置を記録するクラスを格納
from_frame = -1 # 再生開始(再開)に選ばれたフレーム
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

    if start_frame == stop_frame:
        n = int(start_frame)
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
    else:
        for n in range(int(start_frame), int(stop_frame), step_frame):
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


def skip_back(back_frame):
    if cap.isOpened():
        new_frame = current_frame - back_frame
        if new_frame < 0:
            new_frame = 0
        print('frame skipped: {} -> {}'.format(current_frame, new_frame))
        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame) # 再生開始位置指定

def skip_forward(forward_frame):
    if cap.isOpened():
        new_frame = current_frame + forward_frame
        if new_frame > expected_frames:
            new_frame = expected_frames
        print('frame skipped: {} -> {}'.format(current_frame, new_frame))
        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame) # 再生開始位置指定


def sec2frame(second):
    if cap.isOpened() and expected_fps:
        return second * expected_fps
    return None


def frame2sec(frame):
    if cap.isOpened():
        return frame / expected_fps
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
        save_frame_range(self.frame_from, self.frame_to, self.step_frame, "./saved_images/{}".format(self.dirname), self.basename)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

    parser.add_argument(
        '-i', '--input', nargs='?', type=str,required=False, default=None,
        help = 'Video input path'
    )

    parser.add_argument(
        '-s', '--speed', nargs='?', type=float,required=False,default=1.0,
        help = 'Video playback speed'
    )

    parser.add_argument(
        '-e', '--expand', nargs='?', type=float, required=False, default=1.0,
        help = 'Video resolution expand'
    )

    FLAGS = parser.parse_args()

    file_path = FLAGS.input
    if(file_path is None):
        file_path = input('動画ファイルのパスを入力してください: ')
    
    cap = cv2.VideoCapture(file_path)

    if(cap.isOpened()):
        print('{} is loaded'.format(file_path))
    else:
        print('{} is not found'.format(file_path))
        sys.exit()

    expected_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # 総フレーム数の取得
    expected_fps = cap.get(cv2.CAP_PROP_FPS)
    expected_sec = frame2sec(expected_frames)
    delay_interframe = 1/expected_fps # 正確にはwaitkeyが入っていることを考慮する必要がある
    playback_speed = FLAGS.speed
    res_expand = FLAGS.expand

    print(delay_interframe)
    print('expected sec', expected_sec)
    print('expected fps: {}'.format(expected_fps))
    set_playback_frame(0)


    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * res_expand) # サイズ基本デカすぎるので半分に(ツールバーでいじりたい)
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * res_expand)

    print('resolution: {}x{}'.format(cap_width, cap_height))

    cv2.namedWindow("frame", cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    # フレーム間隔をいじれるトラックバーの作成
    cv2.createTrackbar('step', 'frame', step_frame, 50, on_stepframe_bar_change)
    cv2.setTrackbarMin('step', 'frame', 1)

    print_usage()

    wait_counter_from = time.perf_counter() # 動画の再生速度をFPSに合わせるため

    ret = False
    frame = None
    current_frame = 0

    while(cap.isOpened()):
        if(not paused):
            wait_counter_from = time.perf_counter()
            ret, frame = cap.read()

        if(ret):
            is_playing = True
            
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES) # 現在の再生位置（フレーム位置）の取得
            current_sec = frame2sec(current_frame)

            cv2.putText(frame, 'frame: {:.3f}/{:.3f}'.format(current_frame, expected_frames), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), thickness=2)
            cv2.putText(frame, 'sec: {:.3f}/{:.3f}'.format(current_sec, expected_sec), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), thickness=2)

            # フレームサイズの変更
            frame = cv2.resize(frame, dsize=(cap_width, cap_height))
            
            cv2.imshow('frame', frame)

            while True:
                elapsed: float = time.perf_counter() - wait_counter_from
                if elapsed >= delay_interframe / playback_speed:
                    break

        else:
            is_playing = False

        key = cv2.waitKey(1) & 0xFF # get pressed key
        if key == ord('q'):
            break
        elif key == ord('w'): # pause/resume
            toggle_pause()
        elif key == ord('a'): # back 5s
            skip_back(5*expected_fps)
        elif key == ord('d'): # skip 5s
            skip_forward(5*expected_fps)
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