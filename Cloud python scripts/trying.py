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
        
    if FaceDetected == True:
       findFace()
    else:
        print("Try again")

def findFace(Rekognition):
    found = False
    #for loop if multple images are seen
        for match in Rekognition['FaceMatches']:
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
    
    
    






