#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Class for managing S3 buckets."""

from botocore.exceptions import ClientError
import mimetypes
from pathlib import Path
import util


class BucketManager:
    """Manage an S3 Bucket."""


    def __init__(self, session):
        """Create a BucketManager object."""

        self.s3 = session.resource('s3')

    def get_region_name(self, bucket):
        """Obtain bucket's region."""

        bucket_location = self.s3.meta.client.get_bucket_location(Bucket=bucket.name)
        return bucket_location['LocationConstraint'] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Obtain url for bucket."""

        return "http://{}.{}".format(bucket.name, util.get_endpoint(self.get_region_name(bucket)).host)

    def all_buckets(self):
        """Get an Iterator for all buckets."""

        return self.s3.buckets.all()


    def all_objects(self, bucket_name):
        """Get an iterator for all objects in a bucket."""

        return self.s3.Bucket(bucket_name).objects.all()


    def init_bucket(self, bucket_name):
        "Setting up a New Bucket"

        s3_bucket=None

        try:
        	s3_bucket=self.s3.create_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket=self.s3.Bucket(bucket_name)
            else:
                raise e

        return s3_bucket


    def set_policy(self, bucket):
        """Set up policy for bucket"""

        policy="""{
            "Version": "2008-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadForGetBucketObjects",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "*"
                    },
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::%s/*"
                }
            	]
        	}""" % bucket.name

        policy = policy.strip()
        pol = bucket.Policy()
        pol.put(Policy=policy)


    def configure_website(self, bucket):
        """Configuring bucket for website hosting."""

        ws = bucket.Website()
        ws.put(WebsiteConfiguration={
        		'ErrorDocument': {
        			'Key':'error.html'},
        		'IndexDocument': {
        			'Suffix':'index.html'}
        	})


    @staticmethod
    def upload_file(bucket, path, key):
        """Uploading file in a path to a bucket."""

        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        return bucket.upload_file(
						path,
						key,
						ExtraArgs={
							'ContentType':content_type
				    })


    def sync(self, pathname, bucket_name):
        """Syncing directory of files to a bucket."""

        root=Path(pathname).expanduser().resolve()
        s3_bucket=self.s3.Bucket(bucket_name)

        def handle_directory(pathname):
            for p in pathname.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(s3_bucket, str(p), str(p.relative_to(root)))

        handle_directory(root)
