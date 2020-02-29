"""
This module is for the VPC Reosurce
"""
import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_vpc")
class AWSVPC(AWSResource):
    resource_type = "aws_vpc"

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s resources..." % self.resource_type)
        ec2 = self._get_resource('ec2', region)
        rd = ResourceDirectory()

        for vpc in ec2.vpcs.filter():
            try:
                item = rd.get_item(predicted_id=vpc.id)
                item.real_id = vpc.id
                item.real_data = vpc
            except KeyError:
                FoundItem(self.resource_type, real_id=vpc.id, real_data=vpc)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=instance["attributes"]["id"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, item, depth):
        pass
