from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    dynamodb = boto3.client('dynamodb')

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']

    # Get data from S3 bucket
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = response['Body'].read().decode('utf-8')
    
    entryFullName = ret['Metadata']['fullname']
    entryDate = ret['Metadata']['date']
    entryMatch = ret['Metadata']['match']
    entryTime = ret['Metadata']['time']
    entryStudentNo = ret['Metadata']['studentno']
    entryPass = ret['Metadata']['pass']
   
    
    # Store data in DynamoDB table
    table_name = 'logging_data'
    dynamodb.put_item(TableName=table_name, Item=
                      {'FileName': {'S': file_key},
                       'Date': {'S': entryDate},
                       'FullName': {'S': entryFullName},
                       'Match': {'S': entryMatch},
                       'Pass': {'N': entryPass},
                       'StudentId': {'S': entryStudentNo},
                       'Time': {'S': entryTime},
                       }
                      )
    
    return 'Data stored in DynamoDB table successfully'