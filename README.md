# Miney Distribution

This build script compiles the miney distribution. For now it's only for windows.

It includes:

* Minetest with mineysocket
* Python with preinstalled miney
* A launcher for quickstart

This build_minetest script downloads all needed sources and compiles them, so it can take some time depending on your hardware.
It's far easier to just download a precompiled release from the release page of this project.

## Requirements 

- python
- git
- Visual Studio 2019 Build Tools

## Usage


    git clone --recurse-submodules https://github.com/miney-py/miney_distribution.git
    cd miney_distribution
    python build.py <x86/x64>

## LICENSE

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
