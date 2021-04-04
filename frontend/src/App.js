import React, { useState, useEffect } from "react";
import { ReactComponent as MicrophoneIcon } from "./mic.svg";
import "./App.css";
import MicRecorder from "mic-recorder-to-mp3";
import { Table, Thead, Tbody, Tr, Th, Td } from "react-super-responsive-table";
import "react-super-responsive-table/dist/SuperResponsiveTableStyle.css";

const Recorder = new MicRecorder({ bitRate: 128 });

function App() {
  const [allowedMic, setAllowedMic] = useState(false);
  const [listening, setlistening] = useState(false);

  const [list_of_objects, set_list_of_objects] = useState({
    "House Keys": "Living Room Table",
    Charger: "Outlet near the fridge",
    Headphones: "Desk in the bedroom",
  });
  localStorage.setItem("list_of_objects", JSON.stringify(list_of_objects));

  React.useEffect(() => {
    window.addEventListener("storage", () => {
      set_list_of_objects(
        JSON.parse(localStorage.getItem("list_of_objects")) || {}
      );
    });
  }, []);

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

  const keys = Object.keys(list_of_objects);

  return (
    <Table>
      <Thead>
        <Tr>
          <Th>Object</Th>
          <Th>Location</Th>
        </Tr>
      </Thead>
      <Tbody>
        {keys.map((item) => {
          return (
            <Tr key={item}>
              <Td>{item}</Td>
              <Td>{list_of_objects[item]}</Td>
            </Tr>
          );
        })}
      </Tbody>
      <React.Fragment>
        <button onClick={onStartRecording} disabled={listening}>
          Start
        </button>
        <button onClick={onStopRecording} disabled={!listening}>
          Stop
        </button>
        <audio src={blobUrl} control="controls" />
      </React.Fragment>
    </Table>
  );
}

export default App;
