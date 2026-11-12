import { useState } from "react";
import Home from "./components/Home"
import Chat from './components/Chat'

export default function App(){
  const[screen, setScreen]=useState("Home")

  return screen==="Home"?<Home onStart={()=>setScreen("chat")}/>
  :<Chat/>
}