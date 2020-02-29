"""
This module is for Elastic Load Balancers v2 (alb/nlb).
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register

from ...aws_resource import AWSResource

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
            # FIXME: how do we know its a lb or an alb?
            item = FoundItem("aws_lb", terraform_id=instance["attributes"]["name"], state_data=state_resource) 
            self._lbs_in_state[instance["attributes"]["name"]] = item

    def compare(self, depth):

        for key, val in self._lbs_in_state.items():
            if key in self._lbs_in_aws:
                val.real_id = key
                val.real_data = self._lbs_in_aws[key]

        for key, val in self._lbs_in_aws.items():
            if key not in self._lbs_in_state:
                # FIXME: need to know if its a lb or alb
                item = FoundItem("aws_lb", real_id=key, real_data=val)

    @property
    def load_balancers_in_aws(self):
        return self._lbs_in_aws
