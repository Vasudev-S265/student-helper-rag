import { useState } from "react";

const API_URL="http://127.0.0.1:8000";


function SourceTags({sources}){
    const unique=[... new Map(sources.map((s)=>[`${s.source}-${s.page}`, s])).values()];

    return(
        <div className="tags">
            {unique.map((s)=>(
                <span className="tag" key={`${s.source} - ${s.page}`}>
                    {s.source} . p{s.page}
                </span>
            ))}
        </div>
    );
}


function FeedbackButtons({interactionId}){
    const[choice, setChoice]=useState(null)
    const[comment, setComment]=useState("")
    const[state, setState]=useState("idle")

    async function send(helpful, text) {
        setState("sending")

        try{
            const res=await fetch(`${API_URL}/feedback`, {
                method:"POST",
                headers:{"Content-type":"application/json"},
                body:JSON.stringify({interaction_id:interactionId, helpful, comment:text})
            });

            if (!res.ok) throw new Error();

            setState("sent");
        }
        catch{
            console.error(err)
            setState("failed")
        }
    }

    if (state==="sent") return <div className="feedback-note"> Thanks for the feedback!</div>

    return(
        <div className="feedback">
            <div className="feedback-buttons">
                <button disabled={state==="sending"} onClick={()=>send(true, null)}>👍</button>
                <button disabled={state==="sending"} onClick={()=>setChoice("down")}>👎</button>
            </div>

            {choice==="down" && (
                <div className="comment-box">
                    <textarea
                    value={comment}
                    onChange={(e)=>setComment(e.target.value)}
                    placeholder="What went wrong? (optional, please do not include personal details.)"
                    maxLength={500}
                    />
                    <button disabled={state==="sending"} onClick={()=>send(false, comment.trim() || null)}>Send</button>
                </div>
            )}
            {state==="failed" && <div className="feedback-note error-text"> Couldn't send feedback. Try again.</div>}
        </div>
    );
}

export default function Message({message}){
    return(
        <div className={`msg ${message.role}`}>
            <div>{message.text}</div>

            {message.role==="bot" && (
                <>
                <SourceTags sources={message.sources}/>
                <FeedbackButtons interactionId={message.interactionId}/>
                </>
            )}
        </div>
    );
}