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
from flask import Flask
from acumosintegrationservice.api.restplus import api_v2, blueprint_v2
from acumosintegrationservice.api.v2.endpoints import api as acumos_services_namespace
from acumosintegrationservice.api.global_constants import GlobalConstants
from acumosintegrationservice.api.config_util import get_config_value
import logging


app = Flask(__name__)


def initialize_app(flask_app):
    api_v2.namespaces.clear()
    api_v2.add_namespace(acumos_services_namespace)
    app.register_blueprint(blueprint_v2)
    logging.basicConfig(level=logging.DEBUG)


def main():
    port = get_config_value(GlobalConstants.SERVER_PORT, section='SERVER')
    initialize_app(app)
    print('Application Running on port : ' + port)
    app.run(host='0.0.0.0', debug=True, port=port)


if __name__ == '__main__':
    main()
