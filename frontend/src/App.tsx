import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Admin from './pages/Admin'
import Survey from './pages/Survey'
import Results from './pages/Results'
import ClusterDetail from './pages/ClusterDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/admin" replace />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/survey/:id" element={<Survey />} />
        <Route path="/results/:id" element={<Results />} />
        <Route path="/results/:id/cluster/:clusterId" element={<ClusterDetail />} />
      </Routes>
    </BrowserRouter>
  )
}
