import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  const [errands, setErrands] = useState([]);

  useEffect(() => {
    const fetchErrands = async () => {
      const data = [
        { id: 1, title: 'Buy groceries', description: 'Need someone to buy groceries' },
        { id: 2, title: 'Dog walking', description: 'Walk my dog in the park' },
        { id: 3, title: 'House cleaning', description: 'Need a cleaner for my apartment' },
      ];
      setTimeout(() => setErrands(data), 500);
    };

    fetchErrands();
  }, []);

  return (
    <div className="home-container">
      <header className="navbar">
        <h1 className="logo">AvailableErrand</h1>
        <div className="profile">
          <Link to="/profile">
            <img src="https://via.placeholder.com/40" alt="Profile" className="profile-img" />
          </Link>
        </div>
      </header>
      <section className="hero">
        <h2>Enrich your profile to help others</h2>
        <p>Get your job done with just a click.</p>
        <button className="create-btn">+ Post a New Errand</button>
      </section>
      <section className="errands-grid">
        {errands.map((errand) => (
          <div key={errand.id} className="errand-card">
            <h3>{errand.title}</h3>
            <p>{errand.description}</p>
            <button className="claim-btn">Claim</button>
          </div>
        ))}
      </section>
    </div>
  );
}

export default Home;