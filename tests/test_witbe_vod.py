import os
import random
import time

import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.VOD.conftest import *
from set_top_box.client_api.Menu.conftest import setup_cleanup_parental_and_purchase_controls, setup_enable_video_window
from set_top_box.client_api.my_shows.conftest import setup_delete_book_marks
from set_top_box.client_api.Menu.conftest import setup_disable_closed_captioning
from pytest_testrail.plugin import pytestrail
from set_top_box.client_api.Menu.conftest import disable_parental_controls


@pytest.mark.vod
@pytest.mark.usefixtures("setup_vod")
@pytest.mark.usefixtures("is_service_vod_alive")
class TestWitbeVOD(object):

    @pytest.mark.timeout(Settings.timeout)
    def test_vod_playback_after_nDVR_rec_playback(self, setup_myshows_delete_recordings):
        """
        C8880235
        Verify playing a nDVR recording and then playing a VOD asset.
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
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_vod_playback(self)

    @pytest.mark.timeout(Settings.timeout)
    def test_back_button_on_vod_playback(self):
        """
        C8880238, C8880233
        Verify watching live TV, playing a VOD asset.
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.select_and_watch_program(self)
        self.guide_assertions.verify_live_playback()
        # watch the live show for a few minutes.
        self.vod_page.wait(90)
        status, result = self.vod_api.getOffer_fvod()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
