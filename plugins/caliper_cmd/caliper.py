"""Run caliper tests."""

import getpass
import logging
import sys

from avocado.core import exit_codes
from avocado.core import loader
from avocado.core.plugin_interfaces import CLI


class Caliper(CLI):

    """
    Run Caliper tests.
    """

    name = 'caliper'
    description = "Caliper options for 'run' subcommand"

    def configure(self, parser):

        run_subcommand_parser = parser.subcommands.choices.get('run', None)
        if run_subcommand_parser is None:
            return

        run_subcommand_parser.output.add_argument(
            '--caliper',  dest="config_filename", type=str,
            #default="config",
            metavar='FILE',
            help='Enables Caliper Benchmarking and specify the '
                 'configuration file for caliper benchmarks')

        run_subcommand_parser.output.add_argument(
            '--caliper_output_dir',  dest="caliper_output", type=str,
            #default="config",
            metavar='DIRECTORY',
            help='Optionally specify the output folder '
                 'for caliper benchmarks')

        #args = run_subcommand_parser.parse_args()

        #print "Caliper config file name is : %s " % args.config_filename
        #print "Caliper configured is : %s " % self.configured

        self.configured = True


    def run(self, args):
        #print "From Plugin --- Caliper config file name is : %s " % args.config_filename
        pass
