#!/usr/bin/env python3
"""
Gera as duas saídas a partir de src/:

  dist/  — arquivo único com as imagens embutidas como data-URI.
           É o formato exigido pelos Artifacts (a CSP bloqueia hosts externos).

  docs/  — site estático para GitHub Pages: imagens como arquivos de verdade,
           documento HTML completo com <head>, e HTML ~60x menor.

Uso: python3 build.py
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
FINAL = ROOT / "assets" / "final"
DIST = ROOT / "dist"
SITE = ROOT / "docs"   # GitHub Pages só aceita "/" ou "/docs" como origem

PLACEHOLDER = "/*__ASSETS__*/"

# og:image precisa de URL absoluta — a maioria dos scrapers ignora caminho relativo
BASE = "https://raphaelneumann.github.io/sanabriavinhos/"

# no formato Artifact as páginas se referenciam pelas URLs publicadas
ARTIFACT_MOCK = "https://claude.ai/code/artifact/670a4853-7382-4cab-ba32-b1b3de072b0d"
ARTIFACT_PROPOSTA = "https://claude.ai/code/artifact/df94392e-f15f-46f9-965a-eca6888ad49a"

PAGES = [
    {
        "src": "mock.html",
        "dist": "mock-sanabria.html",
        "out": "index.html",
        "assets": None,                       # todas
        "desc": "Mock da nova home da Sanabria — Laboratório de Vinhos Naturais. "
                "Tudo em preto e branco; só os rótulos têm cor.",
    },
    {
        "src": "proposta.html",
        "dist": "proposta-sanabria.html",
        "out": "proposta.html",
        "assets": ["logo"],                   # a proposta só usa o logotipo
        "desc": "Proposta de redesign para sanabriavinhos.com: diagnóstico do site "
                "atual, sistema de design e instruções priorizadas.",
    },
]

DOC = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="img/favicon.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
</head>
<body>
{body}
</body>
</html>
"""


def read_assets():
    """Lê assets/final e devolve {nome: (mime, bytes, extensão)}."""
    if not FINAL.is_dir():
        sys.exit("!! assets/final não existe — rode ./build-assets.sh primeiro")
    out = {}
    for f in sorted(FINAL.iterdir()):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        mime = "image/png" if f.suffix.lower() == ".png" else "image/jpeg"
        out[f.stem] = (mime, f.read_bytes(), f.suffix.lower())
    return out


def css_inline(assets, only):
    import base64
    rows = []
    for name, (mime, data, _) in assets.items():
        if only and name not in only:
            continue
        b64 = base64.b64encode(data).decode()
        rows.append(f'  --img-{name}:url("data:{mime};base64,{b64}");')
    return ":root{\n" + "\n".join(rows) + "\n}"


def css_files(assets, only, prefix="img/"):
    rows = []
    for name, (_, _, ext) in assets.items():
        if only and name not in only:
            continue
        rows.append(f'  --img-{name}:url("{prefix}{name}{ext}");')
    return ":root{\n" + "\n".join(rows) + "\n}"


def split_title(fragment):
    """Os fontes começam com <title>…</title>; no site ele precisa ir no <head>."""
    m = re.match(r"\s*<title>(.*?)</title>\s*", fragment, re.S)
    if not m:
        sys.exit("!! fragmento sem <title>")
    return m.group(1).strip(), fragment[m.end():]


def main():
    assets = read_assets()
    DIST.mkdir(exist_ok=True)
    (SITE / "img").mkdir(parents=True, exist_ok=True)

    # imagens como arquivos, para o site estático
    for name, (_, data, ext) in assets.items():
        (SITE / "img" / f"{name}{ext}").write_bytes(data)
    # favicon e og:image ficam fora de assets/final de propósito: não devem
    # entrar nos data-URIs do artifact
    for extra in ("favicon.png", "og.png"):
        f = FINAL.parent / extra
        if f.exists():
            shutil.copy(f, SITE / "img" / extra)
    (SITE / ".nojekyll").write_text("")

    for page in PAGES:
        fragment = (SRC / page["src"]).read_text()
        if PLACEHOLDER not in fragment:
            sys.exit(f"!! {page['src']}: placeholder ausente")

        # --- artifact: arquivo único ---
        one = fragment.replace(PLACEHOLDER, css_inline(assets, page["assets"]))
        one = one.replace("__PROPOSTA__", ARTIFACT_PROPOSTA)
        (DIST / page["dist"]).write_text(one)

        # --- site estático ---
        title, body = split_title(fragment)
        body = body.replace(PLACEHOLDER, css_files(assets, page["assets"]))
        # entre páginas do site, os links são relativos
        body = body.replace("__PROPOSTA__", "proposta.html")
        body = body.replace(ARTIFACT_MOCK, "./")
        doc = DOC.format(title=title, desc=page["desc"], og=BASE + "img/og.png", body=body)
        (SITE / page["out"]).write_text(doc)

        print(f"{'dist/' + page['dist']:34} {len(one)/1024/1024:6.2f} MB")
        print(f"{'docs/' + page['out']:34} {len(doc)/1024:6.1f} KB")

    total = sum(len(d) for _, d, _ in assets.values())
    print(f"{'docs/img/ (' + str(len(assets)) + ' imagens)':34} {total/1024:6.1f} KB")


if __name__ == "__main__":
    main()
