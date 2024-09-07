import pathlib

import jinja2
import typer
from typing_extensions import Annotated, List

from compudoc import document

app = typer.Typer()


def detect_filetype(filename):
    filepath = pathlib.Path(filename)
    if filepath.suffix == ".tex":
        return "latex"
    if filepath.suffix == ".md":
        return "markdown"


comment_line_strs = {
    "latex": "%",
    "markdown": "[comment]: #",
}


@app.command()
def main(
    input_file: pathlib.Path,
    output_file_template: Annotated[
        str,
        typer.Option(
            help="Output filename template. The output filename will be generated by rendering this template. Use --show-output-filename-render-context to see a list of variables available in the template."
        ),
    ] = "{{input_file_stem}}-rendered.{{input_file_ext}}",
    show_output_filename_render_context: bool = False,
    config_file: Annotated[
        str, typer.Option("--config-file", help="Specify configuration file to load")
    ] = None,
    strip_comment_blocks: Annotated[
        bool, typer.Option(help="Remove comment blocks from document when rendering.")
    ] = False,
    comment_line_str: Annotated[
        str, typer.Option(help="Use TEXT to identify comment lines.")
    ] = None,
):
    """
    Compudoc lets you write python code in you documents to perform calculations and insert the results.
    It is very handy for creating technical write-ups that need to record/report the result of some numerical calculations.
    """

    ctx = {
        "input_file_stem": input_file.stem,
        "input_file_name": input_file.name,
        "input_file_ext": input_file.suffix[1:],
    }

    env = jinja2.Environment()
    output_file = pathlib.Path(env.from_string(output_file_template).render(**ctx))

    if show_output_filename_render_context:
        print("Render context variables (and thier current value)")
        for k in ctx:
            print("  ", k, ":", ctx[k])
        print("Output filename (with current template context) would be")
        print(output_file_template, "->", output_file)

        raise typer.Exit(0)

    filetype = detect_filetype(input_file)
    if filetype is None:
        print(f"Could not determine filetype for {input_file}")
        raise typer.Exit(1)

    print(f"Detected filetype: {filetype}")
    print(f"Comment string: {comment_line_strs[filetype]}")

    if filetype == "markdown":
        strip_comment_blocks = True
    if comment_line_str is None:
        comment_line_str = comment_line_strs[filetype]

    print(f"Rendering document {input_file} -> {output_file}")
    input_text = input_file.read_text()

    output_text = document.render_document(
        input_text,
        comment_line_str=comment_line_str,
        strip_comment_blocks=strip_comment_blocks,
    )

    output_file.write_text(output_text)
