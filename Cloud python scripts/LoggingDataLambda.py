import json
import boto3
import array
from datetime import datetime

from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
  client = boto3.resource('dynamodb', region_name='eu-west-1')
  table = client.Table('logging_data')   
  response =table.scan()
  items=response['Items']
  #covert date to datetime, and then filter by date and time newest first
  sorted_data = sorted(response["Items"], key=lambda x: (datetime.strptime(x["Date"], "%d/%m/%Y"), x["Time"]), reverse=True)
 
  
  print(sorted_data)
  return {
    'statusCode': 200,
    'body': sorted_data
  }