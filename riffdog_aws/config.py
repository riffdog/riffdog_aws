import os

from riffdog.config import RDConfig

DEFAULT_REGION="us-east-1"

def add_args(parser):

    group = parser.add_argument_group('AWS Resource')
    group.add_argument('--aws_region', help="AWS regions to use", action='append')
    
def config():
    config = RDConfig()
    config.aws_regions = get_default_regions()


def get_default_regions():
    """
    Current order of precedence
    - AWS_DEFAULT_REGION overrides everything else
    - region_args come next
    - fall back to us-east-1 I guess
    """
    env_region = os.environ.get('AWS_DEFAULT_REGION', None)

    regions = []

    if env_region is not None and env_region:
        regions.append(env_region)
    else:
        regions.append(DEFAULT_REGION)
    return regions