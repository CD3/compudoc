import re
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

        def add_jinja2_filter(name,function):
            jinja2_env.filters[name] = function

        def fmt_filter(input, spec=""):
          return ("{"+f":{spec}"+"}").format(input)

        add_jinja2_filter('fmt', fmt_filter)
        add_jinja2_filter('insert', lambda filename: pathlib.Path(filename).read_text()  )

        """
        )

    def get_render_code(self, text):
        """
        Return a string that contains code that can be evaluated to render
        the given text using the execution engine.
        """
        return f"jinja2_env.from_string(r'''{text}''').render(**globals())"

    def strip_text(self, text):
        """
        Remove all template markup from text.
        """
        text = re.sub("{{.*}}", "TEMPLATE-EXPRESSION", text)
        text = re.sub("{%.*%}", "TEMPLATE-STATEMENT", text)
        text = re.sub("{#.*#}", "TEMPLATE-COMMENT", text)

        return text
