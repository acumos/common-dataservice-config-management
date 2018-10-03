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

import requests
import logging
from typing import List
from http import HTTPStatus
from pymongo import MongoClient
from datetime import datetime
from acumosintegrationservice.api.config_util import get_config_value
from requests.exceptions import ConnectionError, SSLError


class AcumosNetworkException(Exception):
    pass


class AcumosE5APIException(Exception):
    pass


class AcumosE5API:

    def __init__(self, base_url: str, solution_path: str, revision_path: str, artifact_path: str,
                 cert_file: str, private_key_file: str, verify_certificate=False,
                 ping_path: str='/ping', tmp_dir=".", artifact_info_file="artifact_info.json"):
        self.base_url = base_url
        self._solution_endpoint = base_url + solution_path
        self._revision_endpoint = base_url + revision_path
        self._artifact_endpoint = base_url + artifact_path
        self._ping_endpoint = base_url + ping_path
        self._cert_file = cert_file
        self._private_key_file = private_key_file
        self._verify_certificate = verify_certificate
        self._artifact_info_file = artifact_info_file
        self._tmp_dir = tmp_dir
        self._mongo_db = MongoClient(get_config_value("mongo_hostname", section="DATABASE"),
                                     username=get_config_value("mongo_username", section="DATABASE"),
                                     password=get_config_value("mongo_password", section="DATABASE"),
                                     authSource=get_config_value("mongo_dbname", section="DATABASE"),
                                     port=int(get_config_value("mongo_port", section="DATABASE"))
                                     )[get_config_value("mongo_dbname", section="DATABASE")]

    # Get list of all Acumos Models from Acumos Instance via E5 API
    def get_model_list(self, include_revision=True) -> List:
        solution_response = self._request_e5_api(self._solution_endpoint)
        solutions = solution_response['content']
        model_dict = {solution['solutionId']: AcumosSolution(solution) for solution in solutions}
        collection = self._mongo_db['models']
        mongo_list = []

        if include_revision:
            for solution_id, acumos_model in model_dict.items():
                acumos_model.add_revisions(self._get_revisions(solution_id))

                # Check if instance of a solution id already exists
                if collection.find({'id': solution_id}).count() == 0:
                    mongo_entry = acumos_model
                    collection.insert(mongo_entry.as_dict())

        for document in collection.find({}):
            mongo_list.append(document)
        return mongo_list

    def _get_revisions(self, solution_id: str) -> List:
        revision_url = self._revision_endpoint.format(solutionId=solution_id)
        revision_response = self._request_e5_api(revision_url)
        if 'content' not in revision_response:
            raise AcumosE5APIException(f'Missing required field \'content\' in response: {revision_response}')
        return revision_response['content']

    def _request_e5_api(self, endpoint: str) -> dict:
        try:
            response = requests.get(endpoint, verify=self._verify_certificate,
                                    cert=(self._cert_file, self._private_key_file))
            if response.status_code != HTTPStatus.OK.value:
                raise AcumosNetworkException(f'Error return from Acumos for endpoint: {endpoint}.'
                                             f'Status code: {response.status_code} - Content: {response.text}')
            return response.json()
        except ConnectionError as error:
            logging.exception(f'Exception when connecting to {self._solution_endpoint}: {error}')
            raise

    def validate_connection(self):
        try:
            response = requests.get(self._ping_endpoint, verify=self._verify_certificate,
                                    cert=(self._cert_file, self._private_key_file))
            if response.status_code != HTTPStatus.OK.value:
                raise ConnectionError(f'Error response from E5: {response.status_code} - {response.text}')
        except SSLError as ssl_error:
            raise ConnectionError(f'Invalid SSL certificates: {ssl_error}')
        except ConnectionError as error:
            raise ConnectionError(f'Cannot connect to E5 services: {error}')
        except (KeyError, AttributeError) as internal_error:
            raise AcumosE5APIException(f'Cannot access field/key: {internal_error}')
        except Exception as error:
            raise ConnectionError(f'Error when connecting to E5 services: {error}')

    def get_model_revisions(self, solution_id_list: List) -> dict:
        solution_revision_dict = {solution_id: self._get_revisions(solution_id) for solution_id in solution_id_list}
        return solution_revision_dict

    def get_latest_revision(self, solution_id):
        revisions = self._get_revisions(solution_id)
        latest_version = max([revision['version'] for revision in revisions])
        return latest_version

    def _download_resource_text(self, solution_id: str, artifact_id: str, file_name: str):
        latest_version = self.get_latest_revision(solution_id)
        for revision in self._get_revisions(solution_id):
            if revision['version'] == latest_version:
                revision_id = revision['revisionId']
                break
        url = self.base_url + "/solutions/" + solution_id + "/revisions/" + revision_id + "/artifacts/" + artifact_id \
                            + "/content"
        response = requests.get(url, stream=True, verify=self._verify_certificate,
                                cert=(self._cert_file, self._private_key_file))
        if response.status_code != HTTPStatus.OK.value:
            raise AcumosE5APIException(f'Cannot download artifact at {url}')

        logging.debug(f'Downloaded text from resource: {file_name}')
        r = str(response.text)
        return r

    def get_artifacts(self, solution_id):
        latest_version = self.get_latest_revision(solution_id)
        for revision in self._get_revisions(solution_id):
            if revision['version'] == latest_version:
                revision_id = revision['revisionId']
                break
        e5_artifact_endpoint = self._artifact_endpoint.format(solutionId=solution_id, revisionId=revision_id)
        artifact_response = self._request_e5_api(e5_artifact_endpoint)
        artifact_list = artifact_response['content']
        return artifact_list

    # Update the view count of a solution in Mongo DB instance
    def update_views(self, solution_id) -> List:
        collection = self._mongo_db['models']
        for p in collection.find():
            if p['id'] == solution_id:
                existing = p['views']
                collection.update(
                    {"id": solution_id},
                    {
                        "$set": {
                            "views": existing + 1
                        }
                    }
                )
                return existing + 1

    # Update the download count of a solution in Mongo DB instance
    def update_downloads(self, solution_id) -> List:
        collection = self._mongo_db['models']
        for p in collection.find():
            if p['id'] == solution_id:
                existing = p['downloads']
                collection.update(
                    {"id": solution_id},
                    {
                        "$set": {
                            "downloads": existing + 1
                        }
                    }
                )
                return existing + 1

    # Get the view count of a solution in Mongo DB instance
    def get_views(self, solution_id) -> List:
        collection = self._mongo_db['models']
        for p in collection.find():
            if p['id'] == solution_id:
                existing = p['views']
                return existing

    # Get the download count of a solution in Mongo DB instance
    def get_downloads(self, solution_id) -> List:
        collection = self._mongo_db['models']
        for p in collection.find():
            if p['id'] == solution_id:
                existing = p['downloads']
                return existing


class AcumosSolution:

    def __init__(self, acumos_solution: dict):
        self._id = acumos_solution['solutionId']
        self._name = acumos_solution['name']
        self._created_date = AcumosSolution.convert_date(acumos_solution['created'])
        self._modified_date = AcumosSolution.convert_date(acumos_solution['modified'])
        self._description = acumos_solution['description']
        self._active = acumos_solution['active']
        self._revisions = []
        self._downloads = 0
        self._views = 0
        self._avg_rating = 0
        self._user_ratings = []
        self._metadata = {
            'modelTypeCode': acumos_solution['modelTypeCode'],
            'toolkitTypeCode': acumos_solution['toolkitTypeCode']
        }

    def as_dict(self):
        return {
            'id': self._id,
            'name': self._name,
            'created_date': self._created_date,
            'modified_date': self._modified_date,
            'description': self._description if self._description else '',
            'revisions': self._revisions,
            'metadata': self._metadata,
            'user_ratings': self._user_ratings,
            'downloads': self._downloads,
            'views': self._views,
            'average_rating': self._avg_rating,
            'active': self._active,
        }

    def add_revisions(self, revisions_response: List):
        self._revisions = [AcumosSolution.convert_revision(resp) for resp in revisions_response]

    @staticmethod
    def convert_date(acumos_date_field: float) -> str:
        return datetime.utcfromtimestamp(acumos_date_field / 1000).isoformat()

    @staticmethod
    def convert_revision(revision_resp_obj: dict) -> dict:
        return {
            'version': revision_resp_obj['version'],
            'revisionId': revision_resp_obj['revisionId']
        }
