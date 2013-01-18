from setuptools import setup, find_packages


setup(
    name='moz-addon-packager',
    version='1.0.1',
    description='Creates addons for Mozilla products.',
    long_description=open('README').read(),
    author='Matt Basta',
    author_email='me@mattbasta.com',
    url='http://github.com/mattbasta/addon-packager',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
