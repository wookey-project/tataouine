#/bin/sh!

# https://www.hairpalace.fr/wp-content/themes/hp-design/fonts/fontawesome/svgs/brands/

for f in *.svg; do echo $f && convert $f ${f%.*}.png; done

python3 extract_db.py > fido_db.py
