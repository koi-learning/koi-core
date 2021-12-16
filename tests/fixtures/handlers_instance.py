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

import re
import json
from uuid import UUID
from .handlers_common import cache_controlled
from .common_data import data_models


@cache_controlled
def instances(request, context):
    keys = [
        "could_train",
        "finalized",
        "has_inference",
        "has_training",
        "instance_description",
        "instance_name",
        "instance_uuid",
    ]
    match = re.search(r"http://base/api/model/([0-9,a-f,-]*)/instance", str(request))
    model_id = UUID(match[1])

    model = next((model for model in data_models if UUID(model["model_uuid"]) == model_id), None)
    return [{key: instance[key] for key in keys} for instance in model["instances"]]


@cache_controlled
def instance(request, context):
    match = re.search(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)", str(request))
    model_id = UUID(match[1])
    instance_id = UUID(match[2])

    model = next((model for model in data_models if UUID(model["model_uuid"]) == model_id), None)

    instance = next((instance for instance in model["instances"] if UUID(instance["instance_uuid"]) == instance_id), None,)
    return instance


@cache_controlled
def instance_parameter(request, context):
    return instance(request, context)["parameter"]


@cache_controlled
def instance_parameter_set(request, context):
    match = re.search(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)/parameter", str(request))
    model_id = UUID(match[1])
    instance_id = UUID(match[2])

    req = json.loads(request.text)
    param_id = UUID(req["param_uuid"])
    param_value = req["value"]

    for idx_m, model in enumerate(data_models):
        if UUID(model["model_uuid"]) == model_id:
            for idx_i, instance in enumerate(model["instances"]):
                if UUID(instance["instance_uuid"]) == instance_id:
                    for idx_p, param in enumerate(instance["parameter"]):
                        if param_id == UUID(param["param_uuid"]):
                            data_models[idx_m]["instances"][idx_i]["parameter"][idx_p]["value"] = param_value
                            context.status_code = 200
                            return {}

    context.status_code = 404
    return {}
