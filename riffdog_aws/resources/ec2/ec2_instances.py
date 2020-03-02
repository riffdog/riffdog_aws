"""
This module is for EC2 instance processing - terraform & boto and comparison.
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_instance")
class AWSInstance(AWSResource):
    resource_type = "aws_instance"

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s resources..." % self.resource_type)
        client = self._get_client('ec2', region)
        rd = ResourceDirectory()

        instances = client.describe_instances()

        if instances:
            for reservation in instances["Reservations"]:
                for instance in reservation["Instances"]:
                    try:
                        item = rd.get_item(predicted_id=instance["InstanceId"])
                        item.real_id = instance["InstanceId"]
                        item.real_data = instance
                    except KeyError:
                        FoundItem(self.resource_type, real_id=instance["InstanceId"], real_data=instance)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource['instances']:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, depth):
        pass


def _get_VPC_name(client, vpc_id, vpcs=None):
    if vpcs is None:
        vpcs = client.describe_vpcs()

    for vpc_data in vpcs["Vpcs"]:
        if vpc_data["VpcId"] == vpc_id:
            if "Tags" in vpc_data:
                vpc_tags = vpc_data["Tags"]
                for vpc_tag in vpc_tags:
                    if vpc_tag["Key"] == "Name":
                        return vpc_tag["Value"]
    return ''
