import nox

PYTHON_VERSIONS = ["3.9", "3.10", "3.11"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    session.install(".", "pytest", "clirunner")
    session.run("pytest", "tests/", "-v", *session.posargs)
