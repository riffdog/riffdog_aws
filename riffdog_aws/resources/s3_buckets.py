"""
This module is for S3 bucket processing - terraform & boto and comparison.
"""

import logging
from riffdog.data_structures import FoundItem
from riffdog.resource import register

from ..aws_resource import AWSResource 

logger = logging.getLogger(__name__)

@register("aws_s3_bucket")
class S3Buckets(AWSResource):
    _states_found = {}
    _real_buckets = {}

    regional_resource = False

    def fetch_real_global_resources(self):
        logging.info("Looking for s3 resources")

        client = self._get_client('s3', None)

        response = client.list_buckets()

        for bucket in response['Buckets']:
            self._real_buckets[bucket['Name']] = bucket

    def process_state_resource(self, state_resource, state_filename):
        f = FoundItem("aws_s3_bucket", terraform_id=state_resource['name'], state_data=state_resource)

        self._states_found[state_resource['name']] = f

    def compare(self, depth):
        # this function should be called once, take the local data and return
        # an array of result elements.
        
        for key, item in self._states_found.items():

            real_bucket_name = item.state_data['instances'][0]['attributes']['bucket']
            
            #except (KeyError, IndexError):
            #    real_bucket_name = key

            if real_bucket_name in self._real_buckets:
                item.real_id = real_bucket_name

        for key, val in self._real_buckets.items():
            if key not in self._states_found:
                FoundItem("aws_s3_bucket", real_id=key)

