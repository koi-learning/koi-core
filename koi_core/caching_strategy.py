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

from datetime import datetime


class CachingMeta:
    expires: datetime
    last_modified: datetime


class ExpireCachingStrategy:
    def isValid(self, proxy, key, meta):
        now = datetime.utcnow()

        if meta is None or now >= meta.expires:
            return False
        else:
            return True


class LocalOnlyCachingStrategy:
    def isValid(self, proxy, key, meta):
        return True
