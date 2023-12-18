import sys
import cv2
import mediapipe as mp
import threading
from pythonosc import osc_message_builder
from pythonosc import udp_client
import tkinter as tk
import ctypes
import subprocess
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


sender = udp_client.SimpleUDPClient('127.0.0.1', 4560)
c = 0
stop = True
loop = False
Smode = 'piano'

def exit_window():
    global stop
    
    stop = False
    
    cap.release() 
    
    cv2.destroyAllWindows()
    
    win.destroy
    
    sys.exit()

def set_volume(volume): 
    volume = max(0, min(100, volume))
    subprocess.run(["amixer", "set", "Master", f"{volume}%"])
    
def on_slider_ch(volume):
    set_volume(int(volume))

def toggle_text():
    global loop
    if button["text"] == "LOOP\nON":
        loop = False
        sender.send_message('/trigger/prophet', [Smode, loop, False, 0])
        button["text"] = "LOOP\nOFF"
    else:
        button["text"] = "LOOP\nON"
        loop = True
        sender.send_message('/trigger/prophet', [Smode, loop, False, 0])


def sound(data):
    global c
    global loop
    global Smode
    Smode = 'piano'
    
    if c - 2 < data < c + 2:
        #sender.send_message('/trigger/prophet', [False, data])
        return
    c = data
    print("data :", data)
          
    if data < 30:
        sender.send_message('/trigger/prophet', [Smode, loop, True, 0])
        return
    else:
        sender.send_message('/trigger/prophet', [Smode, loop, False, data])
        return

def dramsound(a, b, c, d):
    global Smode
    Smode = 'drum'
    if (0.35 < a.y < 0.45 and 0.60 < a.x < 0.69) or (0.35 < b.y < 0.45 and 0.60 < b.x < 0.69) :
         sender.send_message('/trigger/prophet', [Smode, loop, False, 0])
         return
         
    elif (0.35 < a.y < 0.45 and 0.50 < a.x < 0.59) or (0.35 < b.y < 0.45 and 0.50 < b.x < 0.59) :
         sender.send_message('/trigger/prophet', [Smode, loop, False, 1])
         return
         
    elif (0.35 < a.y < 0.45 and 0.40 < a.x < 0.49) or (0.35 < b.y < 0.45 and 0.40 < b.x < 0.49) :
         sender.send_message('/trigger/prophet', [Smode, loop, False, 2])
         return
         
    elif (0.35 < a.y < 0.45 and 0.30 < a.x < 0.39) or (0.35 < b.y < 0.45 and 0.30 < b.x < 0.39) :
         sender.send_message('/trigger/prophet', [Smode, loop, False, 3]) 
         return
        
        
def dance(data, ms):
    global Smode
    Smode = 'dance'
    
    print(data, ms)
    
    if (55 < data < 65 and 45 < ms < 53):
        sender.send_message('/trigger/prophet', [Smode, loop, False, 0]) 
        return
    elif (66 < data < 75 and 47 < ms < 53):
        sender.send_message('/trigger/prophet', [Smode, loop, False, 1]) 
        return
    elif (45 < data < 54 and 20 < ms < 26):
        sender.send_message('/trigger/prophet', [Smode, loop, False, 2]) 
        return
    elif (60 < data < 70 and 28 < ms < 36):
        sender.send_message('/trigger/prophet', [Smode, loop, False, 3]) 
        return
    elif (70 < data < 85 and 30 < ms < 40):
        sender.send_message('/trigger/prophet', [Smode, loop, False, 4]) 
        return
    elif (55 < data < 65 and 10 < ms < 20):
        sender.send_message('/trigger/prophet', [Smode, loop, False, 5]) 
        return
    else :
        return
    
    
    

def long(a, b, c, d):
    lwrw = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
    lwla = ((a.x - c.x) ** 2 + (a.y - c.y) ** 2) ** 0.5
    lara = ((d.x - c.x) ** 2 + (d.y - c.y) ** 2) ** 0.5
    rwra = ((b.x - d.x) ** 2 + (b.y - d.y) ** 2) ** 0.5

    solong = int((lwrw + lwla + lara + rwra) * 50)
    
    return solong
    
def tr(a, b, c):
    lwrw = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
    lwzo = ((a.x - c.x) ** 2 + (a.y - c.y) ** 2) ** 0.5
    rwzo = ((b.x - c.x) ** 2 + (b.y - c.y) ** 2) ** 0.5
    
    tra = int((lwrw + lwzo + rwzo) * 50)
    
    return tra
    

def process_frames():
    global stop
    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
        ) as pose:
        
        while True:
            start = time.time()
            if cap.isOpened():
                ret, image = cap.read()
                if not ret:
                    break
                    
                image = cv2.resize(image, (640, 480))
                image.flags.writeable = False
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)
                
                if results.pose_landmarks:
                    left_wrist_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
                    right_wrist_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
                    left_ankle_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
                    right_ankle_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
                    zero_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]

                    #mp_drawing.draw_landmarks(image, results.pose_landmarks)
                    
                    
                    data0 = long(left_wrist_landmark, right_wrist_landmark, left_ankle_landmark, right_ankle_landmark)
                    
                    data1 = tr(left_wrist_landmark, right_wrist_landmark, zero_landmark)
                    
                    if radio_var.get() == 0:
                        sound(data0)
                    elif radio_var.get() == 1:
                        dramsound(left_wrist_landmark, right_wrist_landmark, left_ankle_landmark, right_ankle_landmark)
                    elif radio_var.get() == 2:
                        dance(data0, data1)
                    else:
                        print("NOTTHING")
                            
                    
                    
                    
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                #cv2.imshow('MediaPipe Pose Detection', cv2.flip(image, 1))
                
                
                if cv2.waitKey(1) == ord('q'):
                    break
                elif stop == False:
                    break
                    

# Initialize video capture object
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 10)

# Create the tkinter window
win = tk.Tk()
win.geometry('800x480')
win.title('사용자 UI')
win.protocol('WM_DELETE_WINDOW', exit_window)

# 라디오 버튼 그룹 변수 생성
radio_var = tk.IntVar(value=0)

# 텍스트 추가
text = tk.Label(win, text='사운드 크기', font=('Malgun Gothic', 20))

# Add the loop button
button = tk.Button(win, text='LOOP\nON', font=('Arial', 16), command=toggle_text)
button.config(width=15, height=3)
button.pack()

# 라디오 버튼 생성 및 글자 크기 설정
radio1 = tk.Radiobutton(win, text='Piano', variable=radio_var, value=0, font = ('Arial', 16))
radio2 = tk.Radiobutton(win, text='Drum', variable=radio_var, value=1, font = ('Arial', 16))
radio3 = tk.Radiobutton(win, text='Dance', variable=radio_var, value=2, font = ('Arial', 16))

# Add the volume slider
volume_slider = tk.Scale(win, from_=0, to=100, orient=tk.VERTICAL, command=on_slider_ch, font=('Arial', 8), width=50, length=300)
volume_slider.set(50)
volume_slider.pack(padx=10, pady=10)

# 위젯 배치
radio1.place(x = 150, y = 180)
radio2.place(x = 150, y = 250)
radio3.place(x = 150, y = 320)
volume_slider.place(x = 650, y = 40)
button.place(x = 120, y = 60)
text.place(x = 450, y = 220)

# Start a new thread to process frames

frame_thread = threading.Thread(target=process_frames)
frame_thread.start()


# Start the tkinter event loop
win.mainloop()

# Wait for the frame processing thread to finish
frame_thread.join()

# Release video capture object and destroy all windows
cap.release()
cv2.destroyAllWindows()


