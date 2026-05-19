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
  $ compudoc merge --quiet doc.tex.cd
  $ ls | sort
  doc.tex.cd
  doc.tex.cd.code
  doc.tex.cd.merged
  doc.tex.cd.text
  $ cat doc.tex.cd.merged
  text 1
  text 2
  % {{{
  % msg = "HI"
  % }}}
  msg = {{msg}}
  $ compudoc merge --quiet doc.tex.cd --code-indent 0
  Error: doc.tex.cd.merged already exists. Give --overwrite to overwrite.
  One or more output files exists and --overwrite was not given. Exiting.
  [2]
  $ compudoc merge --quiet doc.tex.cd --code-indent 0 --overwrite
  $ ls | sort
  doc.tex.cd
  doc.tex.cd.code
  doc.tex.cd.merged
  doc.tex.cd.text
  $ cat doc.tex.cd.merged
  text 1
  text 2
  %{{{
  %msg = "HI"
  %}}}
  msg = {{msg}}
  $ compudoc merge --quiet doc.tex.cd --code-indent 2 --overwrite
  $ ls | sort
  doc.tex.cd
  doc.tex.cd.code
  doc.tex.cd.merged
  doc.tex.cd.text
  $ cat doc.tex.cd.merged
  text 1
  text 2
  %  {{{
  %  msg = "HI"
  %  }}}
  msg = {{msg}}
