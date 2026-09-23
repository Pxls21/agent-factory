"""Option-order sensitivity of the local Laya System One endpoint (coordinator probe, 2026-09-23).
Our own code: stdlib only, loopback only. Asks each Choice in all 6 label orders,
(A) one request per order, (B) all 6 orders as questions of ONE request (pijev's batch shape)."""
import itertools, json, sys, time, urllib.request, urllib.error
URL = "http://127.0.0.1:47411/v1/systemone"
CASES = {
    "ticket": ({"ticket": "Since upgrading my plan yesterday, I cannot access the dashboard. The payment went "
                          "through, but the page says my subscription is inactive. Please fix this."},
               "Which team should handle this support ticket? Choose the best primary team.",
               {"billing": "Payments, charges, invoices, and refunds.",
                "technical": "Product failures, errors, and troubleshooting.",
                "account": "Login, account access, and account settings."}),
    "lane": ({"failure": "pytest: 3 failed, 412 passed. The failures are in tests/test_s0_05_egress.py; the "
                         "builder's report claims all gates green. Nobody has reproduced the failures yet."},
             "Which lane should take this next? Choose the best next lane.",
             {"code-implementer": "Fix code whose defect is already understood.",
              "adversarial-verifier": "Attack a finished change and reproduce its claims.",
              "evidence-gatherer": "Collect evidence about an unexplained failure without concluding."}),
}
def post(body):
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=110) as r:
            return r.status, json.loads(r.read()), round(time.time() - t0, 2)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300], round(time.time() - t0, 2)
def q(instr, crit, order):
    return {"type": "choice", "instructions": instr, "criteria": {k: crit[k] for k in order}}
out = {}
for name, (state, instr, crit) in CASES.items():
    labels = sorted(crit)
    orders = list(itertools.permutations(labels))
    sep = []
    for order in orders:
        code, body, secs = post({"state": state, "questions": {"q": q(instr, crit, order)}})
        sep.append({"order": order, "code": code, "secs": secs, "answer": body.get("answers", {}).get("q") if isinstance(body, dict) else body})
    code, body, secs = post({"state": state, "questions": {f"p{i}": q(instr, crit, o) for i, o in enumerate(orders)}})
    bat = {"code": code, "secs": secs, "answers": body.get("answers") if isinstance(body, dict) else body}
    out[name] = {"labels": labels, "separate": sep, "batch": bat}
json.dump(out, sys.stdout, indent=1, sort_keys=True, default=list)
