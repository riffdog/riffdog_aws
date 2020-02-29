"""
This module is for Elastic Load Balancers v2 (alb/nlb).
"""

import logging

from riffdog.data_structures import FoundItem
from riffdog.resource import  register, ResourceDirectory

from ...aws_resource import AWSResource

logger = logging.getLogger(__name__)


@register("aws_lb_listener", "aws_alb_listener")
class AWSLBListener(AWSResource):
    _listeners_in_aws = {}
    _listeners_in_state = {}

    depends_on = ["aws_lb"]

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for aws_lb_listener/aws_alb_listener resources")

        client = self._get_client("elbv2", region)

        load_balancers = ResourceDirectory().lookup("aws_lb").load_balancers_in_aws
        for name, attrs in load_balancers.items():
            response = client.describe_listeners(LoadBalancerArn=attrs["LoadBalancerArn"])
            if "Listeners" in response:
                for listener in response["Listeners"]:
                    self._listeners_in_aws[listener["ListenerArn"]] = listener

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            #FIXME: magic string correect one? alb or lb
            item = FoundItem("aws_lb_listener", terraform_id=instance["attributes"]["arn"], state_data=instance)
            self._listeners_in_state[instance["attributes"]["arn"]] = item

    def compare(self, depth):

        for key, val in self._listeners_in_state.items():
            if key in self._listeners_in_aws:
                val.real_id = key
                val.real_data = self._listeners_in_aws[key]

        for key, val in self._listeners_in_aws.items():
            if key not in self._listeners_in_state:
                item = FoundItem("aws_lb_listener", real_id=key, real_data=val)

    @property
    def listeners_in_aws(self):
        return self._listeners_in_aws


@register("aws_lb_listener_rule", "aws_alb_listener_rule")
class AWSLBListenerRule(AWSResource):
    _rules_in_aws = {}
    _rules_in_state = {}

    depends_on = ["aws_lb_listener"]

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for aws_lb_listener_rule/aws_alb_listener_rule resources")

        client = self._get_client("elbv2", region)

        listeners = ResourceDirectory().lookup("aws_lb_listener").listeners_in_aws
        for arn, attrs in listeners.items():
            response = client.describe_rules(ListenerArn=attrs["ListenerArn"])
            if "Rules" in response:
                for rule in response["Rules"]:
                    self._rules_in_aws[rule["RuleArn"]] = rule

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            #FIXME: as per others
            item = FoundItem("aws_lb_listener_rule", terraform_id=instance["attributes"]["arn"], state_data=instance)
            self._rules_in_state[instance["attributes"]["arn"]] = item

    def compare(self, depth):

        for key, val in self._rules_in_state.items():
            if key in self._rules_in_aws:
                val.real_id = key
                val.real_data = self._rules_in_aws[key]

        for key, val in self._rules_in_aws.items():
            if key not in self._rules_in_state:
                item = FoundItem("aws_lb_listener_rule", real_id=key, state_data=val)



@register("aws_lb_listener_certificate", "aws_alb_listener_certificate")
class AWSLBListenerCertificate(AWSResource):
    _certs_in_aws = {}
    _certs_in_state = {}

    depends_on = ["aws_lb_listener"]

    def fetch_real_regional_resources(self, region):
        logging.info("Looking for aws_lb_listener_rule/aws_alb_listener_rule resources")

        client = self._get_client("elbv2", region)

        listeners = ResourceDirectory().lookup("aws_lb_listener").listeners_in_aws
        for arn, attrs in listeners.items():
            response = client.describe_listener_certificates(ListenerArn=attrs["ListenerArn"])
            if "Certificates" in response:
                for cert in response["Certificates"]:
                    self._certs_in_aws[cert["CertificateArn"]] = cert

    def process_state_resource(self, state_resource, state_filename):
        for instance in state_resource["instances"]:
            item = FoundItem("aws_lb_listener_certificate", terraform_id=instance["attributes"]["arn"], state_data=instance)
            self._certs_in_state[instance["attributes"]["arn"]] = item

    def compare(self, depth):

        for key, val in self._certs_in_state.items():
            if key in self._certs_in_aws:
                val.real_id = key
                val.real_data = self._certs_in_aws[key]

        for key, val in self._certs_in_aws.items():
            if key not in self._certs_in_state:
                item = FoundItem("aws_lb_listener_certificate", real_id=key, real_data=val)


