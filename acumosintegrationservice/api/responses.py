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

"""This file holds common utility responses"""

from flask_restplus import abort
from http import client


def forbidden(message):
    status_code = client.FORBIDDEN
    abort(status_code, message, status=status_code)


def unauthorized(message=None):
    if message is None:
        message = "UNAUTHORIZED"
    status_code = client.UNAUTHORIZED
    abort(status_code, message, status=status_code)


def bad_request(message):
    status_code = client.BAD_REQUEST
    abort(status_code, message, status=status_code)


def not_found(message=None):
    if message is None:
        message = 'NOT FOUND'
    status_code = client.NOT_FOUND
    abort(status_code, message, status=status_code)


def ok_response(message, **kwargs):
    response = {"status": client.OK, "message": message}
    response.update(dict(kwargs))
    return response, client.OK


def no_content_response():
    return '', client.NO_CONTENT
