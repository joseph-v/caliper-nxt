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


class Hardwareinfo(Test):

    """
    Hardware information about the platform undertest
    """

    def setUp(self):
        """
        Build Hardwareinfo
        """
        data_dir = os.path.abspath(self.datadir)
        self.srcdir = os.path.join(data_dir, 'source_code')

        os.chdir(self.srcdir)
        exec_path = os.path.join(self.srcdir, 'bin')
        if not os.path.exists(exec_path):
            try:
                os.mkdir(exec_path)
            except:
                print "Failed to create bin folder"
                return -1

        process.run('cp hw_info_run.sh ./bin/hw_info_run.sh')


    def test(self):

        path = os.path.join(self.srcdir, 'bin')
        os.chdir(path)

        start_log = "%%%%%%         hardwareinfo test start       %%%%%% \n"
        echo_cmd = "echo '%s' " % start_log
        process.run(echo_cmd)
        echo_cmd = "echo '<<BEGIN TEST>>>'"
        process.run(echo_cmd)
        try:
            process.run('./hw_info_run.sh')
        except Exception:
            status = 'FAIL'
        else:
            status = 'PASS'
        echo_cmd = "echo '[status]: %s' " % status
        process.run(echo_cmd)
        echo_cmd = "echo '<<<END>>>'"
        process.run(echo_cmd)
        echo_cmd = "echo '%%%%%% test_end %%%%%%'"
        process.run(echo_cmd)

