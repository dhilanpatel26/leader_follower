import paho.mqtt.client as mqtt
import json
from abstract_network import AbstractTransceiver, AbstractNode
import multiprocessing
#import device_classes as dc
from queue import Queue
import time

class ZigbeeNode(AbstractNode):
     
    def __init__(self, node_id, target_func = None, target_args = None, active: multiprocessing.Value = None):  # type: ignore
        self.transceiver = ZigbeeTransceiver(broker_address='localhost', broker_port=1883)  # address and port subject to change
        self.setup(node_id, target_func, target_args, active)

class ZigbeeTransceiver(AbstractTransceiver):
    
    def __init__(self, broker_address='localhost', broker_port=1883, username=None, password=None):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.sub_client = mqtt.Client()
        self.pub_client = mqtt.Client()
        self.sub_topic = 'zigbee2mqtt/bridge/request/device/permit_join'
        self.rcv_queue = Queue()

        if username and password:
            self.sub_client.username_pw_set(username, password)
            self.pub_client.username_pw_set(username, password)
        
        # sub loop callback funcs
        self.sub_client.on_connect = self.on_sub_connect
        self.sub_client.on_message = self.on_message
        
        # start sub loop
        self.sub_client.user_data_set(self.rcv_queue)
        self.sub_client.connect(self.broker_address, self.broker_port)
        self.sub_client.loop_start()  # Start the loop in a separate thread

        # start pub loop
        self.pub_client.connect(self.broker_address, self.broker_port)
        self.pub_client.loop_start()  # Start the loop in a separate thread

    def send(self, msg, topic='zigbee2mqtt/bridge/request/device/permit_join'):
        # Convert the message to JSON if it's a dictionary
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        
        # Publish the message to the specified topic
        # qos=1 waits for acknowledgement from broker  (we could do 0 which has no wait)
        msg_info = self.client.publish(topic, msg, qos=1)
        # rc is at index 0 of msg_info - will be 0 if success
        # we could use this to decide whether we should resend or not?
    
    def receive(self, timeout):
        # sub client is already subscribed, we just wait for queue to receive
        end = time.time() + timeout
        msg = self.rcv_queue.get(timeout=timeout)
        return msg

    def __del__(self):
        self.client.loop_stop()  # Stop the loop when the object is deleted
        self.client.disconnect()

    def on_message(self, client, userdata, message):
        # we want to put any message received since protocol will
        # handle whether it is valid or not
        # we could change this setup to allow for checks here which may be faster
        userdata.put(self, message.payload)

    def on_sub_connect(self, client, userdata, flags, reason_code, properties):
        client.subscribe(self.sub_topic)