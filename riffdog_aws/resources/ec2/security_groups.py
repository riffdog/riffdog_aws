"""
This module is for EC2 instance processing - terraform & boto and comparison.
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_security_group")
class AWSSecurityGroup(AWSResource):
    _groups_in_aws = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._groups_in_aws = []

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s resources..." % self.resource_type)
        client = self._get_client('ec2', region)
        rd = ResourceDirectory()

        response = client.describe_security_groups()

        for security_group in response["SecurityGroups"]:
            try:
                item = rd.get_item(predicted_id=security_group["GroupId"])
                item.real_id = security_group["GroupId"]
                item.real_data = security_group
            except KeyError:
                item = FoundItem(self.resource_type, real_id=security_group["GroupId"], real_data=security_group)
            finally:
                self._groups_in_aws.append(item)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource['instances']:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["id"], state_data=instance)

    def compare(self, item, depth):
        pass

    @property
    def groups_in_aws(self):
        return self._groups_in_aws


@register("aws_security_group_rule")
class AWSSecurityGroupRule(AWSResource):

    def _generate_unique_id(self, sg_id, protocol, from_port=None, to_port=None):
        """
        Security Group rules aren't a /thing/ on their own in AWS, they
        only exist in the same context as Security Group. As a result
        there isn't an arn/id that we can use, so we generate out own
        using the unique information per rule.
        """
        if not from_port and not to_port:
            pattern = "sgrule:{sg_id}:self/{protocol}"
        else:
            pattern = "sgrule:{sg_id}:{from_port}-{to_port}/{protocol}"
        return pattern.format(
            sg_id=sg_id,
            from_port=from_port,
            to_port=to_port,
            protocol=protocol)

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s resources..." % self.resource_type)
        rd = ResourceDirectory()

        security_groups = ResourceDirectory().lookup("aws_security_group").groups_in_aws

        for security_group in security_groups:
            if "IpPermissions" in security_group.real_data:
                for permission in security_group.real_data["IpPermissions"]:
                    try:
                        uid = self._generate_unique_id(security_group.real_data["GroupId"], permission["IpProtocol"], permission["FromPort"], permission["ToPort"])
                    except KeyError:
                        uid = self._generate_unique_id(security_group.real_data["GroupId"], permission["IpProtocol"])

                    try:
                        item = rd.get_item(predicted_id=uid)
                        item.real_id = uid
                        item.real_data = permission
                    except KeyError:
                        FoundItem(self.resource_type, real_id=uid, real_data=permission)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource['instances']:
            uid = self._generate_unique_id(
                sg_id=instance["attributes"]["security_group_id"],
                protocol=instance["attributes"]["protocol"],
                from_port=instance["attributes"]["from_port"],
                to_port=instance["attributes"]["to_port"])
            print(uid)
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=uid, state_data=instance)

    def compare(self, item, depth):
        pass
