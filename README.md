# compudoc

Add the power of python to your LaTeX and Markdown documents.

## Examples


Python code is embedded in your document's comments. Code blocks within comment blocks
are marked with a '{{{' and '}}}' line. Here is a LaTeX exmaple.



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
