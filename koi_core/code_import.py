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

from typing import TYPE_CHECKING, Union
import zipfile
import io
from os import makedirs
from os.path import sep, dirname
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
from importlib import import_module

if TYPE_CHECKING:
    from koi_core.resources.model import Code


class KoiCodeLoader(Loader, MetaPathFinder):
    _modules = dict()
    _prefix = 'user_code'
    _param_module = _prefix + '.__param__'

    def __init__(self, code: Union['Code', str, bytes], param_dict, temp_dir=None):
        self._code = code

        if type(self._code) in [bytes, str]:
            if type(self._code) == bytes:
                self._code = io.BytesIO(self._code)
            self._archive = zipfile.ZipFile(self._code, mode="r")
            self._namelist = self._archive.namelist()
        else:
            self._archive = None
            self._namelist = list(self._code.gen_namelist())

        self._params = param_dict
        self._temp_dir = temp_dir
        self._extract_noncode()

    def _extract_noncode(self):
        if self._temp_dir is not None:
            for f in self._namelist:
                if not f.endswith(".py") and not f.endswith(".pyc"):
                    if self._archive is None:
                        data_raw = self._code.read(f)
                    else:
                        data_raw = self._archive.read(f)

                    # make sub dirs if they dont exist
                    makedirs(dirname(self._temp_dir + sep + f), exist_ok=True)

                    # write file to temp directory
                    data_file = open(self._temp_dir + sep + f, 'wb')
                    data_file.write(data_raw)
                    data_file.close()

    def exec_module(self, module):
        fullname = module.__name__
        if fullname == self._param_module:
            module.__dict__.update(self._params)
        else:
            code = self._get_module_code(module.__spec__.origin)
            # module.__path__=self._prefix
            module.__param__ = import_module(self._param_module)
            exec(code, module.__dict__)

    def find_spec(self, fullname, paths=None, target=None):
        try:
            path, is_package = self._find_module(fullname)
        except KeyError:
            return None
        return ModuleSpec(fullname, self, origin=path, is_package=is_package)

    def _find_module(self, fullname):
        # make sure that the fullname begins with "{_prefix}." where the dot is optional
        if not fullname[:len(self._prefix)] == self._prefix:
            raise KeyError()
        path = fullname[len(self._prefix):]
        if len(path) > 0:
            if path[0] == '.':
                path = path[1:]
            else:
                raise KeyError()

        if path == '':
            # check if we try to import "user_code" which means we want to import "__model__.py"
            for p in ['__model__.pyc', '__model__.py']:
                if p in self._namelist:
                    if self._archive is None:
                        return self._code.build_path(p), True
                    else:
                        return p, True

        else:
            # check if there is a package with the name
            for p in [path+sep+'__init__.pyc', path+sep+'__init__.py']:
                if p in self._namelist:
                    return p, True
            # check if a module with the name is avaiable
            for p in [path+'.pyc', path+'.py']:
                if p in self._namelist:
                    return p, False

        raise KeyError()

    def _get_module_code(self, path):
        if path[-3:] == '.py':
            # check that we are not using a local zip
            if self._archive is None:
                code = self._code.read(path)
                return compile(code, path, 'exec', dont_inherit=True)
            else:
                code = self._archive.read(path)
                return compile(code, 'ZipFile:'+path, 'exec', dont_inherit=True)
        elif path[-4:] == '.pyc':
            raise NotImplementedError('Can not load bytecode')
        else:
            raise NotImplementedError('Unknown fileextension')
