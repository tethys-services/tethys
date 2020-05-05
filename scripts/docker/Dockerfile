# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG BASE_IMAGE="python:3.7-stretch"

FROM ${BASE_IMAGE} as main

ARG WORKDIR="/opt/tethys"
ARG PIP_VERSION="20.0.2"
ARG TINI_VERSION="v0.18.0"
ARG TETHYS_EXTRAS="all"

ENV PATH="${WORKDIR}/tethys/bin:${PATH}"
ENV LANGUAGE=C.UTF-8 LANG=C.UTF-8 LC_ALL=C.UTF-8 LC_CTYPE=C.UTF-8 LC_MESSAGES=C.UTF-8

LABEL maintainer="Vadim Sharay vadim.sharay@tethys.xyz"

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini

COPY . ${WORKDIR}

WORKDIR ${WORKDIR}

RUN pip install --upgrade pip==${PIP_VERSION} && pip install -e ".[${TETHYS_EXTRAS}]"

COPY ./scripts/docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /tini && chmod +x /entrypoint.sh

ENTRYPOINT ["/tini", "--", "/entrypoint.sh"]

CMD ["--help"]
