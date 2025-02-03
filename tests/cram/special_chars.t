  $ cat << EOF > doc.tex.cd
  > preamble
  > % {{{
  > % msg = r"\decimal"
  > % }}}
  > msg = {{msg}}
  > EOF
  $ ls
  doc.tex.cd
  $ compudoc doc.tex.cd --quiet
  $ ls
  doc.tex
  doc.tex.cd
  $ cat doc.tex
  preamble
  % {{{
  % msg = r"\decimal"
  % }}}
  msg = \decimal
