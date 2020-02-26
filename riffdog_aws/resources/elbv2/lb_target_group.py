"""
This module is for Elastic Load Balancers v2 (alb/nlb) Target Groups.
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_lb_target_group", "aws_alb_target_group")
class AWSLBTargetGroup(AWSResource):
    _tgs_in_aws = {}
    _tgs_in_state = {}

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for aws_lb_target_group/aws_alb_target_group resources")

        client = self._get_client("elbv2", region)

        response = client.describe_target_groups()

        if "TargetGroups" in response:
            for tg in response["TargetGroups"]:
                self._tgs_in_aws[tg["TargetGroupName"]] = tg

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            # FIXME: how to identify which type was matched
            item = FoundItem("aws_lb_target_group", terraform_id=instance["attributes"]["name"], state_data=instance)
            self._tgs_in_state[instance["attributes"]["name"]] = item

    def compare(self, depth):

        for key, val in self._tgs_in_state.items():
            if key in self._tgs_in_aws:
                val.real_id = key
                val.real_data = self._tgs_in_aws[key]

        for key, val in self._tgs_in_aws.items():
            #FIXME: magic string one of two choices
            item = FoundItem("aws_lb_target_group", real_id=key, real_data=val)

    @property
    def target_groups_in_aws(self):
        return self._tgs_in_aws


@register("aws_lb_target_group_attachment", "aws_alb_target_group_attachment")
class AWSLBTargetGroupAttachment(AWSResource):
    _tg_attachments_in_aws = {}
    _tg_attachments_in_state = {}

    depends_on = ["aws_lb_target_group"]

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for aws_lb_target_group_attachment/aws_alb_target_group_attachment resources")

        client = self._get_client("elbv2", region)

        target_groups = ResourceDirectory().lookup("aws_lb_target_group").target_groups_in_aws

        for name, attrs in target_groups.items():
            response = client.describe_target_health(TargetGroupArn=attrs["TargetGroupArn"])
            if "TargetHealthDescriptions" in response:
                for target in response["TargetHealthDescriptions"]:
                    self._tg_attachments_in_aws[target["Target"]["Id"]] = target

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            # FIXME: target group attachment
            item = FoundItem("aws_lb_target_group_attachment", terraform_id=instance["attributes"]["target_id"], state_data=instance)
            self._tg_attachments_in_state[instance["attributes"]["target_id"]] = item

    def compare(self, depth):

        for key, val in self._tg_attachments_in_state.items():
            if key in self._tg_attachments_in_aws:
                val.real_id = key
                val.real_data = self._tg_attachments_in_aws[key]

        for key, val in self._tg_attachments_in_aws.items():
            if key not in self._tg_attachments_in_state:
                item = FoundItem("aws_lb_target_group_attachment", real_id=key, real_data=val)
