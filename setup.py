from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

setup(
	name="hr_saudi",
	version="1.0.0",
	description="Enterprise Workforce Platform for Construction & Hotel Operations on ERPNext",
	author="Al Metaeb Investment",
	author_email="info@almetaeb.com.sa",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
