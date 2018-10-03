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

import logging
import json
import time
import os
import shutil

from acumosintegrationservice.api.global_constants import GlobalConstants

from flask import request
from acumosintegrationservice.api.config_util import get_config_value
from acumosintegrationservice.api.acumos_e5_api import AcumosE5API, AcumosE5APIException, AcumosNetworkException
from bson import json_util


logger = logging.getLogger(__name__)


class InputRequestException(Exception):
    pass


def csrf_json_header_add():
    headers = {'Access-Control-Allow-Origin': '*',
               'Access-Control-Allow-Methods': '*',
               'Access-Control-Allow-Domain': '*',
               'Access-Control-Allow-Credentials': True}
    return headers


def csrf_header_add(resp, response_code):
    resp.status_code = response_code
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = '*'
    resp.headers['Access-Control-Allow-Domain'] = '*'
    resp.headers['Access-Control-Allow-Credentials'] = True
    resp.status_code = response_code
    return resp


def get_federated_models():
    include_revision = True
    try:
        acumos_e5_api = create_acumos_e5_service()
        model_list = acumos_e5_api.get_model_list(include_revision=include_revision)
        return [json.loads(json.dumps(model, indent=4, default=json_util.default)) for model in model_list], 200
    except (AcumosE5APIException, AcumosNetworkException) as exception:
        logging.exception('Exception: ' + exception)
        response_dict = {"status": "failed",
                         "error": "Cannot get Acumos models. Exception " + exception + " ."
                                  "Please check Acumos configuration and Acumos E5 Integration Services log"}
        return response_dict, 500
    except ConnectionError as exception:
        logging.exception('Exception: ' + exception)
        response_dict = {"status": "failed",
                         "error": "Cannot connect to Acumos services. Exception: " + exception}
        return response_dict, 500
    except Exception as exception:
        logging.exception('Exception: ' + exception)
        response_dict = {"status": "failed",
                         "error": "Error when getting models from Acumos. Exception: " + exception}
        return response_dict, 500


def create_acumos_e5_service(tmp_dir: str = ".") -> AcumosE5API:
    base_path = get_config_value(GlobalConstants.ACUMOS_E5_BASE_PATH, section='APP_SETTINGS')
    cert_filename = get_config_value(GlobalConstants.ACUMOS_E5_CERT_FILE)
    private_key_filename = get_config_value(GlobalConstants.ACUMOS_E5_PRIVATE_KEY_FILE)
    acumos_e5_api = AcumosE5API(base_url=base_path,
                                solution_path=get_config_value(GlobalConstants.ACUMOS_E5_SOLUTION_PATH),
                                revision_path=get_config_value(GlobalConstants.ACUMOS_E5_REVISION_PATH),
                                artifact_path=get_config_value(GlobalConstants.ACUMOS_E5_ARTIFACT_PATH),
                                cert_file=cert_filename, private_key_file=private_key_filename,
                                artifact_info_file=get_config_value(GlobalConstants.ACUMOS_E5_DOCKER_URL_FILE_NAME),
                                tmp_dir=tmp_dir)
    return acumos_e5_api


def validate_federation_services():
    try:
        validate_e5_service(request.get_json())
    except ConnectionError as error:
        logging.exception('Error when validating E5 services: ' + error)
        return {'status': 'failed', 'error': str(error)}, 400
    except (AcumosE5APIException, AcumosNetworkException) as error:
        logging.exception('Error from Acumos Integration services: ' + error)
        return {'status': 'failed', 'error': str(error)}, 400
    except Exception as exception:
        logging.exception('Validation failed: ' + exception)
        response_dict = {"status": "failed",
                         "error": "Cannot validate Acumos configuration. Exception: " + exception + " ."
                                  "Please check Acumos E5 Integration Services log for more details"}
        return response_dict, 500
    return {'status': 'success'}, 200


def validate_e5_service(request_body):
    base_path = request_body[GlobalConstants.BASE_URL]
    timestamp = str(time.time())
    tmp_dir = os.path.join(get_config_value(GlobalConstants.ACUMOS_E5_MODEL_PATH), timestamp)
    cert_filename = os.path.join(tmp_dir, GlobalConstants.CERTIFICATE_CER)
    private_key_filename = os.path.join(tmp_dir, GlobalConstants.PRIVATE_KEY)
    os.makedirs(tmp_dir)
    try:
        with open(cert_filename, "w") as cert_file:
            cert_file.write(request_body[GlobalConstants.CERTIFICATE_KEY_FILE_CONTENT])
        with open(private_key_filename, "w") as private_key_file:
            private_key_file.write(request_body[GlobalConstants.PRIVATE_KEY_FILE_CONTENT])

        acumos_e5_api = AcumosE5API(base_url=base_path,
                                    solution_path=get_config_value(GlobalConstants.ACUMOS_E5_SOLUTION_PATH),
                                    revision_path=get_config_value(GlobalConstants.ACUMOS_E5_REVISION_PATH),
                                    artifact_path=get_config_value(GlobalConstants.ACUMOS_E5_ARTIFACT_PATH),
                                    ping_path=get_config_value(GlobalConstants.ACUMOS_E5_PING_PATH),
                                    cert_file=cert_filename, private_key_file=private_key_filename,
                                    artifact_info_file=get_config_value(GlobalConstants.ACUMOS_E5_DOCKER_URL_FILE_NAME),
                                    tmp_dir=tmp_dir)
        acumos_e5_api.validate_connection()
    finally:
        shutil.rmtree(tmp_dir)


def get_federated_model_revision(solution_id):
    try:
        acumos_e5_api = create_acumos_e5_service()
        solution_revision_dict = acumos_e5_api.get_model_revisions(solution_id_list=[solution_id])
        return solution_revision_dict, 200
    except (AcumosE5APIException, AcumosNetworkException) as exception:
        logging.exception('Exception: ' + exception)
        response_dict = {"status": "failed",
                         "error": "Cannot get model revisions. Exception: " + exception + "."
                                  "Please check Acumos configuration and Acumos E5 Integration Services log"}
        return response_dict, 500
    except ConnectionError as exception:
        logging.exception('Exception: ' + exception)
        response_dict = {"status": "failed",
                         "error": "Cannot connect to Acumos services. Exception: " + exception}
        return response_dict, 500
    except Exception as exception:
        logging.exception('Exception: ' + exception)
        response_dict = {"status": "failed",
                         "error": "Error when getting model revisions from Acumos. Exception: " + exception}
        return response_dict, 500


def _download_artifact_text(solution_id, artifact_id, file_name):
    acumos_e5_api = create_acumos_e5_service()
    return acumos_e5_api._download_resource_text(solution_id, artifact_id, file_name)


def _get_artifacts(solution_id):
    acumos_e5_api = create_acumos_e5_service()
    return acumos_e5_api.get_artifacts(solution_id)


def _update_view_count(solution_id):
    acumos_e5_api = create_acumos_e5_service()
    return acumos_e5_api.update_views(solution_id)


def _update_download_count(solution_id):
    acumos_e5_api = create_acumos_e5_service()
    return acumos_e5_api.update_downloads(solution_id)


def _get_view_count(solution_id):
    acumos_e5_api = create_acumos_e5_service()
    return acumos_e5_api.get_views(solution_id)


def _get_download_count(solution_id):
    acumos_e5_api = create_acumos_e5_service()
    return acumos_e5_api.get_downloads(solution_id)
