  $ compudoc example | head -n 2
  
  \documentclass[]{article}

  $ compudoc example typst | head -n 2
  
  #title[Example Document]

  $ compudoc example > main.tex.cd
  $ compudoc --quiet main.tex.cd
  $ ls
  main.tex
  main.tex.cd
  $ compudoc example typst > main.typ.cd
  $ compudoc --quiet main.typ.cd
  $ ls
  main.tex
  main.tex.cd
  main.typ
  main.typ.cd
