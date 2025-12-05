import React, { useEffect, useState } from 'react';
import { DeviceInfo } from '../types/websocket'; // Adjust the import path as necessary
import RobotNode from './robot';

interface TrackBoxProps {
  className?: string;
  onCellClick?: (cellNumber: number) => void;
  devices: DeviceInfo[];
}

const TrackBox: React.FC<TrackBoxProps> = ({ className, onCellClick, devices }) => {
  const [robotPositions, setRobotPositions] = useState<Record<number, DeviceInfo | null>>({
    1: null,
    2: null,
    3: null,
    4: null,
  });

  const [reservePositions, setReservePositions] = useState<Record<number, DeviceInfo | null>>({
    1: null,
    2: null,
    3: null,
    4: null,
  });
  
  const [inactivePositions, setInactivePositions] = useState<Record<number, DeviceInfo | null>>({
    1: null,
    2: null,
    3: null,
    4: null,
    5: null,
    6: null,
    7: null,
    8: null,
  });



  

  useEffect(() => {
    const newPositions: Record<number, DeviceInfo | null> = {1: null, 2: null, 3: null, 4: null};
    const newReserves: Record<number, DeviceInfo | null> = {1: null, 2: null, 3: null, 4: null};
    const newInactive: Record<number, DeviceInfo | null> = {1: null, 2: null, 3: null, 4: null, 5: null, 6: null, 7: null, 8: null};

    let numReserves: number;
    numReserves = 0;
    let numInactive: number;
    numInactive = 0;

    devices.forEach(device => {
      const position = parseInt(device.task); // 5 is the "sleeping" position
      if (position === 0) {
        numReserves += 1;
        newReserves[numReserves] = device;
      } else if (position === 5) {
        numInactive += 1;
        newInactive[numInactive] = device;
      } else {
        newPositions[position] = device;
      }
      
    });

    setRobotPositions(newPositions);
    setReservePositions(newReserves);
    setInactivePositions(newInactive);
  }, [devices]);

  const containerStyle: React.CSSProperties = {
    padding: '20px',
    display: 'flex',
    gap: '20px',
    alignItems: 'center',
  };
  
  const gridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gridTemplateRows: '1fr 1fr',
    gap: '10px',
    width: '300px',
    height: '300px',
    maxWidth: '100%',
  };

  const reserveGridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: '1fr',
    gridTemplateRows: '1fr 1fr 1fr 1fr',
    width: '150px',
    height: '300px',
    maxWidth: '100%',
    border: '1px solid #ccc',
    borderRadius: '4px'
  };

  const inactiveGridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gridTemplateRows: '1fr 1fr 1fr 1fr',
    width: '150px',
    height: '300px',
    maxWidth: '100%',
    border: '1px solid #ccc',
    borderRadius: '4px'
  };

  const cellStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '24px',
    fontWeight: 'bold',
    cursor: onCellClick ? 'pointer' : 'default',
    transition: 'background-color 0.2s',
    position: 'relative',
  };

  const reserveCellStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    borderRadius: '4px',
    fontSize: '24px',
    fontWeight: 'bold',
    cursor: onCellClick ? 'pointer' : 'default',
    transition: 'background-color 0.2s',
    position: 'relative',
  };
  
  const cellNumberStyle: React.CSSProperties = {
    position: 'absolute',
    top: '5px',
    left: '5px',
    fontSize: '22px',
    color: '#666',
    zIndex: 1,
  };

  const reserveNumberStyle: React.CSSProperties = {
    position: 'absolute',
    top: '-30px',
    fontSize: '22px',
    color: '#666',
    zIndex: 1,
  };

  const handleCellClick = (cellNumber: number) => {
    if (onCellClick) {
      onCellClick(cellNumber);
    }
  };

  return (
    <div className={`track-box ${className || ''}`} style={containerStyle}>
      {/* Inactive 4x2 grid */}
      <div style={inactiveGridStyle}>
        {[1, 2, 3, 4, 5, 6, 7, 8].map(cellNumber => (
          <div 
            key={cellNumber}
            style={reserveCellStyle} 
            onClick={() => handleCellClick(cellNumber)}
          >
            <span style={reserveNumberStyle}>{cellNumber === 1 ? 'Inactive' : ''}</span>
            {inactivePositions[cellNumber] && (
              <div style={{ position: 'absolute' }}>
                <RobotNode 
                  node={{
                    id: inactivePositions[cellNumber]?.id || '',
                    role: '',
                    status: 'inactive',
                    task: '',
                    missed: 0
                  }} 
                />
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Main 2x2 grid for positions 1-4 */}
      <div style={gridStyle}>
        {[1, 2, 3, 4].map(cellNumber => (
          <div 
            key={cellNumber}
            style={cellStyle} 
            onClick={() => handleCellClick(cellNumber)}
          >
            <span style={cellNumberStyle}>{cellNumber}</span>
            {robotPositions[cellNumber] && (
              <div style={{ position: 'absolute' }}>
                <RobotNode 
                  node={{
                    id: robotPositions[cellNumber]?.id || '',
                    role: robotPositions[cellNumber]?.leader ? 'leader' : 'follower',
                    status: robotPositions[cellNumber]?.missed > 0 ? 'inactive' : 'active',
                    task: robotPositions[cellNumber]?.task,
                    missed: robotPositions[cellNumber]?.missed
                  }} 
                />
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Reserves 4x1 grid (max 4 reserves) */}
      <div style={reserveGridStyle}>
        {[1, 2, 3, 4].map(cellNumber => (
          <div 
            key={cellNumber}
            style={reserveCellStyle} 
            onClick={() => handleCellClick(cellNumber)}
          >
            <span style={reserveNumberStyle}>{cellNumber === 1 ? 'Reserves' : ''}</span>
            {reservePositions[cellNumber] && (
              <div style={{ position: 'absolute' }}>
                <RobotNode 
                  node={{
                    id: reservePositions[cellNumber]?.id || '',
                    role: reservePositions[cellNumber]?.leader ? 'leader' : 'follower',
                    status: reservePositions[cellNumber]?.missed > 0 ? 'inactive' : 'active',
                    task: reservePositions[cellNumber]?.task,
                    missed: reservePositions[cellNumber]?.missed
                  }} 
                />
              </div>
            )}
          </div>
        ))}
      </div>
      
    </div>
  );
};

export default TrackBox;
