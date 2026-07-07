"""
generate_report.py
==================
Run from the src/ directory (or repo root).
Imports test_compare, runs all metrics, reads SVG/PNG assets,
and writes a self-contained light-themed HTML report to docs/index.html.
"""

import base64
import json
import os
import sys
import datetime

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT  = os.path.dirname(SCRIPT_DIR)

sys.path.insert(0, SCRIPT_DIR)
import test_compare  # noqa: E402

SHAPES = [
    "letter_H", "letter_K", "arrow-turn-down-left",
    "arrow-pointer", "number_3", "number_6", "ampersand",
]

INPUT_DIR   = os.path.join(REPO_ROOT, "input")
OUT_SVG_DIR = os.path.join(REPO_ROOT, "docs", "converted-results")
REF_SVG_DIR = os.path.join(REPO_ROOT, "challenge_reference")
DOCS_DIR    = os.path.join(REPO_ROOT, "docs")


# ---------------------------------------------------------------------------
# Asset helpers
# ---------------------------------------------------------------------------

def _read_svg(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if content.lstrip().startswith("<?xml"):
            content = content[content.index("?>") + 2:].lstrip()
        return content
    except FileNotFoundError:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" fill="#ccc" font-size="12">Not found</text></svg>'


def _png_data_uri(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        return f"data:image/png;base64,{data}"
    except FileNotFoundError:
        return ""


# ---------------------------------------------------------------------------
# HTML building blocks
# ---------------------------------------------------------------------------

LABEL_COLORS = {
    "Excellent": ("#166534", "#dcfce7", "#16a34a"),
    "Good":      ("#1e40af", "#dbeafe", "#3b82f6"),
    "Average":   ("#854d0e", "#fef9c3", "#ca8a04"),
    "Poor":      ("#991b1b", "#fee2e2", "#ef4444"),
}


def _badge(label):
    text_col, bg_col, border_col = LABEL_COLORS.get(label, ("#374151", "#f3f4f6", "#9ca3af"))
    return (
        f'<span class="badge" style="color:{text_col};background:{bg_col};'
        f'border:1px solid {border_col}">{label}</span>'
    )


def _metric_row(shape, r, is_avg=False):
    if "error" in r:
        return f'<tr class="error-row"><td>{shape}</td><td colspan="9">&#9888; {r["error"]}</td></tr>'
    label    = r.get("label", "?")
    recon_ok = r.get("recon_out", 0) >= r.get("recon_ref", 0) - 0.02
    flag     = "&#10003;" if recon_ok else "&#9888;"
    flag_cls = "flag-ok" if recon_ok else "flag-warn"
    row_cls  = "avg-row" if is_avg else ("" if recon_ok else "warn-row")
    name_cls = "shape-name" + (" avg-label" if is_avg else "")
    return (
        f'<tr class="{row_cls}">'
        f'<td class="{name_cls}">{shape}</td>'
        f'<td class="num">{r.get("ref_paths","?")}</td>'
        f'<td class="num">{r.get("out_paths","?")}</td>'
        f'<td class="num">{r.get("iou","?")}</td>'
        f'<td class="num">{r.get("dice","?")}</td>'
        f'<td class="num">{r.get("endpoint_match","?")}</td>'
        f'<td class="num">{r.get("recon_out","?")}</td>'
        f'<td class="num">{r.get("recon_ref","?")}</td>'
        f'<td>{_badge(label)}</td>'
        f'<td class="{flag_cls}">{flag}</td>'
        f'</tr>'
    )


def _shape_card(shape, r):
    png_uri = _png_data_uri(os.path.join(INPUT_DIR, f"{shape}.png"))
    out_svg = _read_svg(os.path.join(OUT_SVG_DIR, f"{shape}.svg"))
    ref_svg = _read_svg(os.path.join(REF_SVG_DIR, f"{shape}.svg"))
    label   = r.get("label", "?")
    recon   = r.get("recon_out", "?")
    iou     = r.get("iou", "?")
    img_tag = f'<img src="{png_uri}" alt="{shape}">' if png_uri else '<span class="missing">Not found</span>'
    return f"""
    <div class="shape-card">
      <div class="card-header">
        <span class="card-title">{shape}</span>
        {_badge(label)}
        <span class="card-meta">RecIoU <strong>{recon}</strong>&nbsp;&nbsp;|&nbsp;&nbsp;IoU <strong>{iou}</strong></span>
      </div>
      <div class="viewers">
        <div class="viewer-col">
          <div class="viewer-label">Input PNG</div>
          <div class="viewer-frame png-frame">{img_tag}</div>
        </div>
        <div class="viewer-col">
          <div class="viewer-label">Our SVG Output</div>
          <div class="viewer-frame svg-frame our-svg">{out_svg}</div>
        </div>
        <div class="viewer-col">
          <div class="viewer-label">Reference SVG</div>
          <div class="viewer-frame svg-frame ref-svg">{ref_svg}</div>
        </div>
      </div>
    </div>"""


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_report():
    print("[generate_report] Running test metrics...")
    results = test_compare.run_all_tests()

    valid = [r for r in results.values() if "error" not in r]
    n = len(valid)
    avg = {}
    if n:
        avg = {
            "iou":            round(sum(r["iou"]            for r in valid) / n, 4),
            "dice":           round(sum(r["dice"]           for r in valid) / n, 4),
            "endpoint_match": round(sum(r["endpoint_match"] for r in valid) / n, 4),
            "recon_out":      round(sum(r["recon_out"]      for r in valid) / n, 4),
            "recon_ref":      round(sum(r["recon_ref"]      for r in valid) / n, 4),
            "label": test_compare.classify_result(
                         sum(r["iou"]       for r in valid) / n,
                         sum(r["dice"]      for r in valid) / n,
                         sum(r["recon_out"] for r in valid) / n),
        }

    table_rows = "\n".join(
        _metric_row(s, results.get(s, {"error": "missing"})) for s in SHAPES
    )
    avg_row  = _metric_row("AVERAGE", avg, is_avg=True) if avg else ""
    cards    = "\n".join(_shape_card(s, results.get(s, {})) for s in SHAPES)
    ts       = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sha      = os.environ.get("GITHUB_SHA", "local")[:7]
    overall  = avg.get("label", "?") if avg else "?"

    css = """
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
      --bg:#f8fafc;--surface:#fff;--surface-2:#f1f5f9;
      --border:#e2e8f0;--border-2:#cbd5e1;
      --text:#0f172a;--text-2:#475569;--text-3:#94a3b8;
      --accent:#4f46e5;--accent-light:#eef2ff;
      --radius:12px;--radius-sm:6px;
      --shadow:0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04);
      --shadow-md:0 4px 16px rgba(0,0,0,.08),0 2px 4px rgba(0,0,0,.04);
      --mono:'JetBrains Mono',ui-monospace,monospace;
    }
    body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
    .site-header{background:var(--surface);border-bottom:1px solid var(--border);padding:0 24px}
    .header-inner{max-width:1200px;margin:0 auto;padding:28px 0 24px}
    .header-eyebrow{font-size:.75rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
    h1{font-size:clamp(1.75rem,3vw,2.5rem);font-weight:700;letter-spacing:-.03em;line-height:1.15}
    .header-meta{margin-top:10px;font-size:.85rem;color:var(--text-2);display:flex;flex-wrap:wrap;gap:12px;align-items:center}
    .chip{display:inline-flex;align-items:center;gap:5px;background:var(--surface-2);border:1px solid var(--border);border-radius:99px;padding:3px 10px;font-size:.78rem;font-family:var(--mono);color:var(--text-2)}
    .main{max-width:1200px;margin:0 auto;padding:40px 24px 80px}
    .section-title{font-size:1.05rem;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:10px}
    .section-title::after{content:'';flex:1;height:1px;background:var(--border)}
    .table-wrap{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);overflow:auto;margin-bottom:48px}
    table{width:100%;border-collapse:collapse;font-size:.875rem}
    thead th{background:var(--surface-2);color:var(--text-2);font-size:.72rem;font-weight:600;letter-spacing:.07em;text-transform:uppercase;padding:10px 14px;text-align:left;white-space:nowrap;border-bottom:1px solid var(--border)}
    thead th.num{text-align:right}
    tbody tr{border-bottom:1px solid var(--border);transition:background .12s}
    tbody tr:last-child{border-bottom:none}
    tbody tr:hover{background:var(--surface-2)}
    td{padding:10px 14px}
    td.num{text-align:right;font-family:var(--mono);font-size:.82rem}
    td.shape-name{font-weight:600;font-family:var(--mono);font-size:.82rem;color:var(--accent)}
    .avg-row{background:var(--accent-light)!important;font-weight:600}
    .avg-row td,.avg-label{color:var(--accent)!important}
    .error-row td{color:#dc2626;font-style:italic}
    .flag-ok{color:#16a34a;font-weight:700;text-align:center}
    .flag-warn{color:#ca8a04;font-weight:700;text-align:center}
    .badge{display:inline-block;border-radius:99px;padding:2px 9px;font-size:.72rem;font-weight:600;letter-spacing:.03em;white-space:nowrap}
    .cards-grid{display:flex;flex-direction:column;gap:28px}
    .shape-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow-md);overflow:hidden;animation:fadeUp .4s ease both}
    @keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
    .shape-card:nth-child(1){animation-delay:.05s}.shape-card:nth-child(2){animation-delay:.10s}
    .shape-card:nth-child(3){animation-delay:.15s}.shape-card:nth-child(4){animation-delay:.20s}
    .shape-card:nth-child(5){animation-delay:.25s}.shape-card:nth-child(6){animation-delay:.30s}
    .shape-card:nth-child(7){animation-delay:.35s}
    .card-header{padding:13px 18px;border-bottom:1px solid var(--border);background:var(--surface-2);display:flex;align-items:center;gap:10px;flex-wrap:wrap}
    .card-title{font-family:var(--mono);font-size:.88rem;font-weight:600}
    .card-meta{margin-left:auto;font-size:.78rem;color:var(--text-2)}
    .card-meta strong{color:var(--text)}
    .viewers{display:grid;grid-template-columns:repeat(3,1fr)}
    .viewer-col{padding:14px;border-right:1px solid var(--border)}
    .viewer-col:last-child{border-right:none}
    .viewer-label{font-size:.7rem;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:var(--text-3);margin-bottom:8px}
    .viewer-frame{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius-sm);display:flex;align-items:center;justify-content:center;min-height:170px;padding:10px;overflow:hidden}
    .png-frame img{max-width:100%;max-height:170px;object-fit:contain}
    .svg-frame{background:#fff}
    .svg-frame svg{max-width:100%;max-height:190px;width:100%;height:auto}
    .missing{color:var(--text-3);font-size:.8rem}
    .site-footer{text-align:center;padding:22px;font-size:.78rem;color:var(--text-3);border-top:1px solid var(--border);background:var(--surface)}
    .site-footer a{color:var(--accent)}
    @media(max-width:700px){
      .viewers{grid-template-columns:1fr}
      .viewer-col{border-right:none;border-bottom:1px solid var(--border)}
      .viewer-col:last-child{border-bottom:none}
    }
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>PNG to SVG Centerline Results</title>
  <meta name="description" content="Automated results dashboard for PNG to SVG centerline extraction pipeline."/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <style>{css}</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <div class="header-eyebrow">Automated Results Dashboard</div>
    <h1>PNG &#x2192; SVG Centerline Extraction</h1>
    <div class="header-meta">
      <span class="chip">&#x23F1; {ts}</span>
      <span class="chip">&#x1F516; {sha}</span>
      <span class="chip">&#x1F4D0; {len(SHAPES)} shapes</span>
      <span class="chip">&#x2B50; Overall: {overall}</span>
    </div>
  </div>
</header>
<main class="main">
  <h2 class="section-title">&#x1F4CA; Evaluation Metrics</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Shape</th>
          <th class="num">Ref Paths</th>
          <th class="num">Out Paths</th>
          <th class="num">IoU</th>
          <th class="num">Dice</th>
          <th class="num">EndPt</th>
          <th class="num">RecOut</th>
          <th class="num">RecRef</th>
          <th>Label</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {table_rows}
        {avg_row}
      </tbody>
    </table>
  </div>
  <h2 class="section-title">&#x1F5BC; Shape Gallery</h2>
  <div class="cards-grid">
    {cards}
  </div>
</main>
<footer class="site-footer">
  Generated by <strong>generate_report.py</strong> &nbsp;&middot;&nbsp;
  Pure Python standard library &nbsp;&middot;&nbsp;
  <a href="https://github.com/dungnguyen73/upgraded-guacamole-SVG-converter">GitHub</a>
</footer>
</body>
</html>
"""

    os.makedirs(DOCS_DIR, exist_ok=True)
    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[generate_report] Report written -> {out_path}")
    return out_path


if __name__ == "__main__":
    build_report()
