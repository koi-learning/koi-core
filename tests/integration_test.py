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

import io
import koi_core as koi


def run_all_models(persistence=None):
    koi.init()

    if persistence:
        pool = koi.create_api_object_pool(
            host="testing://base",
            username="user",
            password="password",
            persistance_file=persistence,
        )
    else:
        pool = koi.create_api_object_pool(
            host="testing://base",
            username="user",
            password="password"
        )
    models = pool.get_all_models()
    for model in models:
        instances = model.instances
        for instance in instances:
            koi.control.train(instance, dev=True)

    koi.deinit()


def test_training(api_mock):
    run_all_models()


def test_persistive_caching(api_mock):
    persistence = io.BytesIO()
    run_all_models(persistence)
    api_calls = api_mock.call_count
    api_mock.reset_mock()

    assert persistence.tell() > 0  # check that we actually persitified something

    persistence.seek(0)
    persistence.truncate()  # note we reset the persitive file here
    run_all_models(persistence)
    assert (
        api_mock.call_count == api_calls
    )  # check that the second iteration still calls the api
    api_mock.reset_mock()

    persistence.seek(0)
    run_all_models(persistence)
    assert (
        api_mock.call_count < api_calls
    )  # check that the this iteration calls the api less often
    api_mock.reset_mock()
