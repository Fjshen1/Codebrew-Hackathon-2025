import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("/api/greet")               // calls Flask at localhost:5000/api/greet
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => console.error("API error:", err));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        {message
          ? <h1>{message}</h1>
          : <p>Loading…</p>
        }
      </header>
    </div>
  );
}

export default App;
