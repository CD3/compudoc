import asyncio
import textwrap

import rich

from .execution_engines import *
from .parsing import *
from .template_engines import *


def render_document(
    text,
    comment_line_str="%",
    template_engine=Jinja2(),
    execution_engine=Python(),
    strip_comment_blocks=False,
):
    async def run(text):
        process = Python()
        comment_block_parser = parsers.make_commented_code_block_parser(
            comment_line_str
        )
        separator_bar_text = "=" * 100
        await process.start()
        rich.print("RUNNING SETUP CODE")
        code = template_engine.get_setup_code()
        for line in code.split("\n"):
            rich.print(f"[yellow]CODE: {line}[/yellow]")
        await process.exec(code)
        error = await process.flush_stderr()
        for line in error.split("\n"):
            rich.print(f"[red]STDERR: {line}[/red]")
        out = await process.flush_stdout()
        for line in out.split("\n"):
            rich.print(f"[green]STDOUT: {line}[/green]")
        rich.print(separator_bar_text)

        chunks = chunk_document(
            text,
            comment_block_parser=comment_block_parser,
        )

        rendered_chunks = []
        for i, chunk in enumerate(chunks):
            if is_commented_code_block(chunk, comment_block_parser):
                code = extract_code(chunk, comment_line_str)
                rich.print("[green]RUNNING CODE BLOCK[/green]")
                for line in code.split("\n"):
                    rich.print(f"[yellow]CODE: {line}[/yellow]")

                await process.exec(code)

                error = await process.flush_stderr()
                for line in error.split("\n"):
                    rich.print(f"[red]STDERR: {line}[/red]")
                out = await process.flush_stdout()
                for line in out.split("\n"):
                    rich.print(f"[green]STDOUT: {line}[/green]")

                rich.print(separator_bar_text)

                if not strip_comment_blocks:
                    rendered_chunks.append(chunk)

            else:
                rendered_chunk = await process.eval(
                    template_engine.get_render_code(chunk)
                )
                # the rendered text comes back as a string literal. i.e. it is a string of a string
                #
                # 'this is some rendered text\nwith a new line in it'
                #
                # use exec to make it a string.
                exec(f"rendered_chunks.append( {rendered_chunk} )")

        await process.stop()
        rendered_document = "".join(rendered_chunks)

        return rendered_document

    loop = asyncio.get_event_loop()
    rendered_text = loop.run_until_complete(run(text))
    return rendered_text
