# import boto3
# import re
# from spelling_check import check_spelling


# def list_resources_in_region(region, account_id):
#     ec2_client = boto3.client("ec2", region_name=region)
#     instance_id_list = []
#     instances = ec2_client.describe_instances()

#     for reservation in instances["Reservations"]:
#         for instance in reservation["Instances"]:
#             print(
#                 f"Account: {account_id}, Region: {region}, Instance ID: {instance['InstanceId']}"
#             )
#             instance_id_list.append(instance["InstanceId"])
#             return instance_id_list


# def fix_ec2_tags(regions, account_id):
#     for region in regions:
#         session = boto3.Session(region_name=region)
#         print(f"  Processing Region: {region}")
#         instance_id_list = list_resources_in_region(region, account_id)
#         if instance_id_list is not None:
#             for instance_id in instance_id_list:
#                 print(f"  Processing Instance: {instance_id}")

#                 key_pattern = r"^trhc:[a-z][a-z0-9:/.-]*$"
#                 # key_pattern = r'^[a-z][a-z0-9:/.-]*$'
#                 sp_chars = ["__", " ", "&", "_"]
#                 ec2_client = session.client("ec2", region_name=region)
#                 # response = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [instance_id]}])
#                 response = ec2_client.describe_tags(
#                     Filters=[{"Name": "resource-id", "Values": [instance_id]}]
#                 )
#                 # print(response)
#                 tags = response["Tags"]
#                 if tags is not None:
#                     for tag in tags:
#                         # print(tag['Key'])
#                         if re.match(key_pattern, tag["Key"]) and " " not in tag["Key"]:
#                             # print("pattern matched")
#                             fetched_key = tag["Key"]
#                         else:
#                             # print("pattern not matched")
#                             fetched_key = tag["Key"].strip()
#                             if fetched_key.startswith(
#                                 "trhc:"
#                             ) or fetched_key.startswith("accenture"):
#                                 fetched_key = tag["Key"].lower()
#                             else:
#                                 fetched_key = "trhc:" + fetched_key.lower()

#                             for sp_char in sp_chars:
#                                 if sp_char in fetched_key:
#                                     if fetched_key.startswith(
#                                         sp_char
#                                     ) or fetched_key.endswith(sp_char):
#                                         fetched_key = fetched_key.replace(sp_char, "")
#                                     else:
#                                         fetched_key = fetched_key.replace(sp_char, "-")

#                         # print(tag['Key'])

#                         correct_key = check_spelling(fetched_key)
#                         # tag['Key'] = correct_key

#                         if correct_key != tag["Key"]:
#                             ec2_client.delete_tags(
#                                 Resources=[instance_id], Tags=[{"Key": tag["Key"]}]
#                             )
#                             ec2_client.create_tags(
#                                 Resources=[instance_id],
#                                 Tags=[{"Key": correct_key, "Value": tag["Value"]}],
#                             )

#                             print("modified")
#                         print(
#                             tag["Key"],
#                             "...................................",
#                             fetched_key,
#                         )
#                         print("\n\n")
