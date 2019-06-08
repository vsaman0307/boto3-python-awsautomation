"""Class for Cloud Front Distribution."""

import uuid

class DistributionManager:

    def __init__(self, session):
        self.session = session
        self.client = self.session.client('cloudfront')


    def find_matching_dist(self, domain_name):
        """Find a distribution matching domain name."""

        paginator = self.client.get_paginator('list_distributions')
        for page in paginator.paginate():
            print(page)
            for dist in page['DistributionList']['Items']:
                for alias in dist['Aliases']['Items']:
                    if alias == domain_name:
                        return dist
        return None


    def create_dist(self, domain_name, cert):
        """Create a distribution for domain name and cert."""

        origin_id = 'S3-' + domain_name
        result = self.client.create_distribution(
                           DistributionConfig={
                             'CallerReference' : str(uuid.uuid4()),
                             'Aliases' : {
                                'Quantity' : 1,
                                'Items' : [domain_name]
                             },
                             'DefaultRootObject' : 'index.html',
                             'Comment' : 'Created by Automation script',
                             'Enabled' : True,
                             'Origins' : {
                                   'Quantity' : 1,
                                   'Items' : [ {
                                      'Id' : origin_id,
                                      'DomainName' : '{}.s3.amazonaws.com'.format(domain_name),
                                      'S3OriginConfig' : {
                                          'OriginAccessIdentity' : ''
                                      }
                                   }]
                             },
                             'DefaultCacheBehavior' : {
                                  'TargetOriginId' : origin_id,
                                  'ViewerProtocolPolicy' : 'redirect-to-https',
                                  'TrustedSigners' : { 'Quantity' : 0,
                                                        'Enabled' : False},
                                  'ForwardedValues' : { 'Cookies' : {'Forward' : 'all'},
                                                      'Headers' : {'Quantity' : 0},
                                                      'QueryString' : False,
                                                      'QueryStringCacheKeys' : {'Quantity' : 0}
                                                      },
                                  'DefaultTTL' :  86400,
                                  'MinTTL' : 3600
                             },
                             'ViewerCertificate':{
                                  'ACMCertificateArn' : cert['CertificateArn'],
                                  'SSLSupportMethod' : 'sni-only',
                                  'MinimumProtocolVersion' : 'TLSv1.1_2016'
                             }
                           }
                )

        return result['Distribution']

    def await_deploy(self, dist):
        """Wait for distribution to be deployed"""

        waiter = self.client.get_waiter('distribution_deployed')
        waiter.wait(Id=dist['Id'], WaiterConfig={
                                     'Delay' : 30,
                                     'MaxAttempts' : 50})
