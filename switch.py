import numpy as np
import cv2
import time
import imutils
from imutils.video import FileVideoStream, VideoStream
from utils import *
import json
import socket, pickle
import string  
import socket


UDP_IP = "127.0.0.1"
UDP_PORT = 7777
Message = b"0"
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


def stream():
    fvs = FileVideoStream(path).start()
    return fvs


class Switch():
    
    def __init__(self, THRESH=200):
        self.THRESH = THRESH
        self.last_switch = time.time()
        self.setup()
        self.gap = 1 
    
    
    def setup(self):      
        self.backgroundobject = cv2.createBackgroundSubtractorMOG2(detectShadows = False)

        
        time.sleep(2.0) 
        TIMER_SETUP = 2 
        t = time.time()

        while True:
            frame = get_frame(stream())
            if frame is None:
                break
            curr = (time.time() - t)
            if curr > TIMER_SETUP:
                break
            cv2.putText(frame, str(int(TIMER_SETUP - curr)+1), POS_SCREEN, cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLOR_RED, 4)
            cv2.imshow("Setup", frame)
            cv2.waitKey(1)
        
        cv2.destroyAllWindows()
        
        cv2.putText(frame, 'Selecione uma area acima da cabeça do usuário', POS_SCREEN, cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_RED, 2)
        self.bbox = cv2.selectROI(frame, False) 
        cv2.destroyAllWindows()
    
    
    def update(self, frame): 
        x, y, w, h = self.bbox
        region = frame[y:y+h, x:x+w]
        fgmask = self.backgroundobject.apply(region)

        switch_thresh = np.sum(fgmask==255)
        cv2.putText(frame, str(switch_thresh), POS_SCREEN, cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_RED, 2)
        drawbox(self.bbox, frame) 
        if time.time() - self.last_switch < self.gap:
            drawbox(self.bbox, frame, -1) 
        if switch_thresh>self.THRESH and time.time() - self.last_switch > self.gap: 
            drawbox(self.bbox, frame, -1)
            self.last_switch = time.time() #
            return True
        return False

switch = Switch(500)
bbox = switch.bbox


#funcao para enviar sinal a unity
def envia(pula):
     Message = pula
     print(Message)
     sock.sendto(bytes(Message, 'utf-8'), (UDP_IP, UDP_PORT))

color = 3
def change():
    global color
    color = (color + 1) % 4

def colorFrame(frame):
    if color == 3: return 
    for i in range(3):
        if i == color: continue
        frame[:, :, i] = 0


fvs = stream() #vs Video Stream
time.sleep(0.3) #to allow web cam to open

color = 3

while True:
    pula = False
    print(pula)
    ist = str(pula)
    envia(ist)
    frame = get_frame(fvs)
    if frame is None:
        break
    orig = frame.copy()
    drawbox(bbox, orig)
    if switch.update(frame): # se o botão for precionado
        pula = True
        ist = str(pula)
        envia(ist)
        change()
        
    colorFrame(frame)
    cv2.imshow("Original", orig)
    cv2.imshow("Result", frame)
    
    k = cv2.waitKey(1) & 0xff
    if k == 13:
        break

cv2.destroyAllWindows()
fvs.stop()

cv2.destroyAllWindows()
fvs.stop()
