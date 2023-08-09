import boto3
import re
from rapidfuzz import fuzz, process

valid_keys = ["trhc:name",
              "trhc:asset-source",
              "trhc:creation-ticket",
              "trhc:criticality", 
              "trhc:contact-name",
              "trhc:administrator",
              "trhc:business-unit",
              "trhc:product-name",
              "trhc:customer",
              "trhc:data-security-level",
              "trhc:team",
              "trhc:data-privacy-level",
              "trhc:idle-shutdown",
              "trhc:after-hours-shutdown",
              "trhc:workday-auto-start",
              "trhc:backup-policy",
              "trhc:retention-policy",
              "trhc:finance:component",
              "trhc:finance:rev-center",
              "trhc:initiative-epic",
              "trhc:stage",
              "trhc:hostname",
              "trhc:delete-after",
              "trhc:maintenance-window",
              "trhc:durable",
              "trhc:project",
              "trhc:role",
              "accenture"
              ]

session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
    region_name='us-east-2'
)

ec_client = session.client('ec2')

instance_id = 'i-04509bea26414d392'
key_pattern = r'^trhc:[a-z][a-z0-9:/.-]*$'
# key_pattern = r'^[a-z][a-z0-9:/.-]*$'
sp_chars = ["_"," ","&"]

# response = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [instance_id]}])
response = ec_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [instance_id]}])

tags = response['Tags']

def check_spelling(input_item):
    
    best_match = list(process.extractOne(input_item, valid_keys, scorer=fuzz.partial_ratio))
   
    if int(best_match[1])>= 85:
        # print(best_match[1])
        return(best_match[0])
    else:
        # print(best_match[1])
        return(input_item)
            
            
for tag in tags:
    
    print(tag['Key'])
    if re.match(key_pattern, tag['Key']) and " " not in tag['Key']:
        # print("pattern matched")
        pass
    else:
        # print("pattern not matched")
        tag['Key'] = tag['Key'].strip()
        if tag['Key'].startswith("trhc:") or tag['Key'].startswith("accenture"):
            tag['Key']=tag['Key'].lower()
        else:
            tag['Key']="trhc:" + tag['Key'].lower()
        
        for sp_char in sp_chars:
            if sp_char in tag['Key']:
                if tag['Key'].startswith(sp_char) or tag['Key'].endswith(sp_char):
                    tag['Key']=tag['Key'].replace(sp_char,"")
                else:
                    tag['Key']=tag['Key'].replace(sp_char,"-")
            
       
    # print(tag['Key'])
    
    correct_key = check_spelling(tag['Key'])
    tag['Key'] = correct_key
    print(tag['Key'])
    print("\n\n")
    


        
    
