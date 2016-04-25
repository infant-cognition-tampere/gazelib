# -*- coding: utf-8 -*-
import gazelib
from os import path
from gazelib.conversion import utils


def convert(gazedata_file_path, experiment_config_file_path, trial_config_id):
    '''
    Parameters
        gazedata_file_path
        experiment_config_file_path
        trial_config_id
            'mid' or 'shift'

    Return
        CommonV1 object
    '''

    # Known values
    participant_number = 'Akseli'
    was_calibrated = True

    # Read the files
    gdfp = gazedata_file_path  # short alias
    ecfp = experiment_config_file_path
    gd = gazelib.io.load_csv_as_dictlist(gdfp)
    ec = gazelib.io.load_json(ecfp)

    # Convert configuration to object
    expconf = utils.ExperimentConfiguration(ec)
    trialconf = expconf.get_trial_configuration(trial_config_id)

    # Return with a gazelib-common-v1 Object.
    c = gazelib.containers.CommonV1()

    # Build environment constants
    participant_number = str(participant_number)
    c.add_environment('gazelib/gaze/head_id', participant_number)

    trial_config_id = str(trial_config_id)
    c.add_environment('icl/gaze/trial_configuration_id', trial_config_id)

    source_files = [gazedata_file_path, experiment_config_file_path]
    source_files = list(map(path.basename, source_files))
    c.add_environment('gazelib/general/source_files', source_files)

    assert isinstance(was_calibrated, bool)
    c.add_environment('icl/gaze/tracker_successfully_calibrated',
                      was_calibrated)

    c.add_environment('gazelib/gaze/eyetracker/manufacturer', 'Tobii')
    c.add_environment('gazelib/gaze/eyetracker/model', 'TX300')

    c.add_environment('gazelib/gaze/tracked_display_size', {
        "physical_mm": {
            "width": 510.0,
            "height": 288.0
        },
        "resolution_px": {
            "width": 1024,
            "height": 768
        }
    })

    # Build timeline

    def get_microseconds(tet_time):
        '''Takes in time in microseconds'''
        # tet_time might be string, hence int()
        return int(tet_time)

    global_time = get_microseconds(gd[0]['TETTime'])
    # Reference point in microseconds
    global_time_micros = global_time

    def convert_to_relative(tet_time):
        '''Convert to relative times, ints in microseconds'''
        return int(tet_time) - global_time_micros

    def get_relative_time(gazepoint):
        '''Convert gazepoint's TETTime to CommonV1 compliant relative time'''
        return convert_to_relative(gazepoint['TETTime'])

    timeline = list(map(get_relative_time, gd))

    c.set_time_reference(global_time)
    c.add_timeline('eyetracker', timeline)

    # Build streams

    def tobii_validity_to_confidency(validity):
        '''Take in integer validity, return float confidence'''
        validity = int(validity)
        if validity == 0:
            return 1.0
        if validity == 1:
            return 0.8
        if validity == 2:
            return 0.5
        if validity == 3:
            return 0.1
        if validity == 4:
            return 0.0
        raise Exception('Invalid Tobii validity: ' + str(validity))

    left_confidency = []
    right_confidency = []

    left_eye_x_relative_stream = []
    left_eye_y_relative_stream = []
    left_eye_pupil_mm_stream = []
    right_eye_x_relative_stream = []
    right_eye_y_relative_stream = []
    right_eye_pupil_mm_stream = []

    def convert_x(x):
        '''X's already in relative units but may be strings'''
        x = float(x)
        if x == -1.0:
            return None
        return x

    def convert_y(y):
        '''Y's already in relative units but may be strings'''
        y = float(y)
        if y == -1.0:
            return None
        return y

    def convert_pupil(pupil_diam):
        d = float(pupil_diam)
        if d == -1.0:
            return None
        return d

    for gazepoint in gd:
        l_validity = gazepoint['ValidityLeftEye']
        r_validity = gazepoint['ValidityRightEye']
        l_confidency = tobii_validity_to_confidency(l_validity)
        r_confidency = tobii_validity_to_confidency(r_validity)
        left_confidency.append(l_confidency)
        right_confidency.append(r_confidency)

        left_eye_x_relative = convert_x(gazepoint['XGazePosLeftEye'])
        left_eye_y_relative = convert_y(gazepoint['YGazePosLeftEye'])
        left_eye_pupil_mm = convert_pupil(gazepoint['LeftEyePupilDiameter'])
        right_eye_x_relative = convert_x(gazepoint['XGazePosRightEye'])
        right_eye_y_relative = convert_y(gazepoint['YGazePosRightEye'])
        right_eye_pupil_mm = convert_pupil(gazepoint['RightEyePupilDiameter'])

        left_eye_x_relative_stream.append(left_eye_x_relative)
        left_eye_y_relative_stream.append(left_eye_y_relative)
        left_eye_pupil_mm_stream.append(left_eye_pupil_mm)
        right_eye_x_relative_stream.append(right_eye_x_relative)
        right_eye_y_relative_stream.append(right_eye_y_relative)
        right_eye_pupil_mm_stream.append(right_eye_pupil_mm)

    c.add_stream('gazelib/gaze/left_eye_x_relative',
                 'eyetracker', left_eye_x_relative_stream)
    c.add_stream('gazelib/gaze/left_eye_y_relative',
                 'eyetracker', left_eye_y_relative_stream)
    c.add_stream('gazelib/gaze/left_eye_pupil_mm',
                 'eyetracker', left_eye_pupil_mm_stream)
    c.add_stream('gazelib/gaze/right_eye_x_relative',
                 'eyetracker', right_eye_x_relative_stream)
    c.add_stream('gazelib/gaze/right_eye_y_relative',
                 'eyetracker', right_eye_y_relative_stream)
    c.add_stream('gazelib/gaze/right_eye_pupil_mm',
                 'eyetracker', right_eye_pupil_mm_stream)

    # Build events

    #######
    # ICL experiment period tags
    #######
    def value_converter(r):
        tag = r['tag']
        # Skip nones
        if tag == '':
            raise ValueError()
        if tag == 'Wait':
            return 'icl/experiment/reaction/period/wait'
        if tag == 'Target' or tag == 'midbox':
            return 'icl/experiment/reaction/period/target'
        raise utils.ConversionException('Unexpected tag value: ' + str(tag))

    def time_converter(r):
        return get_relative_time(r)

    tag_ranges = utils.split_to_ranges_at_change_in_value(gd,
                                                          value_converter,
                                                          time_converter)
    for tag in tag_ranges:
        c.add_event([tag['value']], tag['start'], tag['end'])

    #########
    # Trials
    ##########
    def value_converter(r):
        if r['trialnumber'] == '':
            raise ValueError()
        return int(r['trialnumber'])

    def time_converter(r):
        return get_relative_time(r)

    ranges = utils.split_to_ranges_at_change_in_value(gd,
                                                      value_converter,
                                                      time_converter)
    for r in ranges:
        extra = {
            'icl/experiment/reaction/trial/sequence_number': r['value']
        }
        c.add_event(['icl/experiment/reaction/trial'],
                    r['start'], r['end'], extra=extra)

    ##################
    # Image stimuli i.e. UserDefined_1 & Aoi
    ##################
    def value_converter(r):
        # Split when at least one of the two changes
        if r['stim'] == '' or r['aoi'] == '':
            raise ValueError()
        return r['stim'] + '-' + r['aoi']

    ranges = utils.split_to_ranges_at_change_in_value(gd, value_converter,
                                                      time_converter)
    for r in ranges:
        original_row = r['first']
        image_index = int(original_row['stim'])
        aoi_index = int(original_row['aoi'])
        extra = {
            'original_area_of_interest_index': aoi_index,
            'original_image_index': image_index,
            'icl/stimulus/image/filename':
                trialconf.get_image_name(image_index),
            'icl/stimulus/image/rectangle':
                trialconf.get_aoi_rectangle(aoi_index)
        }
        c.add_event(['icl/stimulus', 'icl/stimulus/image'],
                    r['start'], r['end'], extra=extra)

    return c
