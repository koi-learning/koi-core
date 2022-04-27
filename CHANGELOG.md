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