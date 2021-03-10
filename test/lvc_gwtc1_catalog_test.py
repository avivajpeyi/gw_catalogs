import os
import shutil
import unittest
from catalog_generators.lvc_gwtc1_parser import LvcGwtc1EventParser
from catalog_generators.utils import sort_parameters

class CatalogTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.GW150914_path = "../data/lvc_search/GW150914_GWTC-1.hdf5"

    def test_gw150914_load(self):
        gw150914 = LvcGwtc1EventParser.load_event_samples(self.GW150914_path)
        sort_parameters(gw150914.samples)


if __name__ == '__main__':
    unittest.main()
