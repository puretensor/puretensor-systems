#!/usr/bin/env python3
"""Build models/Ripple-65B-Preview-1x-RTX-PRO-6000/index.html from the LocalMaxxing run records.

usage: build_ripple.py RUNS.json FRESH.txt
  RUNS.json  the speedTests list from /api/speed-tests?hfId=ricursiveAI/Ripple-65B-Preview-NVFP4
  FRESH.txt  one paragraph (HTML) on the fresh-clone reproduction
"""
import json, sys
from pathlib import Path

RUNS = json.load(open(sys.argv[1]))
RUNS = RUNS.get("speedTests", RUNS) if isinstance(RUNS, dict) else RUNS
L = {r["id"]: r for r in RUNS}
FRESH = Path(sys.argv[2]).read_text().strip()
OUT = Path(__file__).resolve().parent.parent / "models/Ripple-65B-Preview-1x-RTX-PRO-6000/index.html"
REPO = "https://github.com/puretensor/Ripple-65B-Preview-1x-RTX-PRO-6000"
RUN = "https://www.localmaxxing.com/runs/"

CODE, REASON = "cmw2sfbvd0bcdoa01shm40fuh", "cmw2sfbi20bcaoa01hqj3newo"
NOSPEC_C, NOSPEC_R = "cmw2s16bu0bc7oa01jms6k4uk", "cmw2s15m70bc4oa01fzbv9hen"
FRASER, L16K = "cmw2sfc5l0bcgoa01poovjnf5", "cmw2sfcs00bcjoa01ciqggo8d"
TP2_CODE, TP2_REASON = "cmw346qh50bi6oa01ppqdfwov", "cmw346r1m0bi9oa01bafzu0wk"
TP2_CONFIRM = {"pairs": 3, "ratio": "1.589", "ci": "1.512-1.641"}  # maxxloop confirm ab-20261105T051330 (fox-n0, 2g space)
OWN = {r["id"]: r for r in RUNS if (r.get("promptSample") or "").endswith(("about regret", "1000 lines"))}
ESSAY = next(i for i, r in OWN.items() if r["promptSample"].endswith("about regret"))
SCRIPT = next(i for i, r in OWN.items() if r["promptSample"].endswith("1000 lines"))

for i in (CODE, REASON, NOSPEC_C, NOSPEC_R, TP2_CODE, TP2_REASON):
    assert L[i]["verifiedRun"], i
assert L[TP2_CODE]["hardware"]["gpuCount"] == 2 and L[TP2_REASON]["hardware"]["gpuCount"] == 2
for i in (CODE, NOSPEC_C):
    assert L[i]["promptSha256"].startswith("a737db73"), i
for i in (REASON, NOSPEC_R):
    assert L[i]["promptSha256"].startswith("9000edaa"), i


def v(i): return f'{L[i]["tokSOut"]:.1f}'
def a(i, text): return f'<a href="{RUN}{i}">{text}</a>'


def tps(i):  # tokens per step from the run's engine timings: (completion_tokens - 1) / verify steps
    steps = L[i]["engineTimingsRaw"]["specCounters"]["drafts"]
    return (L[i]["outputTokens"] - 1) / steps


LEDGER = [
    ("NVFP4 + DFlash2", "code-v1", CODE), ("NVFP4 + DFlash2", "reasoning-v1", REASON),
    ("NVFP4 + DFlash2", "our prompt: 1,000-line script", SCRIPT), ("NVFP4 + DFlash2", "our prompt: essay and poem", ESSAY),
    ("NVFP4 + DFlash2", f"{L[FRASER]['promptTokens']:,}-token prompt", FRASER),
    ("NVFP4 + DFlash2", f"{L[L16K]['promptTokens']:,}-token prompt", L16K),
    ("NVFP4, no drafter", "code-v1", NOSPEC_C), ("NVFP4, no drafter", "reasoning-v1", NOSPEC_R),
    ("Two cards, TP2", "code-v1", TP2_CODE), ("Two cards, TP2", "reasoning-v1", TP2_REASON),
]
ledger = []
for lab, case, i in LEDGER:
    x = L[i]
    badge = '<span class="ok">Verified</span>' if x["verifiedRun"] else "not canonical"
    ledger.append(f'''<div class="ledger-row"><span class="what">{lab}<small>{case}</small></span>
<a href="{RUN}{i}">{i}</a><span class="r">{x["tokSOut"]:.2f}</span><span class="r">{x["ttftMs"]:,.0f} ms</span>
<span>prompt {x["promptSha256"][:8]} · out {x["outputSha256"][:8]} · {badge}</span></div>''')

CEIL = 31.4  # one token per 57 GB pass at 1.79 TB/s
chart = [
    {"label": "No drafter", "sub": "code-v1", "ceil": CEIL, "v": L[NOSPEC_C]["tokSOut"]},
    {"label": "Essay and poem", "sub": "our prompt", "ceil": CEIL, "v": L[ESSAY]["tokSOut"]},
    {"label": "Reasoning", "sub": "reasoning-v1", "ceil": CEIL, "v": L[REASON]["tokSOut"]},
    {"label": "1,000-line script", "sub": "our prompt", "ceil": CEIL, "v": L[SCRIPT]["tokSOut"]},
    {"label": "Code", "sub": "code-v1 · ./start.sh", "ceil": CEIL, "v": L[CODE]["tokSOut"], "hot": True},
]

SAMPLE = L[CODE]["outputSample"]
TOKENS = L[CODE]["outputTokens"]
assert len(SAMPLE) < 4000, "the sample must be the whole reply"
n_verified = sum(1 for r in RUNS if r["verifiedRun"])
words = {6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve"}

sub = {
    "{{ROWS}}": "", "{{LEDGER}}": "\n".join(ledger), "{{REPO}}": REPO, "{{RUN}}": RUN,
    "{{SAMPLE}}": json.dumps(SAMPLE).replace("</", "<\\/"), "{{CHARS}}": f"{len(SAMPLE):,}",
    "{{TOKENS}}": str(TOKENS), "{{TOKENS_FMT}}": f"{TOKENS:,}",
    "{{CODE}}": v(CODE), "{{REASON}}": v(REASON), "{{NOSPEC}}": v(NOSPEC_C),
    "{{CODE_ID}}": CODE, "{{REASON_ID}}": REASON, "{{ESSAY_ID}}": ESSAY, "{{SCRIPT_ID}}": SCRIPT,
    "{{CODE_RATE}}": f'{L[CODE]["tokSOut"]:.2f}', "{{CODE_TTFT}}": f'{L[CODE]["ttftMs"]:.1f}',
    "{{NOSPEC_RATE}}": f'{L[NOSPEC_C]["tokSOut"]:.2f}', "{{NOSPEC_TTFT}}": f'{L[NOSPEC_C]["ttftMs"]:.1f}',
    "{{ESSAY}}": v(ESSAY), "{{SCRIPT}}": v(SCRIPT),
    "{{ESSAY_OUT}}": f'{L[ESSAY]["outputTokens"]:,}', "{{SCRIPT_OUT}}": f'{L[SCRIPT]["outputTokens"]:,}',
    "{{ESSAY_TPS}}": f"{tps(ESSAY):.1f}", "{{SCRIPT_TPS}}": f"{tps(SCRIPT):.1f}",
    "{{NOSPEC_LINK_C}}": a(NOSPEC_C, v(NOSPEC_C)), "{{NOSPEC_LINK_R}}": a(NOSPEC_R, v(NOSPEC_R)),
    "{{N_VERIFIED}}": str(n_verified), "{{N_RUNS_WORD}}": words.get(len(LEDGER), str(len(LEDGER))),
    "{{CHART}}": json.dumps(chart), "{{CHART_MAX}}": "160", "{{FRESH}}": FRESH,
    "{{TP2_CODE}}": v(TP2_CODE), "{{TP2_REASON}}": v(TP2_REASON), "{{TP2_CODE_ID}}": TP2_CODE, "{{TP2_REASON_ID}}": TP2_REASON,
    "{{TP2_PAIRS}}": str(TP2_CONFIRM["pairs"]), "{{TP2_RATIO}}": TP2_CONFIRM["ratio"], "{{TP2_CI}}": TP2_CONFIRM["ci"],
}
page = (Path(__file__).parent / "ripple.tpl.html").read_text()
for k, val in sub.items():
    page = page.replace(k, val)
assert "{{" not in page, page[page.index("{{"):page.index("{{") + 40]
assert "—" not in page, "em dash"
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(page)
print("wrote", OUT, len(page), "bytes")
