from setuptools import setup, find_packages


setup(name="aiotrello",
	version="0.0.7.7",
	description="Async Trello library",
	url="https://github.com/zomien/aiotrello",
	keywords=["async", "trello"],
	author="Julien Kmec",
	author_email="me@julien.dev",
	license="MIT",
	packages=find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Operating System :: OS Independent"
	],
	long_description=open("README.md", "r").read(),
	long_description_content_type="text/markdown",
	zip_safe=False
)
