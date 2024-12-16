import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ui import UserInterface
from zigbee_network import ZigbeeTransceiver
from abstract_network import AbstractTransceiver
import asyncio
import multiprocessing


class TestUI:

    class MockTransceiver(AbstractTransceiver):

        def send(self, msg):
            pass

        def receive(self, timeout):
            pass

    async def async_test_ui():
        ui = UserInterface(TestUI.MockTransceiver())
        task = asyncio.create_task(ui.websocket_client())  # asynchronous, no need to await return 
        ui.flag("NEW", 1)
        await task
    
if __name__ == '__main__':
    # Check if there's an existing event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If the loop is already running, use it to run the coroutine
            loop.run_until_complete(TestUI.async_test_ui())
        else:
            # If the loop is not running, use asyncio.run()
            asyncio.run(TestUI.async_test_ui())
    except RuntimeError:
        # If no event loop is available, create a new one
        asyncio.run(TestUI.async_test_ui())