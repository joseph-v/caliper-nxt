from setuptools import setup

name = 'caliper'
klass = 'Caliper'
entry_point = '%s = %s:%s' % (name, name, klass)

if __name__ == '__main__':
    setup(name='caliper-plugin',
          version='1.0',
          description='Avocado run command options for caliper',
          py_modules=[name],
          entry_points={
              'avocado.plugins.cli': [entry_point],
              }
          )
