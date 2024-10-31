# CHANGELOG

## 3.2.2

- Update documentation adding `pipx` as a method of installation.
- Remove `pytz` dependency to use standard library. Python 3.9 is now required.

## 3.2.1

- Add `pytz` dependency.

## 3.2.0

- Deadlines now have "UTC" time zone.
- Corrected type in the changelog and updated README file.

## 3.1.0

- Net API function `getDataset(variable)` returning a numpy array with the full
 dataset as [time, x, y, z] for 3D variables or [time, x, y] for 2D variable.

## 3.0.0

- Upload code to PyPI.
- Generate `arinfopy` binary executable.

## 2.3.4

- Make code PEP8 compliant

## 2.3.3

- Fixed bug writing `ztop` in record 4.
- Fixed bug computing deadlines period.

## 2.3.2

- Fixed bug in reading the names of 2D and 3D variables.

## 2.3.1

- Bugfix

## 2.3.0

- `arinfopy` gets `adsowritebin` class to write adso/bin files (thanks to Bruno Guillaume).

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
