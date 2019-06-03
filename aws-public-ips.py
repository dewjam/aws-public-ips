import boto3
import csv
import os
import argparse


# Parse flags
parser = argparse.ArgumentParser(description='Collects public IPs from AWS accounts .')
parser.add_argument('--role-name', metavar='-r', type=str, help='AWS IAM role to assume in Linked accounts.')
args = parser.parse_args()

# Set the role name you intend to use across linked accounts
# Usually 'OrganizationAccountAccessRole'
role_name = args.role_name

# CSV File path
csvFilePath = './ips.csv'

# Initialize the ipList variable as an array
ipList = []

# Get all accounts from the Organization API
def getAccounts():
    org = boto3.client('organizations')
    accounts = []
    for i in org.list_accounts()['Accounts']:
        if i['Status'] == 'ACTIVE':
            accounts.append(i['Id'])
    return accounts

# List all regions for which a service is available
def getRegions(service):
    return boto3.session.Session().get_available_regions(service)

# Construct the role ARN using the account number and role name
def getRoleARN(account):
    return 'arn:aws:iam::' + account + ':role/' + role_name

# Assume role to get credentials
def assumeRole(account):
    client = boto3.client('sts').assume_role(RoleArn=getRoleARN(account), RoleSessionName='ipListSession')
    return client['Credentials']

# Get all ENIs from the account and append them to the ipList array
def getEC2(account, credentials):
    regions = getRegions('ec2')
    # Loop through available regions and get all ENIs
    for r in regions:
        # Here we create a client for the appropriate region and set the Credentials we are using
        ec2_resource=boto3.client(
            'ec2',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=r
            )
        # Here we get the actual ENI details using the client we just created
        interfaces = ec2_resource.describe_network_interfaces()
        # Here we're filtering out ENIs which don't have public IP associated and writing to the ipList array
        for i in interfaces['NetworkInterfaces']:
            if 'Association' in i:
                ipList.append({'accountId': account,
                'region': r,
                'address': i['Association']['PublicIp'],
                'description': i['Description']}
                )

def writeToCSV(ipList):
    with open(csvFilePath, 'w') as csvfile:
        fieldnames = ['accountId', 'region', 'address', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in ipList:
            writer.writerow(i)

# Get all accounts from the Organization API (using local access key/secret key to access the API)
accountList = getAccounts()

# Loop through all accounts and get IPs associated with resources
for i in accountList:
    print("Getting ENIs for account", i)
    # Get temp credentials for the role you are assuming
    credentials = assumeRole(i)
    # Get IPs and append them to the list
    getEC2(i, credentials)

print("Writing CSV file to ./ips.csv")
writeToCSV(ipList)
print("Done")
