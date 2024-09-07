---
title: Example
---

# Math

[comment]: # {{{
[comment]: # x = 10
[comment]: # y = 4
[comment]: # z = x / y
[comment]: # }}}

If we have $x = {{x}}$ and $y = {{y}}$, then
$x/y = {{z}}$.


[comment]: # {{{
[comment]: # titles = ["One", "Two", "Three"]
[comment]: # }}}

{% for title in titles %}

# Generating slides in a loop: {{title}}

text...

{% endfor %}

# Including files

[comment]: # {{{
[comment]: # import pathlib
[comment]: # code = pathlib.Path("code.cpp").read_text()
[comment]: # }}}
Some source code
```cpp
{{code}}
```
