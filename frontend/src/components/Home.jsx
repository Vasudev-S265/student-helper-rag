export default function Home({onStart}){
    return(
        <div>
            <h1>AI Mentor</h1>
            <p>Ask questions about your course materials and get the answers within the sources.</p>
            <p>Your questions and feedback are used anonymously to improve this tool.</p>
            <button onClick={onStart}>Start Asking</button>
        </div>
    );
}