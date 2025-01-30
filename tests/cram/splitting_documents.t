  $ cat << EOF > doc.tex.cd
  > text 1
  > text 2
  > % {{{
  > % msg = "HI"
  > % }}}
  > msg = {{msg}}
  > EOF
  $ ls
  doc.tex.cd
  $ compudoc split --quiet doc.tex.cd
  $ ls | sort
  doc.tex.cd
  doc.tex.cd.code
  doc.tex.cd.text
  $ cat doc.tex.cd.code | grep 'msg = "HI"'
  msg = "HI"
  $ cat doc.tex.cd.code | grep 'text 1'
  [1]
  $ cat doc.tex.cd.text
  text 1
  text 2
  COMMENTED-CODE-BLOCK-0
  msg = {{msg}}
