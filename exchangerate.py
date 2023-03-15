from apify_client import ApifyClient 
from datetime import datetime
import json
import logging
import boto3
logger = logging.getLogger()

def lambda_handler(event, context):
    thre = 5 # set your threhold here
    nowtime = datetime.now()

    ses_client = boto3.client('ses', region_name='us-east-1') 
    sender = 'sender@email.com' ## change sender email here
    recipient = ['recipient1@email.com'] ## change recipients emails here
    
    
    apify_client = ApifyClient('TOKEN')  # use your own APIFY token
    rate_param ={
        "from": "CAD",
        "to": "CNY",
        "amount": 1
    }
    actor_call = apify_client.actor('rrortega/google-currency-exchange').call(run_input=rate_param)
    runID = actor_call['id']
    log = apify_client.log(runID).get()
    index = log.find("rate") ## get the log infomation from apify and locate the "rate : *.** "
    
    # try to convert the exchange rate from string to float. and write the email accordingly
    try:
        rate = float(log[index + 7:index + 15])
        body = f"work is done, the rate is <p> {rate} </p>"
        subject = f'Exchange Rate below {thre}'
    except:
        print("there is an error when getting the rates")
        body =  "there is an error when getting the rates"
        subject = 'Error when getting exchange rates'
        rate = 100
        
    if rate <=thre: #send email according to the relationship btw actual rate and threhold rate
        try:
            response = ses_client.send_email(
                Destination={
                    'ToAddresses': recipient,
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': 'UTF-8',
                            'Data': body,
                        },
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': subject,
                    },
                },
                Source=sender,
            )
            print(response)
        except Exception as e:
            print(e)
         
    elif nowtime.hour == 14 and nowtime.minute <=30: ##get a status email for every day 
        body = f"The Exchange rate between CAD and CNY is {rate}. I will be keeping on eye on it"
        response = ses_client.send_email(
            Destination={
                'ToAddresses': recipient,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': "Exchange Rate Daily Update",
                },
            },
            Source=sender,
        )
        


    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
