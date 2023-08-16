import boto3
from credentials import get_aws_credentials
from dotenv import load_dotenv
from validations import validate_tag_key, validate_tag_value
import logger_setup

load_dotenv()


def process_account_tags(master_account_id, accounts, session):
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
                logger.info(" Processing region: %s", region)
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
                    for resource in resources_list:
                        resource_arn = resource["ResourceARN"]
                        resource_tags = resource["Tags"]
                        for resource_tag in resource_tags:
                            tag_key = resource_tag["Key"]
                            tag_value = resource_tag["Value"]
                            correct_key = validate_tag_key(tag_key)
                            correct_value = validate_tag_value(tag_value, correct_key)
                            new_tags = {correct_key: correct_value}
                            
                            if (tag_key != correct_key) or (tag_value != correct_value):
                                response = client.untag_resources(
                                    ResourceARNList=[resource_arn],
                                    TagKeys=[
                                        tag_key,
                                    ],
                                )
                                response = client.tag_resources(
                                    ResourceARNList=[resource_arn], Tags=new_tags
                                )    
                                logger.info("\n    Resource ARN: %s",resource_arn)
                                logger.info("\n    Old Key: %s      Old Value:%s \n    New Tag:%s",tag_key,tag_value,new_tags,"\n")
                                logger.info("    tag modified\n\n")
                                logger.info("new_tags") and open("output.txt", "a").write("new_tags")

accounts_id = []
regions = ["us-west-2", "us-west-1", "us-east-2", "us-east-1"]
session = boto3.Session(region_name="us-east-2")
organizations_client = session.client("organizations")

# to be added
organization_parent_id = 'r-18jb'
response = organizations_client.list_organizational_units_for_parent(ParentId=organization_parent_id)
organizations = response['OrganizationalUnits']

# logger setup
log_filename = "output.log"
logger = logger_setup.setup_logger(log_filename)

if len(organizations) > 0:
    for organization in organizations:
        ou_id = organization['Id']
        logger.info("Processing Organization: %s", ou_id)

        response = organizations_client.list_accounts_for_parent(ParentId=ou_id)
        accounts = response['Accounts']

        # Describe the OU to get its details
        ou_response = organizations_client.describe_organizational_unit(OrganizationalUnitId=ou_id)

        # Extract the master account ID from the response
        master_account_id = ou_response['OrganizationalUnit']['MasterAccountId']
        process_account_tags(master_account_id, accounts, session)

response = organizations_client.describe_organization()
organization_details = response["Organization"]

# Retrieve accounts in your AWS organization
response = organizations_client.list_accounts()
accounts = response["Accounts"]
master_account_id = organization_details["MasterAccountId"]
logger.info("Processing Organization %s", organization_details['Id'])
process_account_tags(master_account_id, accounts, session)

