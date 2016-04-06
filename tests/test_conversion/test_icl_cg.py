# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from gazelib.conversion.icl import cg
import os

# Path to test fixtures
here_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(here_path, 'fixtures')
gazedata_path = os.path.join(fixture_path,
                             'cg8mo_par0_SRT2_trial01.gazedata')
gazedata_emptyrows_name = 'cg8mo_par0_SRT2_trial01.emptyrows.gazedata'
gazedata_emptyrows_path = os.path.join(fixture_path, gazedata_emptyrows_name)

exp_config_path = os.path.join(fixture_path,
                               'cg8mo_experiment-config.json')


class TestCgToGazelibCommon(unittest.TestCase):

    def test_convert(self):

        common = cg.common.convert(gazedata_path,
                                   exp_config_path,
                                   participant_number=0,
                                   trial_config_id='SRT2',
                                   was_calibrated=True)
        required_streams = [
            'gazelib/gaze/left_eye_x_relative',
            'gazelib/gaze/left_eye_y_relative',
            'gazelib/gaze/left_eye_pupil_mm',
            'gazelib/gaze/right_eye_x_relative',
            'gazelib/gaze/right_eye_y_relative',
            'gazelib/gaze/right_eye_pupil_mm'
        ]
        # Test if lists contain same elements
        for req in required_streams:
            self.assertIn(req, common.get_stream_names())

        # common.save_as_json('foo.json')

    def test_empty_rows(self):
        common = cg.common.convert(gazedata_emptyrows_path,
                                   exp_config_path,
                                   participant_number=0,
                                   trial_config_id='SRT2',
                                   was_calibrated=True)
        # Ensure no trial events were created by empty trial number
        evs = list(common.iter_events_by_tag('icl/experiment/reaction/trial'))
        
        self.assertEqual(len(evs), 1)
