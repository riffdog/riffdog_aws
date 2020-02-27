import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_db_instance")
class AWSDBInstance(AWSResource):
    """
    These are a faux thing to Terraform. An aws_rds_cluster_instance is
    just an aws_db_instance that belongs to a Cluster.
    """

    def fetch_real_regional_resources(self, region):
        logger.info("Looking for RDS db resources")

        client = self._get_client("rds", region)

        response = client.describe_db_instances()
        rd = ResourceDirectory()

        for instance in response["DBInstances"]:
            try:
                item = rd.get_item(predicted_id=instance["DBInstanceIdentifier"])
                item.real_id = instance["DBInstanceIdentifier"]
                item.real_data = instance
            except KeyError:
                # that item isnt predicted!
                item = FoundItem("aws_db_instance", real_id=instance["DBInstanceIdentifier"], real_data=instance)

    def process_state_resource(self, state_resource, state_filename):
        print("Found a resource of aws_db_instance!")
        for instance in state_resource["instances"]:
            #item = FoundItem("aws_db_instance", terraform_id=instance["attributes"]["resource_id"], predicted_id=instance["attributes"]["id"], state_data=instance)
            item = FoundItem("aws_db_instance", terraform_id=instance["attributes"]["id"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, item, depth):
        # This is now called multiple times

        #print("------------------")

        #print(item.real_data)
        #print("$$$$$$$$$$$$$$$$$$")
        #print(item.state_data)

        #print("------------------")
        
        # Presumably we could do some kind of 'map table' to loop over justdefining both sides here?
        if not item.state_dta['attributes']['instance_class'] == item.real_data['DBInstanceClass']:
            item.dirty = True
        
        
