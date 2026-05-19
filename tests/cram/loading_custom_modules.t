  $ cat << EOF > doc.tex.cd
  > % {{{
  > % import common
  > % }}}
  > msg = {{common.msg}}
  > EOF
  $ cat << EOF > common.py
  > msg = "HI"
  > EOF
  $ ls
  common.py
  doc.tex.cd
  $ compudoc doc.tex.cd --quiet
  $ ls
  __pycache__
  common.py
  doc.tex
  doc.tex.cd
  $ cat doc.tex
  % {{{
  % import common
  % }}}
  msg = HI
