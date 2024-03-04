iamreader
=========
https://github.com/idlesign/iamreader

|release| |lic|

.. |release| image:: https://img.shields.io/pypi/v/iamreader.svg
    :target: https://pypi.python.org/pypi/iamreader

.. |lic| image:: https://img.shields.io/pypi/l/iamreader.svg
    :target: https://pypi.python.org/pypi/iamreader


**Work in progress. Stay tuned.**


Description
-----------

*Useful tools for audio book creators*

This tool may help you to automate audio books recording, editing and publishing.

It includes:

* A "remote control" for Audacity to save your time on record process;
* Audio to video batch conversion tool to facilitate preparations and publishing on video hosting;
* Audio files annotator (ID3 Tagger)


Requirements
------------

Apart from the requirements automatically installed with ``iamreader``
the following software is needed:

* Audacity 2.4+

  With ``mod-script-pipe`` support enabled in ``Preferences -> Modules``.

* Tkinter
* ffmpeg

Install on Ubuntu 22.04:

.. code-block::

    $ sudo apt install audacity python3-tk ffmpeg


Documentation
-------------

https://iamreader.readthedocs.org/
