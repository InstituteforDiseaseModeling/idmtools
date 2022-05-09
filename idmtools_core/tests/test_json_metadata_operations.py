import unittest


class JSONMetadataOperationsTest(unittest.TestCase):
    def setUp(self):
        self.expected_items = None
        self.found_items = None

    def tearDown(self):
        pass

    #
    # get
    #

    def test_get_works_for_simulations(self):
        raise NotImplementedError('')

    def test_get_works_for_experiments(self):
        raise NotImplementedError('')

    def test_get_works_for_suites(self):
        raise NotImplementedError('')

    def test_get_creates_empty_metadata_for_previously_non_existant_id(self):
        raise NotImplementedError('')

    #
    # set
    #

    def test_set_works_for_simulations(self):
        raise NotImplementedError('')

    def test_set_works_for_experiments(self):
        raise NotImplementedError('')

    def test_set_works_for_suites(self):
        raise NotImplementedError('')

    def test_set_overwrites_existing_metadata(self):
        raise NotImplementedError('')

    #
    # update
    #

    def test_update_works_for_simulations(self):
        raise NotImplementedError('')

    def test_update_works_for_experiments(self):
        raise NotImplementedError('')

    def test_update_works_for_suites(self):
        raise NotImplementedError('')

    def test_update_works_for_previously_non_existant_id(self):
        raise NotImplementedError('')

    #
    # clear
    #

    def test_clear_works_for_simulations(self):
        raise NotImplementedError('')

    def test_works_for_experiments(self):
        raise NotImplementedError('')

    def test_works_for_suites(self):
        raise NotImplementedError('')

    def test_clear_works_for_previously_non_existant_id(self):
        raise NotImplementedError('')

    # filter

    def test_filter_works_for_simulations(self):
        raise NotImplementedError('')

    def test_filter_works_for_experiments(self):
        raise NotImplementedError('')

    def test_filter_works_for_suites(self):
        raise NotImplementedError('')

    def test_filter_works_when_there_are_no_matches(self):
        raise NotImplementedError('')

    def test_filter_works_for_non_existant_ids(self):
        raise NotImplementedError('')

    def test_filter_works_when_requesting_non_existant_metadata_keys(self):
        raise NotImplementedError('')
