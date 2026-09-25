import type { JevAsker } from './jev.js';
import type { ConversationMessage } from './history.js';
export declare const MIN_OUTPUT_TOKENS = 10000;
type OutputCategory = 'build' | 'search' | 'document' | 'unknown';
export type TrimDecision = 'below_threshold' | 'binary' | 'document' | 'few_chunks' | 'no_scoring_capacity' | 'budget_unfit' | 'incomplete_coverage' | 'kept_all' | 'pruned';
export interface TrimOutputOptions {
    minTokens?: number;
    /**
     * agent-factory local change (vendor/jev-pruner/PROVENANCE.md): the floor under
     * minTokens. Default MIN_OUTPUT_TOKENS; only a caller that passes it lowers it.
     */
    minTokensFloor?: number;
    chunkLines?: number;
    /** Optional character target instead of line grouping; 0 uses chunkLines. */
    chunkChars?: number;
    onDecision?: (reason: TrimDecision) => void;
    keepThreshold?: number;
    maxStateTokens?: number;
    /**
     * Cap on rendered pruned output, including markers. If errors or unscored
     * content cannot fit safely, return the original output. 0 means no cap.
     */
    maxChars?: number;
    /** Maximum additional Jev requests, including refinement and retries. */
    maxScoringRequests?: number;
    /** Short omission markers and one recovery footer, included in maxChars. */
    compactMarkers?: boolean;
}
export interface TrimOutputInput {
    command: string;
    goal: string;
    output: string;
    fullOutputPath?: string;
    messages?: readonly ConversationMessage[];
}
export interface TrimOutputResult {
    output: string;
    trimmed: boolean;
    chunks: number;
    kept: number;
    dropped: number;
    charsBefore: number;
    charsAfter: number;
    scores: number[];
}
export declare function exceedsOutputThreshold(output: string, minTokens?: number, minTokensFloor?: number): boolean;
/** Output with NULs or a lot of control bytes is not text worth chunking. */
export declare function looksBinary(output: string): boolean;
/**
 * Output the agent is likely to parse as one document (a file dump, a diff, a
 * JSON blob). Cutting a hole in it leaves something that still looks complete
 * but is not, so it is left alone.
 */
export declare function looksStructured(command: string, output: string): boolean;
export declare function classifyOutput(command: string, output: string): OutputCategory;
export declare function recoveryFooter(path?: string): string;
export declare function trimOutput(input: TrimOutputInput, asker: JevAsker, options?: TrimOutputOptions): Promise<TrimOutputResult>;
export {};
//# sourceMappingURL=output.d.ts.map