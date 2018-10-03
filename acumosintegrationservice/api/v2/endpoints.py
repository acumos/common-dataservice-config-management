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

from acumosintegrationservice.api.v2.parser import error_response_body, error_response_body_500
from acumosintegrationservice.api.namespaces import acumos_services_namespace as api
from flask_restplus import Resource
from acumosintegrationservice.api.business import get_federated_models, validate_federation_services, \
    get_federated_model_revision, _download_artifact_text, _get_artifacts, _update_view_count, _get_view_count, \
    _update_download_count, _get_download_count
from acumosintegrationservice.api.serializers import validate_connection_fields


@api.route('/solutions')
class ModelFederationCollection(Resource):

    @api.response(200, 'Models information successfully retrieved')
    @api.response(400, 'Bad Request', error_response_body)
    @api.response(401, 'Not Authorized')
    @api.response(500, 'Unexpected Error', error_response_body_500)
    @api.doc(params={'includeRevisions': 'Include revisions of model in response'})
    def get(self):
        """
        Get models from Acumos Federation gateway
        """
        return get_federated_models()


@api.route('/connectivity/e5')
class ModelFederationStatus(Resource):
    @api.response(200, 'Validation success')
    @api.response(400, 'Bad Request', error_response_body)
    @api.response(401, 'Not Authorized')
    @api.response(500, 'Unexpected Error', error_response_body_500)
    @api.expect(validate_connection_fields, validate=True)
    def post(self):
        """
        Validate connection to E5 interface
        """
        return validate_federation_services()


@api.route('/solutions/<string:solution_id>/revisions')
class ModelFederationRevisionCollection(Resource):
    @api.response(200, 'Acumos models revision information successfully retrieved')
    @api.response(400, 'Bad Request', error_response_body)
    @api.response(401, 'Not Authorized')
    @api.response(500, 'Unexpected Error', error_response_body_500)
    def get(self, solution_id):
        """
        Retrieves Acumos model revisions for given solution ID
        """
        return get_federated_model_revision(solution_id)


@api.route('/solutions/<string:solution_id>/artifacts')
class ListArtifacts(Resource):
    @api.response(200, 'Acumos solution average rating retrieved successfully')
    @api.response(400, 'Bad Request')
    @api.response(401, 'Not Authorized')
    @api.response(500, 'Unexpected Error')
    def get(self, solution_id):
        """
        Get all artifacts from a given solution id under the latest revision
        """
        return _get_artifacts(solution_id)


@api.route('/artifacts/<string:solution_id>/<string:artifact_id>/<string:file_name>/artifactText')
class DownloadArtifactText(Resource):
    @api.response(200, 'Acumos solution average rating retrieved successfully')
    @api.response(400, 'Bad Request', error_response_body)
    @api.response(401, 'Not Authorized')
    @api.response(500, 'Unexpected Error', error_response_body_500)
    def get(self, solution_id, artifact_id, file_name):
        """
        Get all artifacts from a given solution id under the latest revision
        """
        return _download_artifact_text(solution_id, artifact_id, file_name)


@api.route('/solutions/<string:solution_id>/views')
class ModelViewCount(Resource):
    @api.response(200, 'Acumos solution view count updated successfully')
    @api.response(400, 'Bad Request', error_response_body)
    @api.response(401, 'Not Authorized')
    @api.response(500, 'Unexpected Error', error_response_body_500)
    def post(self, solution_id):
        """
        Updates view count by +1 for a given solutionID
        """
        return _update_view_count(solution_id)

    def get(self, solution_id):
        """
        Retrieves view count for given solutionID
        """
        return _get_view_count(solution_id)


@api.route('/solutions/<string:solution_id>/downloads')
class ModelDownloadCount(Resource):
    @api.response(200, 'Acumos solution download count retrieved successfully')
    @api.response(400, 'Bad Request', error_response_body)
    @api.response(401, 'Not Authorized')
    @api.response(500, 'Unexpected Error', error_response_body_500)
    def post(self, solution_id):
        """
        Updates download count by +1 for a given Acumos solutionID
        """
        return _update_download_count(solution_id)

    def get(self, solution_id):
        """
        Retrieves download count for a given Acumos solutionID
        """
        return _get_download_count(solution_id)
