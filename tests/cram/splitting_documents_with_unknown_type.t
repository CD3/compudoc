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
  
  def add_jinja2_filter(name,function):
      jinja2_env.filters[name] = function
  
  def fmt_filter(input, spec=""):
    return ("{"+f":{spec}"+"}").format(input)
   (glob)
  add_jinja2_filter('fmt', fmt_filter)
  add_jinja2_filter('insert', lambda filename: pathlib.Path(filename).read_text()  )
   (glob)
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
