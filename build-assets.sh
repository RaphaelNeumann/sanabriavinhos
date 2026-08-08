#!/bin/zsh
# Baixa os ativos reais do site atual e gera um CSS com data-URIs.
# Fotos editoriais (pessoas/lugar/processo) -> qualidade baixa, viram P&B via filtro.
# Fotos de garrafa/rotulo -> qualidade alta, mantem cor (a tese do design).
set -e
BASE="https://static.wixstatic.com/media/79ca78_"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
OUT="/Users/rneumann/projects/sanabriavinhos/assets"
TMP="$OUT/final"
mkdir -p "$TMP"

# nome|id|w|h|q|ext
imgs=(
  "logo|85b9c7abdc934ca2a0a8721d94db8e20~mv2.png/v1/crop/x_96,y_192,w_2198,h_825/fill/w_760,h_285|760|285|90|png"
  "hero|d43bceedf3d34cb1af3ed6626e8da4ca~mv2.jpg|860|1180|62|jpg"
  "sign|b49f3b80829e490492a56d5d7941a87c~mv2.jpg|900|900|60|jpg"
  "toast|d51a2c456afa43e39d6b601d6fa5fa5e~mv2.jpeg|1360|780|58|jpg"
  "facade|58d3b72ba8994f5693d6906e072b46c2~mv2.jpeg|760|760|58|jpg"
  "tray|c0b871f55fab4195958b84544632848a~mv2.jpeg|760|760|58|jpg"
  "vineyard|517d9ff513074c7aae225fa6f1d9ec0f~mv2.jpg|1360|700|58|jpg"
  "family|7350a16f820c4c1f898c8d911b00df35~mv2.jpeg|620|760|60|jpg"
  "lab|4fb1084a27f541acb1d8b4d336432328~mv2.jpeg|620|620|58|jpg"
  "flask|53077928872f4784b45531c270374099~mv2.jpeg|620|620|58|jpg"
  "press|263045ae0618411aa9ee2ac334bd0928~mv2.jpg|620|620|58|jpg"
  "harvest|37bd458654f94453a3b11d1cc11656bc~mv2.jpeg|620|620|58|jpg"
  "cave|00e09948014d42d7a996ee7fb2d3ab60~mv2.jpeg|900|560|58|jpg"
  "b1|3d6c449e25634a6da4e5479831b48826~mv2.jpeg|560|730|74|jpg"
  "b2|8a46d1064a914509b122000fdf2e9bf0~mv2.png|560|730|80|png"
  "b3|7fe41bce25384c8e8128a9ee37713f0d~mv2.jpg|560|730|74|jpg"
  "b4|4a31d457b8bd4757b677676bbd65ed08~mv2.jpg|560|730|74|jpg"
  "b5|4809488a0758475bad7254f78014f045~mv2.jpg|560|730|74|jpg"
  "b6|a9c314c59dfc4c86b09174d890fad8b9~mv2.jpg|560|730|74|jpg"
  "art|88d4edc65eb34543b129282cefc317db~mv2.jpg|1100|730|72|jpg"
  "box|ec43a65876224d3aa08fc7bf93698680~mv2.jpeg|900|700|72|jpg"
  "seal|eb5df182fcd642ce8c01f486007b2695~mv2.jpg|620|620|74|jpg"
)

for row in $imgs; do
  name="${row%%|*}"; rest="${row#*|}"
  id="${rest%%|*}"; rest="${rest#*|}"
  w="${rest%%|*}"; rest="${rest#*|}"
  h="${rest%%|*}"; rest="${rest#*|}"
  q="${rest%%|*}"; ext="${rest##*|}"
  if [[ "$id" == *"/v1/"* ]]; then
    url="${BASE}${id},al_c,q_${q},enc_auto/i.${ext}"
  else
    url="${BASE}${id}/v1/fill/w_${w},h_${h},al_c,q_${q},enc_auto/i.${ext}"
  fi
  curl -sL -A "$UA" "$url" -o "$TMP/$name.$ext" &
done
wait

total=0
for f in "$TMP"/*.(jpg|png); do
  sz=$(stat -f%z "$f"); total=$((total+sz))
  printf '%-10s %-4s %8d bytes\n' "${f:t:r}" "${f:e}" "$sz"
done
echo "-----"
echo "total: $((total/1024)) KB em $TMP"
echo "agora rode: python3 build.py"
