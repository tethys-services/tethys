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

:mod:`tethys.core.regobjs.regobj_zero`
======================================

.. py:module:: tethys.core.regobjs.regobj_zero


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. data:: RegObjZT
   

   

.. data:: log
   

   

.. data:: CLASS_PATH_PREFIX
   :annotation: = /zero/

   

.. py:class:: ZeroRegistrableObject

   Bases: :class:`tethys.core.regobjs.regobj_base.RegistrableObjectBase`

   Base class for all entities that used like models for a database.
   It's the Zero generation.

   A few examples:
       .. code-block:: python

           class SomeClass(ZeroRegistrableObject):
               FIELDS_SCHEMA = {
                   "some_field": {"type": "string"}
               }

               def __init__(self, some_field, another_field, **kwargs):
                   self.some_field = some_field
                   self.another_field = another_field

               # ...

           # -------------------------------------------------

           obj1 = SomeClass("str", "no:save", _id="some_id")
           obj2 = SomeClass.load("some_id")

           assert id(obj1) == id(obj2)

           # -------------------------------------------------

           obj1 = SomeClass("str", "no:save")
           obj1.save()

           obj2 = ZeroRegistrableObject.load(obj1.path)

           assert id(obj1) == id(obj2)

           # -------------------------------------------------

           ZeroRegistrableObject.REPOSITORY = JsonFileRepository(create=True)

           obj1 = SomeClass(some_field="str", another_field="no:save", _id="some_id")
           obj1.save()

           assert obj1.some_field == "str"
           assert obj1.another_field == "no:save"

           # restart script

           obj2 = SomeClass.load("some_id")
           assert obj1.some_field == "str"
           assert obj1.another_field == "no:save"  # raise AttributeError: 'SomeClass' object has no attribute 'another_field'


   .. attribute:: CLASS_PATH
      :annotation: = /sandbox/

      Default collection path in the repository


   .. attribute:: FIELDS_SCHEMA
      

      Default fields validators


   .. attribute:: REPOSITORY
      

      Entities repository. You can override it in your own classes


   .. method:: __getnewargs_ex__(self)



   .. method:: __getstate__(self)



   .. method:: __setstate__(self, state: dict)



   .. method:: prepare(cls, item: dict, keys: list = None)
      :classmethod:


      Validate and normalize data in the attrs that define in the :attr:`FIELDS_SCHEMA`


   .. method:: generate_id(cls)
      :classmethod:


      Generate random ID. Default: uuid4


   .. method:: generate_path(cls, obj_id: str)
      :classmethod:


      Generate collection path from the ID


   .. method:: id(self)
      :property:


      Return self._id value


   .. method:: path(self)
      :property:


      Return generate_path(ID) result


   .. method:: version(self)
      :property:


      Return generate_version() result


   .. method:: generate_version(self)


      Return hash of the fields data


   .. method:: __getattr__(self, item: str)



   .. method:: __setattr__(self, key: str, value: Any)



   .. method:: __str__(self)



   .. method:: __hash__(self)



   .. method:: __eq__(self, other: Any)



   .. method:: copy(self)



   .. method:: load(cls: Type[RegObjZT], obj_id: str, with_cache: bool = True, **kwargs)
      :classmethod:


      Load the entity from the repository by ID.
      If the entity already in the memory then method will return cached version.

      :param obj_id: Entity ID or Entity path
      :type obj_id: str
      :param with_cache: load data from the cache (default: True)
      :type with_cache: bool
      :return: ZeroRegistrableObject instance
      :rtype: ZeroRegistrableObject


   .. method:: list(cls: Type[RegObjZT], list_filter: dict = None, **kwargs)
      :classmethod:


      Load list of the entities.
      You can specify some filters, but the filter's query language is experimental.

      Filter example:
          {"some_field>=": 2}     -    list entities where some_field >= 2

          "{field_name}{operator}" - key template

      Basic filters:
          +------------+-----------------------+
          | operator   | python op.            |
          +============+=======================+
          | ->         |  field in {value}     |
          +------------+-----------------------+
          | !>         |  field not in {value} |
          +------------+-----------------------+
          | >=         |  field >= {value}     |
          +------------+-----------------------+
          | >          |  field > {value}      |
          +------------+-----------------------+
          | <=         |  field <= {value}     |
          +------------+-----------------------+
          | <          |  field < {value}      |
          +------------+-----------------------+
          | !=         |  field != {value}     |
          +------------+-----------------------+
          | ==         |  field == {value}     |
          +------------+-----------------------+

      :param list_filter: dictionary of the filters
      :type list_filter: dict
      :return: list of the ZeroRegistrableObject instances
      :rtype: List(ZeroRegistrableObject)


   .. method:: refresh(self: RegObjZT, ignore_errors: bool = True, **kwargs)


      Reload entity from the repository (without cache)

      :param ignore_errors: ignore errors like TethysRONotFound (default: True)
      :type ignore_errors: bool
      :return: return ZeroRegistrableObject instance or None (when error like NotFound)
      :rtype: ZeroRegistrableObject or None


   .. method:: save(self: RegObjZT, save_dependency: bool = True, save_dependency_depth: int = 6, save_dependency_search_depth: int = 0, **kwargs)


      Save current state to the repository.

      :param save_dependency: save related entities
      :type save_dependency: bool
      :param save_dependency_depth: depth of related entities recursion (-1 = infinity)
      :type save_dependency_depth: int
      :param save_dependency_search_depth: depth of searching in the fields values (like dict).
      :type save_dependency_depth: int


   .. method:: delete(self: RegObjZT, **kwargs)


      Delete the object from the repository.

      :return: return self object
      :rtype: ZeroRegistrableObject


   .. method:: lock(self, lock_ttl: float = 60, wait_timeout: float = float('inf'), blocking: bool = True, **kwargs)


      Lock the object in the repository.

      :param lock_ttl: time to live for the lock (next lock will wait for the time or wait_timeout)
      :type lock_ttl: float
      :param wait_timeout: how much time to wait until lock is unlocked
          (after this time the function will have ignored the lock)
      :type wait_timeout: float
      :param blocking: wait for the lock (if false then the function return False)
      :type blocking: bool
      :return: is locked by the current process?


   .. method:: unlock(self, **kwargs)


      Unlock the object in the repository.


   .. method:: lock_context(self, lock_ttl: float = 60, wait_timeout: float = float('inf'), blocking: bool = True, **kwargs)


      Contextmanager for the Locking/Unlocking the object in the repository.
      It allows nested context

      Example:
          .. code-block:: python

              start = time.time()

              def lock():
                  obj.lock()
                  print(time.time() - start)  # ~ 2s

              with obj.lock_context(lock_ttl=1):
                  with obj.lock_context(lock_ttl=2):
                      print(time.time() - start)  # ~ 0s

                      Thread(target=lock).start()
                      time.sleep(5)  # todo_something
