  $ cat << EOF > doc.md.cd
  > text 1
  > text 2
  > <!--{{{-->
  > <!-- msg = "HI" -->
  > <!--}}}-->
  > msg = {{msg}}
  > EOF
  $ ls
  doc.md.cd
  $ compudoc doc.md.cd --quiet --comment-line-pattern "<!--{{CODE}}-->"
  $ ls | sort
  doc.md
  doc.md.cd
  $ cat doc.md.cd
  text 1
  text 2
  <!--{{{-->
  <!-- msg = "HI" -->
  <!--}}}-->
  msg = {{msg}}
  $ cat doc.md
  text 1
  text 2
  msg = HI
  $ compudoc doc.md.cd --quiet --comment-line-pattern "<!--{{CODE}}-->" --no-strip-comment-blocks
  $ cat doc.md
  text 1
  text 2
  <!--{{{-->
  <!-- msg = "HI" -->
  <!--}}}-->
  msg = HI
  $ cat << EOF > doc.md.cd
  > text 1
  > text 2
  > <!-- {{{          -->
  > <!-- msg = "HI"   -->
  > <!-- }}}          -->
  > msg = {{msg}}
  > EOF
  $ compudoc doc.md.cd --quiet --comment-line-pattern "<!--{{CODE}}-->" --no-strip-comment-blocks
  $ cat doc.md
  text 1
  text 2
  <!-- {{{          -->
  <!-- msg = "HI"   -->
  <!-- }}}          -->
  msg = HI
