import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { FaRobot, FaProjectDiagram, FaServer, FaBolt, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';

// Mock Data for the Graph
const healthData = [
  { time: '10:00', load: 20 },
  { time: '10:05', load: 35 },
  { time: '10:10', load: 25 },
  { time: '10:15', load: 60 },
  { time: '10:20', load: 45 },
  { time: '10:25', load: 80 },
  { time: '10:30', load: 55 },
];

const StatCard = ({ title, value, subtext, icon: Icon, color }) => (
  <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl shadow-lg flex items-center justify-between">
    <div>
      <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wider">{title}</h3>
      <div className="text-3xl font-bold text-white mt-2">{value}</div>
      <div className={`text-xs mt-1 ${color === 'green' ? 'text-green-400' : 'text-blue-400'}`}>
        {subtext}
      </div>
    </div>
    <div className={`p-4 rounded-full bg-opacity-10 ${color === 'green' ? 'bg-green-500 text-green-400' : 'bg-blue-500 text-blue-400'}`}>
      <Icon className="text-2xl" />
    </div>
  </div>
);

const DashboardPage = () => {
  return (
    <div className="p-8 space-y-8 animate-fade-in">
      
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white">System Overview</h1>
          <p className="text-gray-400 mt-1">Real-time metrics for Vryndara Kernel</p>
        </div>
        <div className="flex gap-4">
            <span className="flex items-center gap-2 text-green-400 bg-green-900/20 px-4 py-2 rounded-full border border-green-900/50 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Kernel Online
            </span>
        </div>
      </div>

      {/* Top Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Active Agents" value="3" subtext="1 Local, 2 Remote" icon={FaRobot} color="blue" />
        <StatCard title="Running Workflows" value="1" subtext="Optimization Job" icon={FaProjectDiagram} color="green" />
        <StatCard title="Memory Usage" value="24%" subtext="4.2GB / 16GB" icon={FaServer} color="blue" />
        <StatCard title="Total Events" value="1,024" subtext="+120 this hour" icon={FaBolt} color="green" />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Health Graph */}
        <div className="lg:col-span-2 bg-gray-800 border border-gray-700 rounded-xl p-6 shadow-lg">
          <h2 className="text-xl font-bold text-white mb-6">System Load & Activity</h2>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={healthData}>
                <defs>
                  <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                <XAxis dataKey="time" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#fff' }} 
                  itemStyle={{ color: '#10B981' }}
                />
                <Area type="monotone" dataKey="load" stroke="#10B981" fillOpacity={1} fill="url(#colorLoad)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Column: Recent Activity Log */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow-lg">
          <h2 className="text-xl font-bold text-white mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {[
              { time: '10:32', msg: 'Coder Agent generated python_script.py', type: 'success' },
              { time: '10:30', msg: 'User submitted task: "Write TicTacToe"', type: 'info' },
              { time: '10:28', msg: 'Kernel synced with Postgres DB', type: 'info' },
              { time: '10:15', msg: 'Gateway accepted connection from IP 127.0.0.1', type: 'success' },
              { time: '09:55', msg: 'Warning: High Memory usage on Agent-2', type: 'warning' },
            ].map((log, i) => (
              <div key={i} className="flex gap-3 items-start border-b border-gray-700 pb-3 last:border-0">
                <div className={`mt-1 ${log.type === 'warning' ? 'text-yellow-500' : 'text-green-500'}`}>
                    {log.type === 'warning' ? <FaExclamationTriangle /> : <FaCheckCircle />}
                </div>
                <div>
                  <p className="text-gray-300 text-sm">{log.msg}</p>
                  <span className="text-gray-500 text-xs">{log.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default DashboardPage;