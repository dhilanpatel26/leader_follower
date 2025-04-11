import React from 'react';
import { sendWebSocketCommand } from '../lib/websocket';

interface NodeProps {
  node: {
    id: string;
    role: string;
    status?: string;
    task?: number;
  };
}

const RobotNode: React.FC<NodeProps> = ({ node }) => {
  const handleDeactivate = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering parent container click events
    
    if (confirm(`Are you sure you want to deactivate device ${node.id}?`)) {
      // Send deactivate command to backend
      sendWebSocketCommand({
        type: 'deactivate_device',
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
      onClick={handleDeactivate}
      title={`Click to deactivate device ${node.id}`}
    >
      {node.id}
      <div style={{ position: 'absolute', top: '-20px', fontSize: '12px' }}>
        {node.task && `Task: ${node.task}`}
      </div>
    </div>
  );
};

export default RobotNode;