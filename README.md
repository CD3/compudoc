# CompuDoc

Add the power of python to your LaTeX, Markdown, and more. Why would you want this? Because it is awesome.

# Features

Compudoc is a project with similar goals to [pythontex](https://github.com/gpoore/pythontex), [Codebraid](https://codebraid.org/),
[pweave](https://mpastell.com/pweave/) and [pyptex](https://pypi.org/project/pyptex/). It is most similar to
pyptex, and if I had found pyptex earlier, I may not have written Compudoc.

Features include:

- Like pyptex, CompuDoc is a *text preprocessor*. A source file is read in and a "rendered" version is written out.
  That means that Python code is executed and replaced *before* LaTeX, Pandoc, mdSlides, etc. is ran, so CompuDoc can be
  added unintrusively to existing projects.
- As a preprocessor, CompuDoc can be used with all your existing tooling. Just run CompuDoc to produce the source file that would normally go into your pipeline.
- Since CompuDoc works on plain text files, you can use it to add the power of Python to *any* tool that processes plain text.
- Unlike pyptex, CompuDoc is not specific to LaTeX. Any text file can be rendered. LaTeX, Markdown, ReStructuredText, etc. can be rendered with Compudoc.
- Jinja2 is used for injecting values from Python into the source document. That means you can use Jinja2 filters to make common formatting task cleaner.
- Python code is executed in a separate interactive Python instance and incrementally between chunks of document text. That means you can define a variable `x` in
  one block of Python code, use that value in a Jinja2 template in your document, change the value of `x` in a later code block, and use it again in the document.
  The value inserted into the document will be the value of `x` at the point it is inserted.
- If the source file you are rending does not support comments (there is no standard way to put comments in Markdown), you can define your own comment line
  identifier and have CompuDoc strip them during the render process. This means you can use CompuDoc to render *any* plain text source file without the
  final tool knowing anything about it.
- Add unit support to your scripts that don't have native support for units.

## How it works

CompuDoc processes plain text sources files by breaking the file into "chunks" of document text and python code. For example,
a document with the text

```
Some text
% {{{
% import os
% }}}
Some more text
% {{{
% CWD = os.getcwd()
% }}}
The current directory is {{ CWD }}.

```
would be split into 5 chunks. The first chunk is the document text 'Some text\n', the second chunk is python code and so on.

Chunks are then processed **in order**. Python code chunks are passed to a separate Python instance. Document text chunks are
rendered using a jinja2 instance running in the separate Python instance. Because chunks are processed in order, it means that
the value of a variable in a jinja2 template will be determined by the python code chunks that have been processed *before* it.

```
x is not defined yet
% {{{
% x = 2
% }}}
x is {{x}}
% {{{
% x = 4
% }}}
Now x is {{x}}
```

This document will render to
```
x is not defined yet
% {{{
% x = 2
% }}}
x is 2
% {{{
% x = 4
% }}}
Now x is 4
```


## Examples

Python code is embedded in your document's comments. Code blocks within comment blocks
are marked with a '{{{' and '}}}' line. Currently, only single-line-style comments are supported.

### LaTeX

```latex
\documentclass[]{article}

\usepackage{siunitx}
\usepackage{physics}
\usepackage{graphicx}
\usepackage{fullpage}

\author{C.D. Clark III}
\begin{document}
\maketitle

% {{{ {}
% import pint
% ureg = pint.UnitRegistry()
% Q_ = ureg.Quantity
% }}}

Laser exposures are characterized by a power ($\Phi$), energy ($Q$), radiant exposure ($H$),
or irradiance ($E$). Each of these four radiometric quantities are related to each other
through the exposure area and duration.

% {{{ {}
% power = Q_(100,'mW')ljG
% duration = Q_(0.25,'s')
% energy = (power * duration).to("mJ")
% }}}

For example, if a laser outputs a power of {{'{:Lx}'.format(power)}} for a
duration of {{duration | fmt("Lx")}}, then the energy delivered during the
exposure will be {{energy | fmt("Lx")}}.

\end{document}
```
Save this to a file named `main.tex` and run
```bash
$ compudoc main.tex
```
This will create a file named `main-rendered.tex` with the following content

```latex
\documentclass[]{article}

\usepackage{siunitx}
\usepackage{physics}
\usepackage{graphicx}
\usepackage{fullpage}

\author{C.D. Clark III}
\begin{document}
\maketitle

% {{{ {}
% import pint
% ureg = pint.UnitRegistry()
% Q_ = ureg.Quantity
% }}}

Laser exposures are characterized by a power ($\Phi$), energy ($Q$), radiant exposure ($H$),
or irradiance ($E$). Each of these four radiometric quantities are related to each other
through the exposure area and duration.

% {{{ {}
% power = Q_(100,'mW')
% duration = Q_(0.25,'s')
% energy = (power * duration).to("mJ")
% }}}

For example, if a laser outputs a power of \SI[]{100}{\milli\watt} for a
duration of \SI[]{0.25}{\second}, then the energy delivered during the
exposure will be \SI[]{25.0}{\milli\joule}.

\end{document}

```

### Gnuplot

[Gnuplot](http://www.gnuplot.info/) is amazing, it really is. But like most programming languages, there is no support for physical units. Variables
are just numbers. Wouldn't it be nice to enter all of your variables in whatever units are convienient and not have to convert them by "hand"?
With CompuDoc, you can.

```gnuplot
# {{{
# import pint
# ureg = pint.UnitRegistry()
# Q_ = ureg.Quantity()
# beam_waist_diameter = Q_(50, 'um')
# beam_waist_divergence = Q_(2,'mrad')
# }}}

# plot the beam diameter of a laser as a function of propagation range.
# 
# the range equation:
DL(r) = sqrt( D0**2 + (phi*r)**2 )

# note that D0 and r need to be expressed in the _same_ units,
# and phi needs to be expressed in _radian_.
D0 = {{beam_waist_diameter.to("cm").magnitude}} # convert to cm and get the numerical value
phi = {{beam_divergence.to("rad").magnitude}}

set xlabel "range [cm]"
set xlabel "diameter [cm]"

plot DL(r)
```
