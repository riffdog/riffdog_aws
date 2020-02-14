"""
This module is for the VPC Reosurce
"""
import boto3
import logging

from riffdog.data_structures import ReportElement
from riffdog.resource import AWSResource, register

logger = logging.getLogger(__name__)


@register("aws_vpc")
class AWSVPC(AWSResource):
    _vpcs_in_aws = {}
    _vpcs_in_state = {}

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for aws_vpc resources")

        ec2 = boto3.resource('ec2', region_name=region)

        for vpc in ec2.vpcs.filter():
            self._vpcs_in_aws[vpc.id] = vpc

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            self._vpcs_in_state[instance["attributes"]["id"]] = instance

    def compare(self, depth):
        out_report = ReportElement()

        for key, val in self._vpcs_in_state.items():
            if key not in self._vpcs_in_aws:
                out_report.in_tf_but_not_real.append(key)
            else:
                out_report.matched.append(key)

        for key, val in self._vpcs_in_aws.items():
            if key not in self._vpcs_in_state:
                out_report.in_real_but_not_tf.append(key)

        return out_report
