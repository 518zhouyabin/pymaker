# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2017 reverendus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from web3 import EthereumTesterProvider
from web3 import Web3

from pymaker import Address
from pymaker.auth import DSGuard
from pymaker.util import hexstring_to_bytes


class TestDSGuard:
    def setup_method(self):
        self.web3 = Web3(EthereumTesterProvider())
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        self.our_address = Address(self.web3.eth.defaultAccount)
        self.ds_guard = DSGuard.deploy(self.web3)

    def can_call(self, src: str, dst: str, sig: str) -> bool:
        return self.ds_guard._contract.call().canCall(src, dst, hexstring_to_bytes(sig))

    def test_no_permit_by_default(self):
        # expect
        assert not self.can_call(src='0x1111111111222222222211111111112222222222',
                                 dst='0x3333333333444444444433333333334444444444',
                                 sig='0xab121fd7')

    def test_permit_any_to_any_with_any_sig(self):
        # when
        self.ds_guard.permit(DSGuard.ANY, DSGuard.ANY, DSGuard.ANY).transact()

        # then
        assert self.can_call(src='0x1111111111222222222211111111112222222222',
                             dst='0x3333333333444444444433333333334444444444',
                             sig='0xab121fd7')

    def test_permit_specific_addresses_and_sig(self):
        # when
        self.ds_guard.permit(src=Address('0x1111111111222222222211111111112222222222'),
                             dst=Address('0x3333333333444444444433333333334444444444'),
                             sig=hexstring_to_bytes('0xab121fd7')).transact()

        # then
        assert self.can_call(src='0x1111111111222222222211111111112222222222',
                             dst='0x3333333333444444444433333333334444444444',
                             sig='0xab121fd7')

        # and
        assert not self.can_call(src='0x3333333333444444444433333333334444444444',
                                 dst='0x1111111111222222222211111111112222222222',
                                 sig='0xab121fd7')  # different addresses
        assert not self.can_call(src='0x1111111111222222222211111111112222222222',
                                 dst='0x3333333333444444444433333333334444444444',
                                 sig='0xab121fd8')  # different sig