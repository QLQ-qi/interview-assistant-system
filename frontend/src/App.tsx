import { useState } from "react";
import type { ServerMessage, TranscriptionMessage, HintMessage } from "./types";
import { useWebSocket } from "./hooks/useWebSocket";
import { ConnectionPanel } from "./components/ConnectionPanel";
import { TranscriptionPanel } from "./components/TranscriptionPanel";
import { HintsPanel } from "./components/HintsPanel";

function App() {
    const [sessionId, setSessionId] = useState("");
    const [transcriptions, setTranscriptions] = useState<TranscriptionMessage[]>([]);
    const [hints, setHints] = useState<HintMessage[]>([]);

    const { connected, error, connect, disconnect } = useWebSocket((msg: ServerMessage) => {
        if (msg.type === "transcription") {
            setTranscriptions((prev) => [...prev, msg]);
        } else if (msg.type === "hint") {
            setHints((prev) => [...prev, msg]);
        }
    });

    const handleConnect = (sid: string) => {
        setTranscriptions([]);
        setHints([]);
        connect(sid);
    };

    const handleDisconnect = () => {
        disconnect();
    };

    return (
        <div className="app-layout">
            <ConnectionPanel
                connected={connected}
                error={error}
                onConnect={handleConnect}
                onDisconnect={handleDisconnect}
                sessionId={sessionId}
                onSessionIdChange={setSessionId}
            />
            <main className="main-content">
                <div className="content-panels">
                    <TranscriptionPanel entries={transcriptions} />
                    <HintsPanel hints={hints} />
                </div>
            </main>
        </div>
    );
}

export default App;
