"""
This module is for RDS Clusters
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_rds_cluster")
class AWSRDSCluster(AWSResource):
    _clusters_in_aws = {}
    _clusters_in_state = {}

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for RDS resources")

        client = self._get_client("rds", region)

        response = client.describe_db_clusters()

        for cluster in response["DBClusters"]:
            self._clusters_in_aws[cluster["DBClusterIdentifier"]] = cluster

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            item = FoundItem("aws_rds_cluster", terraform_id=instance["attributes"]["cluster_identifier"], state_data = instance)

    def compare(self, depth):

        for key, val in self._clusters_in_state.items():
            if key in self._clusters_in_aws:
                val.real_id = key
                val.real_data = self._clusters_in_aws[key]

        for key, val in self._clusters_in_aws.items():
            if key not in self._clusters_in_state:
                item = FoundItem("aws_rds_cluster", real_id=key, real_data=val)



@register("aws_rds_cluster_instance")
class AWSRDSClusterInstance(AWSResource):
    """
    These are a faux thing to Terraform. An aws_rds_cluster_instance is
    just an aws_db_instance that belongs to a Cluster.
    """
    _instances_in_aws = {}
    _instances_in_state = {}

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for RDS instance resources")

        client = self._get_client("rds", region)

        response = client.describe_db_instances()

        for instance in response["DBInstances"]:
            if "DBClusterIdentifier" in instance:
                if instance["DBClusterIdentifier"]:
                    self._instances_in_aws[instance["DBInstanceIdentifier"]] = instance

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            item = FoundItem("aws_rds_cluster_instance", terraform_id=instance["attributes"]["identifier"], state_data=instance)
            self._instances_in_state[instance["attributes"]["identifier"]] = item

    def compare(self, depth):

        for key, val in self._instances_in_state.items():
            if key in self._instances_in_aws:
                val.real_id=key

        for key, val in self._instances_in_aws.items():
            if key not in self._instances_in_state:
                item = FoundItem("aws_rds_cluster_instance", real_id=key, real_data=val)
