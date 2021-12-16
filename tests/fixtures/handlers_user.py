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
from datetime import datetime, timedelta
from uuid import UUID
from .handlers_common import paged, cache_controlled
from .common_data import data_users


def login(request, context):
    token_valid = datetime.now() + timedelta(minutes=500)

    context.status_code = 200
    return {
        "user_uuid": "00000000-0000-1000-8000-000000000000",
        "token": "00000000000000000000000000000000",
        "expires": token_valid.isoformat(),
    }


@cache_controlled
@paged
def users(request, context, page_offset, page_size):
    context.status_code = 200
    return data_users[page_offset: page_offset + page_size]


@cache_controlled
def user(request, context):
    match = re.search(r"http://base/api/user/([0-9,a-f,-]*)", str(request))
    user_id = UUID(match[1])
    user = next(filter(lambda x: UUID(x["user_uuid"]) == user_id, data_users), None)

    if request._request.method == "GET":
        if user is None:
            context.status_code = 404
            return {}
        context.status_code = 200
        return user

    elif request._request.method == "PUT":
        context.status_code = 200
        new_user = request.json()
        for u in data_users:
            if UUID(u["user_uuid"]) == user_id:
                u.update(new_user)
                return u

    else:
        context.status_code = 405
        return {}
