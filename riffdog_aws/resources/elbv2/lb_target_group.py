"""
This module is for Elastic Load Balancers v2 (alb/nlb) Target Groups.
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSRegionalResource

logger = logging.getLogger(__name__)


@register("aws_lb_target_group", "aws_alb_target_group")
class AWSLBTargetGroup(AWSRegionalResource):
    # All aws_alb_* will be stored as aws_lb_*
    _tgs_in_aws = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tgs_in_aws = []

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s/aws_alb_target_group resources..." % self.resource_type)
        client = self._get_client("elbv2", region)
        rd = ResourceDirectory()

        response = client.describe_target_groups()

        if "TargetGroups" in response:
            for tg in response["TargetGroups"]:
                try:
                    item = rd.get_item(predicted_id=tg["TargetGroupName"])
                    item.real_id = tg["TargetGroupName"]
                    item.real_data = tg
                except KeyError:
                    item = FoundItem(self.resource_type, real_id=tg["TargetGroupName"], real_data=tg)
                finally:
                    self._tgs_in_aws.append(item)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem("aws_lb_target_group", terraform_id=state_resource["name"], predicted_id=instance["attributes"]["name"], state_data=instance)

    def compare(self, depth):
        pass

    @property
    def target_groups_in_aws(self):
        return self._tgs_in_aws


@register("aws_lb_target_group_attachment", "aws_alb_target_group_attachment")
class AWSLBTargetGroupAttachment(AWSRegionalResource):
    # All aws_alb_* will be stored as aws_lb_*
    depends_on = ["aws_lb_target_group"]

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s/aws_alb_target_group_attachment resources..." % self.resource_type)
        client = self._get_client("elbv2", region)
        rd = ResourceDirectory()

        target_groups = ResourceDirectory().lookup("aws_lb_target_group").target_groups_in_aws

        for tg in target_groups:
            response = client.describe_target_health(TargetGroupArn=tg.real_data["TargetGroupArn"])
            if "TargetHealthDescriptions" in response:
                for target in response["TargetHealthDescriptions"]:
                    try:
                        item = rd.get_item(predicted_id=target["Target"]["Id"])
                        item.real_id = target["Target"]["Id"]
                        item.real_data = target
                    except KeyError:
                        FoundItem(self.resource_type, real_id=target["Target"]["Id"], real_data=target)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem("aws_lb_target_group_attachment", terraform_id=state_resource["name"], predicted_id=instance["attributes"]["target_id"], state_data=instance)

    def compare(self, depth):
        pass
