#from abstract_driver import AbstractDriver
import time
import asyncio
from uuid import getnode
from zigbee_network import ZigbeeTransceiver, ZigbeeNode
import device_classes as dc
import multiprocessing

class ZigbeeDriver():

    async def main(self):
        self.mac_id = 1111
        shared_active = multiprocessing.Value('i', 1)
        node = ZigbeeNode(self.mac_id, active= shared_active, ip='192.168.0.208')  # takes care of channel setup and looping (non-blocking)

        # all UI comms will take place over Zigbee, websocket not necessary
        print("Starting 5 second countdown to position robot!")
        end = time.time() + 5
        while time.time() < end:
            node.transceiver.receive(5)
        node.start()
        
    async def test():
        shared_active = multiprocessing.Value('i', 1)
        node = ZigbeeNode(12, active= shared_active, ip='169.254.72.169')

        # Send a message to permit joining new devices
        node.transceiver.send({"value": "true"}, topic='zigbee2mqtt/bridge/request/device/permit_join')

        # Send a custom message to a specific device
        # node.transceiver.send({"state": "ON"}, topic='zigbee2mqtt/my_device/set')


if __name__ == "__main__":
    time.sleep(5)
    driver = ZigbeeDriver()
    # asyncio.run(driver.test())
    asyncio.run(driver.main())
