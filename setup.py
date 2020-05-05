# Copyright 2020 Konstruktor, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import os

from setuptools import find_packages, setup


def read(file_name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), file_name)

    with io.open(path, encoding="utf-8") as f:
        return f.read().strip()


REQUIREMENTS = read("requirements/requirements.txt").split("\n")
DEV_REQUIREMENTS = read("requirements/requirements.dev.txt").split("\n")
EXTENDED_REQUIREMENTS = read("requirements/requirements.extended.txt").split("\n")

VERSION = read("tethys/VERSION")

setup(
    name="tethys",
    version=VERSION,
    install_requires=REQUIREMENTS,
    extras_require={
        "all": EXTENDED_REQUIREMENTS + DEV_REQUIREMENTS,
        "dev": DEV_REQUIREMENTS,
        "extended": EXTENDED_REQUIREMENTS,
        "kafka": list(filter(lambda x: "kafka" in x.lower(), EXTENDED_REQUIREMENTS)),
        "rabbit": list(filter(lambda x: "rabbit" in x.lower(), EXTENDED_REQUIREMENTS)),
        "mongo": list(filter(lambda x: "mongo" in x.lower(), EXTENDED_REQUIREMENTS)),
    },
    scripts=["tethys/bin/tethys"],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.5.2",
    description="A flexible open-source platform for data streams management",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://tethys.xyz/",
    license="Apache License 2.0",
    author="Vadim Sharay",
    author_email="vadim.sharay@tethys.xyz",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Monitoring",
    ],
)
