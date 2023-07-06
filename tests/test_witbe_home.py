import pytest
import os
import time
from set_top_box.test_settings import Settings
from set_top_box.client_api.end2end.conftest import decrease_screen_saver, set_screen_saver_default_value  # noqa: F401
from set_top_box.client_api.home.conftest import *  # noqa: F401
from set_top_box.client_api.Menu.conftest import disable_parental_controls


@pytest.mark.usefixtures("setup_home")
@pytest.mark.home
class TestWitbeHome(object):

    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("set_screen_saver_default_value")
    def test_livetv_indefinite_time(self):
        """
        C8880255
        Go to Menu->Settings->Device settings->Screen saver
        Navigate to Live TV.
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.select_and_watch_program(self)
        self.guide_assertions.verify_live_playback()

    @pytest.mark.timeout(Settings.timeout)
    def test_youtube_playback(self):
        """
        C8880425
        To verify ability to playback an Youtube
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.select_and_watch_program(self)
        self.guide_assertions.verify_live_playback()
        self.home_page.open_youtube()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.apps_and_games_assertions.verify_app_content_playing()
