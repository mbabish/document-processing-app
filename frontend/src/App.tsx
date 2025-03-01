import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ReportList from './components/ReportList';
import './index.css';

interface AppProps {}

const App = (props: AppProps): JSX.Element => {
  return (
    <Router>
      <div className="container">
        <header className="header">
          <h1>Document Processing Dashboard</h1>
        </header>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/reports" element={<ReportList />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;