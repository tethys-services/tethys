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

project = "Tethys"
copyright = "2020, Konstruktor Inc."
author = "Vadim Sharay"
release = "0.0.1"


extensions = [
    "sphinxcontrib.images",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "autoapi.extension",
    "sphinx.ext.imgconverter",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
]

html_static_path = ["_static"]
templates_path = ["_templates"]
language = "en"

exclude_patterns = ["api/tethys/index.rst"]

man_pages = [("index", "tethys", "Tethys Documentation", ["Tethys"], 1)]

latex_documents = [
    ("index", "Tethys.tex", "Tethys Documentation", "Tethys", "manual"),
]

texinfo_documents = [
    (
        "index",
        "Tethys",
        "Tethys Documentation",
        "Tethys",
        "Tethys",
        "A flexible open-source platform for data streams management",
        "Miscellaneous",
    ),
]


html_theme = "sphinx_rtd_theme"

html_css_files = [
    "css/tethys_custom.css",
]

autoapi_type = "python"
autoapi_template_dir = "_templates/api"
autoapi_dirs = [
    "../tethys",
]
autoapi_root = "api"
autoapi_options = ["members", "show-inheritance", "special-members", "undoc-members"]
autoapi_python_class_content = "both"
autoapi_keep_files = True
autoapi_add_toctree_entry = False


intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}


suppress_warnings = [
    "autosectionlabel.*",
]
