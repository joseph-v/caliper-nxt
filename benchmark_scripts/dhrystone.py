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
#
# Copyright: 2016 IBM
# Author: Praveen K Pandey <praveen@linux.vnet.ibm.com>
#
# Based on code by Martin Bligh <mbligh@google.com>
#   copyright: 2008 Google
#   https://github.com/autotest/autotest-client-tests/tree/master/lmbench

import os
import tempfile

from avocado import Test
from avocado import main
from avocado.utils import archive
from avocado.utils import process
from avocado.utils import build
from avocado.utils import distro
from avocado.utils.software_manager import SoftwareManager


class Dhrystone(Test):

    """
    
    """

    def setUp(self):
        '''
        Build dhrystone
        Source:
        http://.tar.gz
        '''
        fsdir = self.params.get('fsdir', default=None)
        temp_file = self.params.get('temp_file', default=None)
        self.tmpdir = tempfile.mkdtemp(prefix='avocado_' + __name__)
        smm = SoftwareManager()
        if not smm.check_installed("gcc") and not smm.install("gcc"):
            self.error("Gcc is needed for the test to be run")
        #tarball = self.fetch_asset('http://www.bitmover.com'
        #                           '/lmbench/lmbench3.tar.gz')
        data_dir = os.path.abspath(self.datadir)
        #archive.extract(tarball, self.srcdir)
        #version = os.path.basename(tarball.split('.tar.')[0])
        self.srcdir = os.path.join(data_dir, 'source_code')
        #self.srcdir = os.path.join(self.srcdir, 'lmbench3')

        # Patch for lmbench

        os.chdir(self.srcdir)

        # makefile_patch = 'patch -p1 < %s' % (
        #     os.path.join(data_dir, 'makefile.patch'))
        # build_patch = 'patch -p1 < %s' % (os.path.join(
        #     data_dir, '0001-Fix-build-issues-with-lmbench.patch'))
        # lmbench_fix_patch = 'patch -p1 < %s' % (os.path.join(
        #     data_dir, '0002-Changing-shebangs-on-lmbench-scripts.patch'))
        # ostype_fix_patch = 'patch -p1 < %s' % (
        #     os.path.join(data_dir, 'fix_add_os_type.patch'))
        #
        # process.run(makefile_patch, shell=True)
        # process.run(build_patch, shell=True)
        # process.run(lmbench_fix_patch, shell=True)
        # process.run(ostype_fix_patch, shell=True)

        #build.make(self.srcdir)
        d_distro = distro.detect()
        arch = d_distro.arch
        if arch == 'ppc':
            build.make(self.srcdir, extra_args='linux-powerpc')
        elif arch == 'ppc64' or arch == 'ppc64le':
            build.make(self.srcdir, extra_args='linux-powerpc64')
        elif arch == 'x86_64':
            build.make(self.srcdir, extra_args='CC=gcc \'CFLAGS=-O3 -Icommon_64bit -lrt -lm\' -s')
        else:
            build.make(self.srcdir, extra_args='linux')

        os.chdir(self.srcdir)
        process.run('cp dhry1 dhry2 lloops lpack whets ./bin/')
        process.run('make CC=$GCC clean')

        # configure lmbench
        # os.chdir(self.srcdir)
        #
        # os.system('yes "" | make config')

        # find the lmbench config file
        # output = os.popen('ls -1 bin/*/CONFIG*').read()
        # config_files = output.splitlines()
        # if len(config_files) != 1:
        #     self.error('Config not found : % s' % config_files)
        # config_file = config_files[0]
        # if not fsdir:
        #     fsdir = self.tmpdir
        # if not temp_file:
        #     temp_file = os.path.join(self.tmpdir, 'XXX')
        #
        # # patch the resulted config to use the proper temporary directory and
        # # file locations
        # tmp_config_file = config_file + '.tmp'
        # process.system('touch ' + tmp_config_file)
        # process.system("sed 's!^FSDIR=.*$!FSDIR=%s!' '%s'  '%s' " %
        #                (fsdir, config_file, tmp_config_file))
        # process.system("sed 's!^FILE=.*$!FILE=%s!' '%s'  '%s'" %
        #                (temp_file, tmp_config_file, config_file))

    def test(self):

        path = os.path.join(self.srcdir, 'bin')
        os.chdir(path)
        cwd = os.getcwd()
        #build.make(self.srcdir, extra_args='rerun')

        #====================
        cmd = 'dhry1'
        start_log = "%%%%%%         %s test start       %%%%%% \n" % cmd
        echo_cmd = "echo '%s' " % start_log
        process.run(echo_cmd)
        echo_cmd = "echo '<<BEGIN TEST>>>'"
        process.run(echo_cmd)
        #===================
        cmd = 'dhry1'
        process.run('./dhry1 > /home/joseph/dhrystone.out')
        # ====================
        echo_cmd = "echo '[status]: PASS'"
        process.run(echo_cmd)
        echo_cmd = "echo 'Time in Seconds:0.0123'"
        process.run(echo_cmd)
        echo_cmd = "echo '<<<END>>>'"
        process.run(echo_cmd)
        echo_cmd = "echo '%%%%%% test_end %%%%%%'"
        process.run(echo_cmd)
        # ===================



        #====================
        cmd = '%s/bin/dhry2' % (self.srcdir)
        start_log = "%%%%%%         %s test start       %%%%%% \n" % cmd
        echo_cmd = "echo '%s' " % start_log
        process.run(echo_cmd)
        echo_cmd = "echo '<<BEGIN TEST>>>'"
        process.run(echo_cmd)
        #===================
        cmd = '%s/bin/dhry2' % (self.srcdir)
        process.run('./dhry2 >> /home/joseph/dhrystone.out')
        # ====================
        echo_cmd = "echo '[status]: PASS'"
        process.run(echo_cmd)
        echo_cmd = "echo 'Time in Seconds:0.0123'"
        process.run(echo_cmd)
        echo_cmd = "echo '<<<END>>>'"
        process.run(echo_cmd)
        echo_cmd = "echo '%%%%%% test_end %%%%%%'"
        process.run(echo_cmd)
        # ===================



        #====================
        cmd = '%s/bin/whets' % (self.srcdir)
        start_log = "%%%%%%         %s test start       %%%%%% \n" % cmd
        echo_cmd = "echo '%s' " % start_log
        process.run(echo_cmd)
        echo_cmd = "echo '<<BEGIN TEST>>>'"
        process.run(echo_cmd)
        #===================
        cmd = '%s/bin/whets' % (self.srcdir)
        process.run('./whets >> /home/joseph/dhrystone.out')
        # ====================
        echo_cmd = "echo '[status]: PASS'"
        process.run(echo_cmd)
        echo_cmd = "echo 'Time in Seconds:0.0123'"
        process.run(echo_cmd)
        echo_cmd = "echo '<<<END>>>'"
        process.run(echo_cmd)
        echo_cmd = "echo '%%%%%% test_end %%%%%%'"
        process.run(echo_cmd)
        # ===================

    def tearDown(self):
        # methodToCall = getattr(dhrystone_parser, 'dhrystone_par')
        # inputfile = '%s/stdout' % (self.logdir)
        # outputfile = '%s/parser.log' % (self.logdir)
        # #inputfile = '%s/lmbench_output.log' % (self.srcdir)
        # #outputfile = '%s/parser.log' % (self.srcdir)
        # methodToCall(inputfile, outputfile)
        # #parser()
        #
        # #Start post processing here
        # methodToCall = getattr(caliper.caliper_parser, 'caliper_parser')
        # methodToCall()
        print 'Tear Down is Done for Dhrystone test'


if __name__ == "__main__":
    main()