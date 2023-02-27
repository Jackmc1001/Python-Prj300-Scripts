import boto3
import tkinter as tk 
import io
from PIL import Image
import cv2
from datetime import datetime
import os
import time


s3 = boto3.resource('s3')
rekognition = boto3.client('rekognition', region_name='eu-west-1')
dynamodb = boto3.client('dynamodb', region_name='eu-west-1')


class RekoglockGUI:
    def __init__(self):
        
        
        self.root = tk.Tk()
        self.root.geometry("500x300") #width x height
        
        self.label = tk.Label(self.root, text="Click button to gain Entry", font=("Arial", 18))
        self.label.pack(padx=20,pady=20)
        
        self.button = tk.Button(self.root, text="Click Me!", font=("Arial", 18), command=lambda: [self.Showmsg(), self.Search_faces()])
        self.button.pack(padx=20,pady=20)
        
        self.labelentry = tk.Label(self.root, text=" ", font=("Arial", 18))
        self.labelentry.pack(padx=20,pady=20)
        
        self.root.mainloop()
        
        
    
        
        
    def Search_faces(self):
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
            
        else:
            print("No image detected.")
        
        entry_date = datetime.now().strftime('%d/%m/%Y')
        entry_time = datetime.now().strftime('%H:%M:%S')
        
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
                    personName =face['Item']['FullName']['S']
                    StudentNumber = face['Item']['StudentNo']['S']
                    #print ("Found Person: Name:", face['Item']['FullName']['S'], ", Student No:", face['Item']['StudentNo']['S'])
                    self.labelentry["text"]= "Access Granted"
                    print("Access Granted!")
                    found = True
                    sendtos3( image_name+'.jpg', entry_date, entry_time, personName, StudentNumber,matchconfidence ,1)
             
                
                
            if found == False:
                print("Person cannot be recognized")
                self.labelentry["text"]="Access Denied"
                print("Access Denied")
                sendtos3(image_name+'.jpg', entry_date, entry_time, "Unkown", "Unkown", "0" ,0)
        
        
        os.remove(image_name+".jpg")
        
        
    def Showmsg(self):
        timer = 3
        while timer != 0:
            self.label["text"]=timer
            
            self.root.update()
            time.sleep(1)
            timer = timer - 1
        
        self.label["text"]="smile"
        self.root.update()
        
def sendtos3(Imagename, Date, Time, Name, studentNo, result, Pass):
    file = open(Imagename,'rb')
    object = s3.Object('logging-data-bucket-prj300', Imagename)
    ret = object.put(Body=file, Metadata={'Date': Date,'Time': Time,'FullName':Name, 'StudentNo':studentNo, 'Match':str(result), 'Pass':str(Pass)})
            
        
RekoglockGUI()