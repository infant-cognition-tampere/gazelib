import unittest2 as unittest
from os.path import join, exists
from gazelib.dataset import CSVDataset
import numpy as np

basedir = 'tests/testdataset'
dataset_dirs = ['ATT_9mo_Gaze',
                'Cry_8mo_Gaze',
                'HKI_7mo_Gaze/AED',
                'HKI_7mo_Gaze/Control',
                'HKI_7mo_Gaze/SSRI',
                'Kinship_7mo_Gaze',
                'SANFR_6mo_Gaze',
                'TREC2_7mo_Gaze']
tbt_files = ['disengagement_results.csv',
             'disengagement_tbt_18_12_2015.csv',
             'disengagement_results.csv',
             'disengagement_results.csv',
             'disengagement_results.csv',
             'disengagement_results.csv',
             'SANFRdisengagement_tbt_20_10_2015.csv',
             'disengagement_results 7mo 31.10.2013.csv']


class TestDataset(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dirs = [join(basedir, d) for d in dataset_dirs]

        # Load only datasets that exist
        dir_tbts = filter(lambda x: exists(x[0]) and exists(join(x[0], x[1])), zip(dirs, tbt_files))
        cls.datasets = [CSVDataset(d, tbt) for d, tbt in dir_tbts]

    def test_dataset(self):
        for ds in self.datasets:
            print(ds.directory)
            print(ds.tbt.data.dtype)
            print(ds.list_gazedatas())
            self.assertEqual(len(ds.list_gazedatas()), 1)

    def test_iterate_trials(self):
        """ Try to iterate over trials """
        from gazelib.dataset import TrialIterator

        for ds in self.datasets:
            ti = TrialIterator(ds)

            for t in ti:
                pass

    @unittest.skip("not really a test")
    def test_common_names(self):
        list_of_names = [set(ds.tbt.names) for ds in self.datasets]
        common_names = set.intersection(*list_of_names)

        print(common_names)

        for ds in self.datasets:
            print("Unique names in %s: %s" % (ds.directory, set(ds.tbt.names) - common_names))
            print("Stimulus names :%s" % np.unique(ds.tbt.data['stimulus']))
            print("Userdefined names :%s" % np.unique(ds.tbt.data['stimulus']))

        list_of_gznames = [set(ds.get_gazedata(ds.list_gazedatas()[0]).data.dtype.names) for ds in self.datasets]
        common_gznames = set.intersection(*list_of_gznames)

        print(common_gznames)

        for gzn, datasetname in zip(list_of_gznames, dataset_dirs):
            print("Unique gazedata header names in %s: %s" % (datasetname, gzn - common_gznames))
