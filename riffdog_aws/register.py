import logging

import os
import pkgutil
from importlib import import_module

logger = logging.getLogger(__name__)

def register_resources():
    logger.info("AWS Resource Pack loading")

    for (_, name, is_package) in pkgutil.walk_packages([os.path.join(os.path.dirname(__file__), "resources")]):
        if is_package:
            package_name = name
            for (_, name, _) in pkgutil.iter_modules(
                    [os.path.join(os.path.dirname(__file__), "resources", package_name)]):
                import_module('riffdog_aws.resources.%s.%s' % (package_name, name))
        else:
            for (_, name, _) in pkgutil.iter_modules([os.path.join(os.path.dirname(__file__), "resources")]):
                import_module('riffdog_aws.resources.%s' % name)