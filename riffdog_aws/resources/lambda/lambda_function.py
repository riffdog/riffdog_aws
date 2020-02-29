import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_lambda_function")
class AWSLambdaFunction(AWSResource):
    """
    This is aws Lambda functions
    """

    def fetch_real_regional_resources(self, region):
        logger.info("Looking for lambda function resources")

        client = self._get_client("lambda", region)

        response = client.list_functions()
        rd = ResourceDirectory()

        for instance in response["Functions"]:
            try:
                item = rd.get_item(predicted_id=instance["FunctionName"])
                item.real_id = instance["FunctionName"]
                item.real_data = instance
            except KeyError:
                # that item isnt predicted!
                item = FoundItem("aws_lambda_function", real_id=instance["FunctionName"], real_data=instance)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of aws_lambda function!")
        # print(state_resource)
        for instance in state_resource["instances"]:
            #item = FoundItem("aws_db_instance", terraform_id=instance["attributes"]["resource_id"], predicted_id=instance["attributes"]["id"], state_data=instance)
            item = FoundItem("aws_lambda_function", terraform_id=state_resource["name"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, item, depth):
        # This is now called multiple times

        #print("------------------")

        #print(item.real_data)
        #print("$$$$$$$$$$$$$$$$$$")
        #print(item.state_data)

        #print("------------------")
        
        # Presumably we could do some kind of 'map table' to loop over justdefining both sides here?
        # if not item.state_data['attributes']['instance_class'] == item.real_data['DBInstanceClass']:
        #     item.dirty = True

        pass
        
        
