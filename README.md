## aws-public-ips
This script will get all linked accounts in an AWS Organization and will look
for ENIs with public IP addresses.  It loops through each linked account and each
region and will export a list of public IPs to a CSV file.

#### A Word of Caution
Please note that I cannot commit to supporting the provided code. This is meant to be used as an example and requires further testing to be used in a production environment.

#### Prerequisites
1. You must have python3 and boto3 installed
1. You must have a user with sufficient IAM permissions in the AWS master account
in order to get a list of all linked accounts.
1. You must have a role that can be assumed in each linked account that has sufficient
IAM permissions to describe network interfaces (ENIs).
1. You must have a lot of time to spare (this script will take a long time to run depending on how many linked accounts are in your Organization).

#### Instructions
1. Clone this repo to your local machine
```
git clone git@github.com:dewjam/aws-public-ips.git
```
1. Run the script
```
python3 aws-public-ips.py --role-name <role_name> ('OrganizationAccountAccessRole')
```
1. Review the CSV file.  The file will be saved to the current directory with name `ips.csv`.
