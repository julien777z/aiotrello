from setuptools import setup, find_packages


setup(name="aiotrello",
	version="0.0.5",
	description="Async Trello library",
	url="https://github.com/bloxlink/aiotrello",
	keywords=["async", "trello"],
	author="tigerism",
	author_email="admin@blox.link",
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
