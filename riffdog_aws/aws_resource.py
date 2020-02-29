import boto3

from riffdog.resource import Resource
from riffdog.config import RDConfig


class AWSResource(Resource):
    """
    Middle Inheritance to handle getting the correct client & resource objects
    """

    # set this to False if this class is a Global resource (e.g. s3)
    regional_resource = True

    def fetch_real_resources(self):
        
        if self.regional_resource:
            for region in RDConfig().aws_regions:
                self.fetch_real_regional_resources(region)
        else:
            self.fetch_real_global_resources()

    def fetch_real_regional_resources(self, region):
        raise NotImplemented()

    
    def fetch_real_global_resources(self):
        raise NotImplemented()
    

    def _get_client(self, aws_client_type, region):

        # FIXME: Some previous code to bring back to allow alternative queries

        # if account.auth_method == Account.IAM_ROLE:
        #     credentials = _get_sts_credentials(account)
        #     client = boto3.client(
        #         aws_client_type,
        #         region_name=region, aws_access_key_id=credentials['AccessKeyId'],
        #         aws_secret_access_key=credentials['SecretAccessKey'],
        #         aws_session_token=credentials['SessionToken'])
        # else:
        #   client = boto3.client(
        #       aws_client_type,
        #       region_name=region,
        #       aws_access_key_id=account.key,
        #       aws_secret_access_key=account.secret)

        client = boto3.client(aws_client_type, region_name=region)
        return client

    def _get_resource(self, aws_resource_type, region):
        # if not account:
        #     account = Account.objects.get(default=True)

        # if account.auth_method == Account.IAM_ROLE:
        #     credentials = _get_sts_credentials(account)
        #     resource = boto3.resource(
        #         aws_resource_type,
        #         region_name=region, aws_access_key_id=credentials['AccessKeyId'],
        #         aws_secret_access_key=credentials['SecretAccessKey'],
        #         aws_session_token=credentials['SessionToken'])

        # else:
        #     resource = boto3.resource(
        #         aws_resource_type,
        #         region_name=region,
        #         aws_access_key_id=account.key,
        #         aws_secret_access_key=account.secret)

        resource = boto3.resource(aws_resource_type, region_name=region)
        return resource
