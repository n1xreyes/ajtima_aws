import json
import boto3
import base64

def lambda_handler(event, context):
    
    s3 = boto3.client("s3")
    bucket_name = event["pathParameters"]["bucket"]
    file_name = event["queryStringParameters"]["file"]
    fileObj = s3.get_object(Bucket=bucket_name, Key=file_name)
    file_content = fileObj["Body"].read()
    
    URL = s3.generate_presigned_url('get_object',
                                    Params={'Bucket': bucket_name,
                                            'Key': file_name},
                                            ExpiresIn=100)
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        # "body": base64.b64encode(file_content),
        "body": json.dumps({"URL": URL})
    }