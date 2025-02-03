import numpy as np
import cv2
import streamlit as st
import time

st.title("Real-time Slow-motion")
st.write("https://dl.acm.org/doi/10.1145/3641517.3664399")

latency_frame = 16  # 遅延に使用するフレームの枚数
# latency_frame+1個の番号を各2回ずつ繰り返し、最初と最後を除去→計32個のインデックス
list_index = [i for i in range(latency_frame + 1) for _ in range(2)][1:-1]
list_frame = []  # 遅延した映像用のフレームを格納
counter = 0     # 過去の映像をどの程度表示するか決定するためのカウンター

prev_time = time.time()
camera_index = 0
cap = cv2.VideoCapture(camera_index)
if not cap.isOpened():
    st.error("カメラを開けません。カメラが接続されているか確認してください。")
else:
    left_column, right_column = st.columns(2)
    with left_column:
        left_display = st.empty()
    with right_column:
        right_display = st.empty()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            st.warning("フレームを取得できませんでした。")
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        list_frame.append(frame_rgb)
        # リングバッファが十分に溜まっていなければ表示せずループ
        if len(list_frame) < 2*latency_frame:
            continue
        # 格納フレーム数が2*latency_frameを超えたら、古いフレームを削除
        if len(list_frame) > 2*latency_frame:
            list_frame = list_frame[1:]
        
        index_right = counter % (2*latency_frame)
        index_left  = index_right - latency_frame
        if index_left < 0:
            index_left += 2*latency_frame
        
        # 最新フレームは list_frame[-1] にあるので、
        # "Xフレーム前" を参照するには list_frame[-1 - X] で取るのが正しい
        delay_right = list_index[index_right]   # 右側の遅延フレーム数
        delay_left  = list_index[index_left]      # 左側の遅延フレーム数
        
        right_frame = list_frame[-1 - delay_right]
        left_frame  = list_frame[-1 - delay_left]
        
        right_display.image(right_frame, use_column_width=True)
        left_display.image(left_frame, use_column_width=True)
        
        counter += 1
    
    cap.release()