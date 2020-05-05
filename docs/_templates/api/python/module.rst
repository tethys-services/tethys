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

{% if not obj.display %}
:orphan:

{% endif %}
:mod:`{{ obj.name }}`
======={{ "=" * obj.name|length }}

.. py:module:: {{ obj.name }}

{% if obj.docstring %}
.. autoapi-nested-parse::

   {{ obj.docstring|prepare_docstring|indent(3) }}

{% endif %}

.. toctree::
   :titlesonly:
   :maxdepth: 3

{% block subpackages %}
{% set visible_subpackages = obj.subpackages|selectattr("display")|list %}
{% if visible_subpackages %}

{% for subpackage in visible_subpackages %}
   {{ subpackage.short_name }}/index.rst
{% endfor %}


{% endif %}
{% endblock %}
{% block submodules %}
{% set visible_submodules = obj.submodules|selectattr("display")|list %}
{% if visible_submodules %}

{% for submodule in visible_submodules %}
   {{ submodule.short_name }}/index.rst
{% endfor %}


{% endif %}
{% endblock %}

{% block content %}
{% if obj.all is not none %}
{% set visible_children = obj.children|selectattr("short_name", "in", obj.all)|list %}
{% elif obj.type is equalto("package") %}
{% set visible_children = obj.children|selectattr("display")|list %}
{% else %}
{% set visible_children = obj.children|selectattr("display")|rejectattr("imported")|list %}
{% endif %}
{% if visible_children and obj.type != "package" %}
{{ obj.type|title }} Contents
{{ "-" * obj.type|length }}---------

{% set visible_classes = visible_children|selectattr("type", "equalto", "class")|list %}
{% set visible_functions = visible_children|selectattr("type", "equalto", "function")|list %}

{% if "show-module-summary" in autoapi_options and (visible_classes or visible_functions) %}
{% block classes %}
{% if visible_classes %}
Classes
~~~~~~~

.. autoapisummary::

{% for klass in visible_classes %}
   {{ klass.id }}
{% endfor %}


{% endif %}
{% endblock %}

{% block functions %}
{% if visible_functions %}
Functions
~~~~~~~~~

.. autoapisummary::

{% for function in visible_functions %}
   {{ function.id }}
{% endfor %}


{% endif %}
{% endblock %}
{% endif %}
{% for obj_item in visible_children %}
{{ obj_item.rendered|indent(0) }}
{% endfor %}
{% endif %}
{% endblock %}
