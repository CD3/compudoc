class Examples:
    def latex():
        return r"""
\documentclass[]{article}

\usepackage{siunitx}
\usepackage{physics}
\usepackage{graphicx}
\usepackage{fullpage}

\author{C.D. Clark III}
\title{On...}
\begin{document}
\maketitle

% setup pint for automatic unit conversions
% {{{
% import pint
% ureg = pint.UnitRegistry()
% Q_ = ureg.Quantity
% }}}

% add a jinja2 fillter to format units with siunitx
% compudoc already defines a `fmt` filter that calls a function named
% `fmt_filter`, so we can just call that wit the Lx format
% modifier
% {{{
% def Lx_filter(input,fmt=""):
%   text = fmt_filter(input,fmt+"Lx")
%   return text
% jinja2_env.filters["Lx"] = Lx_filter
% }}}

Laser exposures are characterized by a power ($\Phi$), energy ($Q$), radiant exposure ($H$),
or irradiance ($E$). Each of these four radiometric quantities are related to each other
through the exposure area and duration.

% define some quantities to use
% {{{
% power = Q_(100,'mW')
% duration = Q_(0.25,'s')
% energy = (power * duration).to("mJ")
% }}}

For example, if a laser outputs a power of {{power | Lx}} for a
duration of {{duration | Lx}}, then the energy delivered during the
exposure will be {{energy | Lx}}, or {{energy.to("J")|Lx}}.

\end{document}
"""
    def markdown():
        return r"""
---
title: Thermal Physics
header-includes:
    - \usepackage{fullpage}
    - \usepackage{siunitx}
    - \usepackage{physics}
    - \sisetup{per-mode=fraction}
    - \DeclareSIUnit \degF {\degree F}
    - \DeclareSIUnit \degC {\degree C}
    - \DeclareSIUnit \degK {K}
    - \DeclareSIUnit \mile {mi}
    - \DeclareSIUnit \inch {in}
    - \DeclareSIUnit \foot {ft}
    - \DeclareSIUnit \yard {yd}
    - \DeclareSIUnit \acre {acre}
    - \DeclareSIUnit \lightyear {ly}
    - \DeclareSIUnit \year {yr}
    - \DeclareSIUnit \parcec {pc}
    - \DeclareSIUnit \teaspoon {tsp.}
    - \DeclareSIUnit \tablespoon {tbsp.}
    - \DeclareSIUnit \gallon {gal}
    - \DeclareSIUnit \quart {qt}
    - \DeclareSIUnit \pallet {pallet}
    - \DeclareSIUnit \poundmass {lbm}
    - \DeclareSIUnit \poundforce {lbf}
    - \DeclareSIUnit \gravity {g}
    - \DeclareSIUnit \revolutionsperminute{rpm}
    - \DeclareSIUnit \mph{mph}
    - \DeclareSIUnit \fluidounce{floz}
    - \DeclareSIUnit \turn {rev}
    - \DeclareSIUnit \atmosphere {atm}
---

{% raw %}
# Problems
{% endraw %}

[comment]: # {{{
[comment]: # # setup pint for automatic unit conversions and create some useful
[comment]: # # jinja filters. compudoc already defines a `fmt` filter that calls
[comment]: # # a function named `fmt_filter` that formats variable with the given
[comment]: # # format string.
[comment]: # import pint
[comment]: # ureg = pint.UnitRegistry()
[comment]: # Q_ = ureg.Quantity
[comment]: # def Lx_filter(input,fmt=""):
[comment]: #   return fmt_filter(input,fmt+"Lx")
[comment]: # jinja2_env.filters["Lx"] = Lx_filter
[comment]: # PI = 3.14
[comment]: # }}}


1. Recall that when a fluid is placed in a gravitational field, the pressure will vary with depth according to the equation

    $$\dv{P}{z} = -\rho g$$

   If $\rho$ is a constant (does not depend on $P$), then the solution to this differential equation is just $P(z) = P_0 - \rho g z$, where $P_0$ is
   the pressure at $z = 0$. For ``incompressible fluids'', like water or mercury, this works well. But for incompressible fluids, like air, it does not.

   Use the ideal gas law to write the density of air as a function of $P$. Then plug it in and solve the differential equation above to get the
   pressure as a function of height of air, assuming that the temperature is constant. This will be an approximation of the air pressure with altitude above ground.

1. Based on your solution to the previous problem, how far above ground would the air pressure be about \SI{0.5}{\atmosphere}?

1. How far below the surface would the water pressure in a pool be about \SI{2}{\atmosphere}?

1. Estimate the average speed of a Nitrogen and Oxygen molecule in this room using the
   RMS velocity. Which one travels faster on average?

1. Compute the total thermal energy of a liter of helium gas at room temperature and
   atmospheric pressure. Then repeat the calculation for air and water vapor.

1. The ideal gas law is an approximate equation of state that works well for low density gasses.
   But it is not the only equation of state, any posed
   relationship between $P$, $V$, and $T$ is called an equation of state.
   Another famous equation of state for gasses is the van der Waals equation:
   $$
      \qty(P + \frac{an^2}{V^2})\qty(V-nb) = nRT.
   $$
[comment]: #  {{{
[comment]: #  H_a = Q_('0.2476 L^2 bar/mol^2').to('J m^3/mol^2')
[comment]: #  H_b = Q_('0.02661 L/mol').to_base_units()
[comment]: #  CO2_a = Q_('3.64 L^2 bar/mol^2').to('J m^3/mol^2')
[comment]: #  CO2_b = Q_('0.04267 L/mol').to_base_units()
[comment]: #  }}}
  This equation accounts for particle interaction (including attraction between particles and the size
  of the particles), and is therefore more
  accurate for dense fluids. Here, $a$ and $b$ are positive constants that
  depend on the type of gas; $a$ quantifies the average interaction between
  particles and $b$ is the volume of one mole of the fluid if you packed the
  particles together tightly.
  For example, for Hydrogen, $a = {{H_a|Lx(".2e")}}$ and $b = {{H_b|Lx(".2e")}}$. For Carbon Dioxide, $a = {{CO2_a|Lx(".2e")}}$ and $b = {{CO2_b|Lx(".2e")}}$.
[comment]: #  {{{
[comment]: #  Amount1 = Q_(0.001,'mol')
[comment]: #  Amount2 = Q_(10,'mol')
[comment]: #  Volume = Q_(1,'L')
[comment]: #  Temperature = Q_(20,'degC')
[comment]: #  }}}
    1. Consider a {{Volume|Lx}} container filed with Hydrogen gas helt at room temperature.
    Sketch a plot of the pressure as a function of $n$ using both the ideal gas law and
    van der Waals equation.
    1. Compare the pressure (compute a percent difference) of the Hydrogen gas predicted by the ideal gas law to the
     pressure predicted by the van der Waals equation for $n = {{Amount1|Lx}}$.
    1. Compare the pressure (compute a percent difference) of the Hydrogen gas predicted by the ideal gas law to the
     pressure predicted by the van der Waals equation for $n = {{Amount1|Lx}}$.
"""

    def gnuplot():
        return r"""
# {{{
# import pint
# import math
# ureg = pint.UnitRegistry()
# Q_ = ureg.Quantity
# l = Q_(532,'nm')
# k = 2*math.pi/l
# }}}

k = {{k.to("1/nm").magnitude}}

set xrange[0:3*{{l.to('nm').magnitude}}]

set xlabel "wavenumber [1/nm]"
set ylabel "electric field [N/C]"
unset key

plot sin(k*x)

"""


