# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest  # to support Python 2.6
except ImportError:
    import unittest

from gazelib.conversion.icl import gazelibfixtures
import os

# Path to test fixtures
here_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(here_path, 'fixtures')
exp_config_path = os.path.join(fixture_path,
'gazelibfixtures_experiment-config.json')
trial_path = os.path.join(fixture_path,
'gazelibfixtures_shift_trial01.gazedata')
trials_path = os.path.join(fixture_path,
'gazelibfixtures_shift_trials00-02.gazedata')

class TestGazelibFixturesToGazelibCommon(unittest.TestCase):

    def test_convert(self):
        c = gazelibfixtures.common.convert(trial_path, exp_config_path,
                                           trial_config_id='shift')
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
            self.assertIn(req, c.get_stream_names())

    def test_correct_number_of_events(self):
        c = gazelibfixtures.common.convert(trials_path, exp_config_path,
                                           trial_config_id='shift')
        self.assertEqual(c.count_events('icl/experiment/reaction/trial'), 3)
