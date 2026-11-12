import { useState } from "react";
import Message from "./Message";


const API_URL="http://127.0.0.1:8000";

function getSessionId(){
    let id=localStorage.getItem("session_id")
    if(!id){
        id=crypto.randomUUID();
        localStorage.setItem("session_id", id)

    }

    return id;
}


export default function Chat(){
    const[messages, setMessages]=useState([])
    const[input, setInput]=useState("")
    const[status, setStatus]=useState("idle")

    async function sendQuestion(e) {
       e.preventDefault();
       const question=input.trim();
       if(!question|| status=="thinking") return;
       
       setMessages((prev)=>[...prev, {role:"user", text:question}]);
       setInput("");
       setStatus("Thinking");

       try{
        const res=await fetch(`${API_URL}/ask`, {
            method:"POST",
            headers:{"Content-type":"application/json"},
            body:JSON.stringify({question, session_id:getSessionId()}),
        });

        const data = await res.json();
        if(!res.ok){
            throw new Error(typeof data.detail==="string"? data.detail:"Something went wrong.");

        }

        setMessages((prev)=>[
            ...prev,
            {role:"bot", text:data.answer, sources:data.sources, interactionId: data.interaction_id},
        ]);
        setStatus("idle");
       }
       catch(err){
        const text = err instanceof TypeError ? "Can't reach the server. Try again in a few moments." : err.message;
        setMessages((prev)=>[...prev, {role:"error", text}]);
        setStatus("error");
       }
    }

    return(
        <div className="chat">
            <div className="messages">
                {messages.map((m, i) => <Message key={i} message={m} />)}

                {status==="thinking" && <div className="thinking"> Thinking... </div>}
            </div>

            <form className="input-bar" onSubmit={sendQuestion}>
                <input
                value={input}
                onChange={(e)=>setInput(e.target.value)}
                placeholder="Ask a question..."
                maxLength={500}/>
                <button disabled={status==="thinking"}>Send</button>
            </form>
        </div>
    );
}