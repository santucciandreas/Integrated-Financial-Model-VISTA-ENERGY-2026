"""
build_standalone.py
-------------------
Produces `app-standalone.html`: the stlite page with every Python file embedded
directly in the HTML, instead of fetched from the repository at runtime.

Why this exists
---------------
The networked version (`app.html`) fetches app.py and src/*.py over HTTP. If any
one of them is missing from the published site, the web server answers with its
404 page — and Python then tries to execute that HTML as source, producing a
confusing SyntaxError. Embedding the sources removes that failure mode entirely:
the only file still fetched is the Excel model.

The Python sources are carried in <script type="text/plain"> blocks rather than
JavaScript string literals, so backticks, quotes and backslashes inside the code
need no escaping.

Usage:
    python build_standalone.py            # writes app-standalone.html
    python build_standalone.py out.html
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

#: Virtual-filesystem path -> file on disk. Order is irrelevant; the entrypoint
#: is named explicitly in the mount call below.
SOURCES = {
    "app.py": ROOT / "app.py",
    "src/data_loader.py": ROOT / "src" / "data_loader.py",
    "src/theme.py": ROOT / "src" / "theme.py",
    "src/charts.py": ROOT / "src" / "charts.py",
}

STLITE_VERSION = "1.8.1"


def build(destination: Path) -> Path:
    blocks = []
    for virtual_path, disk_path in SOURCES.items():
        source = disk_path.read_text(encoding="utf-8")
        if "</script" in source:
            raise ValueError(f"{disk_path} contains '</script' and cannot be inlined safely.")
        blocks.append(
            f'    <script type="text/plain" class="py-source" data-path="{virtual_path}">\n'
            f"{source}\n"
            f"    </script>"
        )
    embedded = "\n".join(blocks)

    html = f"""<!doctype html>
<!--
  app-standalone.html — self-contained GitHub Pages build
  ======================================================
  Streamlit compiled to WebAssembly (stlite): Python runs inside the visitor's
  browser via Pyodide, with no server involved.

  Every Python source is embedded below, so nothing can 404 at runtime. The only
  file fetched from the site is the Excel model. Regenerate this page after
  editing any .py file:

      python build_standalone.py

  Publish with: Settings -> Pages -> Deploy from a branch -> main / (root)
-->
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>Vista Energy (VIST) — Equity Story Dashboard</title>
    <meta
      name="description"
      content="Interactive DCF and comparables valuation dashboard for Vista Energy, the largest independent shale oil producer in Vaca Muerta."
    />
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@stlite/browser@{STLITE_VERSION}/build/stlite.css"
    />
    <style>
      html, body {{
        margin: 0; padding: 0; height: 100%;
        background: linear-gradient(135deg, #150B26 0%, #1E1038 55%, #24124A 100%);
      }}
      #boot {{
        position: fixed; inset: 0; display: flex; flex-direction: column;
        align-items: center; justify-content: center; gap: 1rem; text-align: center;
        font-family: 'Space Grotesk', 'Segoe UI', sans-serif; color: #F3EEFA;
        background: transparent; z-index: 10; padding: 2rem;
      }}
      #boot h1 {{ font-size: 1.4rem; font-weight: 700; margin: 0; }}
      #boot p {{ font-family: 'Inter', 'Segoe UI', sans-serif; color: #9D8FB8;
                font-size: .95rem; max-width: 46ch; margin: 0; line-height: 1.55; }}
      #boot .err {{ color: #FF6B8A; font-size: .88rem; max-width: 60ch; }}
      .spinner {{
        width: 34px; height: 34px; border: 3px solid #35204F;
        border-top-color: #A96BEE; border-radius: 50%; animation: spin 900ms linear infinite;
      }}
      @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
      @media (prefers-reduced-motion: reduce) {{ .spinner {{ animation: none; }} }}
    </style>
  </head>

  <body>
    <div id="boot">
      <div class="spinner" role="status" aria-label="Loading"></div>
      <h1>Starting the dashboard…</h1>
      <p>
        Python is loading in your browser — no server involved. The first visit takes
        about a minute; after that it is cached and opens straight away.
      </p>
      <p class="err" id="boot-error"></p>
    </div>

    <div id="root"></div>

    <!-- Python sources, embedded verbatim ------------------------------- -->
{embedded}

    <script type="module">
      import {{ mount }} from "https://cdn.jsdelivr.net/npm/@stlite/browser@{STLITE_VERSION}/build/stlite.js";

      // Collect the embedded sources into stlite's virtual filesystem.
      const files = {{}};
      document.querySelectorAll("script.py-source").forEach((block) => {{
        files[block.dataset.path] = block.textContent;
      }});

      // The workbook is the only file still fetched from the site.
      files["data/vista_financial_model.xlsx"] = {{ url: "./data/vista_financial_model.xlsx" }};

      mount(
        {{
          entrypoint: "app.py",
          requirements: ["plotly==5.24.1", "openpyxl==3.1.5", "jinja2"],
          files: files,
          streamlitConfig: {{
            "theme.base": "dark",
            "theme.primaryColor": "#A96BEE",
            "theme.backgroundColor": "#150B26",
            "theme.secondaryBackgroundColor": "#241440",
            "theme.textColor": "#F3EEFA",
            "client.toolbarMode": "viewer",
          }},
        }},
        document.getElementById("root"),
      );

      // Hide the boot screen once Streamlit paints, and surface load failures
      // instead of leaving a spinner turning forever.
      const boot = document.getElementById("boot");
      const observer = new MutationObserver(() => {{
        if (document.querySelector('#root [data-testid="stAppViewContainer"]')) {{
          boot.style.display = "none";
          observer.disconnect();
        }}
      }});
      observer.observe(document.getElementById("root"), {{ childList: true, subtree: true }});

      window.addEventListener("error", (event) => {{
        document.getElementById("boot-error").textContent =
          "Something failed while loading: " + (event.message || "unknown error");
      }});
    </script>
  </body>
</html>
"""
    destination.write_text(html, encoding="utf-8")
    return destination


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "app-standalone.html"
    print(f"Wrote {build(target)}")
