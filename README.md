# boto3-python-awsautomation

Scripts to manage Ec2 instances and snapshots.
Scripts to manage S3 buckets, website hosting, and configuring DNS.

# About

These are scripts to automate EC2 service - listing instances by filters, stopping and starting EC2 instances, Listing EC2 volumes, Listing snapshots, and the creation of snapshots for volumes attached to EC2 instances

S3 service - Listing buckets, listing objects within a bucket, Configuring bucket for website hosting, syncing website files to S3 bucket, Configuring hosted zone and domain A record in Route53, and configuring Cloudfront with SSL.

# Configuration Setup - Configure aws profile with key and secret access key. Grant necessary permissions to the role and attach to the profile. (Ec2 full access and S3 full access)

aws configure --profile profile_name


# Running ec2-script.py

# for EC2 automation tasks such as creating, starting and stopping instances, listing instances, volumes and snapshots, and creating snapshots

pipenv run python ec2-scripts/ec2list.py <command> <subcommand> <--project=PROJECT>
command is instances,volumes and snapshots
#For instances command, below are subcommands:
instances --help
#List EC2 instances filtered by Tag
instances list --project(option - Ex: project=Dev)

#Stop Instances filtered by tag
instances list --project(option - Ex: project=Dev)

#Start Instances filtered by tag
instances start --project(option - Ex: project=Dev)

#Create snapshot for Instances by tags
instances snapshot --project(option - Ex: project=prod)

#For volumes command, below are subcommands:
volumes list

#For snapshot command, below are subcommands:
snapshot --project --all (project and all are options, project used to filter by tag and all is True of False to list all or latest snapshot)

sub-command is list, start or stop (depending on command)
project is optional ( project is tag on ec2 instances)

# Running s3-script.py
# for S3 to perform various S3 automation tasks

Commands with profile sent as option
python s3-script.py --help

#List all buckets
#List all buckets
--profile=profilename list-buckets

#List all objects in a bucket
--profile=profilename list-bucket-objects <name of bucket>

#Configure a bucket with policy and website hosting
--profile=profilename setup-bucket <name of bucket>

#Sync directory of website files to a bucket
--profile=profilename sync <directory tree> <bucket>

#Set up hosted zone and a-record for the bucket
--profile=profilename setup-domain <domain name>

#Set up cdn with SSL for website hosting
--profile=profilename setup-cdn <domain> <bucket>

Modules used:
#bucket.py - Defines a class BucketManager to perform various tasks for bucket-methods are get region for bucket, get bucket url, get buckets, get all objects for bucket, set bucket policy, create bucket, configure bucket for website hosting, syncing files to a buckets

#domain.py - Defines a class DomainManager to manage Route53 DomainName - methods are find hosted zone, create hosted zone, create s3 domain record in Route53, create cloudfront domain record in Route53

#certificate.py - Defines a class CertificateManager to manage certificates in ACM - methods are to find a matching certificate with domain name.

#distribution.py - Defines class to manage Cloudfront distribution - methods are find mathcing distribution and create a cloudfront distribution.

#util.py - Defines endpoints for various AWS regions. Region name, Host and zone for the region of S3 bucket. 
