#!/usr/bin/python
# -*- coding: utf-8 -*-

"""S3 various automation tasks and deploying website within AWS.

 Create bucket in AWS
 Setup Bucket for static website hosting
 Deploy local files to bucket for Website
 List all objects in a buckets"
 Configure DNS with AWS Route53
 Configure Content Delivery Network and SSL with AWS Certificate Manager"""


import boto3
import click
from pathlib import Path
from bucket import BucketManager
from domain import DomainManager
from certificate import CertificateManager
from cdn import DistributionManager
import util

session = None
bucket_manager = None
domain_manager = None
certificate_manager = None
ist_manager = None

@click.group()
@click.option('--profile', default=None, help="Enter a profile")
def cli(profile):
    """This script executes various commands for S3"""

    global session, bucket_manager, domain_manager, certificate_manager, dist_manager
    session_cfg = {}
    if(profile):
        session_cfg['profile_name'] = profile

    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)
    domain_manager = DomainManager(session)
    certificate_manager = CertificateManager(session)
    dist_manager = DistributionManager(session)


@cli.command('list-buckets')
def list_buckets():
    "List all S3 Buckets."

    for bucket in bucket_manager.all_buckets():
        print(bucket)

    return


@cli.command('list-bucket-objects')
@click.argument('bucketname')
def list_bucket_objects(bucketname):
    "Listing all objects in buckets"

    for obj in bucket_manager.all_objects(bucketname):
        print(obj)

    return


@cli.command('setup-bucket')
@click.argument('bucketname')
def setup_bucket(bucketname):
    """Configuring new bucket."""

    s3_bucket = bucket_manager.init_bucket(bucketname)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)

    return


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    "Sync contents of pathname to Bucket"

    bucket_manager.sync(pathname, bucket)
    print(bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucket)))


@cli.command('setup-domain')
@click.argument('domain')
def setup_domain(domain):
	"""Configure Domain to point to bucket"""
	bucket = domain
	zone = domain_manager.find_hosted_zone(domain) or domain_manager.create_hosted_zone(domain)
	endpoint = util.get_endpoint(bucket_manager.get_region_name(bucket_manager.s3.Bucket(bucket)))
	a_record = domain_manager.create_s3_domain_record(zone, domain, endpoint)

@cli.command('find-cert')
@click.argument('domain')
def find_cert(domain):
	print(certificate_manager.find_matching_cert(domain))


@cli.command('setup-cdn')
@click.argument('domain')
@click.argument('bucket')
def setup_cdn(domain, bucket):
    dist = dist_manager.find_matching_dist(domain)

    if not dist:
        cert = certificate_manager.find_matching_cert(domain)
        if not cert:
            print("No certificate found for the domain")
            return

        dist = dist_manager.create_dist(domain, cert)
        print("Waiting for distribution deployment.")
        dist_manager.await_deploy(dist)

    zone = domain_manager.find_hosted_zone(domain) or domain_manager.create_hosted_zone(domain)
    a_record = domain_manager.create_cf_domain_record(zone, domain, dist['DomainName'])
    print("Domain configured: https://{}".format(domain))

    return

if __name__ == '__main__':
    cli()
