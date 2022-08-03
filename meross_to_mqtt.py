#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import Namespace
from ast import arg
import asyncio
from asyncio_mqtt import Client, ProtocolVersion 
import os, json
from typing import List
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.push.generic import GenericPushNotification
from meross_iot.controller.device import BaseDevice

# client, user and device details
mqtt_serverUrl   = "LOCAL MQTT SERVER"
mqtt_username    = "LOCAL MQTT SERVER USER"
mqtt_password    = "LOCAL MQTT SERVER PASSWORD"

EMAIL = os.environ.get('MEROSS_EMAIL') or "MEROSS EMAIL ACCOUNT"
PASSWORD = os.environ.get('MEROSS_PASSWORD') or "MEROSS PASSWORD"

async def main():
    # Setup the HTTP client API from user-password
    global http_api_client 
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)

    # Setup and start the device manager
    global manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Bind push notification 
    manager.register_push_notification_handler_coroutine(manager_push_handler)

    # Discover devices.
    await manager.async_device_discovery()
    meross_devices = manager.find_devices()

    # # Print them
    # print("I've found the following devices:")
    # for dev in meross_devices:
    #     print(f"- {dev.name} ({dev.type}): {dev.online_status} {dev.uuid}")

async def manager_push_handler(push: GenericPushNotification, devices: List[BaseDevice], manager: MerossManager):
    message = {"name": "", "type": "", "multiChan": False, "state": None, "states": None}
    for dev in devices:
        await dev.async_update()

        message["name"] = dev.name
        message["type"] = dev.type

        if len(dev.channels)> 1:
            message["multiChan"] = True
            states = {}
            for chan in dev.channels:
                if chan.is_master_channel:
                    message["state"] = dev.is_on(channel=chan.index)
                else:
                    states[chan.index]=dev.is_on(channel=chan.index)
                
                message["states"] = states
              #  print(chan.index)
              #  print(f"- {dev.name} ({dev.type}): {dev.is_on(channel=chan.index)}")
        else:
            message["multiChan"] = False
            message["state"] = dev.is_on()
           # print(f"- {dev.name} ({dev.type}): {dev.is_on()}")


        async with Client(
            mqtt_serverUrl,
            username=mqtt_username,
            password=mqtt_password,
            protocol=ProtocolVersion.V31
        ) as client:
            await client.publish(f"meross/{dev.uuid}", payload=json.dumps(message), qos=2, retain=True)

        #print(push)

async def close_manager():
    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()

if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        #print("Caught keyboard interrupt.")
        loop.run_until_complete(close_manager())
    finally:
        loop.close()
