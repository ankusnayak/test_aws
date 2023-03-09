import json
import boto3
import urllib
import os
import sys
from botocore.exceptions import ClientError
from datetime import datetime


class Tools:
    
    @staticmethod
    def debugging(*msg):
        try:
            if msg:
                for m in msg:
                    print(m)
            else:
                print("Empty Message")
            # input()
            
        except Exception as e:
            print("Error:: %s"%str(e))
            sys.exit()
        
    @staticmethod
    def get_datetime():
        
        # return a current datetime string 
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    

class EmailOperation:
    
    def __init__(self,status):
        self.ses_client = self.sesClientObject()
        self.template_name = status+"_template"
        
        
    def sesClientObject(self):
        try:
            return boto3.client('ses')
            
        except ClientError as e:
            print("Error: while create boto3 sns client \n %s"%str(e))
            
        
    def createAndUpdateTemplate(self):
        
        # self.ses_client.delete_template(
        #     TemplateName = self.template_name
        # )
        
        try:
            
            response=self.ses_client.get_template(TemplateName=self.template_name)
            if response['Template'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
                self.ses_client.update_template(
                        Template={
                            "TemplateName": self.template_name,
                            "SubjectPart": "{{status}} : 'File Name': {{file_name}} || Date: {{date}}",
                            # "SubjectPart": "Subject",
                            "HtmlPart": "Hello Ankus HTML",
                            "TextPart": "Hello Ankus Text"
                        }
                    )
                
        except ClientError as e:
            
            self.ses_client.create_template(
                    Template =  {
                        "TemplateName": self.template_name,
                        "SubjectPart": "{{status}} : 'File Name': {{file_name}} || Date: {{date}}",
                        # "SubjectPart": "Subject",
                        "HtmlPart": "Hello Ankus HTML",
                        "TextPart": "Hello Ankus Text"
                    }
                )
        else:
            return True

    def mailStatus(self,mail_response):

        if mail_response:
            if mail_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('email sent successfully..')
                # return True
            else:
                print('email sending failed..')
                # return False
        else:
            print('email response is empty...')
            # return False
        
    def sendEmail(self,source_email,dest_email,mail_data):
        
        response = None
        
        try:
            response = self.ses_client.send_templated_email(
                    Source = source_email,
                    Destination={
                        'ToAddresses': [
                            dest_email
                        ],
                        # 'CcAddresses': ['iamankus7@gmail.com']
                    },
                    Template=self.template_name,
                    # TemplateData = mail_data
                    TemplateData = mail_data
                )
                
            return response
        except Exception as e:
            print("Error: %s"%str(e))
        


def lambda_handler(event, context):
    
    s3_client = boto3.client('s3')
    
    if event:
        file_obj = event['Records'][0]
        bucket_name = file_obj['s3']['bucket']['name']
        # key = urllib.parse.unquote_plus(file_obj['s3']['object']['key'], encoding='utf-8')
        key = file_obj['s3']['object']['key']
        key = urllib.parse.unquote_plus(key,encoding='utf-8')
        
        # - Need to find better approach for assign...
        file_name,file_prefix,file_type = None, None, None
        
        if os.path.dirname(key):
            file_name = key.split('/')[-1]
            file_prefix = key.split('/')[-2]
            file_type = file_name.split('.')[-1]
        else:
            file_name = key
            file_type = key.split('.')[-1]
        
        # Tools.debugging(file_name,file_prefix,file_type)
        
        
        
        # try:
        #     response = s3_client.get_object(Bucket=bucket_name, Key=key)
        #     print("Content Type: ",response['ContentType'])
        #     return response['ContentType']
        # except Exception as e:
        #     print("Error: %s" %str(e))
        #     # raise e
        
        status = None
        error_reason = None
        
        try:
            if file_prefix:
                decider_folder = file_prefix.split('/')[0]
                
                if decider_folder.lower() == "success":
                    status = "success"
                elif decider_folder.lower() == "error":
                    status = "error"
                else:
                    print("Undetected Folder")
                    error_reason = "Undetected Folder"
                    status = "error"
            else:
                status = "error"
                error_reason = "No File Prefix || So Unable to determine the status."
                # sys.exit("No File Prefix || So Unable to determine the status.")
        except Exception as e:
            sys.exit("Error: %s"%str(e))
        
        ##################Testing###################
        
        
        ######Createing Test Dict#########
        
        test_data = {
                'status': status,
                'file_name': file_name,
                'date': Tools.get_datetime()
            }
            
        if error_reason:
            test_data['error_reason'] = error_reason
        
        
        emailObj = EmailOperation(status)
                
        # Tools.debugging("This is test",status,emailObj.template_name)
        
        if emailObj.createAndUpdateTemplate():
            mailResponse = emailObj.sendEmail('iamankus7@gmail.com','iamankus7@gmail.com',json.dumps(test_data))
            emailObj.mailStatus(mailResponse)
