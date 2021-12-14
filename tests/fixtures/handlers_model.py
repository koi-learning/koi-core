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
from uuid import UUID
from .handlers_common import cache_controlled
from .common_data import data_models, data_code


@cache_controlled
def models(request, context):
    keys = [
        "finalized",
        "has_code",
        "has_label_plugin",
        "has_visual_plugin",
        "model_description",
        "model_name",
        "model_uuid",
    ]
    return [{key: model[key] for key in keys} for model in data_models]


@cache_controlled
def model_code(request, context):
    match = re.search(r"http://base/api/model/(\d*)/code", str(request))
    model_id = UUID(match[1])

    model = next((model for model in data_models if model["model_uuid"] == model_id), None)
    return data_code[model["code"]]


@cache_controlled
def model_parameter(request, context):
    match = re.search(r"http://base/api/model/(\d*)/parameter", str(request))
    model_id = UUID(match[1])

    model = next((model for model in data_models if model["model_uuid"] == model_id), None)
    if model is not None:
        return model["parameter"]
    else:
        return []
