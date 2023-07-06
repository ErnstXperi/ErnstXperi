import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.api_integration.conftest import setup_api_tester
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings
from set_top_box.client_api.Menu.conftest import disable_parental_controls
from pytest_testrail.plugin import pytestrail
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions


@pytest.mark.usefixtures("setup_api_tester")
@pytest.mark.api
class TestAPI(object):
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_create_delete_socu_and_non_socu_recording(self):
        channels = self.service_api.get_random_recordable_socu_channel()[0][0]
        show = self.api.record_currently_airing_shows(1, includeChannelNumbers=channels)
        non_socu_show = self.api.record_currently_airing_shows(1)
        for program in [show[0][0], non_socu_show[0][0]]:
            self.api_assertions.verify_recording_myshows(self, program)
            self.api.cancel_all_recordings(state="inProgress")
            self.api_assertions.verify_recording_deleted_from_myshows(self, program)

    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_create_onepass_validate(self):
        show = self.service_api.extract_offer_id(self.service_api.get_grid_row_search(is_preview_offer_needed=True),
                                                 genre='movie', count=1)
        collectionId = show[0][1]
        subscriptionId = self.api.subscribe(Settings.tsn, collectionId)
        subscriptionList = self.api.subscriptionSearch(Settings.tsn, subscriptionId)
        self.api_assertions.verify_onepass_subscription(subscriptionList, collectionId)

    @pytest.mark.timeout(Settings.timeout)
    def test_verify_program_search(self):
        """
        Verify the search result for episode, show and movie.
        """
        channel = self.service_api.get_random_live_channel_rich_info(movie=False, episodic=True)
        result = self.api.get_unified_item_search(channel[0][2])
        self.api_assertions.verify_search_result(result, channel[0][2])
        channel = self.service_api.get_random_live_channel_rich_info(movie=False, episodic=False)
        result = self.api.get_unified_item_search(channel[0][2])
        self.api_assertions.verify_search_result(result, channel[0][2])
        channel = self.service_api.get_random_live_channel_rich_info(movie=True, episodic=False)
        result = self.api.get_unified_item_search(channel[0][2])
        self.api_assertions.verify_search_result(result, channel[0][2], channel[0][3])

    @pytest.mark.timeout(Settings.timeout)
    def test_verify_menu_items_on_home_screen(self):
        home_menu_shortcuts = self.api.get_quick_menu_instructions()
        self.api_assertions.validate_menu_items_on_home_screen(self, home_menu_shortcuts)

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_create_delete_future_recording_in_todolist(self):
        """
        Create and delete future recording and validate in todolist
        """
        api = self.service_api
        # Let's take cached get_grid_row_search() since it's already called in get_random_recordable_channel()
        show = api.map_channel_number_to_currently_airing_offers(api.get_random_recordable_channel(channel_count=-1,
                                                                 is_preview_offer_needed=True),
                                                                 api.get_grid_row_search(use_cached_grid_row=True),
                                                                 genre="series",
                                                                 future=2,
                                                                 count=1)
        offerId = show[0][3]
        contentId = show[0][2]
        self.api.record_this_content(contentId=contentId, offerId=offerId)
        self.api_assertions.verify_future_recording_in_todolist(self, show[0][0])
        self.api.delete_all_subscriptions()
        self.api_assertions.verify_future_recording_deleted_from_todolist(self, show[0][0])

    @pytest.mark.timeout(Settings.timeout)
    def test_create_and_verify_bookmark_shows(self):
        movie_details = self.service_api.get_random_live_channel_rich_info(movie=True)
        if movie_details is None:
            pytest.fail("Could not find any movies for bookmark")
        self.api.bookmark_show(movie_details[0][5], movie_details[0][6])
        self.service_api.verify_content_is_bookmarked(movie_details[0][6], movie_details[0][5])
        show_details = self.service_api.get_random_live_channel_rich_info(movie=False, episodic=False)
        if show_details is None:
            pytest.fail("Could not find any shows for bookmark")
        self.api.bookmark_show(show_details[0][5], show_details[0][6])
        self.service_api.verify_content_is_bookmarked(show_details[0][6], show_details[0][5])

    @pytest.mark.search_ccu
    def test_verify_search_response_is_fetched_same_from_trio_and_openAPI(self):
        """
            This test case verifies that the search response is returned successfully by Open and Morpheus APIs and the
            response values are same. This test case is a P1 in scope of Open API automation.
            """
        self.api_assertions.verify_search_response_is_found_same_for_morpheus_and_open_api()
