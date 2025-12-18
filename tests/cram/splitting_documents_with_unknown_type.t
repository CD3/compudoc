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
  $ compudoc split --quiet doc.unknown.cd
  Could not determine filetype .* (re)
  .* (re)
  [1]
  $ compudoc split --quiet doc.unknown.cd --comment-line-pattern "//{{CODE}}"
  $ ls | sort
  doc.unknown.cd
  doc.unknown.cd.code
  doc.unknown.cd.text
  $ cat doc.unknown.cd.text
  text 1
  text 2
  COMMENTED-CODE-BLOCK-1
  msg = {{msg}}
  $ cat doc.unknown.cd.code
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
  $ compudoc merge --quiet doc.unknown.cd --comment-line-pattern "//{{CODE}}"
  $ ls | sort
  doc.unknown.cd
  doc.unknown.cd.code
  doc.unknown.cd.merged
  doc.unknown.cd.text
  $ cat doc.unknown.cd.merged
  text 1
  text 2
  // {{{
  // msg = "HI"
  // }}}
  msg = {{msg}}
