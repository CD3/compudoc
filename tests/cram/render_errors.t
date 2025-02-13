  $ cat << EOF > doc.tex.cd
  > text 1
  > % {{{
  > % missing
  > % }}}
  > msg = {{msg}}
  > EOF
  $ ls
  doc.tex.cd
  $ compudoc doc.tex.cd --quiet
  There was a problem rendering document.
  [2]
