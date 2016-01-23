# Copyright (c) 2010 Witchspace <witchspace81@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Exception definitions.
"""


class VERGEException(Exception):
    """
    Base class for exceptions received from VERGE server.

    - *code* -- Error code from ``verged``.
    """
    # Standard JSON-RPC 2.0 errors
    INVALID_REQUEST  = -32600,
    METHOD_NOT_FOUND = -32601,
    INVALID_PARAMS   = -32602,
    INTERNAL_ERROR   = -32603,
    PARSE_ERROR      = -32700,

    # General application defined errors
    MISC_ERROR                  = -1  # std::exception thrown in command handling
    FORBIDDEN_BY_SAFE_MODE      = -2  # Server is in safe mode, and command is not allowed in safe mode
    TYPE_ERROR                  = -3  # Unexpected type was passed as parameter
    INVALID_ADDRESS_OR_KEY      = -5  # Invalid address or key
    OUT_OF_MEMORY               = -7  # Ran out of memory during operation
    INVALID_PARAMETER           = -8  # Invalid, missing or duplicate parameter
    DATABASE_ERROR              = -20 # Database error
    DESERIALIZATION_ERROR       = -22 # Error parsing or validating structure in raw format

    # P2P client errors
    CLIENT_NOT_CONNECTED        = -9  # VERGE is not connected
    CLIENT_IN_INITIAL_DOWNLOAD  = -10 # Still downloading initial blocks

    # Wallet errors
    WALLET_ERROR                = -4  # Unspecified problem with wallet (key not found etc.)
    WALLET_INSUFFICIENT_FUNDS   = -6  # Not enough funds in wallet or account
    WALLET_INVALID_ACCOUNT_NAME = -11 # Invalid account name
    WALLET_KEYPOOL_RAN_OUT      = -12 # Keypool ran out, call keypoolrefill first
    WALLET_UNLOCK_NEEDED        = -13 # Enter the wallet passphrase with walletpassphrase first
    WALLET_PASSPHRASE_INCORRECT = -14 # The wallet passphrase entered was incorrect
    WALLET_WRONG_ENC_STATE      = -15 # Command given in wrong wallet encryption state (encrypting an encrypted wallet etc.)
    WALLET_ENCRYPTION_FAILED    = -16 # Failed to encrypt the wallet
    WALLET_ALREADY_UNLOCKED     = -17 # Wallet is already unlocked

    def __init__(self, error):
        Exception.__init__(self, error['message'])
        self.code = error['code']


class TransportException(Exception):
    """
    Class to define transport-level failures.
    """
    def __init__(self, msg, code=None, protocol=None, raw_detail=None):
        self.msg = msg
        self.code = code
        self.protocol = protocol
        self.raw_detail = raw_detail
        self.s = """
        Transport-level failure: {msg}
        Code: {code}
        Protocol: {protocol}
        """.format(msg=msg, code=code, protocol=protocol)

    def __str__(self):
        return self.s


##### General application defined errors
class SafeMode(VERGEException):
    """
    Operation denied in safe mode (run ``verged`` with ``-disablesafemode``).
    """


class JSONTypeError(VERGEException):
    """
    Unexpected type was passed as parameter
    """
InvalidAmount = JSONTypeError  # Backwards compatibility


class InvalidAddressOrKey(VERGEException):
    """
    Invalid address or key.
    """
InvalidTransactionID = InvalidAddressOrKey  # Backwards compatibility


class OutOfMemory(VERGEException):
    """
    Out of memory during operation.
    """


class InvalidParameter(VERGEException):
    """
    Invalid parameter provided to RPC call.
    """


##### Client errors
class ClientException(VERGEException):
    """
    P2P network error.
    This exception is never raised but functions as a superclass
    for other P2P client exceptions.
    """


class NotConnected(ClientException):
    """
    Not connected to any peers.
    """


class DownloadingBlocks(ClientException):
    """
    Client is still downloading blocks.
    """


##### Wallet errors
class WalletError(VERGEException):
    """
    Unspecified problem with wallet (key not found etc.)
    """
SendError = WalletError  # Backwards compatibility


class InsufficientFunds(WalletError):
    """
    Insufficient funds to complete transaction in wallet or account
    """


class InvalidAccountName(WalletError):
    """
    Invalid account name
    """


class KeypoolRanOut(WalletError):
    """
    Keypool ran out, call keypoolrefill first
    """


class WalletUnlockNeeded(WalletError):
    """
    Enter the wallet passphrase with walletpassphrase first
    """


class WalletPassphraseIncorrect(WalletError):
    """
    The wallet passphrase entered was incorrect
    """


class WalletWrongEncState(WalletError):
    """
    Command given in wrong wallet encryption state (encrypting an encrypted wallet etc.)
    """


class WalletEncryptionFailed(WalletError):
    """
    Failed to encrypt the wallet
    """


class WalletAlreadyUnlocked(WalletError):
    """
    Wallet is already unlocked
    """


# For convenience, we define more specific exception classes
# for the more common errors.
_exception_map = {
    VERGEException.FORBIDDEN_BY_SAFE_MODE: SafeMode,
    VERGEException.TYPE_ERROR: JSONTypeError,
    VERGEException.WALLET_ERROR: WalletError,
    VERGEException.INVALID_ADDRESS_OR_KEY: InvalidAddressOrKey,
    VERGEException.WALLET_INSUFFICIENT_FUNDS: InsufficientFunds,
    VERGEException.OUT_OF_MEMORY: OutOfMemory,
    VERGEException.INVALID_PARAMETER: InvalidParameter,
    VERGEException.CLIENT_NOT_CONNECTED: NotConnected,
    VERGEException.CLIENT_IN_INITIAL_DOWNLOAD: DownloadingBlocks,
    VERGEException.WALLET_INSUFFICIENT_FUNDS: InsufficientFunds,
    VERGEException.WALLET_INVALID_ACCOUNT_NAME: InvalidAccountName,
    VERGEException.WALLET_KEYPOOL_RAN_OUT: KeypoolRanOut,
    VERGEException.WALLET_UNLOCK_NEEDED: WalletUnlockNeeded,
    VERGEException.WALLET_PASSPHRASE_INCORRECT: WalletPassphraseIncorrect,
    VERGEException.WALLET_WRONG_ENC_STATE: WalletWrongEncState,
    VERGEException.WALLET_ENCRYPTION_FAILED: WalletEncryptionFailed,
    VERGEException.WALLET_ALREADY_UNLOCKED: WalletAlreadyUnlocked,
}


def wrap_exception(error):
    """
    Convert a JSON error object to a more specific VERGE exception.
    """
    # work around to temporarily fix https://github.com/bitcoin/bitcoin/issues/3007
    if error['code'] == VERGEException.WALLET_ERROR and error['message'] == u'Insufficient funds':
        error['code'] = VERGEException.WALLET_INSUFFICIENT_FUNDS
    return _exception_map.get(error['code'], VERGEException)(error)
