#enviornment variables - room no
#system variables - mac and ip address

import socket
import boto3
import time
import io
from PIL import Image
import cv2
from datetime import datetime
import os

s3 = boto3.resource('s3')
rekognition = boto3.client('rekognition', region_name='eu-west-1')
dynamodb = boto3.client('dynamodb', region_name='eu-west-1')



def capture_and_save_image(cam_port=0):
    image_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    
    cam = cv2.VideoCapture(cam_port)

    result, image = cam.read()

    if result:
        cv2.imshow(image_name, image)
        cv2.imwrite(image_name+".jpg", image)
        #cv2.waitKey(0)
        cv2.destroyWindow(image_name)
        cam.release()
        return image_name
    else:
        print("No image detected.")
        return image_name
        
        
        
def search_faces(image_name):
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
                
                print("Access Granted!")
                found = True
                sendtos3(image_name+'.jpg', entry_date, entry_time, personName, StudentNumber,matchconfidence ,1)
            
            
            
        if found == False:
            print("Person cannot be recognized")
            print("Access Denied")
            sendtos3(image_name+'.jpg', entry_date, entry_time, "Unkown", "Unkown", "0" ,0)
    
    
        os.remove(image_name+".jpg")  
            
def sendtos3(Imagename, Date, Time, Name, studentNo, result, Pass):
    file = open(Imagename,'rb')
    object = s3.Object('logging-data-bucket-prj300', Imagename)
    ret = object.put(Body=file, Metadata={'Date': Date,'Time': Time,'FullName':Name, 'StudentNo':studentNo, 'Match':str(result), 'Pass':str(Pass)})
        
def main():
    x = True;
    hostname=socket.gethostname()   
    IPAddr=socket.gethostbyname(hostname)   
    #print("Your Computer Name is:"+hostname)   
    print("Your Computer IP Address is:"+IPAddr) 
    while x == True:
        key_entry = "value"
        #time.sleep(3)
        key_entry = input("Hit the Enter button to continue")
        if key_entry == "":
        
            Image_Name = capture_and_save_image()
            search_faces(Image_Name)
            
            #time.sleep(3)
        else:
            time.sleep(3)
            
    
    

if __name__ == "__main__":
    main()

