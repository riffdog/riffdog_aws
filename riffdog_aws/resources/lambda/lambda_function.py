import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSRegionalResource

logger = logging.getLogger(__name__)


@register("aws_lambda_function")
class AWSLambdaFunction(AWSRegionalResource):
    """
    This is aws Lambda functions
    """

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s resources..." % self.resource_type)
        client = self._get_client("lambda", region)
        rd = ResourceDirectory()

        response = client.list_functions()

        for instance in response["Functions"]:
            try:
                item = rd.get_item(predicted_id=instance["FunctionName"])
                item.real_id = instance["FunctionName"]
                item.real_data = instance
            except KeyError:
                # that item isnt predicted!
                FoundItem("aws_lambda_function", real_id=instance["FunctionName"], real_data=instance)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem("aws_lambda_function", terraform_id=state_resource["name"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, item, depth):
        pass
