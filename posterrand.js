import React, { useState } from 'react';
import './posterrand.css';

const PostErrand = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [budget, setBudget] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log({ title, description, budget });
  };

  return (
    <div className="post-errand-container">
      <h2>What needs to be done</h2>
      <p>Fill in the details and post your errand today</p>

      <form onSubmit={handleSubmit} className="errand-form">
        <label>
          Title
          <input
            type="text"
            placeholder="e.g. Fix the plummer"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>

        <label>
          Description
          <textarea
            placeholder="Describe your errand"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          ></textarea>
        </label>

        <label>
          Budget (AUD)
          <input
            type="number"
            placeholder="e.g. 25"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
          />
        </label>

        <button type="submit" className="submit-btn">
          Post Errand
        </button>
      </form>
    </div>
  );
}

export default PostErrand;