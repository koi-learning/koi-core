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
from .handlers_common import paged, cache_controlled
from .common_data import data_roles_model, data_roles_instance, data_roles_general


@cache_controlled
@paged
def roles(request, context, page_offset, page_size):
    match = re.search(r"http://base/api/userroles/(\w*)", str(request))
    t = match[1]

    if t == "general":
        data = data_roles_general
    elif t == "model":
        data = data_roles_model
    elif t == "instance":
        data = data_roles_instance
    else:
        context.status_code = 404
        return

    context.status_code = 200
    return data[page_offset: page_offset + page_size]


def role(request, context):
    match = re.search(r"http://base/api/userroles/(\w*)/(\d*)", str(request))
    role_id = UUID(match[2])
    t = match[1]

    if t == "general":
        data = data_roles_general
    elif t == "model":
        data = data_roles_model
    elif t == "instance":
        data = data_roles_instance
    else:
        context.status_code = 404
        return

    role = next(filter(lambda x: UUID(x["role_uuid"]) == role_id, data), None)

    if role is None:
        context.status_code = 404
        return {}

    if request._request.method == "GET":
        context.status_code = 200
        return role

    elif request._request.method == "PUT":
        context.status_code = 200
        for role in data:
            if UUID(role["role_uuid"]) == role_id:
                role.update(request.json)
                return role

    else:
        context.status_code = 405
        return {}
