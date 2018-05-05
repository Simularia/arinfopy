arinfopy
========

`arinfopy` is a parser for **ADSO/BIN** files written in python.
It requires Python 3.5.x but it is also working with Python 2.7.x (unsupported).

Use
---

You can either use it as an ordinary executable: `$ ./arinfopy.py  filename` or as a python script: `$ python arinfopy.py filename`.

For more details and some options see help: `$ ./arinfopy.py -h`.

API
---

`arinfopy` can also be used an external module in other `python` scripts to acces **ADSO/BIN** files.

Features
--------

It currently supports ADSO/bin files generated by atmospheric dispersion models such as [SPRAY][spray] and others.

Installation
------------

In order to ues is at as a module library, you can install it with the `pip` utility in the active python installation,  as:
```
> pip install git+https://github.com/Simularia/arinfopy
```

To use at as a command line utility, you have to clone locally the remote repository and possibly link `arinfopy.py` in a folder included in your `$PATH`, as in:
```
> git clone https://github.com/Simularia/arinfopy
> cd arinfopy
> ln -s arinfopy.py ~/bin/arinfo
> arinfo test_file.bin
```

Who Are You?
------------

We are [Simularia][simularia] and we do numerical simulations of 
atmospheric phenomena and data analysis with `R` and `Python`.

License
-------

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
via Principe Tommaso 39
Torino, Italy
[www.simularia.it][simularia]
<info@simularia.it>

[spray]:http://www.aria-net.it/
[simularia]:http://www.simularia.it
