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

from flask_restplus import fields
from acumosintegrationservice.api.namespaces import acumos_services_namespace as api

validate_connection_fields = api.model('ValidateConnection', {
    'base_url': fields.String(required=True, description='Name of the model',
                              example='https://acumosr-test.research.att.com:9084'),
    'certificatekeyfilecontent': fields.String(required=True,
                                               description='Content of certificate'),
    'privatekeyfilecontent': fields.String(required=True,
                                           description='Content of private key'),
})

