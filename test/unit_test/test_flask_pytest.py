#!/usr/bin/env python3
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
import sys

from os.path import dirname, realpath, join
from flask import Flask
from microservice_flask import initialize_app
from mock import patch

parentddir = dirname(dirname(dirname(realpath(__file__))))
sys.path.append(join(parentddir, 'acumosintegrationservice'))


BASE_URL = 'http://127.0.0.1:5000/v2/'

app = Flask(__name__)

initialize_app(app)

'''
@pytest.fixture(scope='session')
def test_client():
    testing_client = app.test_client()
    initialize_app(testing_client)
    testing_client.testing = True
    return testing_client
'''


@patch('acumosintegrationservice.api.acumos_e5_api.AcumosE5API.get_model_list')
def test_get_solutions(get_model_list):
    get_model_list.return_value = {
        'solutions': [
            {
                'id': '4dc5adf3-650b-4c68-abd3-64f300543968',
                'name': 'DB_Anomaly',
                'created_date': '2018-09-27T01:45:39',
                'active': 'true'
            }, {
                'id': '9071ce8c-a361-4b3f-a7f1-5568bc8462f9',
                'name': 'image_classifier',
                'created_date': '2018-09-28T15:13:28',
                'active': 'true'
            }
        ]
    }

    with app.test_client() as c:
        response = c.get('/v2/solutions')

        assert response.status_code == 200
        assert len(response.get_data()) > 0


@patch('acumosintegrationservice.api.acumos_e5_api.AcumosE5API.get_model_revisions')
def test_get_revisions(get_model_revisions):
    get_model_revisions.return_value = {
        'revisions': [{
            'version': '2',
            'revisionId': 'c35ce47c-248f-4d6f-9f8d-25e61ae0ea13'
        }
        ]
    }

    solution_id = '4dc5adf3-650b-4c68-abd3-64f300543968'
    with app.test_client() as c:
        response = c.get('/v2/solutions/' + solution_id + '/revisions')

        assert response.status_code == 200
        assert len(response.get_data()) > 0


@patch('acumosintegrationservice.api.acumos_e5_api.AcumosE5API.get_artifacts')
def test_get_artifacts(get_artifacts):
    get_artifacts.return_value = {
        'artifacts': [
            {
                'artifactId': '2fb643bb-f788-4e97-a45a-45158e54aeee',
                'version': '2',
                'artifactTypeCode': 'MI',
                'name': 'model.zip',
                'description': 'model.zip',
            },
            {
                'artifactId': '3900bc01-8427-4767-9405-25923f93fe42',
                'version': '2',
                'artifactTypeCode': 'PJ',
                'name': 'PROTOBUF',
                'description': 'Tosca file : PROTOBUF for SolutionID : 2',
            }
        ]
    }

    solution_id = '4dc5adf3-650b-4c68-abd3-64f300543968'
    with app.test_client() as c:
        response = c.get('/v2/solutions/' + solution_id + '/artifacts')

        assert response.status_code == 200
        assert len(response.get_data()) > 0


@patch('acumosintegrationservice.api.acumos_e5_api.AcumosE5API._download_resource_text')
def test_get_artifact_content(_download_resource_text):
    _download_resource_text.return_value = 'This is artifact Content'

    solution_id = '4dc5adf3-650b-4c68-abd3-64f300543968'
    artifact_id = '2fb643bb-f788-4e97-a45a-45158e54aeee'
    file_name = 'model'

    with app.test_client() as c:
        response = c.get('/v2/artifacts/' + solution_id + '/' + artifact_id + '/' + file_name + '/artifactText')

        assert response.status_code == 200
        assert response.get_data().decode() == '"This is artifact Content"\n'


@patch('acumosintegrationservice.api.acumos_e5_api.AcumosE5API.get_downloads')
def test_get_download_count(get_downloads):
    get_downloads.return_value = 5

    solution_id = '4dc5adf3-650b-4c68-abd3-64f300543968'

    with app.test_client() as c:
        response = c.get('/v2/solutions/' + solution_id + '/downloads')

        assert response.status_code == 200
        assert response.get_data().decode() == '5\n'


@patch('acumosintegrationservice.api.acumos_e5_api.AcumosE5API.get_views')
def test_get_view_count(get_views):
    get_views.return_value = 5

    solution_id = '4dc5adf3-650b-4c68-abd3-64f300543968'

    with app.test_client() as c:
        response = c.get('/v2/solutions/' + solution_id + '/views')

        assert response.status_code == 200
        assert response.get_data().decode() == '5\n'


@patch('acumosintegrationservice.api.acumos_e5_api.AcumosE5API.update_views')
def test_update_view_count(update_views):
    update_views.return_value = 6

    solution_id = '4dc5adf3-650b-4c68-abd3-64f300543968'

    with app.test_client() as c:
        response = c.post('/v2/solutions/' + solution_id + '/views')

        assert response.status_code == 200
        assert response.get_data().decode() == '6\n'


@patch('acumosintegrationservice.api.acumos_e5_api.AcumosE5API.update_downloads')
def test_update_download_count(update_downloads):
    update_downloads.return_value = 2

    solution_id = '4dc5adf3-650b-4c68-abd3-64f300543968'

    with app.test_client() as c:
        response = c.post('/v2/solutions/' + solution_id + '/downloads')

        assert response.status_code == 200
        assert response.get_data().decode() == '2\n'
