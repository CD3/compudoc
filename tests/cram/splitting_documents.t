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
  $ cat doc.tex.cd.text
  text 1
  text 2
  COMMENTED-CODE-BLOCK-1
  msg = {{msg}}
  $ cat doc.tex.cd.code
  #SETUP
   (glob)
  import jinja2
  import pathlib
  jinja2_env = jinja2.Environment(keep_trailing_newline=True)
  def fmt_filter(input, spec=""):
    return ("{"+f":{spec}"+"}").format(input)
   (glob)
  def insert_filter(filename):
    return pathlib.Path(filename).read_text()
   (glob)
  jinja2_env.filters['fmt'] = fmt_filter
  jinja2_env.filters['insert'] = insert_filter
  #COMMENTED-CODE-BLOCK-1
  msg = "HI"
  $ compudoc split --quiet doc.tex.cd
  [2]
  $ rm *
  $ cat << EOF > doc.md.cd
  > text 1
  > text 2
  > <!-- {{{ -->
  > <!-- msg = "HI"-->
  > <!-- }}} -->
  > msg = {{msg}}
  > EOF
  $ ls
  doc.md.cd
  $ compudoc split --quiet doc.md.cd --comment-line-pattern "<!--{{CODE}}-->"
  $ ls | sort
  doc.md.cd
  doc.md.cd.code
  doc.md.cd.text
  $ cat doc.md.cd.text
  text 1
  text 2
  COMMENTED-CODE-BLOCK-1
  msg = {{msg}}
  $ cat doc.md.cd.code
  #SETUP
   (glob)
  import jinja2
  import pathlib
  jinja2_env = jinja2.Environment(keep_trailing_newline=True)
  def fmt_filter(input, spec=""):
    return ("{"+f":{spec}"+"}").format(input)
   (glob)
  def insert_filter(filename):
    return pathlib.Path(filename).read_text()
   (glob)
  jinja2_env.filters['fmt'] = fmt_filter
  jinja2_env.filters['insert'] = insert_filter
  #COMMENTED-CODE-BLOCK-1
  msg = "HI"

