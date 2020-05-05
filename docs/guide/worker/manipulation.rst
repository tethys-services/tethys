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

Workers Starting/Stopping
=========================

You can start the Station worker very simply.


.. code-block:: bash

    tethys apps Worker start


But in most cases, you will need to set some configurations.
You can add specific settings to the command:

.. code-block:: bash

    tethys apps Worker start --home-dir='/home/user/.tethys' --daemon --processes 8 --station='station_id'

And you can add specific settings to the file.
The worker supports several formats: .json, .yaml, .ini, .py

.. code-block:: bash

    tethys apps Worker start --config worker.conf.yaml

Full configurations list you can learn in the next page: :ref:`Workers Configuration <Workers Configuration>`.


If you need to stop the process you can run the "stop" command.

.. code-block:: bash

    tethys apps Worker stop --home-dir='/home/user/.tethys' station_id
