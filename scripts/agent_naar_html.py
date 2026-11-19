"""Zet een agentbestand (.claude/agents/*.md) om naar een leesbare HTML-pagina.

Gebruik:
    python scripts/agent_naar_html.py .claude/agents/orm-modelleur.md docs/agents/orm-modelleur.html

Elk hoofdstuk (## kop) wordt in- en uitklapbaar. Paragrafen (### kop) blijven gewoon staan.
Draai het script opnieuw als het agentbestand verandert.
"""

from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent

CSS = """
@font-face { font-family: "Source Sans 3"; font-weight: 200 900; font-display: swap;
  src: url("{fonts}/source-sans-3-latin-wght-normal.woff2") format("woff2"); }
:root { --bg:#f7f8fa; --vlak:#ffffff; --tekst:#1c2430; --zacht:#5a6575; --lijn:#dde2e8;
  --primair:#1f3a5f; --accent:#1a8f86; --link:#1a6f9a; --code:#eef2f6; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg:#11161d; --vlak:#18202a; --tekst:#e3e8ee; --zacht:#9aa6b4; --lijn:#2a3542;
  --primair:#8cb3dd; --accent:#7fc8c0; --link:#8cc4e6; --code:#212b37; color-scheme: dark; } }
:root[data-theme="dark"] { --bg:#11161d; --vlak:#18202a; --tekst:#e3e8ee; --zacht:#9aa6b4; --lijn:#2a3542;
  --primair:#8cb3dd; --accent:#7fc8c0; --link:#8cc4e6; --code:#212b37; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--tekst);
  font: 16px/1.6 "Source Sans 3", "Segoe UI", system-ui, sans-serif; }
main { max-width: 980px; margin: 0 auto; padding: 32px 16px 64px; }
header { display:flex; gap:16px; align-items:center; margin-bottom: 8px; }
header img { width:56px; height:56px; flex:none; }
h1 { margin:0; font-size: 2rem; color: var(--primair); letter-spacing:-0.01em; }
.omschrijving { color: var(--zacht); margin: 4px 0 16px; }
.kenmerken { display:flex; flex-wrap:wrap; gap:8px; margin-bottom: 24px; }
.kenmerken span { background: var(--vlak); border:1px solid var(--lijn); border-radius: 999px;
  padding: 2px 12px; font-size: .875rem; color: var(--zacht); }
.kenmerken b { color: var(--tekst); font-weight:600; }
.knoppen { display:flex; gap:8px; margin: 24px 0 12px; }
button { font: inherit; font-size:.875rem; background: var(--vlak); color: var(--tekst);
  border:1px solid var(--lijn); border-radius:8px; padding: 4px 12px; cursor:pointer; }
button:hover { border-color: var(--accent); }
details { background: var(--vlak); border:1px solid var(--lijn); border-radius: 12px; margin: 12px 0; }
summary { cursor:pointer; list-style:none; padding: 14px 20px; font-size: 1.35rem; font-weight: 700;
  color: var(--primair); display:flex; align-items:center; gap:12px; }
summary::-webkit-details-marker { display:none; }
summary::before { content:""; width:8px; height:8px; flex:none; border-right:2px solid var(--accent);
  border-bottom:2px solid var(--accent); transform: rotate(-45deg); transition: transform .15s; }
details[open] > summary::before { transform: rotate(45deg); }
summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 12px; }
.inhoud { padding: 0 20px 16px; border-top: 1px solid var(--lijn); }
h3 { font-size: 1.1rem; color: var(--primair); margin: 24px 0 8px; }
a { color: var(--link); }
code { background: var(--code); border-radius: 4px; padding: 1px 5px; font-size: .9em;
  font-family: Consolas, "Cascadia Mono", monospace; }
pre { background: var(--code); border-radius: 8px; padding: 12px 16px; overflow-x:auto; line-height:1.45; }
pre code { background: none; padding: 0; }
.tabel { overflow-x:auto; }
table { border-collapse: collapse; width: 100%; font-size: .95rem; }
th, td { text-align:left; vertical-align: top; padding: 8px 10px; border-bottom:1px solid var(--lijn); }
th { color: var(--zacht); font-weight:600; white-space: nowrap; }
td:first-child { color: var(--accent); font-weight:700; white-space: nowrap; }
ul { padding-left: 1.2em; }
li { margin: 4px 0; }
li > strong:first-child { color: var(--accent); }
footer { margin-top: 32px; color: var(--zacht); font-size: .875rem; }
"""

JS = """
document.getElementById('open').onclick = () => document.querySelectorAll('details').forEach(d => d.open = true);
document.getElementById('dicht').onclick = () => document.querySelectorAll('details').forEach(d => d.open = false);
"""


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    bron, doel = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    tekst = bron.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", tekst, re.S)
    meta = yaml.safe_load(m.group(1)) if m else {}
    lijf = tekst[m.end():] if m else tekst

    delen = re.split(r"^## (.+)$", lijf, flags=re.M)
    md = lambda s: markdown.markdown(s, extensions=["tables", "fenced_code"])
    tabel = lambda h: h.replace("<table>", '<div class="tabel"><table>').replace("</table>", "</table></div>")

    intro = tabel(md(delen[0]))
    hoofdstukken = []
    for kop, inhoud in zip(delen[1::2], delen[2::2]):
        hoofdstukken.append(
            f'<details>\n<summary>{html.escape(kop.strip())}</summary>\n'
            f'<div class="inhoud">\n{tabel(md(inhoud))}\n</div>\n</details>'
        )

    assets = os.path.relpath(ROOT / "docs" / "assets", doel.parent).replace(os.sep, "/")
    naam = meta.get("name", bron.stem)
    titel = naam.replace("-", " ").capitalize()
    kenmerken = "".join(
        f"<span>{k} <b>{html.escape(str(v))}</b></span>"
        for k, v in (("model", meta.get("model")), ("tools", meta.get("tools"))) if v
    )
    pagina = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titel)}</title>
<meta name="description" content="{html.escape(meta.get('description', ''))}">
<link rel="icon" type="image/svg+xml" href="{assets}/orm-modelleur.svg">
<style>{CSS.replace('{fonts}', assets + '/fonts')}</style>
</head>
<body>
<main>
<header>
<img src="{assets}/orm-modelleur.svg" alt="">
<h1>{html.escape(titel)}</h1>
</header>
<p class="omschrijving">{html.escape(meta.get('description', ''))}</p>
<div class="kenmerken">{kenmerken}</div>
{intro}
<div class="knoppen"><button id="open" type="button">Alles uitklappen</button><button id="dicht" type="button">Alles inklappen</button></div>
{chr(10).join(hoofdstukken)}
<footer>Gemaakt uit <code>{bron.relative_to(ROOT).as_posix()}</code> met <code>scripts/agent_naar_html.py</code>. Pas het agentbestand aan, niet deze pagina.</footer>
</main>
<script>{JS}</script>
</body>
</html>
"""
    doel.parent.mkdir(parents=True, exist_ok=True)
    doel.write_text(pagina, encoding="utf-8", newline="\n")
    print(f"{doel.relative_to(ROOT).as_posix()}: {len(hoofdstukken)} hoofdstukken")
    return 0


if __name__ == "__main__":
    sys.exit(main())
