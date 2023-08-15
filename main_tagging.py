import boto3
from credentials import get_aws_credentials
from dotenv import load_dotenv
from validations import validate_tag_key, validate_tag_value

load_dotenv()


accounts_id = []
regions = ["us-west-2", "us-west-1", "us-east-2", "us-east-1"]
session = boto3.Session(region_name="us-east-2")
organizations_client = session.client("organizations")
response = organizations_client.describe_organization()
organization_details = response["Organization"]

# Retrieve accounts in your AWS organization
response = organizations_client.list_accounts()
accounts = response["Accounts"]
master_account_id = organization_details["MasterAccountId"]


# Iterate through each account
for account in accounts:
    account_id = account["Id"]
    role_name = "admin_role"  # replace "admin_role" with your role_name
    print("\nProcessing account:__________", account_id, "\n")
    if len(accounts_id) == 0 or (len(accounts_id) > 0 and (account_id in accounts_id)):
        if account_id != master_account_id:
            access_key, secret_key, session_token = get_aws_credentials(
                account_id, role_name
            )

        # Iterate through each region
        for region in regions:
            print("Processing region     ", region)
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
                # PaginationToken='string',
                TagFilters=[],
                # ResourcesPerPage=3,
                # TagsPerPage=3,
                # ResourceTypeFilters=[
                #     resource_type,
                # ],
                IncludeComplianceDetails=True,
                ExcludeCompliantResources=False,
                # ResourceARNList=[
                #     'ec2','rds','s3'
                # ]
            )
            resources = response["ResourceTagMappingList"]
            for resource in resources:
                resource_arn = resource["ResourceARN"]
                resource_tags = resource["Tags"]
                print(resource_arn)
                for resource_tag in resource_tags:
                    print("Processing resource     ", resource)
                    tag_key = resource_tag["Key"]
                    tag_value = resource_tag["Value"]
                    correct_key = validate_tag_key(tag_key)
                    correct_value = tag_value
                    new_tags = {correct_key: correct_value}
                    print("old key : ", tag_key, "\n new tag:", new_tags, "\n\n\n\n")
                    if tag_key != correct_key:
                        response = client.untag_resources(
                            ResourceARNList=[resource_arn],
                            TagKeys=[
                                tag_key,
                            ],
                        )
                        response = client.tag_resources(
                            ResourceARNList=[resource_arn], Tags=new_tags
                        )
