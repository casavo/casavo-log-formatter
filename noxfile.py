import nox


@nox.session(python=["3.9", "3.10", "3.11"])
def run_tests(session):
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    session.run("python", "-m", "unittest")
