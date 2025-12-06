  $ cat << EOF > doc.tex.cd
  > % {{{
  > % import common
  > % }}}
  > msg = {{common.msg}}
  > EOF
  $ cat << EOF > common.py
  > msg = "HI"
  $ ls
  common.py
  doc.tex.cd
  $ compudoc doc.tex.cd --quiet
  $ ls
  common.py
  doc.tex
  doc.tex.cd
  $ cat doc.tex
  % {{{
  % import common
  % }}}
  msg = HI
