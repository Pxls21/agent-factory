import type { JevAsker } from '../jev.js';
export declare function pruneCodexOutput(output: Buffer, command: string, options: {
    cwd: string;
    sessionId?: string;
    apiKey?: string;
    home?: string;
    asker?: JevAsker;
    signal?: AbortSignal;
}): Promise<Buffer>;
//# sourceMappingURL=prune.d.ts.map