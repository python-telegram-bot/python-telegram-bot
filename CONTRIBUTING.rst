How To Contribute
=================

Every open source project lives from the generous help by contributors that sacrifice their time and ``python-telegram-bot`` is no different. To make participation as pleasant as possible, this project adheres to the `Code of Conduct`_ by the Python Software Foundation.

Setting things up
-----------------

1. Fork the ``python-telegram-bot`` repository to your GitHub account.

2. Clone your forked repository of ``python-telegram-bot`` to your computer:

   ``$ git clone https://github.com/<your username>/python-telegram-bot``

   ``$ cd python-telegram-bot``

3. Add a track to the original repository:

   ``$ git remote add upstream https://github.com/python-telegram-bot/python-telegram-bot``

4. Install dependencies:

   ``$ pip install -r requirements.txt -r requirements-dev.txt``


5. Install pre-commit hooks:

   ``$ pre-commit install``

Finding something to do
-----------------------

If you already know what you'd like to work on, you can skip this section.

If you have an idea for something to do, first check if it's already been filed on the `issue tracker`_. If so, add a comment to the issue saying you'd like to work on it, and we'll help you get started! Otherwise, please file a new issue and assign yourself to it.

Another great way to start contributing is by writing tests. Tests are really important because they help prevent developers from accidentally breaking existing code, allowing them to build cool things faster. If you're interested in helping out, let the development team know by posting to the `developers' mailing list`_, and we'll help you get started.

Instructions for making a code change
-------------------------------------

The central development branch is ``master``, which should be clean and ready for release at any time. In general, all changes should be done as feature branches based off of ``master``.

Here's how to make a one-off code change.

1. **Choose a descriptive branch name.** It should be lowercase, hyphen-separated, and a noun describing the change (so, ``fuzzy-rules``, but not ``implement-fuzzy-rules``). Also, it shouldn't start with ``hotfix`` or ``release``.

2. **Create a new branch with this name, starting from** ``master``. In other words, run:

   ``$ git fetch upstream``

   ``$ git checkout master``

   ``$ git merge upstream/master``

   ``$ git checkout -b your-branch-name``

3. **Make a commit to your feature branch**. Each commit should be self-contained and have a descriptive commit message that helps other developers understand why the changes were made.

   - You can refer to relevant issues in the commit message by writing, e.g., "#105".

   - Your code should adhere to the `PEP 8 Style Guide`_, with the exception that we have a maximum line length of 99.

   - For consistency, please conform to `Google Python Style Guide`_ and `Google Python Style Docstrings`_. In addition, code should be formatted consistently with other code around it.

   - The following exceptions to the above (Google's) style guides applies:

        - Documenting types of global variables and complex types of class members can be done using the Sphinx docstring convention.

   - Please ensure that the code you write is well-tested.

   - Don’t break backward compatibility.

   - Add yourself to the AUTHORS.rst_ file in an alphabetical fashion.

   - Before making a commit ensure that all automated tests still pass:

      ``$ make test``

   - To actually make the commit (this will trigger test for yapf, lint and pep8 automatically):

      ``$ git add your-file-changed.py``

        - yapf may change code formatting, make sure to re-add them to your commit.

      ``$ git commit -a -m "your-commit-message-here"``

   - Finally, push it to your GitHub fork, run:

      ``$ git push origin your-branch-name``

4. **When your feature is ready to merge, create a pull request.**

   - Go to your fork on GitHub, select your branch from the dropdown menu, and click "New pull request".

   - Add a descriptive comment explaining the purpose of the branch (e.g. "Add the new API feature to create inline bot queries."). This will tell the reviewer what the purpose of the branch is.

   - Click "Create pull request". An admin will assign a reviewer to your commit.

5. **Address review comments until all reviewers give LGTM ('looks good to me').**

   - When your reviewer has reviewed the code, you'll get an email. You'll need to respond in two ways:

       - Make a new commit addressing the comments you agree with, and push it to the same branch. Ideally, the commit message would explain what the commit does (e.g. "Fix lint error"), but if there are lots of disparate review comments, it's fine to refer to the original commit message and add something like "(address review comments)".

       - In addition, please reply to each comment. Each reply should be either "Done" or a response explaining why the corresponding suggestion wasn't implemented. All comments must be resolved before LGTM can be given.

   - Resolve any merge conflicts that arise. To resolve conflicts between 'your-branch-name' (in your fork) and 'master' (in the ``python-telegram-bot`` repository), run:

      ``$ git checkout your-branch-name``

      ``$ git fetch upstream``

      ``$ git merge upstream/master``

      ``$ ...[fix the conflicts]...``

      ``$ ...[make sure the tests pass before committing]...``

      ``$ git commit -a``

      ``$ git push origin your-branch-name``

   - At the end, the reviewer will merge the pull request.

6. **Tidy up!** Delete the feature branch from both your local clone and the GitHub repository:

   ``$ git branch -D your-branch-name``

   ``$ git push origin --delete your-branch-name``

7. **Celebrate.** Congratulations, you have contributed to ``python-telegram-bot``!

.. _`Code of Conduct`: https://www.python.org/psf/codeofconduct/
.. _`issue tracker`: https://github.com/python-telegram-bot/python-telegram-bot/issues
.. _`developers' mailing list`: mailto:devs@python-telegram-bot.org
.. _`PEP 8 Style Guide`: https://www.python.org/dev/peps/pep-0008/
.. _`Google Python Style Guide`: https://google-styleguide.googlecode.com/svn/trunk/pyguide.html
.. _`Google Python Style Docstrings`: http://sphinx-doc.org/latest/ext/example_google.html
.. _AUTHORS.rst: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/AUTHORS.rst
