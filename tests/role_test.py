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


def helper_check_role(user, role, object=None):
    assert user.has_role(role, object) is False

    user.grant_access(role, object)

    assert user.has_role(role, object) is True

    user.revoke_access(role, object)

    assert user.has_role(role, object) is False


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


def test_user_check_grant_revoke_general_access(api_mock):
    koi.init()

    pool = koi.create_api_object_pool(host="http://base", username="user", password="password")

    roles = list(pool.get_all_general_roles())

    user = next(pool.get_all_users())

    helper_check_role(user, roles[0])

    koi.deinit()


def test_user_check_grant_revoke_model_access(api_mock):
    koi.init()

    pool = koi.create_api_object_pool(host="http://base", username="user", password="password")

    roles = list(pool.get_all_model_roles())

    user = next(pool.get_all_users())

    model = next(pool.get_all_models())

    assert user.has_role(roles[0], model) is True

    helper_check_role(user, roles[1], model)

    koi.deinit()


def test_user_check_grant_revoke_instance_access(api_mock):
    koi.init()

    pool = koi.create_api_object_pool(host="http://base", username="user", password="password")

    roles = list(pool.get_all_instance_roles())

    user = next(pool.get_all_users())

    model = next(pool.get_all_models())

    instance = next(model.instances)

    assert user.has_role(roles[0], instance) is True

    helper_check_role(user, roles[1], instance)

    koi.deinit()
