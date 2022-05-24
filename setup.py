from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in salary_edition/__init__.py
from salary_edition import __version__ as version

setup(
	name="salary_edition",
	version=version,
	description="Everest Salary Edition",
	author="IBSL-IT",
	author_email="shantanu@frappe.io",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
