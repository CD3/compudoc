import asyncio
import inspect
import sys
import textwrap


class ExecutionEngine:
    async def start(self):
        raise RuntimeError(f"{inspect.stack()[0][3]}() method not implemented")

    async def stop(self):
        raise RuntimeError(f"{inspect.stack()[0][3]}() method not implemented")

    async def send(self, text):
        raise RuntimeError(f"{inspect.stack()[0][3]}() method not implemented")

    async def exec(self, code):
        raise RuntimeError(f"{inspect.stack()[0][3]}() method not implemented")

    async def eval(self, statement):
        raise RuntimeError(f"{inspect.stack()[0][3]}() method not implemented")

    async def getline(self, timeout=0.1):
        raise RuntimeError(f"{inspect.stack()[0][3]}() method not implemented")

    async def getline_stderr(self, timeout=0.1):
        raise RuntimeError(f"{inspect.stack()[0][3]}() method not implemented")

    async def flush_stdout(self):
        raise RuntimeError(f"{inspect.stack()[0][3]}() method not implemented")

    async def flush_stderr(self):
        raise RuntimeError(f"{inspect.stack()[0][3]}() method not implemented")


class Python(ExecutionEngine):
    """
    An engine for executing python code.
    """

    def __init__(self):
        self.process: asyncio.Process = None

    async def start(self):
        self.process: asyncio.Process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-i",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await self.send("import sys\n")

        return None

    async def stop(self):
        if self.process:
            await self.send("\nexit()\n")
            try:
                status_code = await asyncio.wait_for(self.process.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                self.process.terminate()
            self.process = None

    async def send(self, text):
        self.process.stdin.write(text.encode())
        await self.process.stdin.drain()

    async def exec(self, code):
        await self.send(f'exec( """{code}""" )')
        await self.send("\n")

    async def eval(self, statement):
        statement = textwrap.dedent(statement)
        await self.flush_stdout()
        await self.flush_stderr()
        await self.send(statement)
        if not statement.endswith("\n"):
            await self.send("\n")
        await self.send("print('EOL')\n")
        result = await self.flush_stdout()
        error = await self.flush_stderr()
        if result.endswith("EOL\n"):
            result = result[:-5]
        else:
            raise RuntimeError(
                rf"There was a problem retrieving result from eval of '{statement}'. Expected 'EOL\n' at end of stdout, but recieved '{result}'."
            )
        if error != "":
            raise RuntimeError(
                rf"There was an error while running eval of '{statement}'. STDERR: '{error}'."
            )
        return result

    async def getline(self, timeout=0.1):
        try:
            line = await asyncio.wait_for(
                self.process.stdout.readline(), timeout=timeout
            )
            return line.decode()
        except asyncio.TimeoutError:
            pass

        return None

    async def getline_stderr(self, timeout=0.1):

        try:
            line = await asyncio.wait_for(
                self.process.stderr.readline(), timeout=timeout
            )
            return line.decode()
        except asyncio.TimeoutError:
            pass

        return None

    async def flush_stdout(self):
        await self.send("print('FLUSH')\n")
        text = ""
        while True:
            line = await self.getline(1)
            if line is None:
                continue
            if line.endswith("FLUSH\n"):
                break
            text += line
        return text

    async def flush_stderr(self):
        await self.send("print('FLUSH',file=sys.stderr)\n")
        text = ""
        while True:
            line = await self.getline_stderr(1)
            if line is None:
                continue
            if line.endswith("FLUSH\n"):
                break
            text += line
        return text
