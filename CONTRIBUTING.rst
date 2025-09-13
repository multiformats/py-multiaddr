.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/multiformats/py-multiaddr/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Python version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Multiaddr could always use more documentation, whether as part of the
official Multiaddr docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/multiformats/py-multiaddr/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `multiaddr` for local development.

1. Fork the `multiaddr` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/py-multiaddr.git

3. Install your local copy into a virtual environment::

    $ python -m venv venv
    $ source venv/bin/activate  # On Windows: venv\Scripts\activate
    $ pip install -e ".[dev]"

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, run the development workflow::

    $ make pr

   This will run: clean → fix → lint → typecheck → test

   Or run individual commands::

    $ make fix      # Fix formatting & linting issues with ruff
    $ make lint     # Run pre-commit hooks on all files
    $ make typecheck # Run mypy and pyrefly type checking
    $ make test     # Run tests with pytest
    $ make coverage # Run tests with coverage report

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.10+ (Python 3.9 support was dropped).
4. All type checking must pass (mypy and pyrefly).
5. All pre-commit hooks must pass.
6. Code must be formatted with ruff.

Development Workflow
--------------------

The project follows a py-libp2p-style development workflow:

1. **Clean**: Remove build artifacts
2. **Fix**: Auto-fix formatting and linting issues
3. **Lint**: Run pre-commit hooks
4. **Typecheck**: Run mypy and pyrefly
5. **Test**: Run the test suite

Use ``make pr`` to run the complete workflow.

Release Notes
-------------

When contributing, please add a newsfragment file in the ``newsfragments/`` directory.
See ``newsfragments/README.md`` for details on the format and types.

Tips
----

To run a subset of tests::

    $ python -m pytest tests/test_multiaddr.py

To run with coverage::

    $ make coverage

To build documentation::

    $ make docs
