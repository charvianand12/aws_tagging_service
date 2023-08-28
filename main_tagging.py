import boto3
from credentials import get_aws_credentials
from dotenv import load_dotenv
from validations import validate_tag_key, validate_tag_value
import logger_setup
import csv
import sys

load_dotenv()

def get_logger():
    log_filename = "output.log"
    logger = logger_setup.setup_logger(log_filename)
    return logger

def modify_tags():
    '''
    Works on the csv file and iterates over each row to make tag changes
    '''
    # Enter Master Account id
    role_name = "admin_role"
    print(master_account_id)
# Reading data from CSV file
    file_name = "tag_changes.csv"
    with open(file_name, mode="r") as file:
        reader = csv.DictReader(file, delimiter=";")       
        for row in reader:
            org_id = row["org_id"]
            account_id = row["account_id"]
            region = row["region"]
            resource_arn = row["resource_arn"]
            old_tag_key = row["old_tag_key"]
            new_tag_key = row["new_tag_key"]
            old_tag_value = row["old_tag_value"]
            new_tag_value = row["new_tag_value"]
            new_tags = {new_tag_key: new_tag_value}
            # org_ids.append(row["org_id"])
            # account_ids.append(row["account_id"])
            # resource_arns.append(row["resource_arn"])
            # old_tag_keys.append(row["old_tag_key"])
            # new_tag_keys.append(row["new_tag_key"])
            # old_tag_values.append(row["old_tag_value"])
            # new_tag_values.append(row["new_tag_value"])
            if account_id != master_account_id:
                access_key, secret_key, session_token = get_aws_credentials(
                    account_id, role_name
                )
                client = session.client(
                    "resourcegroupstaggingapi",
                    region_name=region,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token=session_token,
                )
            else:
                client = session.client("resourcegroupstaggingapi", region_name=region)
            response = client.untag_resources(
                ResourceARNList=[resource_arn],
                TagKeys=[
                    old_tag_key,
                ],
            )
            response = client.tag_resources(
                ResourceARNList=[resource_arn], Tags=new_tags
            )    
            logger.info("\n Old Key: %s  Old Value: %s \n  New Tag: %s",old_tag_key,old_tag_value,new_tags)
            logger.info("    tag modified\n\n")


def append_data_csv_file(tag_list):
    '''
    Updates Csv file with the proposed tag changes
    '''
    # Specify the file name
    file_name = "tag_changes.csv"

    # Writing data to CSV file
    with open(file_name, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(tag_list)
    print(f"CSV file '{file_name}' update successfully.")
    
    
def process_account_tags(master_account_id, accounts, ou_id, tags_list, session):
    '''
    Processes the Account to find the tag changes and returns the list of the changes as list for  input to append_data_csv_file function
    '''
    # Iterate through each account
    for account in accounts:
        account_id = account["Id"]
        role_name = "admin_role"  # replace "admin_role" with your role_name
        logger.info("\n\nProcessing account: %s \n", account_id )
        if len(accounts_id) == 0 or (len(accounts_id) > 0 and (account_id in accounts_id)):
            if account_id != master_account_id:
                access_key, secret_key, session_token = get_aws_credentials(
                    account_id, role_name
                )

            # Iterate through each region
            for region in regions:
                logger.info("\n Processing region: %s", region)
                if account_id != master_account_id:
                    client = session.client(
                        "resourcegroupstaggingapi",
                        region_name=region,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        aws_session_token=session_token,
                    )
                else:
                    client = session.client("resourcegroupstaggingapi", region_name=region)

                response = client.get_resources(
                            # PaginationToken='',
                            TagFilters=[],
                            ResourcesPerPage=1,
                            IncludeComplianceDetails=True,
                            ExcludeCompliantResources=False,
                        )
                resources_list=response["ResourceTagMappingList"]
                if len(resources_list) > 0:
                    pagination_token=response["PaginationToken"]
                    while pagination_token != "":
                        response = client.get_resources(
                            PaginationToken=pagination_token,
                            TagFilters=[],
                            ResourcesPerPage=100,
                            IncludeComplianceDetails=True,
                            ExcludeCompliantResources=False,
                        )
                        pagination_token=response["PaginationToken"]
                        resources_list = resources_list + (response["ResourceTagMappingList"])
                    # To be added for Testing. Keep it empty list for production run
                    resource_arn_list = []
                    for resource in resources_list:
                        resource_arn = resource["ResourceARN"]
                        resource_tags = resource["Tags"]
                        logger.info("\n Processing Resource: %s \n",resource_arn)
                        for resource_tag in resource_tags:
                            tag_key = resource_tag["Key"]
                            tag_value = resource_tag["Value"]
                            if tag_key.startswith("trhc"):
                                correct_key = validate_tag_key(tag_key, logger)
                                correct_value = validate_tag_value(tag_value, correct_key, logger)
                                new_tags = {correct_key: correct_value}
                                if (tag_key != correct_key) or (tag_value != correct_value):
                                    tag_data = []
                                    tag_data.append(ou_id)
                                    tag_data.append(account_id)
                                    tag_data.append(region)
                                    tag_data.append(resource_arn)
                                    tag_data.append(tag_key)
                                    tag_data.append(correct_key)
                                    tag_data.append(tag_value)
                                    tag_data.append(correct_value)
                                    tags_list.append(tag_data)                        
    return tags_list

accounts_id = []
regions = ["us-west-2", "us-west-1", "us-east-2", "us-east-1"]
session = boto3.Session(region_name="us-east-2")
organizations_client = session.client("organizations")

# to be added
organization_parent_id = 'r-18jb'
response = organizations_client.list_organizational_units_for_parent(ParentId=organization_parent_id)
organizations = response['OrganizationalUnits']
logger = get_logger()

file_name = "tag_changes.csv"
header_list = [
    ["org_id", "account_id", "region", "resource_arn", "old_tag_key", "new_tag_key", "old_tag_value", "new_tag_value"],
]
dry_run = sys.argv[1] if len(sys.argv) > 1 else None
# Writing data to CSV file
if dry_run is not None and dry_run == "dry_run":
    with open(file_name, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(header_list)    
    
tags_list = []
master_account_id = "473670996314"
if len(organizations) > 0:
    for organization in organizations:
        ou_id = organization['Id']
        logger.info("Processing Organization: %s", ou_id)

        response = organizations_client.list_accounts_for_parent(ParentId=ou_id)
        accounts = response['Accounts']

        # Describe the OU to get its details
        ou_response = organizations_client.describe_organizational_unit(OrganizationalUnitId=ou_id)

        # Extract the master account ID from the response
        if dry_run is not None and dry_run == "dry_run":
            tags_list = process_account_tags(master_account_id, accounts, ou_id, tags_list, session)

response = organizations_client.describe_organization()
organization_details = response["Organization"]

# Retrieve accounts in your AWS organization
response = organizations_client.list_accounts()
accounts = response["Accounts"]
logger.info("Processing Organization %s", organization_details['Id'])
if dry_run is not None and dry_run == "dry_run":
    tags_list = process_account_tags(master_account_id, accounts, organization_details['Id'], tags_list, session)
    append_data_csv_file(tags_list)
if dry_run is None and dry_run != "dry_run":
    print(dry_run)
    modify_tags()