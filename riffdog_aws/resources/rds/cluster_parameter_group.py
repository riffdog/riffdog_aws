"""
This module is for RDS Cluster Parameter Groups
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_rds_cluster_parameter_group")
class AWSRDSClusterParameterGroup(AWSResource):
    _cluster_pgs_in_aws = {}
    _cluster_pgs_in_state = {}

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for RDS resources")

        client = self._get_client("rds", region)

        response = client.describe_db_cluster_parameter_groups()

        for pg in response["DBClusterParameterGroups"]:
            self._cluster_pgs_in_aws[pg["DBClusterParameterGroupName"]] = pg

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            item = FoundItem("aws_rds_cluster_parameter_group", aws_id=instance["attributes"]["cluster_identifier"], state_data=instance)
            self._cluster_pgs_in_state[instance["attributes"]["cluster_identifier"]] = item

    def compare(self, depth):

        for key, val in self._cluster_pgs_in_state.items():
            if key in self._cluster_pgs_in_aws:
                val.real_id = key
                val.real_data = self._cluster_pgs_in_aws[key]

        for key, val in self._cluster_pgs_in_aws.items():
            if key not in self._cluster_pgs_in_state:
                FoundItem("aws_rds_cluster_parameter_group", real_id=key, real_data=val)
