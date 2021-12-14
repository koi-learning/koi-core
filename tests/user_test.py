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

import koi_core as koi


def test_get_users(api_mock):
    koi.init()
    # create pool
    pool = koi.create_api_object_pool(host="http://base", username="user", password="password")

    users = list(pool.get_all_users())
    assert len(users) > 0

    user = users[0]

    assert user.name == "admin"

    user = users[2]
    assert user.name == "user2"
    user.name = "user2_new"
    assert user.name == "user2_new"

    koi.deinit()
