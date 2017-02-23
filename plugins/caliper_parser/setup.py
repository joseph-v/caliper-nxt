from setuptools import setup, find_packages

name = 'caliper_post_parser'
klass = 'Parser'
entry_point = '%s = %s:%s' % (name, name, klass)

if __name__ == '__main__':
    setup(name='caliper-post-process',
          version='1.0',
          description='Avocado Pre/Post Job Parser',
          py_modules=[name],
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found
    #recursively.)
    packages = find_packages(),
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    #package_data = {'parser_scripts' : files },
    #'runner' is in the root.
    #scripts = ["runner"],
    #long_description = """Really long text here."""
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []

    entry_points={
          'avocado.plugins.job.prepost': [entry_point],
          }
      )
