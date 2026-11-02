#!/usr/bin/env python3
"""Build models/Nanbeige4.3-33B-1x-RTX-PRO-6000-MaxQ/index.html from the LocalMaxxing run records."""
import html, json, sys
from pathlib import Path

RUNS = json.load(open(sys.argv[1]))
L = {r["id"]: r for r in RUNS}
OUT = Path(__file__).resolve().parent.parent / "models/Nanbeige4.3-33B-1x-RTX-PRO-6000-MaxQ/index.html"
REPO = "https://github.com/puretensor/Nanbeige4.3-33B-1x-RTX-PRO-6000-MaxQ"
RUN = "https://www.localmaxxing.com/runs/"

# (label, sub, engine, code id, reasoning id, profile, best)
SETUPS = [
    ("NVFP4 + n-gram drafts", "vLLM, Triton attention", "fast", "cmvyw8r1y099eoa01xq99kr01", "cmvyw8rcg099hoa01t3x4khyy", "x1.37 [1.36-1.40]", True),
    ("NVFP4 + DFlash2", "SGLang, 6 draft tokens", "code", "cmvyw8kkx098woa01l92z4h01", "cmvyw8kv3098zoa01zkr6ua68", "x1.75 [1.73-1.76]", False),
    ("FP8 + DFlash2", "SGLang, 8 draft tokens", "fp8-dflash", "cmvyw886e098noa01ny4j4g4y", "cmvyw88r3098qoa01lr243sva", "x1.79 [1.75-1.82]", False),
    ("NVFP4 stock", "vLLM", "stock-nvfp4", "cmvyw8p990995oa017i6hxslk", "cmvyw8phv0998oa01pss77jof", "baseline", False),
    ("FP8 + n-gram drafts", "vLLM, Triton attention", "fp8", "cmvywuzhd099woa01u456jtqe", "cmvywuzro099zoa01fjtmu3gq", "x1.37 [1.36-1.39]", False),
    ("NVFP4 stock", "SGLang", None, "cmvyvhblc098doa01dw6wiu80", "cmvyvhbuc098goa01hg73ofr1", "baseline", False),
    ("FP8 stock", "SGLang", None, "cmvyvgzak0981oa0188vetq9j", "cmvyvgzxn0984oa013dizpil2", "baseline", False),
    ("FP8 stock", "vLLM", "stock-fp8", "cmvywuwjm099noa018kcrdkcc", "cmvywuwsa099qoa01jggx09vw", "baseline", False),
]
for _, _, _, c, r, _, _ in SETUPS:
    assert L[c]["verifiedRun"] and L[r]["verifiedRun"], (c, r)
    assert L[c]["promptSha256"].startswith("a737db73") and L[r]["promptSha256"].startswith("9000edaa"), (c, r)

def v(i): return f'{L[i]["tokSOut"]:.1f}'
def a(i, text): return f'<a href="{RUN}{i}">{text}</a>'

rows = []
for lab, sub, prof, c, r, gain, best in SETUPS:
    rows.append(f'''<tr{' class="best"' if best else ''}>
  <td><strong>{lab}</strong><br><span class="small">{sub}</span></td>
  <td>{f"<code>./start.sh {prof}</code>" if prof else '<span class="small">not a profile</span>'}</td>
  <td class="n">{a(c, v(c))}</td><td class="n">{a(r, v(r))}</td>
  <td class="n">{gain if gain == "baseline" else gain.split(" ")[0] + ' <span class="ci">' + gain.split(" ")[1] + '</span>'}</td>
</tr>''')

ledger = []
for lab, sub, _, c, r, _, _ in SETUPS:
    for i, case in ((c, "code-v1"), (r, "reasoning-v1")):
        x = L[i]
        ledger.append(f'''<div class="ledger-row"><span class="what">{lab}<small>{sub} · {case}</small></span>
<a href="{RUN}{i}">{i}</a><span class="r">{x["tokSOut"]:.2f}</span><span class="r">{x["ttftMs"]:.0f} ms</span>
<span>prompt {x["promptSha256"][:8]} · out {x["outputSha256"][:8]} · <span class="ok">Verified</span></span></div>''')

SAMPLE = L["cmvyw8r1y099eoa01xq99kr01"]["outputSample"]
assert L["cmvyw8r1y099eoa01xq99kr01"]["outputTokens"] == 1024 and len(SAMPLE) < 4000  # the whole reply
sample_js = json.dumps(SAMPLE).replace("</", "<\\/")

tpl = (Path(__file__).parent / "nanbeige.tpl.html").read_text()
page = (tpl.replace("{{ROWS}}", "\n".join(rows)).replace("{{LEDGER}}", "\n".join(ledger))
           .replace("{{SAMPLE}}", sample_js).replace("{{REPO}}", REPO).replace("{{CHARS}}", str(len(SAMPLE))))
assert "{{" not in page
assert "—" not in page, "em dash"
OUT.write_text(page)
print("wrote", OUT, len(page), "bytes")
