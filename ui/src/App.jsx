import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import DashboardPage from './pages/DashboardPage';
import AgentGalleryPage from './pages/AgentGalleryPage';
import WorkflowEditorPage from './pages/WorkflowEditorPage';
import LiveConsolePage from './pages/LiveConsolePage';
import VrindaAIApp from './pages/VrindaAIApp'; // <--- IMPORT THIS

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/agents" element={<AgentGalleryPage />} />
          <Route path="/workflows" element={<WorkflowEditorPage />} />
          <Route path="/logs" element={<LiveConsolePage />} />
          <Route path="/vrinda-ai" element={<VrindaAIApp />} /> {/* <--- ADD ROUTE */}
          
          <Route path="/settings" element={<div className="p-8 text-white">Settings Page</div>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;