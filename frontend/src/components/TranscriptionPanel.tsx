import type { TranscriptionMessage } from "../types";

interface TranscriptionPanelProps {
    entries: TranscriptionMessage[];
}

export function TranscriptionPanel({ entries }: TranscriptionPanelProps) {
    if (entries.length === 0) {
        return (
            <div className="transcription-panel">
                <div className="panel-header">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        <line x1="12" y1="19" x2="12" y2="23" />
                        <line x1="8" y1="23" x2="16" y2="23" />
                    </svg>
                    <span>Transcription</span>
                </div>
                <div className="transcription-empty">
                    <p>No transcription data yet</p>
                    <p className="hint-sub">Real-time transcription will appear here once the meeting starts</p>
                </div>
            </div>
        );
    }

    return (
        <div className="transcription-panel">
            <div className="panel-header">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                    <line x1="12" y1="19" x2="12" y2="23" />
                    <line x1="8" y1="23" x2="16" y2="23" />
                </svg>
                <span>Transcription</span>
                <span className="badge">{entries.length}</span>
            </div>
            <div className="transcription-list">
                {entries.map((entry, i) => (
                    <div key={i} className={`transcription-entry ${entry.speaker}`}>
                        <div className="entry-header">
                            <span className="speaker-label">
                                {entry.speaker === "interviewer" ? "Interviewer" : "Candidate"}
                            </span>
                            <span className="entry-time">
                                {new Date(entry.timestamp).toLocaleTimeString()}
                            </span>
                        </div>
                        <p className="entry-text">{entry.text}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
