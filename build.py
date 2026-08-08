#!/usr/bin/env python3
"""
Gera as duas saídas a partir de src/:

  docs/  — site estático para GitHub Pages: imagens como arquivos de verdade,
           documento HTML completo com <head>, e HTML ~60x menor.

  dist/  — arquivo único com as imagens embutidas como data-URI.
           É o formato exigido pelos Artifacts (a CSP bloqueia hosts externos).

Os fontes em src/ são fragmentos com marcadores que este script substitui:

  /*__ASSETS__*/  as imagens (data-URI ou url(img/…), conforme a saída)
  /*__BASE__*/    src/_base.css     — tokens e primitivas
  /*__CHROME__*/  src/_chrome.css   — cabeçalho e rodapé
  <!--__HEADER__-->  <!--__FOOTER__-->  <!--__SCRIPT__-->
  __HOME__        raiz do site, relativa à página

Uso: python3 build.py
"""
import base64
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
FINAL = ROOT / "assets" / "final"
DIST = ROOT / "dist"
SITE = ROOT / "docs"   # GitHub Pages só aceita "/" ou "/docs" como origem

# og:image e canonical precisam de URL absoluta — a maioria dos scrapers ignora
# caminho relativo. A conta tem domínio próprio, então não é *.github.io.
BASE = "https://rneumann.me/sanabriavinhos/"

PAGES = [
    {
        "src": "mock.html",
        "out": "index.html",
        "dist": "mock-sanabria.html",
        "nav": None,
        "assets": None,                       # todas
        # na home tudo é âncora — inclusive o clube, que só sai da página
        # quando o visitante pede mais detalhe
        "links": {"__NAV_CLUBE__": "#clube", "__ASSINAR__": "clube.html#planos"},
        "desc": "Mock da nova home da Sanabria — Laboratório de Vinhos Naturais. "
                "Tudo em preto e branco; só os rótulos têm cor.",
    },
    {
        "src": "clube.html",
        "out": "clube.html",
        "dist": "clube-sanabria.html",
        "nav": "clube",
        "assets": None,
        "links": {"__NAV_CLUBE__": "clube.html", "__ASSINAR__": "#planos"},
        "desc": "Clube Sanabria: assinatura mensal de vinhos naturais, com curadoria "
                "do enólogo e frete grátis em todos os planos.",
    },
    {
        "src": "proposta.html",
        "out": "proposta.html",
        "dist": "proposta-sanabria.html",
        "nav": None,
        "assets": ["logo"],                   # a proposta só usa o logotipo
        "links": {},                          # não usa o cabeçalho do site
        "desc": "Proposta de redesign para sanabriavinhos.com: diagnóstico do site "
                "atual, sistema de design e instruções priorizadas.",
    },
]

PARTIALS = {
    "/*__BASE__*/":       "_base.css",
    "/*__CHROME__*/":     "_chrome.css",
    "/*__AGEGATE__*/":    "_agegate.css",
    "<!--__THEME__-->":   "_theme.html",
    "<!--__AGEGATE__-->": "_agegate.html",
    "<!--__HEADER__-->": "_header.html",
    "<!--__FOOTER__-->": "_footer.html",
    "<!--__SCRIPT__-->": "_script.html",
}

DOC = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{canonical}">
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
    rows = [
        f'  --img-{n}:url("data:{mime};base64,{base64.b64encode(data).decode()}");'
        for n, (mime, data, _) in assets.items() if not only or n in only
    ]
    return ":root{\n" + "\n".join(rows) + "\n}"


def css_files(assets, only):
    rows = [
        f'  --img-{n}:url("img/{n}{ext}");'
        for n, (_, _, ext) in assets.items() if not only or n in only
    ]
    return ":root{\n" + "\n".join(rows) + "\n}"


def expand(fragment, nav):
    """Aplica as parciais e marca o item de menu da página atual."""
    for marker, name in PARTIALS.items():
        if marker in fragment:
            fragment = fragment.replace(marker, (SRC / name).read_text().rstrip())
    if nav:
        fragment = fragment.replace(
            f'data-nav="{nav}"', f'data-nav="{nav}" aria-current="page"'
        )
    return fragment


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

    # imagens viram arquivos de verdade no site estático
    live = {f"{n}{ext}" for n, (_, _, ext) in assets.items()} | {"favicon.png", "og.png"}
    for name, (_, data, ext) in assets.items():
        (SITE / "img" / f"{name}{ext}").write_bytes(data)
    # favicon e og:image ficam fora de assets/final de propósito: não devem
    # entrar nos data-URIs do artifact
    for extra in ("favicon.png", "og.png"):
        f = FINAL.parent / extra
        if f.exists():
            shutil.copy(f, SITE / "img" / extra)
    # imagens que saíram do projeto não podem ficar para trás em docs/
    for f in (SITE / "img").iterdir():
        if f.name not in live:
            f.unlink()
            print(f"removido  docs/img/{f.name}")
    (SITE / ".nojekyll").write_text("")

    for page in PAGES:
        fragment = expand((SRC / page["src"]).read_text(), page["nav"])
        for marker, target in page["links"].items():
            fragment = fragment.replace(marker, target)
        title, body_src = split_title(fragment)

        # --- artifact: arquivo único. As páginas irmãs ficam no site público,
        #     senão os links quebram fora do contexto do Artifact.
        one = body_src.replace("/*__ASSETS__*/", css_inline(assets, page["assets"]))
        one = one.replace("__HOME__", BASE)   # antes do regex: vira href absoluto
        one = re.sub(r'href="(?!https?:|#)([^"]*)"',
                     lambda m: f'href="{BASE}{m.group(1)}"', one)
        (DIST / page["dist"]).write_text(f"<title>{title}</title>\n{one}")

        # --- site estático: tudo relativo ---
        body = body_src.replace("/*__ASSETS__*/", css_files(assets, page["assets"]))
        body = body.replace("__HOME__", "" if page["out"] == "index.html" else "index.html")
        body = body.replace('href=""', 'href="./"')   # link nu para a própria home
        canonical = BASE + ("" if page["out"] == "index.html" else page["out"])
        doc = DOC.format(title=title, desc=page["desc"], og=BASE + "img/og.png",
                         canonical=canonical, body=body)
        (SITE / page["out"]).write_text(doc)

        print(f"{'docs/' + page['out']:30} {len(doc)/1024:7.1f} KB"
              f"    {'dist/' + page['dist']:24} {len(one)/1024/1024:5.2f} MB")

    total = sum(len(d) for _, d, _ in assets.values())
    print(f"{'docs/img/ (' + str(len(assets)) + ' imagens)':30} {total/1024:7.1f} KB")


if __name__ == "__main__":
    main()
