interface TranscriptionMessage {
    type: "transcription";
    session_id: string;
    text: string;
    speaker: "interviewer" | "candidate";
    timestamp: string;
}

interface HintMessage {
    type: "hint";
    session_id: string;
    hint: string;
    hint_type: "standard_talk" | "case_reference" | "warning";
    confidence: number;
}

interface PingMessage {
    type: "pong";
}

type ServerMessage = TranscriptionMessage | HintMessage | PingMessage;

export type { TranscriptionMessage, HintMessage, ServerMessage };
