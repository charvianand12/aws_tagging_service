import boto3


def get_aws_credentials(account_id, role_name):
    sts_client = boto3.client("sts")
    # Assume the specified IAM role in the target AWS account
    response = sts_client.assume_role(
        RoleArn=f"arn:aws:iam::{account_id}:role/{role_name}",
        RoleSessionName="role_session",
    )
    credentials = response["Credentials"]
    access_key = credentials["AccessKeyId"]
    secret_key = credentials["SecretAccessKey"]
    session_token = credentials["SessionToken"]
    return access_key, secret_key, session_token
