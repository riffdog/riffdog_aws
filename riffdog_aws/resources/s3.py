"""
This module is for S3 bucket processing - terraform & boto and comparison.
"""

import logging
from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ..aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_s3_bucket")
class AWSS3Bucket(AWSResource):
    resource_type = "aws_s3_bucket"
    regional_resource = False

    def fetch_real_global_resources(self):
        logging.info("Looking for %s resources..." % self.resource_type)
        client = self._get_client('s3', None)
        rd = ResourceDirectory()

        response = client.list_buckets()

        for bucket in response['Buckets']:
            try:
                item = rd.get_item(predicted_id=bucket["Name"])
                item.real_id = bucket["Name"]
                item.real_data = bucket
            except KeyError:
                FoundItem(self.resource_type, real_id=bucket["Name"], real_data=bucket)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["bucket"], state_data=instance)

    def compare(self, depth):
        pass
