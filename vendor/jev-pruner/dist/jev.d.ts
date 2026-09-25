export declare const SYSTEM_ONE_URL = "https://api.typesafe.ai/v1/systemone";
export declare const DEFAULT_MODEL = "jev-latest";
/** The `state` of a Jev request: a string or any JSON-serialisable object. */
export type JevState = string | object;
export interface NoulQuestion {
    type: 'noul';
    instructions: string;
    criteria?: {
        true?: string;
        false?: string;
    };
}
export interface ChoiceQuestion {
    type: 'choice';
    instructions: string;
    criteria: Record<string, string | null>;
}
export interface ScoreQuestion {
    type: 'score';
    instructions: string;
    criteria: string[];
}
export type JevQuestion = NoulQuestion | ChoiceQuestion | ScoreQuestion;
export type JevQuestions = Record<string, JevQuestion>;
export interface NoulAnswer {
    type?: 'noul';
    noul: number;
}
export interface ChoiceAnswer {
    type?: 'choice';
    choice: string;
    confidence: number;
    probabilities: Record<string, number>;
}
export interface ScoreAnswer {
    type?: 'score';
    score: number;
    confidence: number;
    probabilities: Record<string, number>;
}
export type JevAnswer = NoulAnswer | ChoiceAnswer | ScoreAnswer;
export interface JevResponse {
    model?: string;
    answers: Record<string, JevAnswer>;
    usage?: {
        input_tokens?: number;
        output_tokens?: number;
    };
    [key: string]: unknown;
}
/** Anything that can answer Jev questions: `JevClient`, or a host-provided adapter. */
export interface JevAsker {
    ask(state: JevState, questions: JevQuestions): Promise<JevResponse>;
}
export interface JevRequest {
    url: string;
    method: 'POST';
    headers: Record<string, string>;
    body: string;
}
/** The HTTP request for one Jev call, for any fetch-like transport. */
export declare function buildJevRequest(params: {
    apiKey: string;
    model?: string;
    baseUrl?: string;
}, state: JevState, questions: JevQuestions): JevRequest;
/** Validates a Jev response body; throws on anything but an `answers` object. */
export declare function parseJevResponse(status: number, ok: boolean, text: string): JevResponse;
/** The `noul` probability of one answer; throws when it is not there. */
export declare function noulAnswer(answers: Record<string, JevAnswer>, name: string): number;
/**
 * Estimates tokens without a tokenizer: a word costs one token per six
 * letters, a digit half a token, any other symbol nine tenths. Calibrated
 * against the usage Jev reports for real transcripts, where it lands 2–18%
 * above the true count; a plain characters-per-token ratio undercounts the
 * JSON-heavy states by up to 40%.
 */
export declare function estimateTokens(text: string): number;
export declare function estimateStateTokens(text: string): number;
//# sourceMappingURL=jev.d.ts.map