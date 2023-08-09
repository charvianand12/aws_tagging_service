import boto3
from dotenv import load_dotenv
import re
from rapidfuzz import fuzz, process



load_dotenv()
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

# Initialize AWS clients
session = boto3.Session(
    region_name='us-east-2'
)
def list_resources_in_region(region, account_id):
    ec2_client = boto3.client('ec2', region_name=region)
    instance_id_list = []
    instances = ec2_client.describe_instances()
    # print(instances)
    for reservation in instances['Reservations']:
        # print(reservation)
        for instance in reservation['Instances']:
            print(f"Account: {account_id}, Region: {region}, Instance ID: {instance['InstanceId']}")
            instance_id_list.append(instance['InstanceId'])
            return instance_id_list
 
def check_spelling(input_item):
        
    best_match = list(process.extractOne(input_item, valid_keys, scorer=fuzz.ratio))
    print(best_match)
    match_string = None
    if int(best_match[1])>= 79:
        match_string = best_match[0]
    else:
        match_string = (input_item)
    # print(best_match[1])
    return match_string
 
           
organizations_client = session.client('organizations')
resource_groups_tagging_api_client = session.client('resourcegroupstaggingapi')

# Retrieve accounts in your AWS organization
response = organizations_client.list_accounts()
accounts = response['Accounts']

# Iterate through each account
for account in accounts:
    account_id = account['Id']
    print(f"Processing Account: {account_id}")
    tagging_client = session.client('resourcegroupstaggingapi')
    
    # Retrieve regions for the account
    ec2_client = session.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    # Iterate through each region
    for region in regions:
        print(f"  Processing Region: {region}")
        instance_id_list = list_resources_in_region(region, account_id)
        if instance_id_list is not None:
            for instance_id in instance_id_list:
                print(f"  Processing Instance: {instance_id}")
        # instance_id = 'i-04509bea26414d392'
                key_pattern = r'^trhc:[a-z][a-z0-9:/.-]*$'
                # key_pattern = r'^[a-z][a-z0-9:/.-]*$'
                sp_chars = ["_"," ","&"]

                # response = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [instance_id]}])
                response = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [instance_id]}])

                tags = response['Tags']
                if tags is not None:
                    for tag in tags:
                        
                        # print(tag['Key'])
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
                        