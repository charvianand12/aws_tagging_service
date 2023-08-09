import boto3
from dotenv import load_dotenv

load_dotenv()


# Initialize AWS clients
session = boto3.Session(
    region_name='us-east-2'
)

organizations_client = session.client('organizations')
resource_groups_tagging_api_client = session.client('resourcegroupstaggingapi')

# # Define your naming conventions and rules
# def validate_tag(tag_key, tag_value):
#     # Implement your tag validation rules here
#     # Return True if the tag is valid, otherwise False
#     return True

# def modify_tag(tag_key, tag_value):
#     # Implement your tag modification logic here
#     # Return the modified tag key and value
#     new_tag_key = tag_key
#     new_tag_value = tag_value
#     return new_tag_key, new_tag_value

# Retrieve accounts in your AWS organization
response = organizations_client.list_accounts()
accounts = response['Accounts']

# Iterate through each account
for account in accounts:
    account_id = account['Id']
    print(f"Processing Account: {account_id}")
    
    # Switch to the account's session
    # account_session = boto3.Session(
    #     aws_session_token=session.get_session_token()['Credentials']['SessionToken'],
    #     region_name='us-east-1'  # Specify the default region or choose a region
    # )
    
    # Initialize the resource groups tagging API client
    tagging_client = session.client('resourcegroupstaggingapi')
    
    # Retrieve regions for the account
    ec2_client = session.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    # Iterate through each region
    for region in regions:
        print(f"  Processing Region: {region}")
        
        # Retrieve resources with tags in the region
        resources = tagging_client.get_resources(
            ResourceTypeFilters=['ec2:instance'],  # Specify the resource types you want to validate
            TagFilters=[
                {'Key': 'your_tag_key'}  # Specify your tag key
            ],
            ResourcesPerPage=50  # Adjust the pagination if needed
        )['ResourceTagMappingList']
        
        # Iterate through each resource
        for resource in resources:
            resource_arn = resource['ResourceARN']
            print(resource_arn)
            # tags = resource['Tags']
            
            # # Iterate through each tag of the resource
            # for tag in tags:
            #     tag_key = tag['Key']
            #     tag_value = tag['Value']
                
            #     # Validate the tag according to your rules
            #     if not validate_tag(tag_key, tag_value):
            #         # Modify the tag
            #         new_tag_key, new_tag_value = modify_tag(tag_key, tag_value)
                    
            #         # Update the tag
            #         tagging_client.tag_resources(
            #             ResourceARNList=[resource_arn],
            #             Tags=[
            #                 {'Key': new_tag_key, 'Value': new_tag_value}
            #             ]
            #         )
            #         print(f"    Tag Modified for Resource: {resource_arn}")
