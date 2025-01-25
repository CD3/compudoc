import asyncio
import textwrap

import rich

from .execution_engines import *
from .parsing import *
from .template_engines import *


class DocumentBlock:
    """
    A baseclass for code and text blocks.
    """

    def __init__(self, text: str):
        self._text: str = text

    @property
    def text(self):
        return self._text

    def is_code_block(self):
        return False

    def is_text_block(self):
        return False


class CodeBlock(DocumentBlock):
    def __init__(self, text: str):
        super().__init__(text)

    def is_code_block(self):
        return True


class TextBlock(DocumentBlock):
    def __init__(self, text: str):
        super().__init__(text)

    def is_text_block(self):
        return True


class Document:
    """
    A document is a list of text and code blocks.
    """

    def __init__(self):
        self.__blocks: list[TextBlock | CodeBlock] = []
        self.__comment_block = None
        self.__template_engine = None
        self.__execution_engine = None

    def set_comment_block(self, obj):
        self.__comment_block = obj

    @property
    def comment_block(self):
        return self.__comment_block

    def set_template_engine(self, engine):
        self.__template_engine = engine

    @property
    def template_engine(self):
        return self.__template_engine

    def set_execution_engine(self, engine):
        self.__execution_engine = engine

    @property
    def execution_engine(self):
        return self.__execution_engine

    def append(self, block: TextBlock | CodeBlock):
        self.__blocks.append(block)

    def iter_blocks(self):
        for block in self.__blocks:
            yield block
        return

    def iter_code_blocks(self):
        """
        Return iterator (as generator) of all code blocks
        """
        for block in self.__blocks:
            if block.is_code_block():
                yield block
        return

    def iter_text_blocks(self):
        """
        Return iterator (as generator) of all text blocks
        """
        for block in self.__blocks:
            if block.is_text_block():
                yield block
        return

    def enumerate_blocks(self):
        """
        Return an iterator (as generator) of two element tuples containing blocks and their index in the document.
        Index is returned in first element, just as with enumerate().
        """
        for item in enumerate(self.__blocks):
            yield item
        return

    def enumerate_code_blocks(self):
        """
        Return an iterator (as generator) of two element tuples containing code blocks and their index in the document.
        Index is returned in first element, just as with enumerate().
        """
        for item in enumerate(self.__blocks):
            if item[1].is_code_block():
                yield item
        return

    def enumerate_text_blocks(self):
        """
        Return an iterator (as generator) of two element tuples containing text blocks and their index in the document.
        Index is returned in first element, just as with enumerate().
        """
        for item in enumerate(self.__blocks):
            if item[1].is_text_block():
                yield item
        return

    def parse(self, text):
        """
        Split text into code and text blocks and add them to the document list.
        """
        if self.__comment_block is None:
            raise RuntimeError("No comment block given, cannot parse document.")
        else:
            comment_block = self.__comment_block
        i = 0
        for match in self.comment_block.get_comment_code_blocks(text):
            ibeg = match[1]
            iend = match[2]
            # need to add the text chunk before
            # this code chunk
            chunk = text[i:ibeg]
            self.append(TextBlock(chunk))

            # and this code chunk
            chunk = text[ibeg:iend]
            self.append(CodeBlock(chunk))
            i = iend
        chunk = text[i:]
        self.append(TextBlock(chunk))

    def render(
        self,
        strip_comment_blocks=False,
        quiet=False,
    ) -> str:

        if self.__template_engine is None:
            raise RuntimeError("No template engine given, cannot render document")
        else:
            template_engine = self.__template_engine

        if self.__execution_engine is None:
            raise RuntimeError("No execution engine given, cannot render document")
        else:
            execution_engine = self.__execution_engine

        if self.__comment_block is None:
            raise RuntimeError(
                "No comment code block type given, cannot render document"
            )
        else:
            comment_block = self.__comment_block

        async def run():
            process = execution_engine
            console = rich.console.Console(stderr=True, quiet=quiet)
            console.rule("[bold red]START")
            await process.start()
            console.print("RUNNING SETUP CODE")
            code = template_engine.get_setup_code()
            for line in code.split("\n"):
                console.print(f"[yellow]CODE: {line}[/yellow]")
            await process.exec(code)
            error = await process.flush_stderr()
            for line in error.split("\n"):
                console.print(f"[red]STDERR: {line}[/red]")
            out = await process.flush_stdout()
            for line in out.split("\n"):
                console.print(f"[green]STDOUT: {line}[/green]")

            rendered_chunks = []
            for i, block in self.enumerate_blocks():
                if block.is_code_block():
                    console.rule(f"[bold red]CHUNK {i}")
                    code = self.__comment_block.extract_code(block.text)
                    console.print("[green]RUNNING CODE BLOCK[/green]")
                    for line in code.split("\n"):
                        console.print(f"[yellow]CODE: {line}[/yellow]")

                    await process.exec(code)

                    error = await process.flush_stderr()
                    for line in error.split("\n"):
                        console.print(f"[red]STDERR: {line}[/red]")
                    out = await process.flush_stdout()
                    for line in out.split("\n"):
                        console.print(f"[green]STDOUT: {line}[/green]")

                    if not strip_comment_blocks:
                        rendered_chunks.append(block.text)

                else:
                    try:
                        rendered_chunk = await process.eval(
                            template_engine.get_render_code(block.text)
                        )
                        # the rendered text comes back as a string literal. i.e. it is a string of a string
                        #
                        # 'this is some rendered text\nwith a new line in it'
                        #
                        # use exec to make it a string.
                        exec(f"rendered_chunks.append( {rendered_chunk} )")
                    except Exception as e:
                        console.print(
                            f"[red]ERROR: An exception was thrown while trying to render chunk {i} of the document.[/red]"
                        )
                        console.print(f"[red]{e}[/red]")
                        console.print(f"Document chunk was")
                        console.print(f"[red]vvvvvvvv\n{block.text}\n^^^^^^^^[red]")

            console.rule("[bold red]END")

            await process.stop()
            rendered_document = "".join(rendered_chunks)

            return rendered_document

        loop = asyncio.get_event_loop()
        rendered_text = loop.run_until_complete(run())
        return rendered_text

        return "".join(rendered_blocks)


def render_document(
    text,
    comment_line_str="%",
    template_engine=Jinja2(),
    execution_engine=Python(),
    strip_comment_blocks=False,
):
    async def run(text):
        process = execution_engine
        comment_block_parser = parsers.make_commented_code_block_parser(
            comment_line_str
        )
        console = rich.console.Console(stderr=True)
        console.rule("[bold red]START")
        await process.start()
        console.print("RUNNING SETUP CODE")
        code = template_engine.get_setup_code()
        for line in code.split("\n"):
            console.print(f"[yellow]CODE: {line}[/yellow]")
        await process.exec(code)
        error = await process.flush_stderr()
        for line in error.split("\n"):
            console.print(f"[red]STDERR: {line}[/red]")
        out = await process.flush_stdout()
        for line in out.split("\n"):
            console.print(f"[green]STDOUT: {line}[/green]")

        chunks = chunk_document(
            text,
            comment_block_parser=comment_block_parser,
        )

        rendered_chunks = []
        for i, chunk in enumerate(chunks):
            if is_commented_code_block(chunk, comment_block_parser):
                console.rule(f"[bold red]CHUNK {i}")
                code = extract_code(chunk, comment_line_str)
                console.print("[green]RUNNING CODE BLOCK[/green]")
                for line in code.split("\n"):
                    console.print(f"[yellow]CODE: {line}[/yellow]")

                await process.exec(code)

                error = await process.flush_stderr()
                for line in error.split("\n"):
                    console.print(f"[red]STDERR: {line}[/red]")
                out = await process.flush_stdout()
                for line in out.split("\n"):
                    console.print(f"[green]STDOUT: {line}[/green]")

                if not strip_comment_blocks:
                    rendered_chunks.append(chunk)

            else:
                try:
                    rendered_chunk = await process.eval(
                        template_engine.get_render_code(chunk)
                    )
                    # the rendered text comes back as a string literal. i.e. it is a string of a string
                    #
                    # 'this is some rendered text\nwith a new line in it'
                    #
                    # use exec to make it a string.
                    exec(f"rendered_chunks.append( {rendered_chunk} )")
                except Exception as e:
                    console.print(
                        f"[red]ERROR: An exception was thrown while trying to render chunk {i} of the document.[/red]"
                    )
                    console.print(f"[red]{e}[/red]")
                    console.print(f"Document chunk was")
                    console.print(f"[red]vvvvvvvv\n{chunk}\n^^^^^^^^[red]")

        console.rule("[bold red]END")

        await process.stop()
        rendered_document = "".join(rendered_chunks)

        return rendered_document

    loop = asyncio.get_event_loop()
    rendered_text = loop.run_until_complete(run(text))
    return rendered_text
