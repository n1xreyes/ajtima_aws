const AWS = require('aws-sdk')
const s3 = new AWS.S3()

exports.handler = async function(event, context, callback) {
    const allKeys = [];
    await getKeys({ Bucket: 'cloudixia-images',Prefix: event.queryStringParameters.folderPath }, allKeys);
    console.log('folderPath', event.queryStringParameters.folderPath);
    // callback(null, {
    //         statusCode: 200, 
    //         body: "great success!"
    //     });
    const url_prefix = 'https://s3-us-east-2.amazonaws.com/cloudixia-images/';
    const attachmentUrls = [];
    allKeys.forEach(key => {
      const fileName = key.substr(key.lastIndexOf("/")+1);
      attachmentUrls.push({"url": url_prefix + key, "fileName": fileName, "key": key});
      });
    // return allKeys;
    console.log('attachmentUrls', attachmentUrls);
    return attachmentUrls;
}

async function getKeys(params, keys){
  // const response = await s3.listObjectsV2(params).promise();
  const response = await s3.listObjectsV2(params).promise();
  response.Contents.forEach(obj => {
    console.log('obj', obj);
    keys.push(obj.Key)
    });

  if (response.IsTruncated) {
    const newParams = Object.assign({}, params);
    newParams.ContinuationToken = response.NextContinuationToken;
    await getKeys(newParams, keys); // RECURSIVE CALL
  }
}