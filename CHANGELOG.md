# Changelog
## 0.3
- Added proxies for users and access objects
- Added tests for user access
- changed the transfer protocol for request_mock to http, as requests does not support url parameters with custom url schemes
- fixed some minor code smells
### 0.3.1 -0.3.3
- fixed a major bug when accessing roles
- more bug fixes for role access
### 0.3.4
- added support for additional files in model zip files
- unified the code loaders for remote and local code
### 0.3.5
- multiple RunableInstances can be used (when using a command from the control namespace the number of allowed instances is now an optional parameter)
### 0.3.6
- added missing check for user id in "has_role"
- fixed tests for role management
### 0.3.7
- added "last_modified" field to instances and models --> This needs koi_api version to be 0.3.3+!
### 0.3.8
- made koi_core compatible with Python3.6
- added tagged releases on github
### 0.3.9
- fixed the persistence functions
- using UUID as id for every object as hash() is salted for strings since Py3.3
## 0.4
- added `is_koi_reachable(base_url: str)`
- added `try_create_api_object_pool(...)`
### 0.4.1
- removed setup.py
- added pyproject.toml
- use of entrypoints instead of scripts
