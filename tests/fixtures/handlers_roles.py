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
from uuid import UUID, uuid1
from .handlers_common import paged, cache_controlled
from .common_data import (
    data_roles_model,
    data_roles_instance,
    data_roles_general,
    data_access_general,
    data_access_model,
    data_access_instance,
)


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
    match = re.search(r"http://base/api/userroles/(\w*)/([0-9,a-f,-]*)", str(request))
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
                role.update(request.json())
                return role

    else:
        context.status_code = 405
        return {}


def access_general(request, context):
    match = re.search(r"http://base/api/access((/)([0-9,a-f,-]*))?", str(request))
    access_uuid = match[3]
    if access_uuid is not None:
        access_uuid = UUID(access_uuid)

    if request._request.method == "GET":
        if access_uuid is None:
            context.status_code = 200
            return data_access_general
        else:
            for access in data_access_general:
                if UUID(access["access_uuid"]) == access_uuid:
                    context.status_code = 200
                    return access
    elif request._request.method == "POST" and access_uuid is None:
        new_access = request.json()
        new_access["access_uuid"] = str(uuid1())
        data_access_general.append(new_access)
        context.status_code = 200
        return {}

    elif request._request.method == "DELETE" and access_uuid is not None:
        for access in data_access_general:
            if UUID(access["access_uuid"]) == access_uuid:
                data_access_general.remove(access)
                context.status_code = 200
                return {}
    else:
        context.status_code = 405
        return {}


def access_model(request, context):
    match = re.search(r"http://base/api/model/([0-9,a-f,-]*)/access((/)([0-9,a-f,-]*))?", str(request))

    access_uuid = match[4]
    if access_uuid is not None:
        access_uuid = UUID(access_uuid)

    if request._request.method == "GET":
        if access_uuid is None:
            context.status_code = 200
            return data_access_model
        else:
            for access in data_access_model:
                if UUID(access["access_uuid"]) == access_uuid:
                    context.status_code = 200
                    return access

    elif request._request.method == "POST" and access_uuid is None:
        new_access = request.json()
        new_access["access_uuid"] = uuid1().hex
        new_access["model_uuid"] = UUID(match[1]).hex
        data_access_model.append(new_access)
        context.status_code = 200
        return {}

    elif request._request.method == "DELETE" and access_uuid is not None:
        temp_access = list(data_access_model)
        for access in temp_access:
            if UUID(access["access_uuid"]) == access_uuid:
                data_access_model.remove(access)
                context.status_code = 200
                return {}
    else:
        context.status_code = 405
        return {}


def access_instance(request, context):
    match = re.search(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)/access((/)([0-9,a-f,-]*))?", str(request))

    access_uuid = match[5]
    if access_uuid is not None:
        access_uuid = UUID(access_uuid)

    if request._request.method == "GET":
        if access_uuid is None:
            context.status_code = 200
            return data_access_instance
        else:
            for access in data_access_instance:
                if UUID(access["access_uuid"]) == access_uuid:
                    context.status_code = 200
                    return access

    elif request._request.method == "POST" and access_uuid is None:
        new_access = request.json()
        new_access["access_uuid"] = uuid1().hex
        new_access["instance_uuid"] = UUID(match[2]).hex
        data_access_instance.append(new_access)
        context.status_code = 200
        return {}

    elif request._request.method == "DELETE" and access_uuid is not None:
        temp_access = list(data_access_instance)
        for access in temp_access:
            if UUID(access["access_uuid"]) == access_uuid:
                data_access_instance.remove(access)
                context.status_code = 200
                return {}
    else:
        context.status_code = 405
        return {}
