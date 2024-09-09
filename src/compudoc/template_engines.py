import textwrap


class Jinja2:
    def __init__(self):
        pass

    def get_setup_code(self):
        """
        Return code string to setup the template engine in the execution engine.
        """
        return textwrap.dedent(
            """
        import jinja2
        import pathlib
        jinja2_env = jinja2.Environment(keep_trailing_newline=True)
        def fmt_filter(input, spec=""):
          return ("{"+f":{spec}"+"}").format(input)

        def insert_filter(filename):
          return pathlib.Path(filename).read_text()

        jinja2_env.filters['fmt'] = fmt_filter
        jinja2_env.filters['insert'] = insert_filter
        """
        )

    def get_render_code(self, text):
        """
        Return a string that contains code that can be evaluated to render
        the given text using the execution engine.
        """
        return f"jinja2_env.from_string(r'''{text}''').render(**globals())"
