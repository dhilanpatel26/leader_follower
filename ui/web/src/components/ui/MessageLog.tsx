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

export function MessageLog({ messages }: MessageLogProps) {
  return (
    <div>
      <h2 className="text-xl font-semibold my-4">Recent Messages</h2>
      <div className="bg-card rounded-lg p-4 shadow max-h-80 overflow-y-auto">
        {messages.length === 0 ? (
          <p>No messages</p>
        ) : (
          <ul className="divide-y">
            {messages.slice().reverse().map((msg, index) => (
              <li key={index} className="py-2">
                <p className={msg.type === 'sent' ? 'text-blue-600' : 'text-green-600'}>
                  {msg.type === 'sent' ? 'Sent' : 'Received'}: {actions[msg.action]}
                </p>
                <p className="text-sm">
                  Leader: {msg.leaderId}, Follower: {msg.followerId}, Payload: {msg.payload}
                </p>
                <p className="text-xs text-gray-500">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
