"""
Build a miney distribution for windows.

Copyright (C) 2019 Robert Lieback <robertlieback@zetabyte.de>

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
"""
import os
from os import path
import sys
from subprocess import run
import logging
from datetime import datetime
from distutils.dir_util import copy_tree
from shutil import copyfile as copy_file
import urllib.request

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - MINEYDIST - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

start_time = datetime.now()

if len(sys.argv) > 1:
    if "x86" in sys.argv:
        ARCH = "x86"
    elif "x64" in sys.argv:
        ARCH = "x64"
    else:
        ARCH = "x86"
else:
    ARCH = "x86"
logger.info(f"Set CPU architecture to {ARCH}")

join = path.join

ROOT_PATH = os.getcwd()
BUILD = join(ROOT_PATH, "build")
DIST = join(ROOT_PATH, "dist")
REPOS = join(ROOT_PATH, "repos")
MINEY = join(DIST, "miney_" + ARCH)
MINETEST = join(MINEY, "Minetest")
PYTHON = join(MINEY, "Python")

if not path.isdir(BUILD): os.mkdir(BUILD)
if not path.isdir(DIST): os.mkdir(DIST)
if not path.isdir(MINEY): os.mkdir(MINEY)

if not path.isdir(join(DIST, "minetest_" + ARCH)):
    logger.info(f"Minetest - Not found minetest_{ARCH} in dist folder, start compilation")
    ret = run(["python", join("repos", "minetest-windows", "build_minetest.py"), ARCH], cwd=ROOT_PATH)
    if ret.returncode != 0:
        raise Exception("Couldn't compile minetest")
else:
    logger.info("Minetest - Found minetest in dist")

if not path.isdir(MINETEST):
    logger.info(f"Copy minetest to {MINEY}")
    copy_tree(join(DIST, "minetest_" + ARCH), MINETEST)
else:
    logger.info(f"minetest found in {MINETEST}")

if not path.isdir(join(MINETEST, "mods", "mineysocket")):
    logger.info("Copy mineysocket into minetest mods directory")
    copy_tree(join(REPOS, "mineysocket"), join(MINETEST, "mods", "mineysocket"))
    os.unlink(join(MINETEST, "mods", "mineysocket", ".git"))
else:
    logger.info("Found mineysocket in minetest mods directory")

if not path.isfile(join(MINETEST, "minetest.conf")):
    logger.info("Adding mineysocket as trusted_mods to minetest.conf")
    with open(join(MINETEST, "minetest.conf"), "w") as f:
        f.write("secure.trusted_mods = mineysocket\n")
else:
    logger.info("Found minetest.conf")

if not path.isdir(PYTHON):
    logger.info("Downloading and installing Python")

    if path.isfile(join(BUILD, ARCH, "python.exe")):
        os.unlink(join(BUILD, ARCH, "python.exe"))
    if path.isdir(join(BUILD, ARCH, "python_tmp")):
        os.system(f'rmdir /s /q "{join(BUILD, ARCH, "python_tmp")}"')

    if ARCH == "x64":
        urllib.request.urlretrieve(
            "https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64-webinstall.exe",
            join(BUILD, ARCH, "python.exe")
        )
    else:
        urllib.request.urlretrieve(
            "https://www.python.org/ftp/python/3.9.0/python-3.9.0-webinstall.exe", join(BUILD, ARCH, "python.exe"))
    run([join(BUILD, ARCH, "python.exe"), "/quiet", "/layout", join(BUILD, ARCH, "python_tmp")])
    logger.info("Installing python msi files")
    run(["msiexec.exe", "/quiet", "/a", join(BUILD, ARCH, "python_tmp", "core.msi"), f"targetdir={PYTHON}"])
    run(["msiexec.exe", "/quiet", "/a", join(BUILD, ARCH, "python_tmp", "doc.msi"), f"targetdir={PYTHON}"])
    run(["msiexec.exe", "/quiet", "/a", join(BUILD, ARCH, "python_tmp", "exe.msi"), f"targetdir={PYTHON}"])
    run(["msiexec.exe", "/quiet", "/a", join(BUILD, ARCH, "python_tmp", "lib.msi"), f"targetdir={PYTHON}"])
    run(["msiexec.exe", "/quiet", "/a", join(BUILD, ARCH, "python_tmp", "tcltk.msi"), f"targetdir={PYTHON}"])
    run(["msiexec.exe", "/quiet", "/a", join(BUILD, ARCH, "python_tmp", "tools.msi"), f"targetdir={PYTHON}"])
    os.system(f"del {PYTHON}\\*.msi")

    logger.info("Installing pip")
    urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", join(BUILD, ARCH, "python_tmp", "get-pip.py"))
    run([join(PYTHON, "python.exe"), join(BUILD, ARCH, "python_tmp", "get-pip.py")], cwd=PYTHON)
else:
    logger.info("Found Python directory")

if not path.isdir(join(PYTHON, "Lib", "site-packages", "miney")):
    logger.info("Installing miney with pip")
    run([join(PYTHON, "python.exe"), "-m", "pip", "install", "miney"], cwd=PYTHON)
else:
    logger.info("Found miney in python packages")

if not path.isfile(join(MINEY, "miney_launcher.exe")):
    logger.info("Installing launcher")

    if not path.isdir(join(MINEY, "Miney")):
        os.mkdir(join(MINEY, "Miney"))

    if not path.isdir(join(MINEY, "Miney", "examples")):
        os.mkdir(join(MINEY, "Miney", "examples"))

    copy_file(join(REPOS, "launcher", "win32", "launcher.exe"), join(MINEY, "miney_launcher.exe"))
    copy_file(join(REPOS, "launcher", "launcher.py"), join(MINEY, "Miney", "launcher.py"))
    copy_file(join(REPOS, "launcher", "quickstart.py"), join(MINEY, "Miney", "quickstart.py"))
    copy_file(join(REPOS, "launcher", "LICENSE"), join(MINEY, "Miney", "LICENSE"))
    copy_tree(join(REPOS, "launcher", "res"), join(MINEY, "Miney", "res"))
else:
    logger.info("Found launcher")

if not path.isdir(join(MINEY, "Minetest", "worlds", "Miney")):
    logger.info("Create miney default world")
    if not path.isdir(join(MINEY, "Minetest", "worlds", "Miney")):
        os.mkdir(join(MINEY, "Minetest", "worlds", "Miney"))

    with open(join(MINEY, "Minetest", "worlds", "Miney", "world.mt"), "w") as f:
        f.write("enable_damage = true\n")
        f.write("creative_mode = false\n")
        f.write("gameid = minetest\n")
        f.write("player_backend = sqlite3\n")
        f.write("backend = sqlite3\n")
        f.write("auth_backend = sqlite3\n")
        f.write("load_mod_mineysocket = true\n")
        f.write("server_announce = false\n")
        f.write("seed = 746036489947438842\n")

logger.info(
    "### That run took " + str(datetime.now() - start_time) + "\nYour finished Miney distribution directory: " + MINEY
)
