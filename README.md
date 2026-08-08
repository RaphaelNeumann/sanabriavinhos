# Sanabria — proposta de redesign

Mock de apresentação para o redesign de [sanabriavinhos.com](https://www.sanabriavinhos.com/).

**🍷 Mock da home:** https://raphaelneumann.github.io/sanabriavinhos/
**📐 Proposta:** https://raphaelneumann.github.io/sanabriavinhos/proposta.html

> **Aviso.** Este repositório é uma **peça de apresentação de design**, não o site oficial
> da Sanabria e não um site de e-commerce em funcionamento. O logotipo, as fotografias e
> os textos pertencem à Sanabria Vinhos e são usados aqui apenas para demonstrar a direção
> proposta. Nada nesta página vende nada.

---

## A direção

> **Tudo em preto e branco. Só o vinho tem cor.**

O site atual mistura quatro linguagens fotográficas incompatíveis (retrato de luz dura,
vinhedo diurno, packshots cada um num fundo diferente, buteco noturno) sem nenhum
tratamento em comum. Converter toda a fotografia editorial para monocromático unifica as
quatro **sem refotografar nada** — e libera espaço para o ativo mais forte e mais
desperdiçado da marca: os rótulos, que são pinturas originais encomendadas uma a uma.

A regra do sistema cabe em uma linha: **a cor só existe onde há rótulo.** Pessoas, lugar e
processo em P&B; garrafas e artes de rótulo em cor plena. Na home isso vira o único gesto
animado da página — a estante entra monocromática e ganha cor conforme aparece na tela.

A segunda âncora é a palavra *Laboratório* no próprio nome da marca. A estrutura da página
é a de um caderno de laboratório: réguas de 1px, número de série por seção e ficha técnica
em monoespaçada.

**Referência estrutural:** [vinicolaserradosol.com.br](https://vinicolaserradosol.com.br/) —
adaptada à identidade da Sanabria.

## Tokens

| | |
|---|---|
| Papel | `#E9E6DE` |
| Tinta | `#15130F` |
| Grafite | `#5F5A50` |
| Régua | `#C7C2B6` |
| Segunda tinta | `#8A2F1D` (o vinho da marca, usado como carimbo) |
| Display | Times, peso 400, `line-height .88`, `letter-spacing −.03em` |
| Dados | monoespaçada, caixa alta, `letter-spacing .175em` |
| Corpo | Helvetica, 16px / 1.65 |

Nenhuma webfont: sem risco de fallback silencioso e sem custo de carregamento.

## Estrutura

```
src/                 fontes editáveis (fragmentos HTML com <style> embutido)
  mock.html            home proposta
  proposta.html        documento da proposta
assets/
  final/               imagens já redimensionadas
  favicon.png  og.png
build-assets.sh      baixa e redimensiona os ativos do site atual
build.py             gera docs/ e dist/
docs/                site estático publicado no GitHub Pages
dist/                versão de arquivo único, com imagens em data-URI  (ignorado no git)
```

Cada página existe em dois formatos a partir do mesmo fonte: o site estático, com imagens
como arquivos de verdade, e um arquivo único com tudo embutido em data-URI — necessário
onde uma CSP bloqueia hosts externos.

## Build

```bash
./build-assets.sh    # opcional: rebaixa os ativos do site atual
python3 build.py     # gera docs/ e dist/
```

Para ver localmente:

```bash
python3 -m http.server 8000 --directory docs
```

## Verificado

- Sem overflow horizontal a 390px, 700px e 2560px
- Temas claro e escuro completos, incluindo o estado "sistema" (sem `data-theme`)
- `prefers-reduced-motion` desliga toda a animação e já entrega os rótulos coloridos
- `alt` / `aria-label` em toda imagem de conteúdo; foco de teclado visível
