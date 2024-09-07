# compudoc

Add the power of python to your LaTeX and Markdown documents.

## Examples

{% raw %}
Python code is embedded in your document's comments. Code blocks within comment blocks
are marked with a '{{{' and '}}}' line. Here is a LaTeX exmaple.
{% endraw %}

// {{{
// from pathlib import Path
// listing = Path("examples/latex_with_units/main.tex").read_text()
// }}}

```latex
{{listing}}
```
Save this to a file named `main.tex` and run
```bash
$ compudoc main.tex
```
This will create a file named `main-rendered.tex` with the following content
// {{{
// from pathlib import Path
// listing = Path("examples/latex_with_units/main-rendered.tex").read_text()
// }}}

```latex
{{listing}}
```
