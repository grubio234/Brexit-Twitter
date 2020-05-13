"""
Import some configuration options from a custom configuration file.
Compare them, or fall back to a default config file.
The importing mechanism employed here is rather hacky and involves  importing
the same module twice.
"""

import os.path

import config.default_config

def checkIsValidCustomConfigModule(config_module):
    for module_object_name in dir(config.default_config):
        if module_object_name not in dir(config_module):
            raise Exception("The custom configuration file {} does not contain "
                "all necessary objects. The object '{}' is missing."
                "".format(config_module, module_object_name))
    print("A custom configuration module is imported.")


custom_config_file = "config/custom_config.py"
if os.path.isfile(custom_config_file):
    import config.custom_config as cc
    checkIsValidCustomConfigModule(cc)
    from config.custom_config import *
else:
    from config.default_config import *
