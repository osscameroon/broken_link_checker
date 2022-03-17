from setuptools import setup, find_packages


VERSION = '0.0.1'
DESCRIPTION = 'Check the broken links on a website'

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

# Setting up
setup(
        name="broken_link_checker",
        version=VERSION,
        author="pythonbrad",
        author_email="fomegnemeudje@outlook.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        packages=find_packages(where="src"),
        install_requires=["urllib3>=1.26.8<2.0"],
        keywords=["link", "url", "broken", "check"],
        classifiers=[
            "Topic :: Internet :: WWW/HTTP",
        ],
        python_requires='>=3.9',
        package_dir={"": "src"},
)
