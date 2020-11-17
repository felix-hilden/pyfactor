import setuptools
import os
from pathlib import Path

"""
See the following resources:
* https://setuptools.readthedocs.io/en/latest/setuptools.html
* https://docs.python.org/3.7/distutils/setupscript.html
"""

root = Path(os.path.realpath(__file__)).parent
version_file = root / 'package' / 'VERSION'
readme_file = root / 'readme.rst'

pypi_url = 'https://pypi.org/project/python-package'
github_url = 'https://github.com/felix-hilden/python-package'
documentation_url = github_url + '/wiki'

extras_require = {
    'docs': [
        'sphinx',
        'sphinx-rtd-theme',
        'sphinx-autodoc-typehints'
    ],
    'tests': [
        'coverage',
        'pytest',
    ],
    'checks': [
        'tox',
        'doc8',
        'flake8',
        'flake8-bugbear',
        'pydocstyle',
        'pygments',
    ]
}
extras_require['dev'] = (
    extras_require['docs'] + extras_require['tests'] + extras_require['checks']
)

setuptools.setup(
    name='python-package',
    version=version_file.read_text().strip(),
    description='Python package template',
    long_description=readme_file.read_text(),
    long_description_content_type='text/x-rst',

    url=documentation_url,
    download_url=pypi_url,
    project_urls={
        'Source': github_url,
        'Issues': github_url + '/issues',
        'Documentation': documentation_url,
    },

    author='Felix Hildén',
    author_email='felix.hilden@gmail.com',
    maintainer='Felix Hildén',
    maintainer_email='felix.hilden@gmail.com',

    license='MIT',
    keywords='python package template',
    packages=setuptools.find_packages(exclude=('tests', 'tests.*',)),
    include_package_data=True,
    package_data={
        'package': ['VERSION']
    },

    python_requires='>=3.6',
    install_requires=[],
    extras_require=extras_require,

    classifiers=[],
)
