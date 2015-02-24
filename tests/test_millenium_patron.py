import pkgutil
import os
from nose.tools import (
    eq_,
    set_trace,
)

from ..millenium_patron import MilleniumPatronAPI

class DummyResponse(object):
    def __init__(self, content):
        self.content = content

class DummyAPI(MilleniumPatronAPI):

    def __init__(self):
        super(DummyAPI, self).__init__()
        self.queue = []
        base_path = os.path.split(__file__)[0]
        self.resource_path = os.path.join(
            base_path, "files", "millenium_patron")

    def sample_data(self, filename):
        path = os.path.join(self.resource_path, filename)
        data = open(path).read()
        return data

    def enqueue(self, filename):
        data = self.sample_data(filename)
        self.queue.append(data)

    def request(self, *args, **kwargs):
        return DummyResponse(self.queue.pop())


class TestMilleniumPatronAPI(object):

    def setUp(self):
        self.api = DummyAPI()

    def test_dump_no_such_barcode(self):
        self.api.enqueue("dump.no such barcode.html")
        eq_(dict(ERRNUM='1', ERRMSG="Requested record not found"),
                 self.api.dump("bad barcode"))

    def test_dump_success(self):
        self.api.enqueue("dump.success.html")
        response = self.api.dump("good barcode")
        eq_('SHELDON, ALICE', response['PATRN NAME[pn]'])

        # The 'note' field has a list of values, not just one.
        eq_(2, len(response['NOTE[px]']))

    def test_pintest_no_such_barcode(self):
        self.api.enqueue("pintest.no such barcode.html")
        eq_(False, self.api.pintest("wrong barcode", "pin"))

    def test_pintest_wrong_pin(self):
        self.api.enqueue("pintest.bad.html")
        eq_(False, self.api.pintest("barcode", "wrong pin"))

    def test_pintest_correct_pin(self):
        self.api.enqueue("pintest.good.html")
        eq_(True, self.api.pintest("barcode", "correct pin"))