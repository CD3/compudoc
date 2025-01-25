# {{{
# import pint
# import math
# ureg = pint.UnitRegistry()
# Q_ = ureg.Quantity
# l = Q_(532,'nm')
# k = 2*math.pi/l
# }}}

k = 0.01181049869770599

set xrange[0:3*532]

set xlabel "wavenumber [1/nm]"
set ylabel "electric field [N/C]"
unset key

plot sin(k*x)
