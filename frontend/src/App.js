import React, { useState, useEffect } from "react";
import { ReactComponent as MicrophoneIcon } from "./mic.svg";
import "./App.css";
import MicRecorder from "mic-recorder-to-mp3";

const Recorder = new MicRecorder({ bitRate: 128 });

function App() {
  const [allowedMic, setAllowedMic] = useState(false);
  const [listening, setlistening] = useState(false);

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        console.log("Got audio permissions");
        setAllowedMic(true);
      })
      .catch((err) => console.log("Permission Denied\n" + err));
  });

  const onStartRecording = () => {
    if (allowedMic) {
      Recorder.start()
        .then(() => {
          setlistening(true);
        })
        .catch((e) => console.error(e));
    }
  };
  const onStopRecording = () => {
    console.log("Got here!");
    setlistening(false);
    Recorder.stop()
      .getMp3()
      .then(([buffer, blob]) => {
        console.log(blob);
        const result = URL.createObjectURL(blob);
        console.log(result);
      })
      .catch((e) => console.error(e));
  };

  return (
    <React.Fragment>
      <button onClick={onStartRecording} disabled={listening}>
        Start
      </button>
      <button onClick={onStopRecording} disabled={!listening}>
        Stop
      </button>
    </React.Fragment>
  );
}

export default App;
