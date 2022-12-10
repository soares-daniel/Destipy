import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Destipy",
    version="0.0.1",
    author="Daniel Soares",
    author_email="sedam.code@gmail.com",
    license="MIT",
    keywords=["destiny", "bungie", "wrapper", "async"],
    description="Async wrapper for Bungie API in Python",
    long_description=long_description,
    url="https://github.com/soares-daniel/Destipy/",
    packages=setuptools.find_packages(),
    install_requires=[
        "aiohttp>=3.6.2",
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ]
)
