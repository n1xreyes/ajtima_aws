import json
import base64
import boto3
import email

def lambda_handler(event, context):
    
    s3_client = boto3.client('s3')
    
    # decoding form-data into bytes
    post_data = base64.b64decode(event['body'])
    # fetching content-type
    content_type = event["headers"]['Content-Type']
    # concate Content-Type: with content_type from event
    ct = "Content-Type: "+content_type+"\n"
    
    # parsing message from bytes
    msg = email.message_from_bytes(ct.encode()+post_data)
    
    # checking if the message is multipart
    print("Multipart check : ", msg.is_multipart())
    
    # if content-type is multipart/form-dat
    if msg.is_multipart():
        multipart_content = {}
        # retrieving form-data
        for part in msg.get_payload():
            multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)

        # filename from form-data
        file_name = json.loads(multipart_content["Metadata"])["fileName"]
        token_val = json.loads(multipart_content["Metadata"])["token"]
        print('file name : ', file_name)
        
        # verify token
        if not check_token(file_name, token_val):
            return {
            'statusCode': 401,
            'headers': {

                'Access-Control-Allow-Origin': 'http://localhost:4200',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token, X-Requested-With,  Access-Control-Allow-Origin, Access-Control-Allow-Headers, Access-Control-Allow-Methods,Access-Control-Allow-Credentials',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Unauthorized')
        }
        
        # get the S3 
        get_slice_object = file_name.find(get_key_val(token_val))
        new_key = file_name[get_slice_object]
        print('get token user id val : ', get_key_val(token_val))
        print('slice object : ', get_slice_object)
        print('test get key: ', new_key)
            
        
            
        try:
            # delete object from s3
            response = s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        except ClientError as e:
            logging.error(e)
            return None
        
        # on delete success
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'http://localhost:4200',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token, X-Requested-With,  Access-Control-Allow-Origin, Access-Control-Allow-Headers, Access-Control-Allow-Methods,Access-Control-Allow-Credentials',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({"response": response})
        }
    else:
        # on upload failure
        return {
            'statusCode': 500,
            'headers': {

                'Access-Control-Allow-Origin': 'http://localhost:4200',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token, X-Requested-With,  Access-Control-Allow-Origin, Access-Control-Allow-Headers, Access-Control-Allow-Methods,Access-Control-Allow-Credentials',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE',
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Delete failed!')
        }


def check_token(file_name, token):
    # (header, payload, sig) = token.split('.')
    # hdata = header + '.' + payload
    # payload += '=' * (-len(payload) % 4)
    # payload_data = json.loads(base64.urlsafe_b64decode(payload).decode())
    payload_data = get_key_val(token)
    print('payload : ', payload_data)
    
    return payload_data in file_name
    
def get_key_val(token):
    (header, payload, sig) = token.split('.')
    hdata = header + '.' + payload
    payload += '=' * (-len(payload) % 4)
    payload_data = json.loads(base64.urlsafe_b64decode(payload).decode())
    
    return payload_data["user_id"]

def check_token(file_name, token):
    try:
        (header, payload, sig) = token.split('.')
    except ValueError as e:
        logging.error(e)
        return {
            'statusCode': 500,
            'headers': {

                'Access-Control-Allow-Origin': 'http://localhost:4200',
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
    print('payload : ', payload_data["user_id"])
    
    return payload_data["user_id"] in file_name
