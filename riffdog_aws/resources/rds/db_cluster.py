"""
This module is for RDS Clusters
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSRegionalResource

logger = logging.getLogger(__name__)


@register("aws_rds_cluster")
class AWSRDSCluster(AWSRegionalResource):

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s resources..." % self.resource_type)
        client = self._get_client("rds", region)
        rd = ResourceDirectory()

        response = client.describe_db_clusters()

        for cluster in response["DBClusters"]:
            try:
                item = rd.get_item(predicted_id=cluster["DBClusterIdentifier"])
                item.real_id = cluster["DBClusterIdentifier"]
                item.real_data = cluster
            except KeyError:
                FoundItem(self.resource_type, real_id=cluster["DBClusterIdentifier"], real_data=cluster)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, item, depth):
        pass


@register("aws_rds_cluster_instance")
class AWSRDSClusterInstance(AWSRegionalResource):
    """
    These are a faux thing to Terraform. An aws_rds_cluster_instance is
    just an aws_db_instance that belongs to a Cluster.
    """
    resource_type = "aws_rds_cluster_instance"

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s resources..." % self.resource_type)
        client = self._get_client("rds", region)
        rd = ResourceDirectory()

        response = client.describe_db_instances()

        for instance in response["DBInstances"]:
            if "DBClusterIdentifier" in instance:
                if instance["DBClusterIdentifier"]:
                    try:
                        item = rd.get_item(predicted_id=instance["DBInstanceIdentifier"])
                        item.real_id = instance["DBInstanceIdentifier"]
                        item.real_data = instance
                    except KeyError:
                        FoundItem(self.resource_type, real_id=instance["DBInstanceIdentifier"], real_data=instance)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, depth):
        pass
