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

from typing import TypeVar
from functools import wraps
from datetime import datetime


T = TypeVar("T")


def cache_controlled(func: T) -> T:
    @wraps(func)
    def wrapper(request, context):
        context.headers["Expires"] = datetime(2050, 12, 10).strftime("%a, %d %b %Y %H:%M:%S GMT")
        context.headers["Last-Modified"] = datetime(2020, 12, 10).strftime("%a, %d %b %Y %H:%M:%S GMT")
        return func(request, context)

    return wrapper


def paged(func: T) -> T:
    @wraps(func)
    def wrapper(request, context):
        page_offset = 0
        page_size = 100
        if "page_offset" in request.qs:
            page_offset = int(request.qs["page_offset"][0])
        if "page_size" in request.qs:
            page_size = int(request.qs["page_size"][0])
        return func(request, context, page_offset, page_size)

    return wrapper
