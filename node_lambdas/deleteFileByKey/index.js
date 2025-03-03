const AWS = require('aws-sdk')
const s3 = new AWS.S3()

exports.handler = async (event, context, callback) => {
    const url_prefix = 'https://s3-us-east-2.amazonaws.com/cloudixia-images/';
    // check if params is a url or an actual file key
    if (event.queryStringParameters.fileKey.lastIndexOf(url_prefix) > -1) {
        const fileKey = event.queryStringParameters.fileKey.substr(event.queryStringParameters.fileKey.lastIndexOf(url_prefix)+52);
        console.log('fileKey', fileKey);
        await deleteFromS3(fileKey);
    } else {
        await deleteFromS3(event.queryStringParameters.fileKey);
    }
    // TODO implement
    const response = {
        statusCode: 200,
        body: JSON.stringify('File deleted!'),
    };
    return response;
};

async function deleteFromS3(attachmentId) {
 return s3.deleteObject({ Bucket: 'cloudixia-images', Key: attachmentId }).promise();
}
