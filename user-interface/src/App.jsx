import React, { useEffect, useRef } from 'react';


// Define the App component
function App() {
  const socket = useRef(null);

  useEffect(() => {
  // Connect to the server
  socket.current = new WebSocket('ws://localhost:3000');
  // log when the connection is opened
  socket.current.addEventListener('open', () => {
    console.log('Connected to WS server!');
    socket.current.send('CONNECTED,FRONTEND')  // placement should wait for connection
  });

  // receive messages from the server
  socket.current.addEventListener('message', (event) => {
    console.log('Message from server:', event.data);
    let message = event.data.toString();
    const parts = message.split(',');
    
    if (parts[0] === 'CONNECTED') {
      updateActiveDevices(parts[1], 'ACTIVATE');
    } else if (parts[0] === 'DISCONNECTED') {
      updateActiveDevices(parts[1], 'DEACTIVATE');
    }
  });

  function updateActiveDevices(deviceId, action) {
    const active_container = document.getElementById('active-devices');
    const reserve_container = document.getElementById('reserve-devices');
    if (!active_container || !reserve_container) {
      return;  // a container is missing, TODO: throw exception
    }
    if (deviceId && action === 'ACTIVATE') {
      const device = document.getElementById(`device-${deviceId}`);
      if (device) {
        reserve_container.removeChild(device);
      }

      // add new device div to active devices
      const newDevice = document.createElement('div');
      newDevice.id = `device-${deviceId}`;
      newDevice.style.position = 'absolute';
      newDevice.style.width = '30px';
      newDevice.style.height = '30px';
      newDevice.style.borderRadius = '50%';
      newDevice.style.backgroundColor = 'skyblue';

      const label = document.createElement('div');
      label.textContent = deviceId;  // should already be a string
      label.style.position = 'absolute';
      label.style.textAlign = 'center';
      label.style.width = '100%';
      label.style.top = '-20px';

      active_container.appendChild(newDevice);
      newDevice.appendChild(label);
    } else if (deviceId && action === 'DEACTIVATE') {
      const device = document.getElementById(`device-${deviceId}`);
      if (device) {
        active_container.removeChild(device);
        reserve_container.appendChild(device);
      }
    }
    
    // update relative position of all active devices for both addition and deletion
    const active_devices = active_container.children;
    const numberOfActiveDevices = active_devices.length;
    const radius = 280;
    for (let i = 0; i < numberOfActiveDevices; i++) {
      const angle = (i / numberOfActiveDevices) * Math.PI * 2;  // angle in radians
      const x = radius * Math.cos(angle) + active_container.offsetWidth / 2;
      const y = radius * Math.sin(angle) + active_container.offsetHeight / 2;

      active_devices[i].style.left = `${x}px`;
      active_devices[i].style.top = `${y}px`;
    }

    const reserve_devices = reserve_container.children;
    const numberOfReserveDevices = reserve_devices.length;
    for (let i = 0; i < numberOfReserveDevices; i++) {
      // stack device divs vertically
      reserve_devices[i].style.left = '0px';
      reserve_devices[i].style.top = `${i * 30}px`;
    }
  }

  const buttons = document.querySelectorAll('#control-buttons button');
  const handleClicks = [];

  buttons.forEach((button, index) => {
    const handleClick = (event) => {
      button.style.animation = 'flash 0.5s';
      console.log("Button clicked:", event.target.textContent)
      // ensure the socket is open before sending
      if (socket.current.readyState === WebSocket.OPEN) {
        socket.current.send(`INJECT,${event.target.textContent}`);
      } else {
        console.error("WebSocket is not open. Current state:", socket.current.readyState);
      }
      button.addEventListener('animationend', () => {
        button.style.animation = 'none';
      });
    };

    handleClicks[index] = handleClick;  // storing reference for cleanup
    button.addEventListener('click', handleClick);
  });

  // cleanup function to remove event listeners
  return () => {
    buttons.forEach((button, index) => {
      button.removeEventListener('click', handleClicks[index]);
    });
  };
}, []);

  return (
    <>
    <div id="parent">
      <div id="control-div">
        <h1 id="control-title">Control Panel</h1>
        <div id="control-buttons">
          <button>Create Device</button>
          <button>Delete Device</button>
          <button>Toggle Device</button>
          <button>Toggle Simulation</button>
        </div>
      </div>

      <div id="device-container">
        <div id="active-devices">
        </div>

        <div id="reserve-devices">

        </div>
      </div>
    </div>
    </>
  );

}

export default App;