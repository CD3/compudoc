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
        jinja2_env = jinja2.Environment()
        def fmt_filter(input, spec=""):
          return ("{"+f":{spec}"+"}").format(input)

        jinja2_env.filters['fmt'] = fmt_filter
        """
        )

    def get_render_code(self, text):
        """
        Return a string that contains code that can be evaluated to render
        the given text using the execution engine.
        """
        return f"jinja2_env.from_string(r'''{text}''').render(**globals())"
