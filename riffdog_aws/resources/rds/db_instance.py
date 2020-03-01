import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_db_instance")
class AWSDBInstance(AWSResource):
    resource_type = "aws_db_instance"

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s resources..." % self.resource_type)
        client = self._get_client("rds", region)
        rd = ResourceDirectory()

        response = client.describe_db_instances()

        for instance in response["DBInstances"]:
            try:
                item = rd.get_item(predicted_id=instance["DBInstanceIdentifier"])
                item.real_id = instance["DBInstanceIdentifier"]
                item.real_data = instance
            except KeyError:
                item = FoundItem(self.resource_type, real_id=instance["DBInstanceIdentifier"], real_data=instance)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, item, depth):
        # Presumably we could do some kind of 'map table' to loop over justdefining both sides here?
        if not item.state_dta['attributes']['instance_class'] == item.real_data['DBInstanceClass']:
            item.dirty = True
