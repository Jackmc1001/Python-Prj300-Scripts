from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib

print('Loading function')

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', 'eu-west-1')


# Functions

def index_faces(bucket, key):

    response = rekognition.index_faces(
        Image={"S3Object":
            {"Bucket": bucket,
            "Name": key}},
            CollectionId="Prj300Rekognition")
    return response
    
def update_index(tableName,faceId, fullName, studentNo):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            'RekognitionId': {'S': faceId},
            'FullName': {'S': fullName},
            'StudentNo': {'S': studentNo}
            }
        ) 
    
# Main handler 

def lambda_handler(event, context):

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    print("Records: ",event['Records'])
    key = event['Records'][0]['s3']['object']['key']
    print("Key: ",bucket)
    print("Key: ",key)
    # key = key.encode()
    # key = urllib.parse.unquote_plus(key)

    try:

        # Calls Amazon Rekognition IndexFaces API to detect faces in S3 object 
        # to index faces into specified collection
        
        response = index_faces(bucket, key)
        
        # Commit faceId and full name object metadata to DynamoDB
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId']

            retrieve = s3.head_object(Bucket=bucket,Key=key)
            personFullName = retrieve['Metadata']['fullname']
            personStudentNo = retrieve['Metadata']['studentno']

            update_index('Prj300',faceId,personFullName, personStudentNo)

        # Print response to console
        print(response)

        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket))
        raise 