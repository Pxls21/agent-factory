export interface ConversationMessage {
    role: 'user' | 'assistant';
    text: string;
    toolUses: readonly {
        tool_use_id: string;
        tool: string;
        input: Record<string, unknown>;
        text?: string;
        result?: unknown;
        isError?: boolean;
    }[];
    toolResults?: readonly {
        tool_use_id: string;
        text: string;
        result?: unknown;
        isError?: boolean;
    }[];
}
export interface HistoryEntry {
    i: number;
    role: ConversationMessage['role'];
    text: string;
    tool_calls?: {
        id: string;
        tool: string;
        input: string;
        result: string;
    }[];
    tool_results?: {
        id: string;
        result: string;
    }[];
    part?: {
        field: 'text' | 'tool_calls.input' | 'tool_calls.result' | 'tool_results.result';
        offset: number;
        total_chars: number;
    };
}
export declare function historyEntries(messages: readonly ConversationMessage[]): HistoryEntry[];
export declare function splitHistory(messages: readonly ConversationMessage[], maxTokens: number): HistoryEntry[][];
//# sourceMappingURL=history.d.ts.map