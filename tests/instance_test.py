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
import pytest


def test_instance_parameter(api_mock):
    koi.init()

    # create pool and get the first instance of the first model
    pool = koi.create_api_object_pool(host="http://base", username="user", password="password")

    model = next(pool.get_all_models(), None)

    assert model is not None

    inst = next(model.instances, None)

    assert inst is not None

    # get the current values of the our instance parameters
    value1 = inst.parameter["param1"]
    value2 = inst.parameter["param2"]

    # increment the parameter values
    inst.parameter["param1"] = value1 + 1
    inst.parameter["param2"] = value2 + 1.0

    # check the new values
    assert inst.parameter["param1"] == value1 + 1
    assert inst.parameter["param2"] == value2 + 1.0

    # test the type checking
    with pytest.raises(TypeError):
        inst.parameter["param1"] = 15.0

    with pytest.raises(TypeError):
        inst.parameter["param2"] = "15"
