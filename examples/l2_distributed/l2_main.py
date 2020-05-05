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

"""
pip install tethys[rabbit,mongo]

cd ./examples/l2_distributed

docker-compose up -d

python ./l2_main.py create sess1
python ./l2_main.py send sess1 http://http_host:8000/
python ./l2_main.py send sess1 ftp://ftp_host/
python ./l2_main.py close sess1

# check tmp dir

"""


import click

from tethys.core.regobjs import ZeroRegistrableObject
from tethys.core.regobjs.repositories.repo_mongo import MongodbRepository
from tethys.core.sessions import ZeroSession
from l2_net import get_network


@click.group()
def cli():
    """
     The tethys CLI for managing l2 example environment.
    """


@cli.command(name="create")
@click.argument("session", required=False)
def create_sess(session=None):
    """
     Create session
    """
    network = get_network()
    sess = ZeroSession(network, _id=session).save(save_dependency=False)

    click.echo("Session '{}' was created".format(sess.id))


@cli.command(name="close")
@click.option(
    "--mode",
    "-m",
    required=False,
    default="<hard>",
    help="Session closing mode. Available: SOFT / HARD / INSTANT",
)
@click.argument("session")
def close_sess(session, mode):
    """
     Close session
    """

    sess = ZeroSession.load(session)
    sess.close(mode)

    click.echo("Session '{}' was closed [{} mode]".format(sess.id, mode))


@cli.command(name="send")
@click.argument("session")
@click.argument("uri")
def send_data(session, uri):
    """
     Send data
    """

    sess = ZeroSession.load(session)
    sess.send(uri)


if __name__ == "__main__":
    ZeroRegistrableObject.REPOSITORY = MongodbRepository(
        "mongodb://root:root@127.0.0.1:27017/l2_repo?authSource=admin"
    )

    cli()
