import setuptools
import os
from pathlib import Path

root = Path(os.path.realpath(__file__)).parent
version_file = root / 'pyfactor' / 'VERSION'
readme_file = root / 'readme-pypi.rst'

pypi_url = 'https://pypi.org/project/pyfactor'
github_url = 'https://github.com/felix-hilden/pyfactor'
documentation_url = 'https://pyfactor.rtfd.org'

extras_require = {
    'docs': [
        'sphinx',
        'sphinx-rtd-theme',
        'sphinx-autodoc-typehints',
        'sphinx-argparse',
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
    name='pyfactor',
    version=version_file.read_text().strip(),
    description='A script dependency visualiser.',
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
    keywords='dependency visualiser',
    packages=setuptools.find_packages(exclude=('tests', 'tests.*',)),
    include_package_data=True,
    package_data={
        'pyfactor': ['VERSION']
    },
    entry_points={
        'console_scripts': ['pyfactor=pyfactor:main']
    },

    python_requires='>=3.6',
    install_requires=[
        'dataclasses;python_version<"3.7"',
        'pydot',
        'networkx',
        'graphviz',
    ],
    extras_require=extras_require,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
