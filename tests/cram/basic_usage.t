  $ cat << EOF > doc.tex.cd
  > text 1
  > text 2
  > % {{{
  > msg = "HI"
  > % }}}
  > msg = {{msg}}
  > EOF
  $ ls
  doc.tex.cd
  $ compudoc doc.tex.cd
  $ ls
  doc.tex.cd
