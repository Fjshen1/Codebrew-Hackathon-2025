import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './Home';
import PostErrand from './posterrand';
import Profile from './profile';
import './App.css';


function App() {
  return (
    <Router>
     
     <section className="navigation-buttons">
      <Link to="/"><button className="nav-btn">Home</button></Link>
      <Link to="/post"><button className="nav-btn">Post Errand</button></Link>
      <Link to="/profile"><button className="nav-btn">Profile</button></Link>
      <Link to="/chat"><button className="nav-btn">Chat</button></Link>
    </section>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/post" element={<PostErrand />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
  
    </Router>
  );
}

export default App;
