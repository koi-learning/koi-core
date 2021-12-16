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


def test_get_roles(api_mock):
    koi.init()

    pool = koi.create_api_object_pool(host="http://base", username="user", password="password")

    general_roles = list(pool.get_all_general_roles())
    model_roles = list(pool.get_all_model_roles())
    instance_roles = list(pool.get_all_instance_roles())

    assert len(general_roles) == 2
    assert len(model_roles) == 2
    assert len(instance_roles) == 2

    koi.deinit()


def test_user_check_grant_revoke_access(api_mock):
    koi.init()

    pool = koi.create_api_object_pool(host="http://base", username="user", password="password")

    roles = list(pool.get_all_general_roles())

    user = next(pool.get_all_users())

    assert user.has_role(roles[1]) is False

    user.grant_access(roles[1])

    assert user.has_role(roles[1]) is True

    user.revoke_access(roles[1])

    assert user.has_role(roles[1]) is False

    koi.deinit()
