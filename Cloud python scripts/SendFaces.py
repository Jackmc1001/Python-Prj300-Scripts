import boto3

s3 = boto3.resource('s3')

# Get list of objects for indexing
Faceimages=[('Jack.jpg', 'Jack', 'S00209393'),
        ('Gatis1.jpg', 'Gatis','S00209875'),
        ('Craig1.jpg', 'Craig','S00209542'),
        ('Craig2.jpg', 'Craig','S00209542')
        ,('Sean1.jpg', 'Sean', 'S00210945')
            ]
open("Jack.jpg", "rb")        

# Iterate through list to upload objects to S3   
for x in Faceimages:
    # rb - read binary 
    file = open(x[0],'rb')
    object = s3.Object('facrectestjack', x[0])
    ret = object.put(Body=file, Metadata={'FullName':x[1], 'StudentNo':x[2]})