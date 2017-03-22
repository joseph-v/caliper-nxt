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

import os
import tempfile

from avocado import Test
from avocado import main
from avocado.utils import archive
from avocado.utils import process
from avocado.utils import build
from avocado.utils import distro
from avocado.utils.software_manager import SoftwareManager

def start_marker(cmd):
    start_log = "%%%%%%         %s test start       %%%%%% \n" % cmd
    echo_cmd = "echo '%s' " % start_log
    process.run(echo_cmd)
    echo_cmd = "echo '<<BEGIN TEST>>>'"
    process.run(echo_cmd)

def end_marker(status):
    echo_cmd = "echo '[status]: %s' " % status
    process.run(echo_cmd)
    echo_cmd = "echo '<<<END>>>'"
    process.run(echo_cmd)
    echo_cmd = "echo '%%%%%% test_end %%%%%%'"
    process.run(echo_cmd)


class Dhrystone(Test):
    """
    Benchmark Dhrystone
    """

    def setUp(self):
        """
        Build dhrystone
        """
        smm = SoftwareManager()
        if not smm.check_installed("gcc") and not smm.install("gcc"):
            self.error("Gcc is needed for the test to be run")
        data_dir = os.path.abspath(self.datadir)
        self.srcdir = os.path.join(data_dir, 'source_code')

        os.chdir(self.srcdir)

        d_distro = distro.detect()
        arch = d_distro.arch
        if arch == 'aarch32':
            build.make(self.srcdir, extra_args='CC=gcc \'CFLAGS=-static -O3 -Icommon_32bit -lrt -lm\' -s')
        elif arch == 'aarch64':
            build.make(self.srcdir, extra_args='CC=gcc \'CFLAGS=-static -O3 -funroll-loops -Icommon_64bit -lrt -lm\' -s')
        elif arch == 'x86_64':
            build.make(self.srcdir, extra_args='CC=gcc \'CFLAGS=-O3 -Icommon_64bit -lrt -lm\' -s')
        else:
            build.make(self.srcdir, extra_args='linux')

        exec_path = os.path.join(self.srcdir, 'bin')
        if not os.path.exists(exec_path):
            try:
                os.mkdir(exec_path)
            except:
                print "Failed to create bin folder"
                return -1

        process.run('cp dhry1 dhry2 lloops lpack whets ./bin/')
        process.run('make CC=gcc clean')

    def test(self):

        path = os.path.join(self.srcdir, 'bin')
        os.chdir(path)

        # ====First case===============
        start_marker('dhry1')

        try:
            process.run('./dhry1')
        except Exception:
            status = 'FAIL'
        else:
            status = 'PASS'

        end_marker(status)

        #====Second case================
        start_marker('dhry2')
        try:
            process.run('./dhry2')
        except Exception:
            status = 'FAIL'
        else:
            status = 'PASS'

        end_marker(status)

        #====Third case================
        start_marker('whets')

        try:
            process.run('./whets')
        except Exception:
            status = 'FAIL'
        else:
            status = 'PASS'

        end_marker(status)
