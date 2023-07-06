import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.my_shows.conftest import *  # noqa: F401
from set_top_box.client_api.guide.conftest import *  # noqa: F401
from set_top_box.client_api.Menu.conftest import *  # noqa: F401
from pytest_testrail.plugin import pytestrail
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions
from set_top_box.client_api.home.conftest import set_bridge_status_up


@pytest.mark.usefixtures("setup_my_shows")
@pytest.mark.myshows
class TestWitbeMyShows(object):

    @pytest.mark.timeout(Settings.timeout)
    def test_playback_recording(self, setup_my_shows_sort_to_date, setup_myshows_delete_recordings):
        """
        C8880145,C8880228
        To verify ability to playback an inprogress/completed recording
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
