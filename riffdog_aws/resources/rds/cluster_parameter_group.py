"""
This module is for RDS Cluster Parameter Groups
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSRegionalResource

logger = logging.getLogger(__name__)


@register("aws_rds_cluster_parameter_group")
class AWSRDSClusterParameterGroup(AWSRegionalResource):
    resource_type = "aws_rds_cluster_parameter_group"

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s resources..." % self.resource_type)
        client = self._get_client("rds", region)
        rd = ResourceDirectory()

        response = client.describe_db_cluster_parameter_groups()

        for pg in response["DBClusterParameterGroups"]:
            try:
                item = rd.get_item(predicted_id=pg["DBClusterParameterGroupName"])
                item.real_id = pg["DBClusterParameterGroupName"]
                item.real_data = pg
            except KeyError:
                FoundItem(self.resource_type, real_id=pg["DBClusterParameterGroupName"], real_data=pg)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, depth):
        pass
