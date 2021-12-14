# Copyright (c) individual contributors.
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of
# the License, or any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details. A copy of the
# GNU Lesser General Public License is distributed along with this
# software and can be found at http://www.gnu.org/licenses/lgpl.html

from uuid import UUID
from datetime import datetime


data_models = [
    {
        "finalized": True,
        "has_code": True,
        "has_label_plugin": True,
        "has_visual_plugin": True,
        "model_description": "Description 0",
        "model_name": "Model 0",
        "model_uuid": UUID("00000000-0001-1000-8000-000000000000"),
        "code": "testing_model",
        "parameter": [
            {
                "param_uuid": UUID("00000000-1001-1000-8000-000000000000"),
                "name": "param1",
                "description": "description of param1",
                "constraint": "",
                "type": "int",
            },
            {
                "param_uuid": UUID("00000000-1002-1000-8000-000000000000"),
                "name": "param2",
                "description": "description of param2",
                "constraint": "",
                "type": "int",
            },
        ],
        "instances": [
            {
                "could_train": False,
                "finalized": True,
                "has_inference": True,
                "has_training": True,
                "instance_description": "Instance Description 0",
                "instance_name": "Instance 0",
                "instance_uuid": UUID("00000000-0002-1000-8000-000000000000"),
                "parameter": [
                    {
                        "param_uuid": UUID("00000000-1001-1000-8000-000000000000"),
                        "name": "param1",
                        "description": "description of param1",
                        "constraint": "",
                        "type": "int",
                        "value": "1",
                    },
                    {
                        "param_uuid": UUID("00000000-1002-1000-8000-000000000000"),
                        "name": "param2",
                        "description": "description of param2",
                        "constraint": "",
                        "type": "float",
                        "value": "10.0",
                    },
                ],
            },
            {
                "could_train": True,
                "finalized": True,
                "has_inference": True,
                "has_training": True,
                "instance_description": "Instance Description 1",
                "instance_name": "Instance 1",
                "instance_uuid": UUID("00000000-0002-1000-8000-000000000001"),
                "parameter": [
                    {
                        "param_uuid": UUID("00000000-1001-1000-8000-000000000000"),
                        "name": "param1",
                        "description": "description of param1",
                        "constraint": "",
                        "type": "int",
                        "value": "10",
                    },
                    {
                        "param_uuid": UUID("00000000-1002-1000-8000-000000000000"),
                        "name": "param2",
                        "description": "description of param2",
                        "constraint": "",
                        "type": "float",
                        "value": "0.5",
                    },
                ],
            },
        ],
    },
    {
        "finalized": True,
        "has_code": True,
        "has_label_plugin": True,
        "has_visual_plugin": True,
        "model_description": "Description 1",
        "model_name": "Model 1",
        "model_uuid": UUID("00000000-0001-1000-8000-000000000001"),
        "parameter": [],
        "instances": [],
    },
]

data_users = [
    {
        "user_uuid": "00000000-0000-1000-8000-000000000000",
        "user_name": "admin",
        "user_essential": True,
        "user_created": datetime(2020, 12, 10).strftime("%a, %d %b %Y %H:%M:%S GMT"),
    },
    {
        "user_uuid": "00000000-0000-1000-8000-000000000001",
        "user_name": "user",
        "user_essential": False,
        "user_created": datetime(2020, 12, 10).strftime("%a, %d %b %Y %H:%M:%S GMT"),
    },
    {
        "user_uuid": "00000000-0000-1000-8000-000000000002",
        "user_name": "user2",
        "user_essential": False,
        "user_created": datetime(2020, 12, 10).strftime("%a, %d %b %Y %H:%M:%S GMT"),
    },
]

data_roles_general = [
    {
        "role_uuid": "00000000-0000-1000-8000-000000000000",
        "role_name": "admin",
        "role_essential": True,
        "role_description": "Admin role",
        "grant_access": True,
        "edit_users": True,
        "edit_models": True,
        "edit_roles": True,
     }
]

data_roles_model = [
    {
        "role_uuid": "00000000-0000-1000-8000-000000000000",
        "role_name": "model_owner",
        "role_essential": True,
        "role_description": "owner role",
        "can_see_model": True,
        "instantiate_model": True,
        "edit_model": True,
        "download_model": True,
        "grant_access_model": True,
     },
     {
        "role_uuid": "00000000-0000-1000-8000-000000000000",
        "role_name": "model_guest",
        "role_essential": False,
        "role_description": "owner role",
        "can_see_model": True,
        "instantiate_model": False,
        "edit_model": False,
        "download_model": False,
        "grant_access_model": False,
     }
]

data_roles_instance = [
    {
        "role_uuid": "00000000-0000-1000-8000-000000000000",
        "role_name": "instance_owner",
        "role_essential": True,
        "role_description": "owner role",
        "can_see_instance": True,
        "add_sample": True,
        "get_training_data": True,
        "get_inference_data": True,
        "edit_instance": True,
        "grant_access_instance": True,
        "request_labels": True,
        "respons_labels": True,
     },
     {
        "role_uuid": "00000000-0000-1000-8000-000000000000",
        "role_name": "instance_guest",
        "role_essential": False,
        "role_description": "guest role",
        "can_see_instance": True,
        "add_sample": False,
        "get_training_data": False,
        "get_inference_data": False,
        "edit_instance": False,
        "grant_access_instance": False,
        "request_labels": False,
        "respons_labels": False,
     }
]

data_code = dict()
