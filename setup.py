from setuptools import setup, find_packages

VERSION = '0.0.5'
DESCRIPTION = 'Check the broken links on a website'

with open('README-PYPI.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

# Setting up
setup(
        name="blc",
        version=VERSION,
        author="pythonbrad",
        author_email="fomegnemeudje@outlook.com",
        maintainer="Sanix-Darker",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        packages=find_packages(where="src"),
        install_requires=["requests"],
        keywords=["link", "url", "broken", "check"],
        classifiers=[
            "Topic :: Internet :: WWW/HTTP",
        ],
        python_requires='>=3.8, <4',
        package_dir={"": "src"},
        data_files=[('doc', ['README-PYPI.md'])],
        url="https://github.com/osscameroon/broken_link_checker",
        project_urls={
            'Source': 'https://github.com/osscameroon/broken_link_checker',
            'Tracker': 'https://github.com/osscameroon/broken_link_checker/issues',
        },
)
