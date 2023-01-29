import boto3
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
        cv2.waitKey(0)
        cv2.destroyWindow(image_name)
        cam.release()
        return image_name
    else:
        print("No image detected.")
        
        
def search_faces(image_name):
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
    #for loop if multple images are seen
    if FaceDetected == True:
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
                personName =face['Item']['FullName']['S']
                StudentNumber = face['Item']['StudentNo']['S']
                print ("Found Person: Name:", face['Item']['FullName']['S'], ", Student No:", face['Item']['StudentNo']['S'])
            
                found = True
            return found
            
        if not found:
            print("Person cannot be recognized")
        
def main():
    
    Image_Name = capture_and_save_image()
    
    search_faces(Image_Name)
    
    os.remove(Image_Name+".jpg")

if __name__ == "__main__":
    main()
