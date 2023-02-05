import boto3
import io
from PIL import Image
import cv2
from datetime import datetime
import os

s3 = boto3.resource('s3')

def sendtos3(Image, Date, Time, Name, studentNo, result):
    file = open(Image,'rb')
    object = s3.Object('logging-data-bucket-prj300', Image)
    ret = object.put(Body=file, Metadata={'Date': Date,'Time': Time,'FullName':Name, 'StudentNo':studentNo, 'Match':result})
    

rekognition = boto3.client('rekognition', region_name='eu-west-1')
dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

#camport 0 is laptop camera
cam_port = 0
image_name = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
entry_date = datetime.now().strftime('%d/%m/%Y')
entry_time = datetime.now().strftime('%H:%M:%S')


cam = cv2.VideoCapture(cam_port)

# reading the input using the camera
result, image = cam.read()


if result:
 # shows the image with the image name as the window name
    cv2.imshow(image_name, image)

# saves image
    cv2.imwrite(image_name+".jpg", image)
    
# on a keyboard press, close the window an dturn off the camera

    #cv2.waitKey(0)
    cv2.destroyWindow(image_name)
    cam.release()

# If captured image is corrupted, moving to else part
else:
    print("No image detected.")


#open the image
image = Image.open(image_name + ".jpg")

stream = io.BytesIO()
image.save(stream,format="JPEG")
image_binary = stream.getvalue()

# searches the collection for the face
response = rekognition.search_faces_by_image(
        CollectionId='Prj300Rekognition',
        Image={'Bytes':image_binary}                                       
        )

found = False
#for loop if multple images are seen 
for match in response['FaceMatches']:
    matchconfidence = round(match['Face']['Confidence'], 9 )
    print(matchconfidence)
    
    #uses the RekognitionId to find the face in dynamo
    face = dynamodb.get_item(
        TableName='Prj300',  
        Key={'RekognitionId': {'S': match['Face']['FaceId']}}
        )
    #checks if there is a face, get the metadata e.g name and student no.
    if 'Item' in face:
        personName=face['Item']['FullName']['S']
        StudentNumber= face['Item']['StudentNo']['S']
        print ("Found Person: Name:", face['Item']['FullName']['S'], ", Student No:", face['Item']['StudentNo']['S'])
        
        found = True
        
        sendtos3(image_name +'.jpg', entry_date, entry_time, personName, StudentNumber, str(matchconfidence))
        #deletes the image from my own laptop
os.remove(image_name+".jpg")
if not found:
    print("Person cannot be recognized")