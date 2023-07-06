import random
import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.end2end.conftest import setup_e2e, switch_off_show_only_favorite_channels_in_guide  # noqa: F401
from set_top_box.client_api.end2end.conftest import decrease_screen_saver, set_screen_saver_default_value  # noqa: F401
from set_top_box.client_api.Menu.conftest import disable_parental_controls, enable_netflix, disable_video_window  # noqa: F401
from set_top_box.client_api.Menu.conftest import setup_lock_parental_and_purchase_controls  # noqa: F401
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_start_tivo_app  # noqa: F401
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings


@pytest.mark.e2e
@pytest.mark.witbe_e2ecase
class TestWitbeE2e:

    def test_e2e_74365226_verify_live_show_and_vod_playback(self):
        """
        Xray ID-   https://jira.xperi.com/browse/FRUM-108257
        """
        status, results = self.vod_api.get_offer_playable()
        if results is None:
            pytest.skip("The VOD offer content is not available on catalog")
        if Settings.is_feature_4k():
            channel_list = self.service_api.get_4k_channel(channel_count=-1, recordable=True)
            if not channel_list:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
            channel = random.choice(channel_list)
        else:
            channel_list = self.service_api.get_random_recordable_channel(channel_count=1, filter_channel=True)
            if not channel_list:
                pytest.skip("No channels found")
            channel = channel_list[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.play_any_playable_vod_content(self, results)
        self.vod_assertions.verify_vod_playback(self)
        self.home_page.back_to_home_short()
        self.menu_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    def test_e2e_74383986_verify_pause_replay_modes_for_livetv_show(self):
        """
        https://jira.xperi.com/browse/FRUM-108721
        """
        channel = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True)
        if channel is None:
            pytest.skip("No appropriate channels found")
        self.home_page.goto_live_tv(random.choice(channel))
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(4)  # watch for few min to validate replay
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_page.press_play_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_page.press_left_multiple_times(no_of_times=2)
        self.watchvideo_assertions.is_replay_focused(self)
        self.screen.base.press_enter(10)  # Press 'Start Over' button and wait for 10 sec
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_replay(self, current_position, key_press=10)

    def test_e2e_108262_verify_toggle_between_random_livetv_random_channels(self):
        """
               https://jira.xperi.com/browse/FRUM-108262
        """
        if Settings.is_feature_4k():
            channel_list = self.service_api.get_4k_channel(channel_count=-1, recordable=True)
            if not channel_list:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
            channel = random.choice(channel_list)
        else:
            channel_list = self.service_api.get_random_recordable_channel(channel_count=1, filter_channel=True)
            if not channel_list:
                pytest.skip("No channels found")
            channel = channel_list[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.back_to_home_short()
        self.home_assertions.select_live_channel_from_prediction(self)
        self.home_page.channel_change_in_olg(self)
        self.guide_page.goto_one_line_guide_from_live(self, channel=channel)
        self.guide_page.check_for_overlay_watchnow_or_watchlive()
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_LIVETV_VIEWMODE)

    def test_e2e_74358129_verify_livetv_after_socu_playback(self):
        """
            1. Highlight the SOCU offer in Guide.
            2. Press info button to bring up the Recording Overlay.
            3. Select the "Watch from <CATCHUP_NAME>" option. Verify A.
            4. Press Live TV. Verify B.
            A. Playback begins and video streams successfully from beginning with clear AV.
            B. System goes to Live TV. Video and audio are synced with no issues. (--- This feature will handle future)
            get_available_channels_with_socu_offer
        """
        channels = self.service_api.channels_with_current_show_start_time()
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1,
                                                                             socu=True, grid_row=channels,
                                                                             encrypted=True)
        if channel is None:
            pytest.skip("The SOCu offer content is not available on catalog")
        self.watchvideo_page.calc_end_time_for_30_m_show(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.open_record_overlay()
        catchup_name = self.guide_page.get_watch_now_catchup_name(self)
        self.guide_assertions.verify_text_image_from_screen(catchup_name,
                                                            self.guide_labels.LBL_RECORD_OVERLAY_CATCHUP_ICON)
        self.guide_assertions.verify_more_info_option_on_record_overlay(self)
        self.home_page.goto_live_tv()
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_e2e_74353253_verify_pause_resume_modes_for_ndvr_recording(self):

        """
                https: // jira.xperi.com / browse / FRUM - 108695
        1. Go to My Shows and play the nDVR recording and watch for a few minutes.
        2. Press the Pause button. Verify expected result A.
        3. Press the Play button. Verify expected result B.
        4. Resume playing the recording until the end. Verify expected result C.

        A. The recording is in Pause mode.
        B. The recording is in Play mode.
        C. The recording plays without any issues until the end.
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True,
                                                                        filter_ndvr=True)
        recording = self.api.record_currently_airing_shows(1, includeChannelNumbers=channels, filter_channel=True,
                                                           filter_ndvr=True)
        if not recording:
            pytest.skip("Failed to schedule recording")
        show = recording[0][0]
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_screen_title(self.my_shows_labels.LBL_MY_SHOWS)
        last_screen = self.my_shows_page.play_recording(show)
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_watch_recording_mode(self)
        self.watchvideo_page.skip_hdmi_connection_error()
        self.watchvideo_assertions.verify_playback_play()
        if not self.watchvideo_page.get_trickplay_visible():
            self.screen.base.press_enter()
        self.watchvideo_page.press_play_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.watchvideo_page.wait_for_resume_playing_overlay()
        self.watchvideo_assertions.verify_resume_playing_overlay_shown(True)
        self.watchvideo_page.select_menu(self.liveTv_labels.LBL_STOP_PLAYING_OPTION)
        self.watchvideo_assertions.verify_resume_playing_overlay_shown(False)
        self.watchvideo_assertions.verify_view_mode(last_screen)

    def test_e2e_74376951_verify_back_button_on_vod_playback(self):
        """
        Xray ID-   https://jira.xperi.com/browse/FRUM-
        """
        status, results = self.vod_api.get_offer_playable()
        if results is None:
            pytest.skip("The VOD offer content is not available on catalog")
        if Settings.is_feature_4k():
            channel = self.service_api.get_4k_channel(channel_count=-1, recordable=True)
            if not channel:
                pytest.fail("Could not get UHD channel,please check the provision of the device")
        else:
            channel = self.service_api.get_random_recordable_channel(channel_count=1, filter_channel=True)
        if not channel:
            pytest.skip("No channels found")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.play_any_playable_vod_content(self, results)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.press_back_button(refresh=True)
        if self.my_shows_page.is_action_screen_view_mode():
            self.vod_assertions.verify_view_mode(self.my_shows_labels.LBL_ACTION_SCREEN_VIEW)
        else:
            self.my_shows_assertions.verify_view_mode(self.my_shows_labels.LBL_SERIES_SCREEN_VIEW)
