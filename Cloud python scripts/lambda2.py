from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib

print('Loading function')

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')

def update_index(tableName, faceId, fullName, studentNo):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            'RekognitionId': {'S': faceId},
            'FullName': {'S': fullName},
            'StudentNo': {'S': studentNo}
            }
        ) 
    

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
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            retrieve = s3.head_object(Bucket=bucket,Key=key)
            personFullName = retrieve['Metadata']['fullname']
            personStudentNo = retrieve['Metadata']['studentno']
            personMatch = retrieve['Metadata']['match']
                
            update_index('logging_data', faceId, personFullName, personStudentNo)
                
        print(response)

            
        return response

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket))
        raise 