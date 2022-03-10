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

from io import BytesIO
from zipfile import ZipFile
from tempfile import TemporaryDirectory
import koi_core as koi


def test_code_namelist(api_mock):
    koi.init()

    pool = koi.create_api_object_pool(host="http://base", username="user", password="password")

    # get the first model of the pool
    model = next(pool.get_all_models(), None)
    assert model is not None

    # get the code of the model
    remote_code = model.code
    code_bytes = remote_code.toBytes()

    # read th zip file from the code object
    code_zip = ZipFile(BytesIO(code_bytes), mode='r')

    # extract zipfile into temporary directory
    temp_dir = TemporaryDirectory()
    code_zip.extractall(temp_dir.name)

    # load as local code
    local_code = koi.resources.model.LocalCode(temp_dir.name)

    assert list(local_code.gen_namelist()) == list(remote_code.gen_namelist())

    temp_dir.cleanup()
