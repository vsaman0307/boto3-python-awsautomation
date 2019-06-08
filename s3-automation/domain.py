#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Classes for Route53 domains."""

import uuid
import util

class DomainManager:
    """Manage a Route53 Domain."""

    def __init__(self, session):
        """Create DomainManager object."""

        self.session = session
        self.client = self.session.client('route53')

    def find_hosted_zone(self, domain_name):
        paginator = self.client.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone
        return None


    def create_hosted_zone(self, domain_name):
        """Created a hosted zone for the domain."""
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'

        return self.client.create_hosted_zone(
                           Name=zone_name,
                           CallerReference = str(uuid.uuid4())
                           )

    def create_s3_domain_record(self, zone, domain, endpoint):
        """Creating Alias record for the bucket in the hosted zone."""

        return self.client.change_resource_record_sets(
                     HostedZoneId = zone['Id'],
                     ChangeBatch = {
                         'Comment' : 'Created by s3-script.py',
                         'Changes' : [ {
                             'Action' : 'UPSERT',
                             'ResourceRecordSet' : {
                                'Name' : domain,
                                'Type' : 'A',
                                'AliasTarget' : {
                                    'HostedZoneId' : endpoint.zone,
                                    'DNSName' : endpoint.host,
                                    'EvaluateTargetHealth' : False
                                }
                             }
                         }]
                     }
        )


    def create_cf_domain_record(self, zone, domain, cf_domain):
    """Creating Alias record for the bucket in the hosted zone."""

    return self.client.change_resource_record_sets(
                 HostedZoneId = zone['Id'],
                 ChangeBatch = {
                     'Comment' : 'Created by s3-script.py',
                     'Changes' : [ {
                         'Action' : 'UPSERT',
                         'ResourceRecordSet' : {
                            'Name' : domain,
                            'Type' : 'A',
                            'AliasTarget' : {
                                'HostedZoneId' : 'Z2FDTNDATAQYW2',
                                'DNSName' : cf_domain,
                                'EvaluateTargetHealth' : False
                            }
                         }
                     }]
                 }
    )
