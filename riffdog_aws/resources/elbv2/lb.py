"""
This module is for Elastic Load Balancers v2 (alb/nlb).
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSRegionalResource


logger = logging.getLogger(__name__)


@register("aws_lb", "aws_alb")
class AWSLB(AWSRegionalResource):
    _lbs_in_aws = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lbs_in_aws = []

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s/aws_alb resources" % self.resource_type)
        client = self._get_client("elbv2", region)
        rd = ResourceDirectory()

        response = client.describe_load_balancers()

        if "LoadBalancers" in response:
            for lb in response["LoadBalancers"]:
                try:
                    item = rd.get_item(predicted_id=lb["LoadBalancerName"])
                    item.real_id = lb["LoadBalancerName"]
                    item.real_data = lb
                except KeyError:
                    item = FoundItem(self.resource_type, real_id=lb["LoadBalancerName"], real_data=lb)
                finally:
                    item = self._lbs_in_aws.append(item)

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["name"], state_data=instance) 

    def compare(self, depth):
        pass
        # for key, val in self._lbs_in_state.items():
        #     if key in self._lbs_in_aws:
        #         val.real_id = key
        #         val.real_data = self._lbs_in_aws[key]

        # for key, val in self._lbs_in_aws.items():
        #     if key not in self._lbs_in_state:
        #         # FIXME: need to know if its a lb or alb
        #         item = FoundItem("aws_lb", real_id=key, real_data=val)

    @property
    def load_balancers_in_aws(self):
        return self._lbs_in_aws
