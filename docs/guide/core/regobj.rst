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

Registry Objects and Repositories
=================================

This section will introduce you to the important information how to use the objects.

Object sharing among processes is an important feature of the project.

Every shareable object in the project is inherited from RegistrableObject class.
These classes are responsible for correct synchronization with remote data stores.

In the first version of the project there is one
RegistrableObject class - :class:`ZeroRegistrableObject <tethys.core.regobj.regobj_zero.ZeroRegistrableObject>`.
'Zero' prefix is a generation number. The main idea is that each generation will provide incompatible functionality.
It is because objects schemas and objects states will be stored in a storage. Any significant updates will corrupt the system.

Also, there are repositories interfaces that help to sync with specific data stores.
A repository interface can be set for each class (at the same time or separately).

In most cases you will use high-level interfaces for setting storage interfaces.

This is basic example of setting repository interface:
    .. code-block:: python

        from tethys.core.regobjs import ZeroRegistrableObject
        from tethys.core.regobjs.repositories.repo_mongo import MongodbRepository
        from tethys.core.networks import ZeroNetwork

        uri = "mongodb://root:root@127.0.0.1:27017/some_collection?authSource=admin"
        repo = MongodbRepository(uri)

        # default: ZeroRegistrableObject.REPOSITORY == LocalRepository()
        ZeroRegistrableObject.REPOSITORY = repo

        ZeroNetwork().save()  # will save to the mongodb


Another example of setting repository interface:
    .. code-block:: python

        from tethys.core.regobjs.repositories.repo_local import LocalRepository
        from tethys.core.regobjs.repositories.repo_mongo import MongodbRepository
        from tethys.core.networks import ZeroNetwork

        uri = "mongodb://root:root@127.0.0.1:27017/some_collection?authSource=admin"
        repo = MongodbRepository(uri)

        ZeroNetwork.REPOSITORY = repo

        ZeroNetwork().save()  # will save to the mongodb
        ZeroNetwork(_repo=LocalRepository()).save()  # will save to the local dict()


Each registry object contains methods for database communication.

Methods `load` and `list` allow loading data from storages.
Method `refresh` uses the `load` method to sync data from a database.
Method `delete` remove the object in a database (but you can continue to use local copy).


Example to understand the concept:
    .. code-block:: python

        from tethys.core.regobjs import ZeroRegistrableObject
        from tethys.core.networks import ZeroNetwork
        from tethys.core.pipes import ZeroPipe

        class TestPipe(ZeroPipe):
            FIELDS_SCHEMA = {}

            def __init__(self, **_):
                pass

        TestPipe(_id="test_pipe")

        obj = ZeroNetwork(["test_pipe"], _id="test_net").save(
             save_dependency=True,  # execute save method for related objects (like test_pipe)
             save_dependency_depth=1  # saving recursion depth [will save ZeroNetwork and TestPipe]
        )
        assert obj.pipes_list == ["test_pipe"]

        obj.pipes_list = []
        assert obj.pipes_list == []

        assert obj.load("test_net") is obj
        assert obj.pipes_list == []

        assert obj.load("test_net", with_cache=False) is obj
        assert obj.pipes_list == ["test_pipe"]  # It will be loaded from the repository

        obj.pipes_list = []
        assert obj.pipes_list == []

        assert obj.refresh() is obj
        assert obj.pipes_list == ["test_pipe"]

        obj.pipes_list = []
        assert obj.pipes_list == []

        assert obj.list() == [obj]
        assert obj.pipes_list == ["test_pipe"]

        obj.pipes_list = []
        assert obj.pipes_list == []

        assert obj.delete() is obj
        assert obj.refresh() is None
        assert obj.pipes_list == []

        assert obj.save()
        assert obj.refresh() is obj
        assert obj.pipes_list == []


Also objects provide simple locks. You can lock objects for changes in a database.
It's an example how to use locks in the project:

    .. code-block:: python

        import time
        from tethys.core.networks import ZeroNetwork

        start = time.time()
        obj = ZeroNetwork().save()

        assert obj.lock(lock_ttl=1) is True
        assert obj.lock(blocking=True, lock_ttl=5) is True
        print(time.time() - start)  # ~ 1s

        assert obj.lock(blocking=True, wait_timeout=1) is True
        print(time.time() - start)  # ~ 2s

        with obj.lock_context(blocking=False, lock_ttl=5) as lock_ready:
            assert lock_ready is False
            print(time.time() - start)  # ~ 2s

        assert obj.lock(blocking=True) is True
        print(time.time() - start)  # ~ 2s

        obj.unlock()

This Lock mechanism doesn't provide database locks.

If you need to lock an object in a database, you must use specific repository interfaces
and databases that provide this functionality.
