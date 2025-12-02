import { Link, useLocation } from 'react-router-dom';
import { FaChartPie, FaRobot, FaProjectDiagram, FaTerminal, FaCogs } from 'react-icons/fa';

const Layout = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: FaChartPie, label: 'Dashboard' },
    { path: '/agents', icon: FaRobot, label: 'Agents' },
    { path: '/workflows', icon: FaProjectDiagram, label: 'Workflows' },
    { path: '/logs', icon: FaTerminal, label: 'Logs' },
  ];

  return (
    <div className="flex h-screen bg-gray-900 font-mono">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-green-400">vryndara-platform</h1>
        </div>
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    location.pathname === item.path
                      ? 'bg-green-900/30 text-green-400 font-semibold'
                      : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <item.icon className="text-xl" />
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div className="p-4 border-t border-gray-700">
          <Link to="/settings" className="flex items-center gap-3 px-4 py-3 text-gray-400 hover:bg-gray-700 hover:text-white rounded-lg transition-colors">
            <FaCogs className="text-xl" />
            <span>Settings</span>
          </Link>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
};

export default Layout;