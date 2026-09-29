import { useEffect, useState } from "react";

function App() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/status")
      .then((response) => response.json())
      .then((data) => {
        setStatus(data.message);
      })
      .catch(() => {
        setStatus("Backend connection failed");
      });
  }, []);

  return (
    <div>
      <h1>AISoC</h1>
      <h2>AI-Powered Research Assistant</h2>
      <p>{status}</p>
    </div>
  );
}

export default App;