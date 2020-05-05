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

import errno
import logging
import logging.config
import os
import signal
import time
from collections import Iterable
from inspect import Signature

import click
import daemon
from lockfile.pidlockfile import PIDLockFile
from serobj.utils.path_to_object import import_object_source

from tethys.apps.base import AppBase
from tethys.apps.worker.configurator import ConfigsLoader, Config
from tethys.core.regobjs import ZeroRegistrableObject
from tethys.core.regobjs.repositories.repo_base import RepositoryBase
from tethys.core.stations import ZeroStation

log = logging.getLogger(__name__)


class Worker(AppBase):
    NAME = "Worker"

    @classmethod
    def _get_station_kwargs(cls, station):
        args = []

        try:
            sig = Signature.from_callable(station.__init__)
        except Exception:
            return args

        for p in sig.parameters.values():
            if p.kind in [p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY, p.VAR_KEYWORD]:
                args.append(str(p.name).lower())

        return args

    @classmethod
    def add_click_entry(cls, entry):
        @entry.group(name=cls.NAME)
        def worker_entry():
            """
                Worker object
            """

        for cmd in [cls.start, cls.stop]:
            worker_entry.add_command(cmd)

        return worker_entry

    @staticmethod
    @click.option("--verbose", "-v", is_flag=True, help="Enable verbose mode?")
    @click.option(
        "--home-dir",
        "-h",
        required=False,
        default=None,
        help="Stations home dir. Default: .tethys",
    )
    @click.option(
        "--daemon",
        "-d",
        "is_daemon",
        required=False,
        default=False,
        help="Run in background?",
        is_flag=True,
    )
    @click.option(
        "--processes",
        "-p",
        required=False,
        help="Count of worker processes",
        default=None,
    )
    @click.option(
        "--station",
        "-s",
        "station_id",
        required=False,
        default=None,
        help="Station ID. "
        "If not specified, the Station ID will be randomly generated",
    )
    @click.option(
        "--config",
        "-c",
        required=False,
        help="Worker configs. [.json, .yaml, .py]",
        default=None,
    )
    @click.command()
    def start(station_id, config, processes, is_daemon, home_dir, verbose):
        """ Start workers """

        if config:
            if verbose:
                click.secho("Loading configs from: {}".format(config), fg="green")
            config = ConfigsLoader.load(config)
        else:
            if verbose:
                click.secho("Loading default configs", fg="green")
            config = Config.make_with({})

        # logging config
        log_config = config.pop("LOG_CONFIG", None)
        if log_config:
            logging.config.dictConfig(log_config)

        # repo config
        repo_config = config.pop("REPO_CONFIG", None)
        if repo_config:
            repo_cls = repo_config.get(
                "repo_cls",
                "tethys.core.regobjs.repositories.repo_mongo:MongodbRepository",
            )
            repo_params = repo_config.get("repo_params", [])

            if isinstance(repo_cls, str):
                repo_cls = import_object_source(repo_cls)

            if not issubclass(repo_cls, RepositoryBase):
                raise ValueError("Bad configs: unsupported 'repo_cls' type")

            if isinstance(repo_params, dict):
                repo = repo_cls(**repo_params)
            elif isinstance(repo_params, Iterable):
                repo = repo_cls(*repo_params)
            else:
                raise ValueError("Bad configs: unsupported 'repo_params' type")

            ZeroRegistrableObject.REPOSITORY = repo

            if verbose:
                click.secho("Repository was changed to {}".format(repo), fg="green")

        # station config
        station_config = {
            str(key).lower(): value
            for key, value in config.get("STATION_CONFIG", {}).items()
        }

        station_args = Worker._get_station_kwargs(ZeroStation)
        unrecognized_args = station_config.keys() - set(station_args)
        if unrecognized_args:
            logging.warning(
                "Unrecognized station arguments: %s", ",".join(unrecognized_args)
            )

        if processes:
            station_config["max_processes_count"] = int(processes)

        station_id = (
            station_id or config.pop("STATION_ID", None) or ZeroStation.generate_id()
        )

        station_obj = ZeroStation(**station_config, _id=station_id)
        station_obj.save()

        #  worker config
        home_dir = home_dir or config.pop("STATION_ID", ".tethys")
        pid_files_dir = os.path.join(home_dir, "pid_files")
        if home_dir not in [".", ".."] and not os.path.exists(home_dir):
            if verbose:
                click.secho("Creating home dir: {}".format(home_dir), fg="green")
            os.makedirs(home_dir)

        if not os.path.exists(pid_files_dir):
            os.makedirs(pid_files_dir)

        pid_name = "{}.station.pid".format(station_id)
        pid_file_name = os.path.join(pid_files_dir, pid_name)
        pid_file = PIDLockFile(pid_file_name, threaded=True)

        if config.pop("IS_DAEMON", is_daemon):
            if verbose:
                click.secho("Starting station as daemon...", fg="green")

            with daemon.DaemonContext(working_directory=home_dir, pidfile=pid_file):
                station_obj.start()

        else:
            if verbose:
                click.secho("Creating pid file...", fg="green")

            with pid_file:

                if verbose:
                    click.secho("Starting station...", fg="green")

                station_obj.start()

    @staticmethod
    @click.command()
    @click.option(
        "--home-dir",
        "-h",
        required=False,
        default=".tethys",
        help="Stations home dir. Default: .tethys",
    )
    @click.option(
        "--kill-after",
        "-k",
        "kill_after",
        required=False,
        default=5,
        help="Send SIGKILL after N sec.",
    )
    @click.argument("station")
    def stop(station, home_dir, kill_after):
        """ Stop workers """

        kill_after = int(kill_after or 0)

        pid_files_dir = os.path.join(home_dir, "pid_files")
        pid_name = "{}.station.pid".format(station)
        pid_file_name = os.path.join(pid_files_dir, pid_name)

        pid_file = PIDLockFile(pid_file_name)
        pid = pid_file.read_pid()

        if not pid:
            return

        os.kill(pid, signal.SIGTERM)

        start_time = time.monotonic()
        while Worker._is_running(pid) and start_time + kill_after > time.monotonic():
            time.sleep(0.1)

        if Worker._is_running(pid):
            os.kill(pid, signal.SIGKILL)

    @staticmethod
    def _is_running(pid):
        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                return False
        return True
