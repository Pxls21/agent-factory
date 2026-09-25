export type InformationCategory = 'reference' | 'diagnostic' | 'result' | 'progress' | 'unknown';
export declare function isProtectedLine(text: string): boolean;
export declare function classifyInformation(text: string): InformationCategory;
export declare function keepScore(score: number, threshold: number): boolean;
//# sourceMappingURL=retention.d.ts.map