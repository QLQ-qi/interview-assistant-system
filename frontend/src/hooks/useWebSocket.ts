import { useState, useRef, useCallback, useEffect } from "react";
import type { ServerMessage } from "../types";

interface UseWebSocketReturn {
    connected: boolean;
    error: string | null;
    connect: (sessionId: string) => void;
    disconnect: () => void;
    sendMessage: (msg: object) => void;
}

export function useWebSocket(
    onMessage: (msg: ServerMessage) => void
): UseWebSocketReturn {
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const pingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const onMessageRef = useRef(onMessage);
    onMessageRef.current = onMessage;

    const connect = useCallback((sessionId: string) => {
        if (wsRef.current) return;
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws/meeting/${sessionId}`);
        ws.onopen = () => { setConnected(true); setError(null);
            pingIntervalRef.current = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "ping" }));
            }, 30000);
        };
        ws.onmessage = (event) => {
            try { onMessageRef.current(JSON.parse(event.data)); } catch { /* ignore */ }
        };
        ws.onerror = () => setError("WebSocket connection failed");
        ws.onclose = (event) => {
            setConnected(false);
            if (pingIntervalRef.current) { clearInterval(pingIntervalRef.current); pingIntervalRef.current = null; }
            if (event.code !== 1000) setError(`Connection closed (code ${event.code})`);
            wsRef.current = null;
        };
        wsRef.current = ws;
    }, []);

    const disconnect = useCallback(() => {
        if (wsRef.current) { wsRef.current.close(1000); wsRef.current = null; }
        setConnected(false); setError(null);
        if (pingIntervalRef.current) { clearInterval(pingIntervalRef.current); pingIntervalRef.current = null; }
    }, []);

    const sendMessage = useCallback((msg: object) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send(JSON.stringify(msg));
    }, []);

    useEffect(() => () => disconnect(), [disconnect]);

    return { connected, error, connect, disconnect, sendMessage };
}
