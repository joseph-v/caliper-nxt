from setuptools import setup, find_packages

name = 'caliper-nxt'
name

name1 = 'plugins.caliper_cmd.caliper'
klass1 = 'Caliper'
entry_point1 = '%s = %s:%s' % (name, name1, klass1)

name2 = 'plugins.caliper_parser.caliper_parser'
klass2 = 'Parser'
entry_point2 = '%s = %s:%s' % (name, name2, klass2)


if __name__ == '__main__':
    setup(name='caliper-nxt',
          version='1.0',
          description='Integrating Caliper benchmarking features to Avocado Framework',
          py_modules=[name1, name2],
          packages = find_packages(),
          entry_points={
                        'avocado.plugins.cli': [entry_point1],
                        'avocado.plugins.job.prepost': [entry_point2],
          }
    )
