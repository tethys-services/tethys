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

Workers Configuration
=====================

First of all, you need to set some configs to run your useful worker.


In the current version you can add next several main params to the command line (start command):

+--------------------------------+---------------------------------------+----------+
| Shell param                    | Variable                              | Default  |
+================================+=======================================+==========+
| --home-dir (-h)  [HOME_DIR]    | HOME_DIR                              | .tethys  |
+--------------------------------+---------------------------------------+----------+
| --daemon (-d)                  | IS_DAEMON                             |  false   |
+--------------------------------+---------------------------------------+----------+
| --processes (-p) [INT COUNT]   | STATION_CONFIG["max_processes_count"] |  1       |
+--------------------------------+---------------------------------------+----------+
| --station (-s)   [STATION ID]  | STATION_ID                            | {random} |
+--------------------------------+---------------------------------------+----------+
| --config (-c)    [FILE PATH]   |                                       |          |
+--------------------------------+---------------------------------------+----------+

There are several settings that you can set only in the configuration file.


+---------------------------------------+----------------------------------------------------------------------------+
| Variable                              | Description                                                                |
+=======================================+============================================================================+
| LOG_CONFIG                            | Standard config for the :mod:`logging` python library                      |
+---------------------------------------+----------------------------------------------------------------------------+
| REPO_CONFIG                           | Expect the dict with repo_cls (cls or str path) and repo_params (kwargs)   |
+---------------------------------------+----------------------------------------------------------------------------+
| STATION_CONFIG                        | Kwargs for the :class:`ZeroStation`                                        |
+---------------------------------------+----------------------------------------------------------------------------+


REPO_CONFIG example:
    .. code-block:: python

        REPO_CONFIG = {
            "repo_cls": "tethys.core.regobjs.repositories.repo_mongo:MongodbRepository",
            "repo_params": {
                "uri": "mongodb://root:root@mongo:27017/l2_repo?authSource=admin"
            }
        }


After that, you can start your station anywhere.
