import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_db_instance")
class AWSDBInstance(AWSResource):
    """
    These are a faux thing to Terraform. An aws_rds_cluster_instance is
    just an aws_db_instance that belongs to a Cluster.
    """
    _instances_in_aws = {}
    _instances_in_state = {}

    def fetch_real_regional_resources(self, region):
        logger.info("Looking for RDS resources")

        client = self._get_client("rds", region)

        response = client.describe_db_instances()

        for instance in response["DBInstances"]:
            self._instances_in_aws[instance["DBInstanceIdentifier"]] = instance

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            item = FoundItem("aws_db_instance", terraform_id=instance["attributes"]["id"], state_data=instance)
            self._instances_in_state[instance["attributes"]["id"]] = item

    def compare(self, depth):
        
        for key, val in self._instances_in_state.items():
            if key in self._instances_in_aws:
                val.real_id = key
                val.real_data = self._instances_in_aws[key]

        for key, val in self._instances_in_aws.items():
            if key not in self._instances_in_state:
                item = FoundItem("aws_db_instance", real_id=key, real_data=val)

        
