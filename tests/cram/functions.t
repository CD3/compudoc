  $ cat << EOF > doc.tex.cd
  >   text 1
  >   text 2
  >   % {{{
  >   % def compute(a,b):
  >   %   x = a*2
  >   %   y = b*3
  >   %   return x+y
  >   % a = 10
  >   % b = 5
  >   % ans = compute(a,b)
  >   % }}}
  >   answer = {{ans}}
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
    % def compute(a,b):
    %   x = a*2
    %   y = b*3
    %   return x+y
    % a = 10
    % b = 5
    % ans = compute(a,b)
    % }}}
    answer = 35
