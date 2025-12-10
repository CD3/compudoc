  $ cat << EOF > doc.unknown.cd
  > text 1
  > text 2
  > // {{{
  > // msg = "HI"
  > // }}}
  > msg = {{msg}}
  > EOF
  $ ls
  doc.unknown.cd
  $ compudoc --quiet doc.unknown.cd --comment-line-str //
  $ ls | sort
  doc.unknown
  doc.unknown.cd
  $ cat doc.unknown
  text 1
  text 2
  // {{{
  // msg = "HI"
  // }}}
  msg = HI
  $ rm doc.unknown
  $ compudoc --quiet doc.unknown.cd --comment-line-pattern //{{CODE}}
  $ cat doc.unknown
  text 1
  text 2
  // {{{
  // msg = "HI"
  // }}}
  msg = HI
  $ rm doc.unknown
  $ compudoc --quiet doc.unknown.cd --filetype typst
  $ cat doc.unknown
  text 1
  text 2
  // {{{
  // msg = "HI"
  // }}}
  msg = HI
