import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HomePage } from './pages/HomePage';
import { PlannerPage } from './pages/PlannerPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/plan" element={<PlannerPage />} />
      </Routes>
    </Router>
  );
}

export default App;
