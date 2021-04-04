import React, { useState, useEffect } from "react";
import { ReactComponent as MicrophoneIcon } from "./mic.svg";
import "./App.css";

import { Table, Thead, Tbody, Tr, Th, Td } from 'react-super-responsive-table'


function App() {

  const [list_of_objects, set_list_of_objects] = useState({ 'House Keys': 'Living Room Table', 'Charger': 'Outlet near the fridge', 'Headphones': 'Desk in the bedroom' });
  localStorage.setItem('list_of_objects', JSON.stringify(list_of_objects));

  React.useEffect(() => {
    
    window.addEventListener('storage', () => {
      set_list_of_objects(JSON.parse(localStorage.getItem('list_of_objects')) || {})   
    });
      
    }, [])

  const keys = Object.keys(list_of_objects)

  return (
      <Table>
        <Thead>
          <Tr>
            <Th>Object</Th>
            <Th>Location</Th>
          </Tr>
        </Thead>
        <Tbody>
        {keys.map(item => {
          return (
            <Tr key={item}>
              <Td>{item}</Td>
              <Td>{list_of_objects[item]}</Td>
            </Tr>
          );
        })}
        </Tbody>
      </Table>
  );
}

export default App;

