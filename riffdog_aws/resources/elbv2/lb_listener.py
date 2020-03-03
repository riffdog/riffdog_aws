"""
This module is for Elastic Load Balancers v2 (alb/nlb).
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import register, ResourceDirectory

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_lb_listener", "aws_alb_listener")
class AWSLBListener(AWSResource):

    _listeners_in_aws = None
    depends_on = ["aws_lb"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._listeners_in_aws = []

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s/aws_alb_listener resources..." % self.resource_type)
        client = self._get_client("elbv2", region)
        rd = ResourceDirectory()

        load_balancers = ResourceDirectory().lookup("aws_lb").load_balancers_in_aws
        for lb in load_balancers:
            response = client.describe_listeners(LoadBalancerArn=lb.real_data["LoadBalancerArn"])
            if "Listeners" in response:
                for listener in response["Listeners"]:
                    try:
                        item = rd.get_item(predicted_id=listener["ListenerArn"])
                        item.real_id = listener["ListenerArn"]
                        item.real_data = listener
                    except KeyError:
                        item = FoundItem(self.resource_type, real_id=listener["ListenerArn"], real_data=listener)
                    finally:
                        self._listeners_in_aws.append(item)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["arn"], state_data=instance)

    def compare(self, depth):
        pass

    @property
    def listeners_in_aws(self):
        return self._listeners_in_aws


@register("aws_lb_listener_rule", "aws_alb_listener_rule")
class AWSLBListenerRule(AWSResource):
    # All aws_alb_* will be stored as aws_lb_*
    _rules_in_aws = None
    depends_on = ["aws_lb_listener"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rules_in_aws = []

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s/aws_alb_listener_rule resources..." % self.resource_type)
        client = self._get_client("elbv2", region)
        rd = ResourceDirectory()

        listeners = ResourceDirectory().lookup("aws_lb_listener").listeners_in_aws
        for listener in listeners:
            response = client.describe_rules(ListenerArn=listener.real_data["ListenerArn"])
            if "Rules" in response:
                for rule in response["Rules"]:
                    try:
                        item = rd.get_item(predicted_id=rule["RuleArn"])
                        item.real_id = rule["RuleArn"]
                        item.real_data = rule
                    except KeyError:
                        item = FoundItem(self.resource_type, real_id=rule["RuleArn"], real_data=listener)
                    finally:
                        self._rules_in_aws.append(item)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["arn"], state_data=instance)

    def compare(self, depth):
        pass


@register("aws_lb_listener_certificate", "aws_alb_listener_certificate")
class AWSLBListenerCertificate(AWSResource):
    # All aws_alb_* will be stored as aws_lb_*
    resource_type = "aws_lb_listener_certificate"
    depends_on = ["aws_lb_listener"]

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for %s/aws_alb_listener_rule resources..." % self.resource_type)
        client = self._get_client("elbv2", region)
        rd = ResourceDirectory()

        listeners = ResourceDirectory().lookup("aws_lb_listener").listeners_in_aws
        for listener in listeners:
            response = client.describe_listener_certificates(ListenerArn=listener.real_data["ListenerArn"])
            if "Certificates" in response:
                for cert in response["Certificates"]:
                    try:
                        item = rd.get_item(predicted_id=cert["CertificateArn"])
                        item.real_id = cert["RuleArn"]
                        item.real_data = cert
                    except KeyError:
                        FoundItem(self.resource_type, real_id=cert["CertificateArn"], real_data=listener)

    def process_state_resource(self, state_resource, state_filename):
        logger.info("Found a resource of type %s!" % self.resource_type)
        for instance in state_resource["instances"]:
            FoundItem(self.resource_type, terraform_id=state_resource["name"], predicted_id=instance["attributes"]["arn"], state_data=instance)

    def compare(self, depth):
        pass
