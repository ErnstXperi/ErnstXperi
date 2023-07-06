import time

import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.TTS.conftest import setup_tts, start_tts_log, stop_tts_log
from set_top_box.client_api.Menu.conftest import disable_parental_controls, setup_cleanup_parental_and_purchase_controls, \
    setup_enable_closed_captioning, enable_video_providers
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings
from set_top_box.client_api.guide.conftest import setup_cleanup_list_favorite_channels_in_guide  # noqa: F401
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions
from pytest_testrail.plugin import pytestrail
from set_top_box.client_api.home.conftest import cleanup_ftux


@pytest.mark.usefixtures("setup_tts")
@pytest.mark.usefixtures("start_tts_log")
@pytest.mark.usefixtures("stop_tts_log")
@pytest.mark.tts
@pytest.mark.compliance
# @pytest.mark.test_stabilization
class TestTTSScreen(object):
    def test_303673_home_screen(self):
        self.home_page.back_to_home_short()
        self.home_page.go_to_my_shows(self)
        self.tts_page.clear_log()
        self.guide_page.press_home_button()
        self.tts_assertions.verify_home_screen_tts(self)

    def test_303724_one_pass_options_screen(self):
        self.menu_page.go_to_user_preferences(self)
        self.tts_page.clear_log()
        self.tts_assertions.verify_one_pass_recording_options_tts(self)

    def test_318999_verify_tts_vod(self):
        self.vod_page.go_to_vod(self)
        self.tts_assertions.verify_home_screen_on_demand_tts(self)

    def test_355617_item_name_verification(self):
        self.home_page.back_to_home_short()
        self.tts_page.clear_log()
        self.tts_assertions.verify_home_screen_menu_items(self)

    def test_361374_socu_offer(self):
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True, filter_socu=True)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        self.home_page.go_to_guide(self)
        self.menu_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program)
        self.menu_page.wait_for_screen_ready()
        self.my_shows_page.go_to_cached_action_screen(self)
        self.programoption_assertions.verify_action_view_mode(self)
        self.tts_assertions.verify_program_title_tts(self)
        self.tts_assertions.verify_watch_now_strip(self)
        self.tts_page.clear_log()
        self.home_page.navigate_by_strip(self.home_labels.LBL_WTW_SOCU_ICON)
        self.tts_assertions.verify_socu_offer_tts(self)

    def test_294967_recording_options_overlay(self):
        channel = self.service_api.get_recordable_non_movie_channel()
        if not channel:
            pytest.fail("Test requires recordable channels")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_livetv_mode()
        self.tts_page.clear_log()
        self.screen.base.press_record()
        self.tts_assertions.verify_recording_options_overlay_tts(self)

    def test_74444761_various_keyactions_and_reboot(self):
        self.home_page.back_to_home_short()
        self.tts_assertions.verify_home_menu_strip_highlight_tts(self)
        self.home_assertions.validate_left_right_up_down_ok_key_actions(self)
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_page.back_to_home_short()
        self.tts_assertions.verify_home_menu_strip_highlight_tts(self)
        self.home_assertions.validate_left_right_up_down_ok_key_actions(self)

    @pytest.mark.favoritepanel
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_312064652_tts_favorites_panel_press_ok(self):
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.add_channel_to_favorites(channel)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel, confirm=False)
        self.guide_page.get_live_program_name(self, raise_error_if_no_text=False)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.tts_page.clear_log()
        self.screen.base.long_press_enter()
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_CHANNEL_OPTIONS)
        self.screen.base.press_down()
        self.tts_assertions.verify_display_channel_overlay_tts(self)

    # @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_312064618_pc_change_pin(self):
        """
        Accessibility - Parental Controls - Change PIN

        Testrail - https://testrail.tivo.com//index.php?/tests/view/312064618
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.tts_page.clear_log()
        self.tts_assertions.verify_change_pin_tts(self)
        self.tts_assertions.verify_current_pin_tts(self)
        self.menu_page.enter_default_parental_control_password(self)
        self.tts_assertions.verify_new_pin_tts(self)
        self.menu_page.enter_default_parental_control_password(self)
        self.tts_assertions.verify_confirm_pin_tts(self)
        self.menu_page.enter_default_parental_control_password(self)
        self.tts_assertions.verify_pin_change_notify_tts(self)

    @pytest.mark.favoritepanel
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_312064651_invoke_and_highlight_channels(self):
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.add_channel_to_favorites(channel)
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.tts_page.clear_log()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        # Adding 15 secs wait time for Favorite Strip to get dismissed
        time.sleep(15)
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.tts_assertions.verify_tts_favorite_panel(self)
        expected_text_list = []
        for i in range(5):
            expected_text = self.tts_page.get_expected_text_fav_panel_channel_detail(self.tts_labels.LBL_CHANNEL_INFO)
            if expected_text:
                expected_text_list.append(expected_text)
            else:
                self.screen.base.press_right()
                time.sleep(3)
                self.tts_assertions.verify_tts_text(self, self.tts_labels.LBL_PRESS_RIGHT_FOR_OTHER_FAVORITE_CHANNEL)
            self.screen.base.press_right()
            time.sleep(3)
            self.tts_assertions.verify_tts_text(self, self.tts_labels.LBL_PRESS_RIGHT_FOR_OTHER_FAVORITE_CHANNEL)
        self.screen.base.press_left()
        expected_text = self.tts_page.get_expected_text_fav_panel_channel_detail(self.tts_labels.LBL_CHANNEL_INFO)
        if expected_text:
            expected_text_list.append(expected_text)
        for exp in expected_text_list:
            self.tts_assertions.verify_tts_text(self, exp)
        expected_text_list.clear()

    def test_312064619_tts_in_trickplay(self):
        """
        https://testrail.tivo.com/index.php?/tests/view/312064619
        """
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_title()
        self.watchvideo_page.enter_channel_number(channel[0][0])
        self.guide_page.wait_for_screen_ready()
        self.guide_page.get_live_program_name(self)
        details = self.guide_page.check_if_series()
        self.tts_page.clear_log()
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.tts_assertions.verify_tts_on_trickplay(self, channel[0][0], details)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.tts_page.clear_log()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        log_list = self.tts_page.get_log()
        if log_list:
            self.tts_assertions.verify_tts_text(self, self.tts_labels.LBL_LIVE)

    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_389366355_verify_tts_for_all_options_on_trickplay(self):
        """
        Test case is developed based on pytest logs(expected results are different from pytest logs)
        checking on https://jira.tivo.com/browse/CA-9128
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(
            recordable=True, filter_channel=True, filter_ndvr=True, is_preview_offer_needed=True)
        programs = self.api.record_currently_airing_shows(number_of_shows=1, includeChannelNumbers=channels,
                                                          genre="series", use_cached_grid_row=True)
        if not programs:
            pytest.skip("No recordable shows found")
        program = programs[0][0]
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_recording_playback(self)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.watch_video_for(60 * 2)
        self.tts_page.clear_log()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_page.press_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.tts_page.highlight_and_verify_trickplay_left_side_icons(self)
        self.tts_page.clear_log()
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.tts_page.clear_log()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.tts_page.clear_log()
        self.tts_page.highlight_and_verify_trickplay_right_side_icons(self)
        self.tts_page.clear_log()
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.watch_video_for(60 * 2)
        self.tts_page.clear_log()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.tts_page.verify_play(self)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.tts_page.clear_log()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_page.watch_video_for(10)
        self.tts_page.verify_pause(self)

    @pytestrail.case("C4863305")
    @pytest.mark.ftux
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.timeout(Settings.timeout)
    def test_4863305_press_skip_on_ftux_streaing_apps_screen(self):
        """
        FTUX - Streamin apps Screen - Whisper on "Skip this step"
        Verify:
        1. Message in the whisper is read:
        <Notification: You can repeat first-time setup by going to PATH_FTUX_HELP>PATH_FTUX_HELP = Menu >
        System & Account > Help > Quick Tour
        """
        self.home_page.update_test_conf_and_reboot("device", fast=True, clear_data=True, skip_onepass=False, skip_apps=False,
                                                   skip_pcsetting=True, SKIP_FTUX="false")
        self.home_page.pause(10)  # wait is added to stable the screen
        self.home_page.ftux_onepass_selection_and_verification(self, Settings.app_package, Settings.username)
        self.tts_page.clear_log()
        self.home_assertions.verify_ftux_streamingapps_screen()
        self.home_page.select_skip_this_step(self)
        if self.home_page.is_ftux_pc_settings_screen_view_mode():
            self.home_assertions.verify_ftux_pcsettings_screen()
            self.home_page.select_skip_this_step_ftux_pcsetting_screen()
        self.tts_assertions.verify_tts_after_pressing_skip_option(self)
        self.home_page.pause(10)  # wait is added to stable the screen
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()

    def test_4757101_verify_tts_on_vod_movie_screen(self):
        status, result = self.vod_api.get_entitled_vod_with_within_duration(600, 7200)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.tts_page.clear_log()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.tts_assertions.verify_tts_on_vod_action_screen(self)

    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_frum_114732_verify_tts_on_program_screen_and_demand_episode_strip(self):
        """
        Verify that TTS is pronouncing correctly highlighted On Demand Episodes option on episodic program screen.
        Verify that TTS is pronouncing the content of the FA Video On Demand episodic program.
            - Takes only self as argument
        :return:
        """
        status, results = self.vod_api.getOffer_mapped_svod_entitledSubscribed_series()
        if results is None:
            pytest.skip("Test requires mapped offer to validate episodic asset")
        self.home_page.back_to_home_short()
        self.tts_page.clear_log()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.tts_assertions.verify_tts_episode_action_screen(self)
        self.tts_page.clear_log()
        self.vod_page.nav_to_menu(self.vod_labels.LBL_ON_DEMAND_EPISODES)
        self.vod_page.pause(5)
        self.tts_assertions.verify_tts_on_demand_episode_strip(self)

    def test_frum_136334_tts_on_off(self):
        """
            TTS ON/OFF
        """
        self.screen.base.TTS_on_off()
        self.screen.base.TTS_on_off(tts=True)
        self.screen.base.TTS_on_off()

    @pytest.mark.xray('FRUM-143769')
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_143769_may_also_like_biaxial_strip_tts(self):
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(self.text_search_labels.LBL_SEARCH_TEXT_STRING,
                                                self.text_search_labels.LBL_EXPECTED_SEARCH_STRING)

        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=False)
        self.tts_assertions.verify_tts_may_also_like_biaxial_strip(self)
