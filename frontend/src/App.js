import React, { useState } from "react";
import { ReactComponent as MicrophoneIcon } from "./mic.svg";
import "./App.css";

function App() {
  const [speaking, setspeaking] = useState(false);

  return (
    <React.Fragment>
      {speaking ? "You're unmuted" : "Click mute"}
      <button onClick={() => setspeaking(!speaking)}>Bruh</button>
      <div id="container">
        <h1>Sam the Helper bot</h1>
        <MicrophoneIcon />
      </div>
    </React.Fragment>
  );
}

export default App;
