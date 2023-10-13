#!/usr/bin/python

# Copyright (c) individual contributors.
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of
# the License, or any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details. A copy of the
# GNU Lesser General Public License is distributed along with this
# software and can be found at http://www.gnu.org/licenses/lgpl.html

import logging
import configargparse
import signal
import sys
import multiprocessing
import koi_core as koi
from koi_core.exceptions import KoiApiOfflineException
from time import sleep
from datetime import datetime


signal_interrupt = False


def sigint_handling(signum, frame):
    # provide the user with some guidline about gracefully exiting the worker
    global signal_interrupt
    if signal_interrupt:
        print(
            "\nThe worker will forcefully be turned off RIGHT NOW. "
            "You could'nt wait a few minutes, could you? "
            "Essentially you have just killed me •`_´•"
        )
        sys.exit(0)
    else:
        signal_interrupt = True
        print(
            "\nThe worker will gracefully terminate on the next opportunity. "
            "If a training is in progress this can, however, take a bit longer :( "
            "So if you really want to quit press CTRC-C again. "
            "But we will loose all unsaved progress then :'(. "
            "So better get a cup of coffe instead and let me calculate things :D\n"
        )


def main():
    # define the options
    p = configargparse.ArgParser(description="worker process for the koi-system")
    p.add("-c", "--config", is_config_file=True)

    # logging options
    p.add("-l", "--loglevel", help="logging level", type=str, default="WARNING")
    p.add("--logfile", type=str)

    # filter options
    p.add("-m", "--model", help="the model name to match")
    p.add("-i", "--instance", help="the instance name to match")

    # run behaviour
    p.add("-o", "--once", action="store_true", help="run only once then exit")
    p.add(
        "-f",
        "--force",
        action="store_true",
        help="force a training step even if not needed",
    )
    p.add("--sleep", help="seconds to sleep after iteration", type=int, default=30)

    # connection options
    p.add(
        "-s",
        "--server",
        env_var="KOI_SERVER_URI",
        required=True,
        help="the server uri to connect to",
    )
    p.add(
        "-u",
        "--user",
        env_var="KOI_SERVER_USER",
        required=True,
        help="the user name for authentication",
    )
    p.add(
        "-p",
        "--password",
        env_var="KOI_SERVER_PASSWORD",
        required=True,
        help="the password for authentication",
    )
    p.add(
        "-x",
        "--start-method",
        type=str,
        default="NONE",
        help="The startmethod used for multiprocessing. [spawn, fork, NONE]",
    )
    p.add(
        "-r",
        "--retries",
        type=int,
        default=3,
        help="The number of retries to make before giving up. A negative number will make it retry indefinitly",
    )
    p.add(
        "-t",
        "--sleep-retry",
        type=int,
        default=60,
        help="Number of seconds to wait before a retry",
    )
    p.add(
        "-w",
        "--wait-training",
        type=int,
        default=10,
        help="Number of seconds a instance has to be untouched before atempting to train it",
    )
    p.add(
        "--stay-offline",
        action="store_true",
        help="Do not try to connect to the server. This will only work if the cache is already filled",
        default=False,
    )

    opt = p.parse_args()

    if not opt.start_method == "NONE":
        multiprocessing.set_start_method(opt.start_method)

    # replace default signal interrupt handling to enable graceful exit
    signal.signal(signal.SIGINT, sigint_handling)

    # set the logging
    logging.basicConfig(
        filename=opt.logfile,
        level=opt.loglevel.upper(),
        format="%(asctime)s %(levelname)s:%(message)s",
        datefmt="%d.%m.%Y %H:%M:%S",
    )

    # initialize the koi_core
    koi.init()

    # intialize retry counter
    retries = opt.retries

    # connect using the credentials
    logging.info("connecting to %s", opt.server)
    pool = koi.create_api_object_pool(opt.server, opt.user, opt.password, opt.stay_offline)

    while 1:
        try:
            # gracefully exit if needed
            if signal_interrupt:
                break

            # iterate through all models
            models = pool.get_all_models()
            for model in models:
                # gracefully exit if needed
                if signal_interrupt:
                    break

                # if a filter is set and it does not match -> continue
                if opt.model is not None and opt.model != model.name:
                    logging.debug(
                        "skipping model %s as it does not match the filter %s",
                        model.name,
                        opt.model,
                    )
                    continue

                # skip unfinalized models
                if not model.finalized:
                    logging.debug("skipping model %s as it is not finalized", model.name)
                    continue

                # iterate through all instances
                instances = model.instances
                for instance in instances:
                    # gracefully exit if needed
                    if signal_interrupt:
                        break

                    # if a filter is set and it does not match -> continue
                    if opt.instance is not None and opt.instance != instance.name:
                        logging.debug(
                            "skipping instance %s/%s as it does not match the filter %s",
                            model.name,
                            instance.name,
                            opt.instance,
                        )
                        continue

                    # skip unfinalized instances
                    if not instance.finalized:
                        logging.debug(
                            "skipping instance %s/%s as it is not finalized",
                            model.name,
                            instance.name,
                        )
                        continue
                    
                    # seconds since last instance update
                    last_modified = datetime.fromisoformat(instance.sample_last_modified)
                    sec_since_last_change = (datetime.utcnow() - last_modified).total_seconds()
                    # train the instance if its ready to train or the user forces it
                    if opt.force or (instance.could_train and sec_since_last_change > opt.wait_training):
                        try:
                            logging.info(
                                "start to train instance %s/%s", model.name, instance.name
                            )
                            koi.control.train(instance, None, False)
                        except KoiApiOfflineException as ex:
                            raise ex
                        except Exception:
                            logging.exception(
                                "instance %s/%s had an exception", model.name, instance.name
                            )
                    else:
                        if (instance.could_train and sec_since_last_change < opt.wait_training):
                            logging.info(
                                "skipping instance %s/%s, as data was not present or still changing.",
                                model.name,
                                instance.name
                            )

            # break here if the user selected to run once
            if opt.once:
                break

            # reset the retry counter
            retries = opt.retries

            logging.debug("sleeping for %d seconds", opt.sleep)
            for _ in range(opt.sleep):
                # gracefully exit if needed
                if signal_interrupt:
                    break
                sleep(1)
        except KoiApiOfflineException as ex:
            if retries == 0:
                # if the retry counter is initilizes with a negative value, we will try forever
                logging.error("koi api is offline, giving up")
                sys.exit(-1)

            retries -= 1
            logging.error("koi api is offline, retrying in %d seconds", opt.sleep_retry)
            sleep((float)(opt.sleep_retry))

            # set the online flag and try to athenticate
            try:
                pool.api.reconnect()
            except:
                logging.error("could not reconnect to koi api")

    logging.info("stopped")
    sys.exit(0)


if __name__ == "__main__":
    main()
