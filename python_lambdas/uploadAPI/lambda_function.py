import json
import base64
import boto3
import email
from botocore.exceptions import ClientError
import urllib3

def lambda_handler(event, context):
    s3 = boto3.client("s3")
    
    print('## EVENT')
    print(event)
    
    # decoding form-data into bytes
    post_data = base64.b64decode(event['body'])

    # retrieve the header keys as a list
    key_list = event["headers"].keys()
    is_content_type_present = "content-type" in (string.lower() for string in event["headers"])
    # print('is content type present? : ', is_content_type_present)
    
    if is_content_type_present:
        ct_found = ''
        for str in key_list:
            if str.lower() == 'content-type':
                ct_found = str
    else:
        return {
            'statusCode': 401,
            'headers': {

                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token, X-Requested-With,  Access-Control-Allow-Origin, Access-Control-Allow-Headers, Access-Control-Allow-Methods,Access-Control-Allow-Credentials',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps('content-type not found')
        }
    
    # fetching content-type
    content_type = event["headers"][ct_found]
    # concate Content-Type: with content_type from event
    ct = "Content-Type: "+content_type+"\n"
    
    # parsing message from bytes
    msg = email.message_from_bytes(ct.encode()+post_data)

    # checking if the message is multipart
    print("Multipart check : ", msg.is_multipart())
    
    # if content-type is multipart/form-data
    if msg.is_multipart():
        multipart_content = {}
        # retrieving form-data
        for part in msg.get_payload():
            multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)

        # filename from form-data
        file_name = json.loads(multipart_content["Metadata"])["fileName"]
        print('file name : ', file_name)
        
         # uploading file to S3
        try:
            s3_upload = s3.put_object(Bucket="cloudixia-images", Key=file_name, Body=multipart_content["file"])
        except Exception as e:
            raise IOError(e)
        
        # create a shareable URL
        bucket_location = s3.get_bucket_location(Bucket='cloudixia-images')
        url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location['LocationConstraint'],
        'cloudixia-images',
        file_name)
    
        
        # on upload success
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token, X-Requested-With,  Access-Control-Allow-Origin, Access-Control-Allow-Headers, Access-Control-Allow-Methods,Access-Control-Allow-Credentials',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({"URL": url})
        }
    else:
        # on upload failure
        return {
            'statusCode': 500,
            'headers': {

                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token, X-Requested-With,  Access-Control-Allow-Origin, Access-Control-Allow-Headers, Access-Control-Allow-Methods,Access-Control-Allow-Credentials,',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Upload failed!')
        }

def check_token(file_name, token):
    try:
        (header, payload, sig) = token.split('.')
    except ValueError as e:
        logging.error(e)
        return {
            'statusCode': 500,
            'headers': {

                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token, X-Requested-With,  Access-Control-Allow-Origin, Access-Control-Allow-Headers, Access-Control-Allow-Methods,Access-Control-Allow-Credentials,',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Insufficient characters in token')
        } 
    hdata = header + '.' + payload
    payload += '=' * (-len(payload) % 4)
    payload_data = json.loads(base64.urlsafe_b64decode(payload).decode())
    # print('payload : ', payload_data["user_id"])
    
    return payload_data["user_id"] in file_name

def remove_existing_file(s3CLient, file_name):
    try:
        (user_id, prefix, filename) = str(file_name).split('/')
    except ValueError as e:
        logging.error(e)
        return {
            'statusCode': 500,
            'headers': {

                'Access-Control-Allow-Origin': 'Access-Control-Allow-Origin',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token, X-Requested-With,  Access-Control-Allow-Origin, Access-Control-Allow-Headers, Access-Control-Allow-Methods,Access-Control-Allow-Credentials,',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Error fetching existing file to replace')
        }
    pathToFile = user_id + '/' + prefix + '/'
    foundObjects = s3CLient.list_objects_v2(Bucket='cloudixia-images', Prefix=pathToFile)
    try:
        for foundObject in foundObjects['Contents']:
            (user, subfolder, objectName) = str(foundObject['Key']).split('/')
            # print('objectName : ', str(objectName))
            # print('filename : ', str(filename))
            # print('find filename in objectName : ', str(objectName).find(str(filename[:10])))
            if (str(objectName).find(str(filename[:10])) != -1):
                print('Deleting', foundObject['Key'])
                s3CLient.delete_object(Bucket='cloudixia-images', Key=foundObject['Key'])
    except KeyError as e:
        print("Nothing to delete. We're good here")