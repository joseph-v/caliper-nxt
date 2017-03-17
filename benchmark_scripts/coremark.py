#!/usr/bin/env python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.

import os
import tempfile

from avocado import Test
from avocado import main
from avocado.utils import archive
from avocado.utils import process
from avocado.utils import build
from avocado.utils import distro
from avocado.utils.software_manager import SoftwareManager


class Coremark(Test):
    """
    Benchmark Coremark performances
    """

    def setUp(self):
        """
        Build coremark
        """
        smm = SoftwareManager()
        if not smm.check_installed("gcc") and not smm.install("gcc"):
            self.error("Gcc is needed for the test to be run")

        data_dir = os.path.abspath(self.datadir)
        self.srcdir = os.path.join(data_dir, 'source_code')

        os.chdir(self.srcdir)

        d_distro = distro.detect()
        arch = d_distro.arch
        if arch == 'aarch32' or arch == 'aarch64':
            build.make(self.srcdir, extra_args='PORT_DIR=linux64 CC=gcc compile')
        elif arch == 'x86_64':
            build.make(self.srcdir, extra_args='PORT_DIR=linux64 CC=gcc \'XCFLAGS=-msse4\' compile')
        else:
            build.make(self.srcdir, extra_args='linux')

        os.chdir(self.srcdir)
        process.run('cp coremark.exe ./bin/coremark')
        process.run('make PORT_DIR=linux64 CC=$GCC clean')

    def test(self):

        os.chdir(os.path.join(self.srcdir, 'bin'))
        process.run("echo '%%%%%%         coremark test start       %%%%%% \n' ")
        process.run("echo '<<BEGIN TEST>>>'")
        try:
            process.run('./coremark')
        except Exception:
            status = 'FAIL'
        else:
            status = 'PASS'
        echo_cmd = "echo '[status]: %s' " % status
        process.run(echo_cmd)
        process.run("echo '<<<END>>>'")
        process.run("echo '%%%%%% test_end %%%%%%'")
