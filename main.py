import time
import serial
import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

arduino=serial.Serial("COM3",9600)
time.sleep(2)
last_pattern=""

cap=cv.VideoCapture(0)

options=vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path="hand_landmarker.task"),
    num_hands=1,
    min_hand_detection_confidence=0.7,
)
hands=vision.HandLandmarker.create_from_options(options)

tip_ids=[8,12,16,20]

while True:
    success,frame=cap.read()
    if not success:
        break
    rgb=cv.cvtColor(frame,cv.COLOR_BGR2RGB)
    mp_image=mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb)
    results=hands.detect(mp_image)
    fingers=[0,0,0,0,0]
    if results.hand_landmarks:
        h,w,_=frame.shape
        for hand_landmarks in results.hand_landmarks:
            for id,landmark in enumerate(hand_landmarks):
                x=int(landmark.x*w)
                y=int(landmark.y*h)
                cv.circle(frame,(x,y),5,(0,255,0),-1)
            if abs(hand_landmarks[4].x-hand_landmarks[17].x) > abs(hand_landmarks[3].x-hand_landmarks[17].x):
                fingers[0]=1
            for i,tip_id in enumerate(tip_ids):
                if hand_landmarks[tip_id].y < hand_landmarks[tip_id-2].y:
                    fingers[i+1]=1
    fingers_up=sum(fingers)
    pattern="".join(str(f) for f in fingers)
    if pattern!=last_pattern:
        arduino.write((pattern+"\n").encode())
        last_pattern=pattern
    cv.putText(frame,"Fingers: "+str(fingers_up),(20,60),cv.FONT_HERSHEY_SIMPLEX,1.5,(0,0,255),3)
    cv.imshow("My webcam",frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
arduino.write(b"00000\n")
arduino.close()
cap.release()
hands.close()
cv.destroyAllWindows()