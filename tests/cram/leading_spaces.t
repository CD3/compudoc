  $ cat << EOF > doc.tex.cd
  > text 1
  > text 2
  >   % {{{
  >   % msg = "HI"
  >   % }}}
  > msg = {{msg}}
  > EOF
  $ ls
  doc.tex.cd
  $ compudoc doc.tex.cd --quiet
  $ ls
  doc.tex
  doc.tex.cd
  $ cat doc.tex
  text 1
  text 2
    % {{{
    % msg = "HI"
    % }}}
  msg = HI
