import { useState } from "react";
import { Wifi, WifiOff, LoaderCircle, Plug, PlugZap } from "lucide-react";

interface ConnectionPanelProps {
    connected: boolean;
    error: string | null;
    onConnect: (sessionId: string) => void;
    onDisconnect: () => void;
    sessionId: string;
    onSessionIdChange: (id: string) => void;
}

export function ConnectionPanel({ connected, error, onConnect, onDisconnect, sessionId, onSessionIdChange }: ConnectionPanelProps) {
    const [connecting, setConnecting] = useState(false);

    const handleConnect = () => {
        if (!sessionId.trim()) return;
        setConnecting(true);
        onConnect(sessionId.trim());
        setTimeout(() => setConnecting(false), 1000);
    };

    const handleDisconnect = () => {
        onDisconnect();
        setConnecting(false);
    };

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 11a9 9 0 0 1 9 9" />
                    <path d="M4 4a16 16 0 0 1 16 16" />
                    <circle cx="5" cy="19" r="1" />
                </svg>
                <span>Interview Assistant</span>
            </div>

            <div className="sidebar-section">
                <label className="sidebar-label">Session ID</label>
                <input
                    type="text"
                    className="sidebar-input"
                    placeholder="Enter meeting session ID..."
                    value={sessionId}
                    onChange={(e) => onSessionIdChange(e.target.value)}
                    disabled={connected}
                />
            </div>

            <div className="sidebar-section">
                {!connected ? (
                    <button className="btn btn-primary" onClick={handleConnect} disabled={connecting || !sessionId.trim()}>
                        {connecting ? <LoaderCircle size={16} className="spin" /> : <Plug size={16} />}
                        {connecting ? "Connecting..." : "Connect"}
                    </button>
                ) : (
                    <button className="btn btn-danger" onClick={handleDisconnect}>
                        <PlugZap size={16} />
                        Disconnect
                    </button>
                )}
            </div>

            <div className="status-section">
                <div className={`status-indicator ${connected ? "connected" : "disconnected"}`}>
                    {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
                    <span>{connected ? "Connected" : "Disconnected"}</span>
                </div>
                {connected && (
                    <div className="session-info">
                        <span className="sidebar-label">Session:</span>
                        <span className="session-id">{sessionId}</span>
                    </div>
                )}
                {error && <div className="error-msg">{error}</div>}
            </div>
        </div>
    );
}
