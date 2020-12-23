# arinfopy

`arinfopy` is a Python library to read and write **ADSO/BIN** files generated by atmospheric dispersion models such as [SPRAY][spray], [FARM][farm] and others.

It also includes the following command line tools:

- `arinfopy`

It requires Python 3.5.x. Python2 is unsupported.

## Installation

From `PyPI` with `pip`:

```sh
pip install arinfopy
```

You either want to do this into a *user* environment (putting the `arinofpy` executable in `~/.local/bin/arinfopy`) like this:

```sh
pip install --user arinfopy
```

or put it into a virtualenv, to avoid modifying the system python’s libraries, like this:

```sh
python3 -m venv ./venv
source venv/bin/activate
pip install arinfopy
```

You probably don’t want to use `sudo` when you run `pip`.

## Use

You can use the command line tools as follows.

```sh
> arinfopy --help
usage: arinfopy [-h] [-minmax] [-deadlines] [-v] inifile

arinfopy parser for ADSO/bin files.

positional arguments:
  inifile        File to be parsed

optional arguments:
  -h, --help     show this help message and exit
  -minmax        Show min/max values for each deadline
  -deadlines     Show deadlines
  -v, --verbose  Increse output verbosity.
```

## API

`arinfopy` can also be used an external module in other `python` scripts to read and write **ADSO/BIN** files.

## Who Are You

We are [Simularia][simularia] and we do numerical simulations of atmospheric phenomena and data analysis with `R` and `Python`.

## Contributors

Giuseppe Carlino (Simularia) g.carlino@simularia.it

Bruno Guillaume (ARIA Technologies)                         bguillaume@aria.fr

Matteo Paolo Costa (Arianet s.r.l.) costa@aria-net.it

## License

arinfopy parser for ADSO/bin files.
Copyright (C) 2013  Simularia s.r.l. info@simularia.it

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Simularia S.r.l.
via Sant'Antonio da Padova 12
Torino, Italy
[www.simularia.it][simularia]
<info@simularia.it>

[spray]:http://www.aria-net.it/
[farm]:http://www.aria-net.it
[simularia]:https://www.simularia.it
