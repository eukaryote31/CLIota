from unittest import TestCase
from unittest import mock
from cliota.api.account import Account
from cliota.api.node_mgr import ApiFactory
from cliota.walletfile import WalletFile


class AccountTest(TestCase):
    def test_addr_gen(self):
        acc = Account(WalletFile('wf', 'pass', seed='A' * 81), object())
        acc.walletdata.save = mock.MagicMock()
        acc.cache_new_addresses(4)

        # This method only generates new addresses,
        # it doesn't populate the balance or txsin/txsout.
        expected = [
            {
                'address': 'XUERGHWTYRTFUYKFKXURKHMFEVLOIFTTCNTXOGLDPCZ9CJLKHROOPGNAQYFJEPGK9OKUQROUECBAVNXRX',
                'balance': 0,
                'txs': []
            },
            {
                'address': 'RJBYLCIOUKWJVCUKZQZCPIKNBUOGRGVXHRTTE9ZFSCGTFRKELMJBDDAKEYYCLHLJDNSHQ9RTIUIDLMUOB',
                'balance': 0,
                'txs': []
            },
            {
                'address': 'G9IBAWCWWYOSAVURTPX9JKBJLAFFBHWLOONFHTNENHJZGRLTDUDTMXTMBKYODOVHTAYKKIZBDGVAJJQJD',
                'balance': 0,
                'txs': []
            },
            {
                'address': 'LATEWUUZSHRMEVHYVGW9T9HQKRLDGHTTAEHSN9ERFCQOEBCTNTBTYZPPARUILAYCKFKERLJ9UTYPHIICY',
                'balance': 0,
                'txs': []
            }
        ]

        self.assertEqual(acc.walletdata.addresses, expected)

    def test_refresh_addr(self):
        mockapi = mock.MagicMock()
        mockapi.find_transactions = mock.MagicMock(
            return_value={'hashes': ['aaa', 'bbb', 'ccc']})
        mockapi.get_balances = mock.MagicMock(return_value={
            'balances': [123]
        })

        acc = Account(WalletFile('wf', 'pass', seed='A' * 81),
                      mockapi)
        acc.walletdata.save = mock.MagicMock()
        acc.cache_new_addresses(1)

        # refresh the value of the first address
        acc.refresh_addr(0)

        expected = [
            {
                'address': 'XUERGHWTYRTFUYKFKXURKHMFEVLOIFTTCNTXOGLDPCZ9CJLKHROOPGNAQYFJEPGK9OKUQROUECBAVNXRX',
                'balance': 123,
                'txs': ['aaa', 'bbb', 'ccc']
            }
        ]

        self.assertEqual(acc.walletdata.addresses, expected)
