/*type DeviceStatusProps = {
  device: {
    id: string;
    isLeader: boolean;
    leaderId: string;
  };
};

export function DeviceStatus({ device }: DeviceStatusProps) {
  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Device Status</h2>
      <div className="bg-card rounded-lg p-4 shadow">
        <p>Device ID: <span className="font-mono">{device.id}</span></p>
        <p>Role: {'User Interface'}</p>
      </div>
    </div>
  );
}*/
type ActionDict = Record<number, string>;

const actions: ActionDict = {
  1: 'Attendance', 
  2: 'Attendance Response',
  3: 'Device List',
  4: 'Check In',
  5: 'Delete',
  6: 'New Leader',
  7: 'Task Start',
  8: 'Check In Response',
  9: 'Information',
  10: 'Off',
  11: 'On',
  12: 'New Follower',
  13: 'Activate',
  14: 'Deactivate'
};

type Message = {
  type: 'sent' | 'received';
  action: number
  payload: number;
  leaderId: number;
  followerId: number;
  timestamp: number;
};

type MessageLogProps = {
  messages: Message[];
};

const taskStatus: Record<number, number | null> = {1: null, 2: null, 3: null, 4: null};

export function DeviceStatus({ messages }: MessageLogProps) {
  

  let numCompleted: number;
  numCompleted = 0;

  messages.forEach(msg => {
    if (msg.action === 9) {
      taskStatus[msg.followerId] = msg.payload;
      numCompleted += 1;
    }   
  })

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Sheep Found </h2>
      <div className="bg-card rounded-lg p-4 shadow">
        <p>Quad 1: <span className="font-mono">{taskStatus[1] === null ? 'Counting incomplete' : taskStatus[1]}</span></p>
        <p>Quad 2: <span className="font-mono">{taskStatus[2] === null ? 'Counting incomplete' : taskStatus[2]}</span></p>
        <p>Quad 3: <span className="font-mono">{taskStatus[3] === null ? 'Counting incomplete' : taskStatus[3]}</span></p>
        <p>Quad 4: <span className="font-mono">{taskStatus[4] === null ? 'Counting incomplete' : taskStatus[4]}</span></p>
      </div>
    </div>
  );
}
