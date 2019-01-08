#
# Uber, Inc. (c) 2018
#

import json
import numpy as np
import os

ALLOWED_DTYPES = [
    "float32",
    "float64",
    "string",

    "int8",
    "int16",
    "int32",
    "int64",

    "uint8",
    "uint16",
    "uint32",
    "uint64",
]


def validate_tensor_spec(spec):
    """
    Validates a tensor spec
    """
    for item in spec:
        name = item["name"]
        dtype = item["dtype"]
        shape = item["shape"]

        if dtype not in ALLOWED_DTYPES:
            raise ValueError("{} is not an allowed data type!".format(dtype))

        if not isinstance(name, basestring):
            raise ValueError("Field 'name' must be a string! Got value {} of type {}.".format(name, type(name)))

        if not isinstance(shape, (list, tuple)):
            raise ValueError("Field 'shape' must be a tuple! Got value {} of type {}.".format(shape, type(shape)))

        for dim in shape:
            # A bool is an instance of an int so we have to do that check first
            is_uint = (not isinstance(dim, bool)) and isinstance(dim, (int, long)) and dim > 0

            if dim is None or is_uint or isinstance(dim, basestring):
                continue
            else:
                raise ValueError(
                    "All items in 'shape' must either be None, a string, or a positive integer! Got {}".format(dim))


def validate_neuropod_config(config):
    """
    Validates a neuropod config
    """
    name = config["name"]
    platform = config["platform"]

    if not isinstance(name, basestring):
        raise ValueError("Field 'name' in config must be a string! Got value {} of type {}.".format(name, type(name)))

    if not isinstance(platform, basestring):
        raise ValueError(
            "Field 'platform' in config must be a string! Got value {} of type {}.".format(
                platform, type(platform)))

    validate_tensor_spec(config["input_spec"])
    validate_tensor_spec(config["output_spec"])


def canonicalize_tensor_spec(spec):
    """
    Converts the datatypes in a tensor spec to canonical versions
    (e.g. converts double to float64)
    """
    transformed = []
    for item in spec:
        transformed.append({
            "name": item["name"],
            "dtype": np.dtype(item["dtype"]).name,
            "shape": item["shape"]
        })
    return transformed


def write_neuropod_config(neuropod_path, model_name, platform, input_spec, output_spec):
    """
    Creates the neuropod config file

    :param  neuropod_path:  The path to a neuropod package
    :param  model_name:     The name of the model (e.g. "my_addition_model")
    :param  platform:       The model type (e.g. "python", "pytorch", "tensorflow", etc.)

    :param  input_spec:     A list of dicts specifying the input to the model.
                            Ex: [{"name": "x", "dtype": "float32", "shape": (None, )}]

    :param  output_spec:    A list of dicts specifying the output of the model.
                            Ex: [{"name": "y", "dtype": "float32", "shape": (None, )}]
    """
    # TODO: Switch to prototext
    with open(os.path.join(neuropod_path, "config.json"), "w") as config_file:
        config = {
            "name": model_name,
            "platform": platform,
            "input_spec": canonicalize_tensor_spec(input_spec),
            "output_spec": canonicalize_tensor_spec(output_spec),
        }

        # Verify that the config is correct
        validate_neuropod_config(config)

        # Write out the config as JSON
        json.dump(config, config_file, indent=4)


def read_neuropod_config(neuropod_path):
    """
    Reads a neuropod config

    :param  neuropod_path:  The path to a neuropod package
    """
    with open(os.path.join(neuropod_path, "config.json"), "r") as config_file:
        config = json.load(config_file)

        # Verify that the config is correct
        validate_neuropod_config(config)

        return config