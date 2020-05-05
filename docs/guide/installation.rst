 .. Copyright 2020 Konstruktor, Inc. All Rights Reserved.

 .. Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

 ..   http://www.apache.org/licenses/LICENSE-2.0

 .. Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Installation
============

The installation is easy and quick.


Standard installation
_____________________

.. code-block:: bash

    # To install latest stable version from PyPI
    pip install tethys

OR

.. code-block:: bash

    # To install from github
    pip install -e git+https://github.com/tethys-platform/tethys.git

OR

.. code-block:: bash

    # To install from local directory
    pip install -e .


Installation with extras
________________________

.. code-block:: bash

    pip install tethys[extra-1, extra-2]

OR

.. code-block:: bash

    pip install -e git+https://github.com/tethys-platform/tethys.git#egg=tethys[extra-1, extra-2]

OR

.. code-block:: bash

    pip install -e .[extra-1, extra-2]

Here’s the list of the extras:

   +-----------------------+-----------------------+
   | Extra                 | Meaning               |
   +=======================+=======================+
   | all                   | All extras above      |
   +-----------------------+-----------------------+
   | dev                   | Extras for developing |
   +-----------------------+-----------------------+
   | extended              | Additional extras     |
   +-----------------------+-----------------------+
   | mongo                 | Mongodb integration   |
   +-----------------------+-----------------------+
   | rabbit                | RabbitMQ integration  |
   +-----------------------+-----------------------+
   | kafka                 | Kafka integration     |
   +-----------------------+-----------------------+
