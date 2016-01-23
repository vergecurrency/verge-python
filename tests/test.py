# coding=utf-8
'''
Test script
*WARNING* Don't run this on a production verge server! *WARNING*
Only on the test network.
'''
import argparse
import sys
sys.path.append('../src')

import vergerpc
from vergerpc.exceptions import VERGEException, InsufficientFunds


from decimal import Decimal

parser = argparse.ArgumentParser()
parser.add_argument('--config', help="Specify configuration file")
parser.add_argument('--nolocal', help="Don't use connect_to_local",
                    action='store_true')
parser.add_argument('--noremote', help="Don't use connect_to_remote",
                    action='store_true')
args = parser.parse_args()

if __name__ == "__main__":

    if args.config:
        from vergerpc.config import read_config_file
        cfg = read_config_file(args.config)
    else:
        from vergerpc.config import read_default_config
        cfg = read_default_config(None)
    port = int(cfg.get('rpcport', '20102'))
    rpcuser = cfg.get('rpcuser', '')

    connections = []
    if not args.nolocal:
        local_conn = vergerpc.connect_to_local()  # will use read_default_config
        connections.append(local_conn)
    if not args.noremote:
        remote_conn = vergerpc.connect_to_remote(
                user=rpcuser, password=cfg['rpcpassword'], host='localhost',
                port=port, use_https=False)
        connections.append(remote_conn)

    for conn in connections:
        assert(conn.getinfo().testnet) # don't test on prodnet

        assert(type(conn.getblockcount()) is int)
        assert(type(conn.getconnectioncount()) is int)
        assert(type(conn.getdifficulty()) is Decimal)
        assert(type(conn.getgenerate()) is bool)
        conn.setgenerate(True)
        conn.setgenerate(True, 2)
        conn.setgenerate(False)
        assert(type(conn.gethashespersec()) is int)
        account = "testaccount"
        account2 = "testaccount2"
        vergeaddress = conn.getnewaddress(account)
        conn.setaccount(vergeaddress, account)
        address = conn.getaccountaddress(account)
        address2 = conn.getaccountaddress(account2)
        assert(conn.getaccount(address) == account)
        addresses = conn.getaddressesbyaccount(account)
        assert(address in addresses)
        #conn.sendtoaddress(vergeaddress, amount, comment=None, comment_to=None)
        conn.getreceivedbyaddress(vergeaddress)
        conn.getreceivedbyaccount(account)
        conn.listreceivedbyaddress()
        conn.listreceivedbyaccount()
        #conn.backupwallet(destination)
        x = conn.validateaddress(address)
        assert(x.isvalid == True)
        x = conn.validateaddress("invalid")
        assert(x.isvalid == False)
        messages = ('Hello, world!', u'かたな')
        for message in messages:
            signature = conn.signmessage(vergeaddress, message)
            assert(conn.verifymessage(vergeaddress, signature, message) is True)

        for accid in conn.listaccounts(as_dict=True).iterkeys():
          tx = conn.listtransactions(accid)
          if len(tx) > 0:
            txid = tx[0].txid
            txdata = conn.gettransaction(txid)
            assert(txdata.txid == tx[0].txid)

        assert(type(conn.listunspent()) is list)  # needs better testing

        try:
            conn.sendtoaddress(vergeaddress, 10000000)
            assert(0)  # Should raise InsufficientFunds
        except InsufficientFunds:
            pass

    info = conn.getinfo()
    print "Blocks: %i" % info.blocks
    print "Connections: %i" % info.connections
    print "Difficulty: %f" % info.difficulty

    m_info = conn.getmininginfo()
    print ("Pooled Transactions: {pooledtx}\n"
           "Testnet: {testnet}\n"
           "Hash Rate: {hashes} H/s".format(pooledtx=m_info.pooledtx,
                                            testnet=m_info.testnet,
                                            hashes=m_info.hashespersec))
