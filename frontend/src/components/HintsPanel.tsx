import { User, AlertTriangle, BookOpen, Lightbulb } from "lucide-react";
import type { HintMessage } from "../types";

interface HintsPanelProps {
    hints: HintMessage[];
}

export function HintsPanel({ hints }: HintsPanelProps) {
    if (hints.length === 0) {
        return (
            <div className="hints-panel">
                <div className="panel-header">
                    <Lightbulb size={18} />
                    <span>AI Insights</span>
                </div>
                <div className="hints-empty">
                    <p>Waiting for AI-generated insights...</p>
                    <p className="hint-sub">Insights will appear here during the interview</p>
                </div>
            </div>
        );
    }

    return (
        <div className="hints-panel">
            <div className="panel-header">
                <Lightbulb size={18} />
                <span>AI Insights</span>
                <span className="badge">{hints.length}</span>
            </div>
            <div className="hints-list">
                {[...hints].reverse().map((hint, i) => {
                    const icons: Record<string, React.ReactNode> = {
                        standard_talk: <BookOpen size={16} />,
                        warning: <AlertTriangle size={16} />,
                        case_reference: <User size={16} />,
                    };
                    return (
                        <div key={i} className={`hint-item hint-${hint.hint_type}`}>
                            <div className="hint-icon">{icons[hint.hint_type] || <Lightbulb size={16} />}</div>
                            <div className="hint-content">
                                <span className="hint-text">{hint.hint}</span>
                                <span className="hint-confidence">
                                    {Math.round(hint.confidence * 100)}% confidence
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
