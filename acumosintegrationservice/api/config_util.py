#
# ===============LICENSE_START=======================================================
# Acumos
# ===================================================================================
# Copyright (C) 2018 AT&T Intellectual Property. All rights reserved.
# ===================================================================================
# This Acumos software file is distributed by AT&T
# under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============LICENSE_END=========================================================

"""Utility methods for loading configuration values"""
import configparser
import logging
import os


def get_properties_path():
    dir_path = os.path.dirname(os.path.join(os.path.realpath(__file__)))
    properties_path = os.path.join(dir_path, '..', '..', 'properties')
    return properties_path


_parser = None  # cache parser to avoid constant file IO


def get_parser():
    global _parser
    if _parser is None:
        parser = configparser.ConfigParser()
        config_path = os.path.join(get_properties_path(), 'settings.cfg')
        logging.info("config_path: %s", config_path)
        parser.read(config_path)
        _parser = parser
    return _parser


def get_config_value(env_name, config=None, config_name=None, section='APP_SETTINGS'):
    if config is None:
        config = get_parser()
    if section is not None:
        config = config[section]
    if config_name is None:
        config_name = env_name
    if env_name in os.environ:
        return os.environ[env_name]

    return config[config_name]

