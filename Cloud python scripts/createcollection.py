import boto3

def create_collection(collection_id):

    client=boto3.client('rekognition','eu-west-1' )

    #Create a collection
    print('Creating collection:' + collection_id)
    response=client.create_collection(CollectionId=collection_id)
    print('Collection ARN: ' + response['CollectionArn'])
    print('Status code: ' + str(response['StatusCode']))
    print('Collection created')
    
def main():
    collection_id='Prj300Rekognition'
    create_collection(collection_id)

if __name__ == "__main__":
    main()    