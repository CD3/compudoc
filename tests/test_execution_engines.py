import asyncio

import pytest

from compudoc.execution_engines import *


def test_initializing_engine():

    async def run():
        assert True
        assert True
        temp = "x = {{x}}"
        process = Python()
        await process.start()
        await process.exec("import pint")
        await process.exec("import jinja2")
        await process.exec("x = 2")
        await process.exec("y = [2,3]")
        await process.exec(f"template = jinja2.Template('{temp}')")
        await process.exec(
            f"""def my_square(x):
                                 return x**2"""
        )
        print("===", await process.flush_stdout())
        print("===!", await process.flush_stderr())

        result = await process.eval("x")
        assert result == "2"
        result = await process.eval("my_square(x)")
        assert result == "4"
        result = await process.eval("y")
        assert result == "[2, 3]"
        result = await process.eval("template.render(**globals())")
        assert result == "'x = 2'"

        result = await process.eval(
            """
                                    template.render(**globals())
                                    """
        )
        assert result == "'x = 2'"

        await process.stop()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


def test_execution_engine_method_implementation_errors():
    class MyExecutionEngine(ExecutionEngine):
        pass

    execution_engine = MyExecutionEngine()

    with pytest.raises(RuntimeError):
        asyncio.run(execution_engine.start())
    with pytest.raises(RuntimeError):
        asyncio.run(execution_engine.stop())
    with pytest.raises(RuntimeError):
        asyncio.run(execution_engine.send(""))
    with pytest.raises(RuntimeError):
        asyncio.run(execution_engine.exec(""))
    with pytest.raises(RuntimeError):
        asyncio.run(execution_engine.eval(""))
    with pytest.raises(RuntimeError):
        asyncio.run(execution_engine.getline())
    with pytest.raises(RuntimeError):
        asyncio.run(execution_engine.getline_stderr())
    with pytest.raises(RuntimeError):
        asyncio.run(execution_engine.flush_stdout())
    with pytest.raises(RuntimeError):
        asyncio.run(execution_engine.flush_stderr())
