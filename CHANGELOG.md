# CHANGELOG

## 2.2.2

- `getSlice` returns a numpy array. numpy package is now a requirement.
- Minor improvement in the output of arinfopy summary.

## 2.2.1

- Updated documentation.

## 2.2.0

- Added `getSlice(variable, slice, deadline)` to select a specific deadline and slice (for 3D variables) of the requested variable. This method should also improve the efficiency of 3D data recovery.

## 2.1.0

- Stripping whitespaces from variables names.

- The deadline argument of `getRecord7` is 1-based. If `deadline=0` is passed to the function a `ValueError` is raised.

## 2.0

- Many bugfixes and code cleanup.

- Converted to python3 (still compatible with python2).

- All summary informations are read.

- Added `minmax` option.

- It can be called by other modules.

- Added method to get the list of deadlines.

## 1.0

- First basic working version.
