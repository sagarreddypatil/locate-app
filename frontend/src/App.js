import React, { useState, useEffect } from "react";
import "./App.css";
import MicRecorder from "mic-recorder-to-mp3";
import { Table, Thead, Tbody, Tr, Th, Td } from 'react-super-responsive-table';
import 'react-super-responsive-table/dist/SuperResponsiveTableStyle.css';
import Siriwave from 'react-siriwave';
import ClickNHold from 'react-click-n-hold';

const Recorder = new MicRecorder({ bitRate: 128 });

function App() {
  const [allowedMic, setAllowedMic] = useState(false);
  const [listening, setlistening] = useState(false);

  const existingData = localStorage.getItem("list_of_objects");

  const [list_of_objects, set_list_of_objects] = useState(
    existingData ? JSON.parse(existingData) : {}
  );
  // localStorage.setItem("list_of_objects", JSON.stringify(list_of_objects));

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
        fetch("https://mighty-emu-61.loca.lt/input", {
          method: "POST",
          body: blob,
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.type === "retrieval") {
              let item = data.item;
              console.log("Item key is this: " + item);
              let correspondingLocation = JSON.parse(
                window.localStorage.getItem("list_of_objects")
              )[item];
              console.log(correspondingLocation);
            } else {
              let item = data.item;
              let location = data.location;
              set_list_of_objects((list_of_objects) => {
                const newObjects = { ...list_of_objects, [item]: location };
                window.localStorage.setItem(
                  "list_of_objects",
                  JSON.stringify(newObjects)
                );

                return newObjects;
              });
            }
          })
          .catch((e) => console.error(e));
        const result = URL.createObjectURL(blob);
        console.log(result);
      })
      .catch((e) => console.error(e));
  };

  const keys = Object.keys(list_of_objects);

  return (
      <div className="background table-properties">
        <h1 className="title-header">LoKate</h1>
          <div className="center-everything-pls block">
            <Table className='table-of-objects'>
              <Thead>
                <Tr>
                  <Th className="table-cell">Object</Th>
                  <Th className="table-cell">Location</Th>
                </Tr>
              </Thead>
              <Tbody>
              {keys.map(item => {
                return (
                  <Tr key={item}>
                    <Td className="table-cell">{item}</Td>
                    <Td className="table-cell">{list_of_objects[item]}</Td>
                  </Tr>
                );
              })}
              </Tbody>
            </Table>
          </div>
        <div className='block'>
          <Siriwave style="ios9"></Siriwave>
        </div>
        <div className="block">
          <React.Fragment >
            <div className="record-section">
              <ClickNHold
                time={10} // Time to keep pressing. Default is 2
                onStart={onStartRecording} // Start callback
                onClickNHold={onStartRecording} //Timeout callback
                onEnd={onStopRecording}> 
                <button className='start-stop-buttons'>Click and hold</button> 
              </ClickNHold>
            </div>
          </React.Fragment> 
        </div>
      </div>
  );
}

export default App;
