"""
This module is for Elastic Load Balancers v2 (alb/nlb) Target Groups.
"""

import logging

from riffdog.data_structures import ReportElement
from riffdog.resource import AWSResource, register, ResourceDirectory

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
            self._tgs_in_state[instance["attributes"]["name"]] = instance

    def compare(self, depth):
        out_report = ReportElement()

        for key, val in self._tgs_in_state.items():
            if key not in self._tgs_in_aws:
                out_report.in_tf_but_not_real.append(key)
            else:
                out_report.matched.append(key)

        for key, val in self._tgs_in_aws.items():
            if key not in self._tgs_in_state:
                print(key)
                out_report.in_real_but_not_tf.append(key)

        return out_report

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
            self._tg_attachments_in_state[instance["attributes"]["target_id"]] = instance

    def compare(self, depth):
        out_report = ReportElement()

        for key, val in self._tg_attachments_in_state.items():
            if key not in self._tg_attachments_in_aws:
                out_report.in_tf_but_not_real.append(key)
            else:
                out_report.matched.append(key)

        for key, val in self._tg_attachments_in_aws.items():
            if key not in self._tg_attachments_in_state:
                out_report.in_real_but_not_tf.append(key)

        return out_report
