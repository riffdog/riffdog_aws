"""
This module is for the Subnet Reosurce
"""
import logging

from riffdog.data_structures import ReportElement
from riffdog.resource import AWSResource, register

logger = logging.getLogger(__name__)


@register("aws_subnet")
class AWSSubnet(AWSResource):
    _subnets_in_aws = {}
    _subnets_in_state = {}

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for aws_subnet resources")

        ec2 = self._get_resource('ec2', region)

        for subnet in ec2.subnets.filter():
            self._subnets_in_aws[subnet.id] = subnet

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            self._subnets_in_state[instance["attributes"]["id"]] = "instance"

    def compare(self, depth):
        out_report = ReportElement()

        for key, val in self._subnets_in_state.items():
            if key not in self._subnets_in_aws:
                out_report.in_tf_but_not_real.append(key)
            else:
                out_report.matched.append(key)

        for key, val in self._subnets_in_aws.items():
            if key not in self._subnets_in_state:
                out_report.in_real_but_not_tf.append(key)

        return out_report
