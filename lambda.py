import json
import boto3
import urllib

def debugging(msg):
    
    try:
        if msg:
            print(msg)
        else:
            print("Empty Message")
            
        # input()
        
    except Exception as e:
        print("Error:: %s"%str(e))
        sys.exit()

def lambda_handler(event, context):
    
    s3_client = boto3.client('s3')
    sns_client = boto3.client('sns')
    
    
    if event:
        file_obj = event['Records'][0]
        bucket_name = file_obj['s3']['bucket']['name']
        # key = urllib.parse.unquote_plus(file_obj['s3']['object']['key'], encoding='utf-8')
        key = file_obj['s3']['object']['key']
        key = urllib.parse.unquote_plus(key,encoding='utf-8')
        
        
        file_name = key.split('/')[-1]
        # file_prefix = key.split('/')[-2]
        file_type = file_name.split('.')[-1]
        
        debugging(key)
        
        
        
        # try:
        #     response = s3_client.get_object(Bucket=bucket_name, Key=key)
        #     print("Content Type: ",response['ContentType'])
        #     return response['ContentType']
        # except Exception as e:
        #     print("Error: %s" %str(e))
        #     # raise e
        
