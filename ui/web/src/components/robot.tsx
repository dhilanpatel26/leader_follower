import React from 'react';
import { sendWebSocketCommand } from '../lib/websocket';

interface NodeProps {
  node: {
    id: string;
    role: string;
    status?: string;
    task?: string;
    missed?: number;
  };
}

const RobotNode: React.FC<NodeProps> = ({ node }) => {
  const handleToggleActivation = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering parent container click events
    
    const isActive = node.status !== 'inactive';
    const action = isActive ? 'deactivate' : 'reactivate';
    
    if (confirm(`Are you sure you want to ${action} device ${node.id}?`)) {
      // Send command to backend based on current status
      sendWebSocketCommand({
        type: isActive ? 'deactivate_device' : 'reactivate_device',
        deviceId: node.id
      });
    }
  };
  
  // Determine color based on role and status
  const getColor = () => {
    if (node.status === 'inactive') return '#888888';
    return node.role === 'leader' ? '#4caf50' : '#2196f3';
  };

  return (
    <div 
      style={{
        width: '50px',
        height: '50px',
        borderRadius: '50%',
        backgroundColor: getColor(),
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'white',
        fontWeight: 'bold',
        cursor: 'pointer',
        position: 'relative'
      }}
      onClick={handleToggleActivation}
      title={`Click to ${node.status === 'inactive' ? 'reactivate' : 'deactivate'} device ${node.id}`}
    >
      {node.id}
      <div style={{ position: 'absolute', top: '-20px', fontSize: '12px' }}>
        {node.task && `Task: ${node.task}`}
      </div>
      {node.status === 'inactive' && (
        <div style={{ 
          position: 'absolute', 
          top: '50%', 
          left: '50%', 
          width: '80%', 
          height: '2px', 
          backgroundColor: 'red', 
          transform: 'translate(-50%, -50%) rotate(45deg)'
        }}></div>
      )}
    </div>
  );
};

export default RobotNode;