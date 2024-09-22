# Compudoc

Add the power of python to your LaTeX, Markdown, and more...

# Features

Compudoc is a project with similar goals to [pythontex](https://github.com/gpoore/pythontex), [Codebraid](https://codebraid.org/),
[pweave](https://mpastell.com/pweave/) and [pyptex](https://pypi.org/project/pyptex/). It is most similar to
pyptex, and if I had found pyptex earlier, I may not have written Compudoc.

Features include:

- Like pyptex, compudoc is a preprocessor. All Python code is executed and replaced before LaTeX, Pandoc, mdSlides, etc is ran. You could use it to render Python files if you wanted.
- As a preprocessor, compudoc can be used with all your existing tooling. Just run compudoc to produce the source file that would normally go into your pipeline.
- Unlike pyptex, compudoc is not specific to LaTeX. Any text file can be rendered. LaTeX, Markdown, ReStructuredText, etc. can be rendered with Compudoc.
- Jinja2 is used for injecting values from Python into the source document. That means you can use Jinja2 filters to make common formatting task cleaner.
- Python code is executed in a separate interactive Python instance and incrementally between chunks of document text. That means you can define a variable `x` in
  one block of Python code, use that value in a Jinja2 template in your document, change the value of `x` in a later code block, and use it again in the document.
  The value inserted into the document will be the value of `x` at the point it is inserted.
- Python code is embedded in the comments of your source document, so you can still run the unrendered source file through your toolchain.
- If the source file you are rending does not support comments (there is no standard way to put comments in Markdown), you can define your own comment line
  identifier and have Compudoc strip them during the render process. This means you can use Compudoc to render any plain text source file without the
  final tool knowing anything about it.

## How it works

compudoc processes plain text sources files by breaking the file into "chunks" of document text and python code. For example,
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

## Examples


Python code is embedded in your document's comments. Code blocks within comment blocks
are marked with a '{{{' and '}}}' line. Here is a LaTeX example.



```latex
% arara: pdflatex

% start with vim --server latex %
\documentclass[]{article}

\usepackage{siunitx}
\usepackage{physics}
\usepackage{graphicx}
\usepackage{fullpage}

\author{C.D. Clark III}
\title{On...}
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
% arara: pdflatex

% start with vim --server latex %
\documentclass[]{article}

\usepackage{siunitx}
\usepackage{physics}
\usepackage{graphicx}
\usepackage{fullpage}

\author{C.D. Clark III}
\title{On...}
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
