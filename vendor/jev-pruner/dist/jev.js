export const SYSTEM_ONE_URL = 'https://api.typesafe.ai/v1/systemone';
export const DEFAULT_MODEL = 'jev-latest';
/** The HTTP request for one Jev call, for any fetch-like transport. */
export function buildJevRequest(params, state, questions) {
    return {
        url: params.baseUrl ?? SYSTEM_ONE_URL,
        method: 'POST',
        headers: {
            authorization: `Bearer ${params.apiKey}`,
            'content-type': 'application/json',
        },
        body: JSON.stringify({
            model: params.model ?? DEFAULT_MODEL,
            state,
            questions,
        }),
    };
}
/** Validates a Jev response body; throws on anything but an `answers` object. */
export function parseJevResponse(status, ok, text) {
    if (!ok) {
        throw new Error(`Jev request failed (${status}): ${text.slice(0, 200)}`);
    }
    let parsed;
    try {
        parsed = JSON.parse(text);
    }
    catch {
        throw new Error('Jev returned malformed JSON');
    }
    if (parsed === null ||
        typeof parsed !== 'object' ||
        !('answers' in parsed) ||
        parsed.answers === null ||
        typeof parsed.answers !== 'object') {
        throw new Error('Jev response is missing answers');
    }
    return parsed;
}
/** The `noul` probability of one answer; throws when it is not there. */
export function noulAnswer(answers, name) {
    const answer = answers[name];
    if (!answer ||
        !('noul' in answer) ||
        typeof answer.noul !== 'number' ||
        !Number.isFinite(answer.noul)) {
        throw new Error(`Invalid Jev answer for ${name}`);
    }
    return answer.noul;
}
const TOKEN_PIECES = /[A-Za-z]+|\d+|[^\sA-Za-z\d]/g;
/**
 * Estimates tokens without a tokenizer: a word costs one token per six
 * letters, a digit half a token, any other symbol nine tenths. Calibrated
 * against the usage Jev reports for real transcripts, where it lands 2–18%
 * above the true count; a plain characters-per-token ratio undercounts the
 * JSON-heavy states by up to 40%.
 */
export function estimateTokens(text) {
    let tokens = 0;
    for (const [piece] of text.matchAll(TOKEN_PIECES)) {
        const first = piece.charCodeAt(0);
        if (first >= 48 && first <= 57)
            tokens += piece.length / 2;
        else if ((first >= 65 && first <= 90) || (first >= 97 && first <= 122)) {
            tokens += 1 + Math.floor((piece.length - 1) / 6);
        }
        else
            tokens += 0.9;
    }
    return Math.ceil(tokens);
}
export function estimateStateTokens(text) {
    return estimateTokens(text) + (text.match(/\d/g)?.length ?? 0) / 2;
}
//# sourceMappingURL=jev.js.map