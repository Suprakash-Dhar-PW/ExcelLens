import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import AppLayout from "./components/layout/AppLayout"
import Dashboard from "./pages/Dashboard"
import Upload from "./pages/Upload"
import Copilot from "./pages/Copilot"

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/copilot" element={<Copilot />} />
        </Routes>
      </AppLayout>
    </Router>
  )
}

export default App
