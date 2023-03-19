#aws library 
import boto3
#gui
import tkinter as tk
#libraries for devices and images and basic functionality
import io
from PIL import Image
import cv2
from datetime import datetime
import os
import time
from sys import platform 


#libraries to collect MAC and IP address
import socket
import re,uuid

#resources for AWS
s3 = boto3.resource('s3')
rekognition = boto3.client('rekognition', region_name='eu-west-1')
dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

failCounter = 0 

class RekoglockGUI:
    def __init__(self):
        self.root = tk.Tk()
        #cente
        
        
        self.root.geometry("500x300") #width x height
        
        
        self.labelHead = tk.Label(self.root, text="Click button to gain Entry", font=("Arial", 18))
        self.labelHead.pack(padx=20,pady=20)
        
        self.labeltimer = tk.Label(self.root, text=" ", font=("Arial", 18))
        self.labeltimer.pack(padx=20,pady=20)
        
        self.button = tk.Button(self.root, text="Click Me!", font=("Arial", 18), command=lambda: [self.Showmsg(), self.Search_faces()])
        self.button.pack(padx=20,pady=20)
        
        self.labelentry = tk.Label(self.root, text=" ", font=("Arial", 18))
        self.labelentry.pack(padx=20,pady=20)
        
        
        
        self.root.mainloop()
        
        time.sleep(3)
        
    
        
    #takes picture, gets time of picture taken, finds in rekogniton, then finally
        #compares to dynamodb with the face id
    def Search_faces(self):
        #enviornment variables
        devIP = socket.gethostbyname(socket.gethostname())
        devMAC = (':'.join(re.findall('..', '%012x' % uuid.getnode())))
        Room_No = "B1043"
        
        
        image_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        cam_port = 0
        cam = cv2.VideoCapture(cam_port)

        result, image = cam.read()

        if result:
            cv2.imshow(image_name, image)
            cv2.imwrite(image_name+".jpg", image)
            #cv2.waitKey(0)
            cv2.destroyWindow(image_name)
            cam.release()
            self.labelHead["text"]="Picture taken"
            self.root.update()
            
        else:
            print("No image detected.")
            
        
        entry_date = datetime.now().strftime('%d/%m/%Y')
        entry_time = datetime.now().strftime('%H:%M:%S')
        print(entry_date)
        image = Image.open(image_name + ".jpg")
        
        stream = io.BytesIO()
        image.save(stream,format="JPEG")
        image_binary = stream.getvalue()

        # searches the collection for the face
        FaceDetected = True 
        try:
            
            response = rekognition.search_faces_by_image(
                    CollectionId='Prj300Rekognition',
                    Image={'Bytes':image_binary}                                       
                    )
        except:
            print("no faces detected" )
            self.labeltimer["text"]= "No Face recognised"
            self.labelentry["text"]= "Please contact admin if error persists"
            self.root.update()
            
            FaceDetected = False 
        found = False
        
        #create a list to send image and metadata
        
        
        #for loop if multple images are seen
        if FaceDetected == True:
            for match in response['FaceMatches']:
                matchconfidence = round(match['Face']['Confidence'], 2 )
                #print(matchconfidence)

                #uses the RekognitionId to find the face in dynamo
                face = dynamodb.get_item(
                    TableName='Prj300',  
                    Key={'RekognitionId': {'S': match['Face']['FaceId']}}
                    )
                
                
                
                #checks if there is a face, get the metadata e.g name and student no.
                if 'Item' in face:
                    personName = face['Item']['FullName']['S']
                    StudentNumber = face['Item']['StudentNo']['S']
                    print ("Found Person: Name:", face['Item']['FullName']['S'], ", Student No:", face['Item']['StudentNo']['S'])
                    self.labelentry["text"]= "Access Granted"
                    print("Access Granted!")
                    
                    found = True
                    sendtos3(image_name+'.jpg', entry_date, entry_time, personName, StudentNumber,matchconfidence ,1,
                             Room_No, devIP, devMAC)
             
                
                
            if found == False:
                print("Person cannot be recognized")
                self.labelentry["text"]="Access Denied"
                print("Access Denied")
                
                sendtos3(image_name+'.jpg', entry_date, entry_time, "Unknown", "Unknown", "0" ,0,
                         Room_No, devIP, devMAC)
        
        try:    
            os.remove(image_name+".jpg")
            print("Removed image")
        except:
            print("Image could not be removed")
        self.root.update()
        time.sleep(3)
        self.button["state"] = "normal"
        self.labelentry["text"]=" "
        self.labeltimer["text"]= " "
        self.labelHead["text"]="Click button to gain Entry"
        
        
        
    def Showmsg(self):
        
        self.button["state"] = "disabled"
        self.labelHead["text"]="Face the camera in..."
        timer = 3
        while timer != 0:
            self.labeltimer["text"]=timer
            
            self.root.update()
            time.sleep(1)
            timer = timer - 1
            
        
        
def sendtos3(Imagename, Date, Time, Name, studentNo, result, Pass, roomNo, ipAdd, macAdd):
    file = open(Imagename,'rb')
    object = s3.Object('logging-data-bucket-prj300', Imagename)
    ret = object.put(Body=file, Metadata={'Date': Date,'Time': Time,'FullName':Name, 'StudentNo':studentNo, 'Match':str(result), 'Pass':str(Pass),
                                          'RoomNo':roomNo,'IPAdd':ipAdd, 'MAC':macAdd})
    
    


#main run
RekoglockGUI()
    

