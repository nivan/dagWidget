# dagWidget

A Custom Jupyter Widget Library

## Installation

To install use pip:

    $ pip install dagWidget

For a development installation (requires [Node.js](https://nodejs.org) and [Yarn version 1](https://classic.yarnpkg.com/)),

    $ git clone https://github.com/UFPE/dagWidget.git
    $ cd dagWidget
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --overwrite --sys-prefix dagWidget
    $ jupyter nbextension enable --py --sys-prefix dagWidget

When actively developing your extension for JupyterLab, run the command:

    $ jupyter labextension develop --overwrite dagWidget

Then you need to rebuild the JS when you make a code change:

    $ cd js
    $ yarn run build

You then need to refresh the JupyterLab page when your javascript changes.
