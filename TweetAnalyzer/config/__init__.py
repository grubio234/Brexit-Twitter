from __future__ import print_function

# The following import is overwritten if the custom configuration file exists.
# It is anyways imported to ensure that the default configuration is up to date.
from .default_config import data_dir
try:
    from .custom_config import data_dir
    print("A custom configuration file is loaded.")
except ModuleNotFoundError:
    print("The default configuration is used.")
except ImportError as e:
    print(("!! A custom configuration file was found, but not all required "
        " objects are provided by that file. Please update it."))
    raise e
