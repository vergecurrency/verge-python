```
____   _________________________   ________ ___________
\   \ /   /\_   _____/\______   \ /  _____/ \_   _____/
 \   Y   /  |    __)_  |       _//   \  ___  |    __)_ 
  \     /   |        \ |    |   \\    \_\  \ |        \ 2016 VERGE
   \___/   /_______  / |____|_  / \______  //_______  /
                   \/         \/         \/         \/ 
```
# A Python library for the VERGE Client
It is a set of Python libraries that allows easy access to the
VERGE peer-to-peer cryptocurrency client API.


Installation instructions
===========================

verge-python uses setuptools for the install script. There are no dependencies apart from Python itself.

::

  $ python setup.py build
  $ python setup.py install
  

Pypi / Cheeseshop
==================

It is possible to install the package through Pypi (cheeseshop), see http://pypi.python.org/pypi?:action=display&name=verge-python
::
 $ pip install verge-python
 # if not working, try
 $ pip install --pre verge-python

Connection to verge-qt
=========================

If you want to connect to verge-qt, add server=1 in your VERGE.conf
::

 rpcuser=vergerpcuser
 rpcpassword=A RANDOM GENERATED PASSWORD
 server=1

TODO
======
These things still have to be added:

- SSL support (including certificate verification) for managing remote verge daemons.

verge-python is a fork of bitcoin-python : https://github.com/laanwj/bitcoin-python


