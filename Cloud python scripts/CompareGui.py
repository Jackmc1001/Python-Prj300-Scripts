from tkinter import *
from tkinter import messagebox
import boto3
import io
from PIL import Image
import cv2
from datetime import datetime
import os
import time

class MyWindow:
    def __init__(self, win):
        self.lbl1=Label(win, text='Press Button to take Photo')
        self.lbl1.place(relx=.5, rely=.3,anchor= CENTER)
        
        def showMsg(cam_port=0):
            image_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            cam = cv2.VideoCapture(cam_port)
            t = 3
            while t:
                mins, secs = divmod(t, 60)
                timer = '{:02d}:{:02d}'.format(mins, secs)
                self.lbl2=Label(text=(timer))
                self.lbl2.place(relx=.5, rely=.6,anchor= CENTER)
                #print(timer, end="\r")
                time.sleep(1)
                t -= 1
            result, image = cam.read()
            self.lbl1=Label(text='Processing')
            
            
            print("Smile")
            if result:
                cv2.imshow(image_name, image)
                cv2.imwrite(image_name+".jpg", image)
                #cv2.waitKey(0)
                cv2.destroyWindow(image_name)
                cam.release()
                #return image_name
            else:
                print("No image detected.")
            
        
        self.btn=Button(win, text="Button", command=showMsg)
        self.btn.place(relx=.5, rely=.4,anchor= CENTER)
        



window=Tk()
mywin=MyWindow(window)
window.title('Hello Python')
window.geometry("500x400+10+10")
window.mainloop()