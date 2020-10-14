import sys
import os
import numpy as np
import cv2


file_path: str


if __name__ == "__main__":

    if(len(sys.argv)<2):
        file_path = input('動画ファイルを指定してください: ')
    else:
        file_path = sys.argv[1]
    
    cap = cv2.VideoCapture(file_path)

    if(cap.isOpened()):
        print('{} is loaded'.format(sys.argv[0]))
    else:
        print('{} is not found'.format(sys.argv[0]))

    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # 総フレーム数の取得
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # cv2.namedWindows

    while(cap.isOpened()):
        ret, frame = cap.read()
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) # 現在の再生位置（フレーム位置）の取得
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()