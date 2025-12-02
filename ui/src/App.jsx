import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import DashboardPage from './pages/DashboardPage';
import AgentGalleryPage from './pages/AgentGalleryPage';
import WorkflowEditorPage from './pages/WorkflowEditorPage';
import LiveConsolePage from './pages/LiveConsolePage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/agents" element={<AgentGalleryPage />} />
          <Route path="/workflows" element={<WorkflowEditorPage />} />
          <Route path="/logs" element={<LiveConsolePage />} />
          {/* Add a SettingsPage later */}
          <Route path="/settings" element={<div className="p-8 text-white">Settings Page</div>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;