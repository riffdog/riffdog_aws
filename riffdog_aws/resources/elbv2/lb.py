"""
This module is for Elastic Load Balancers v2 (alb/nlb).
"""

import logging

from riffdog.data_structures import ReportElement
from riffdog.resource import AWSResource, register

logger = logging.getLogger(__name__)


@register("aws_lb", "aws_alb")
class AWSLB(AWSResource):
    _lbs_in_aws = {}
    _lbs_in_state = {}

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for aws_lb/aws_alb resources")

        client = self._get_client("elbv2", region)

        response = client.describe_load_balancers()

        if "LoadBalancers" in response:
            for lb in response["LoadBalancers"]:
                self._lbs_in_aws[lb["LoadBalancerName"]] = lb

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            self._lbs_in_state[instance["attributes"]["name"]] = instance

    def compare(self, depth):
        out_report = ReportElement()

        for key, val in self._lbs_in_state.items():
            if key not in self._lbs_in_aws:
                out_report.in_tf_but_not_real.append(key)
            else:
                out_report.matched.append(key)

        for key, val in self._lbs_in_aws.items():
            if key not in self._lbs_in_state:
                out_report.in_real_but_not_tf.append(key)

        return out_report

    @property
    def load_balancers_in_aws(self):
        return self._lbs_in_aws
