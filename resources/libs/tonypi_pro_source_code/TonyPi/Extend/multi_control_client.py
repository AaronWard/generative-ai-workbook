#!/usr/bin/env python3
# This file is part of TonyPi.
# Copyright (C) 2021 Hiwonder Ltd. <support@hiwonder.com>
#
# rsp_robot_hat_v3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rsp_robot_hat_v3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# title           :multi_control_client.py
# author          :Hiwonder, LuYongping(Lucas)
# date            :20210421
# notes           :This is websocket to connect to service down channel and process the data
# ==============================================================================

import os
import time
import asyncio
import logging
import websockets
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from jsonrpc import JSONRPCResponseManager, Dispatcher
import hiwonder.ActionGroupControl as AGC

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("multi_control_client")
logger.setLevel(level=logging.WARNING)

executor = ThreadPoolExecutor()
dispatcher = Dispatcher()


@dispatcher.add_method
def run_action_set(action_name, repeat):
    if os.path.exists("/dev/input/js0") is True:
        time.sleep(0.01)
    else:
        AGC.runActionGroup(action_name, repeat, False)

@dispatcher.add_method
def stop():
    AGC.stopActionGroup()
    


async def listener():
    while True:
        try:
            websocket = await websockets.connect('ws://192.168.149.1:7788/down')
            async for msg in websocket:
                logger.debug(msg)
                asyncio.ensure_future(
                    loop.run_in_executor(executor, partial(JSONRPCResponseManager.handle, dispatcher=dispatcher), msg))
        except Exception as e:
            logger.error(e)
        await asyncio.sleep(2)


loop = asyncio.get_event_loop()
asyncio.run_coroutine_threadsafe(listener(), loop)
loop.run_forever()
