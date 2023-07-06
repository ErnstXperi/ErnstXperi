import time
import random
import json

import pytest
from hamcrest import assert_that

from set_top_box.test_settings import Settings
from set_top_box.conf_constants import FeAlacarteFeatureList, FeAlacartePackageTypeList, HydraBranches, FeaturesList, \
    DeviceFeatureSearchFeatures, NotificationSendReqTypes, RemoteCommands
from set_top_box.client_api.home.conftest import cleanup_package_names_native,\
    preserve_initial_package_state, remove_packages_if_present_before_test, fill_internal_storage_by_installing_apps, \
    free_up_internal_memory_by_uninstalling, restore_mind_availability, enable_disable_stay_awake, \
    setup_disable_stay_awake, decrease_screen_saver, back_to_home, refresh_ppv_credit_limit
from set_top_box.client_api.watchvideo.conftest import setup_liveTv, setup_cleanup_tivo_plus_channels, \
    setup_cleanup_tivo_plus_channels_first_launch, setup_cleanup_inactivity_timeout, reset_bandwidth_rule, \
    setup_cleanup_turn_on_device_power, cleanup_clear_app_data
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings
from set_top_box.client_api.watchvideo.conftest import increase_timeout_of_widgets_in_watch_video_screen
from set_top_box.shared_context import ExecutionContext
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_bind_hsn, setup_cleanup_pluto_tv_app
from set_top_box.client_api.Menu.conftest import setup_enable_video_window, disable_parental_controls, \
    setup_disable_closed_captioning, setup_cleanup_disable_closed_captioning, disable_video_window, \
    setup_enable_closed_captioning, setup_cleanup_parental_and_purchase_controls, cleanup_favorite_channels, \
    enable_video_providers, setup_cleanup_remove_playback_source, setup_enable_full_screen_video_on_home
from set_top_box.client_api.guide.conftest import setup_cleanup_list_favorite_channels_in_guide, toggle_mind_availability, \
    switch_tivo_service_rasp, setup_prepare_params_for_guide_cells_test, toggle_guide_rows_service_availability
from pytest_testrail.plugin import pytestrail


@pytest.mark.usefixtures("setup_liveTv")
@pytest.mark.usefixtures("is_service_livetv_alive")
@pytest.mark.livetv
@pytest.mark.timeout(Settings.timeout)
class TestLiveTvScreen(object):

    # @pytest.mark.p1_regression
    @pytest.mark.infobanner
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    def test_335008_disable_cc_from_live_tv(self):
        """
        335008
        Disable Closed Captioning from Live TV
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.watchvideo_page.turn_on_cc(self, ON=False)
        self.menu_page.go_to_accessibility(self)
        self.menu_assertions.verify_accessibility_screen_title(self)
        self.menu_page.go_to_closed_captioning(self)
        self.menu_assertions.verify_cc_state(self, ON=False)

    @pytestrail.case("C11123890")
    # @pytest.mark.bat
    @pytest.mark.infobanner
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("setup_disable_closed_captioning", "setup_cleanup_disable_closed_captioning")
    @pytest.mark.xray("FRUM-297")
    @pytest.mark.msofocused
    def test_335003_enable_cc_from_live_tv(self):
        """
        335003
        Enabling Closed Captioning from Live TV
        :return:
        """
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.turn_on_cc(self)

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.infobanner
    @pytest.mark.usefixtures("setup_disable_closed_captioning")
    def test_5595810_info_banner_closed_captions_message_area(self):
        """
        :description:
            To verify the message area for the "Turn Closed Captions OFF" action of the Full Info Banner
            in Watch Video when Closed Captions are enabled
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/5595810
        :return:
        """
        self.home_page.go_to_guide(self)
        channel_info = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0]
        self.watchvideo_page.enter_channel_number(channel_info[0], confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.turn_on_cc(self, press_back=False)
        self.watchvideo_page.navigate_by_strip(self.liveTv_labels.LBL_TURN_CC_OFF)
        self.watchvideo_assertions.verify_message_area_of_info_banner_contains_text(
            self.liveTv_labels.LBL_TURN_CC_OFF,
            self.liveTv_labels.LBL_TURN_CC_OFF_MESSAGE_TEXT)

    @pytest.mark.disabled
    @pytest.mark.iplinear
    def test_330093_home_menu_widget_over_liveTV(self):
        """
        Test was disabled as outdated because predictions panel is no more displayed in watchvideo screens
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.show_home_menu_widget()
        self.watchvideo_assertions.verify_home_menu_widget_is_shown(self.liveTv_labels.LBL_PREDICTION_PANEL_TITLE)

    @pytestrail.case("C11123889")
    @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_309129_schedule_record_from_info_banner(self):
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.goto_live_tv(channel, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_page.pause(4)
        self.watchvideo_page.close_info_banner()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_full_info_banner_is_shown()
        self.watchvideo_page.select_strip(self.liveTv_labels.LBL_RECORD)
        self.watchvideo_page.wait_for_screen_ready(self.guide_labels.LBL_RECORD_OVERLAY)
        self.watchvideo_assertions.verify_overlay()
        self.watchvideo_page.nav_to_menu_by_substring(self.guide_labels.LBL_RECORD)
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)

    # @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.infobanner
    def test_152179_full_info_banner_liveTV(self):
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_full_info_banner_is_shown()
        self.watchvideo_page.close_info_banner()
        self.watchvideo_assertions.verify_full_info_banner_is_not_shown()

    @pytestrail.case("C12792637")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    def test_270343_program_actions_LiveTV(self):
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_view_mode(self.guide_labels.LBL_VIEW_MODE)
        self.guide_page.open_record_overlay()
        self.guide_page.select_menu_by_substring(self.menu_page.get_more_info_name(self))
        self.program_options_assertions.verify_view_mode(self.program_options_labels.LBL_ACTION_SCREEN_VIEW)
        self.program_options_page.select_strip(self.program_options_labels.LBL_WATCH_NOW_FROM_LIVE_TV)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)

    @pytestrail.case("C12792635")
    @pytest.mark.infobanner
    @pytest.mark.iplinear
    def test_186293_verify_banner_and_trickplay_entering_LiveTV(self):
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE, refresh=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_infobanner_and_trickplay_shown()

    @pytestrail.case("C12792636")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    # @pytest.mark.test_stabilization
    def test_157864_verify_pause_mode_in_LiveTV(self):
        """
        Currently test FAILS on AppleTV
        Bug link: https://jira.tivo.com/browse/IPTV-10914
        """
        self.home_page.back_to_home_short()
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True,
                                                                        exclude_tplus_channels=True)
        if not channels:
            pytest.skip("No appropriate channels found.")
        channel = channels[0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.build_cache(60 * 20)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.is_playpause_focused(value="Pause")
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.is_playpause_focused(value="Play")
        self.watchvideo_page.press_ok_button()
        self.guide_assertions.verify_play_normal()
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C12792615")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    # @pytest.mark.test_stabilization
    def test_9648250_verify_live_tv_trickplay_restrictions_pause(self):
        """
        To verify message for IPLINEAR TrickPlay restrictions with Pause disabled.

        Testrail:
            https://testrail.corporate.local/index.php?/cases/view/9648250
        """
        channel_list = self.api.get_linear_channels_with_trickplay_restrictions("linearStreamingRestrictions", "pause",
                                                                                filter_channel=True, entitled=True)
        if not channel_list:
            pytest.skip("There are no channels that have pause trickplay restrictions.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.watchvideo_page.enter_channel_number(channel_list[0], confirm=True)
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_page.press_pause_in_visual_trickplay()
        self.watchvideo_assertions.verify_trickplay_restriction_message_shown(self.liveTv_labels.LBL_PAUSE_NOT_ALLOWED)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    # @pytest.mark.p1_regression
    @pytest.mark.infobanner
    @pytest.mark.ndvr
    def test_78031_info_banner_brandingicon(self):
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.goto_live_tv(channel[0][0])
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.screen.base.press_channel_up()
        self.screen.base.press_channel_down()
        self.home_page.press_info_button()
        self.watchvideo_assertions.verify_full_info_banner_brandingicon_is_shown()

    # @pytest.mark.p1_regression
    """Test script steps got duplicated with BAT TC 355106"""
    @pytest.mark.duplicate
    def test_269366_change_audio_track_from_info_banner(self):
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_full_info_banner_is_shown()
        self.watchvideo_page.select_strip(self.liveTv_labels.LBL_CHANGE_AUDIO_TRACK)
        self.watchvideo_assertions.verify_overlay_shown()
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_AUDIO_TRACK_OVERLAY_TITLE)

    @pytestrail.case("C11123971")
    @pytest.mark.bat
    @pytest.mark.socu
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.cloud_core_vod_socu
    def test_363174_play_encrypted_socu_from_liveTv(self):
        """
        Test Case 363174: SOCU - Encrypted playback
        Attempt to playback the encrypted SOCU offer from Live TV.
        :return:
        """
        channel = self.guide_page.get_encrypted_socu_channel(self, filter_socu=True)
        channel_number = (channel[0][0])
        self.home_page.goto_live_tv(channel_number, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.startover_program_from_livetv_with_socu(self)
        self.watchvideo_assertions.verify_vod_mode()
        self.watchvideo_page.watch_video_for(60 * 2)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.back_to_home_short()

    @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_127813_delete_program_from_watchlist_by_delete_icon(self):
        """
        Test case is developed as a part of https://jira.xperi.com/browse/PARTDEFECT-11906
        """
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, is_preview_offer_needed=True),
            self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True), genre="series", count=1)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][1])
        self.guide_page.get_live_program_name(self)
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_WATCH_LIST)
        self.my_shows_page.delete_recording()
        self.my_shows_page.verify_focus_is_on_watchlist(self.my_shows_labels.LBL_WATCH_LIST)

    @pytestrail.case("C12792616")
    @pytest.mark.p1_regression
    @pytest.mark.socu
    @pytest.mark.iplinear
    @pytest.mark.cloud_core_liveTV
    # @pytest.mark.test_stabilization
    def test_5596996_verify_press_and_hold_to_start_over_tip_is_shown(self):
        """
        To verify the "Press & hold OK to Start over" banner tip of the Standard Info Banner in IPLINEAR

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/5596996
        """
        channel = self.api.get_random_catch_up_channel_current_air(filter_channel=True,
                                                                   filter_socu=True,
                                                                   restrict=False,
                                                                   catchup=False)
        if not channel:
            pytest.skip("Could not find any start over SOCU channel")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=True)
        self.guide_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_press_and_hold_ok_socu_tip(self.liveTv_labels.LBL_PRESS_AND_HOLD_BANNER_TIP)
        self.screen.base.long_press_enter()
        self.vod_page.manage_launched_playback(self, availability_type="svod")
        self.watchvideo_assertions.verify_error_overlay_not_shown()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_VOD_VIEWMODE)

    @pytestrail.case("C12792140")
    @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.skipif("telus" in Settings.mso.lower(), reason="TV-G rating is not available for telus MSO")
    def test_350660_changing_parental_controls_rating_to_tv_G(self):
        """
        Description:
        To verify Parental Conrols OSD and availability to watch show with rating TV-G in Live TV after PIN check
        """
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_page.select_menu(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_assertions.verify_create_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_assertions.verify_confirm_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.select_menu(self.menu_labels.LBL_SET_RATING_LIMITS)
        self.menu_page.wait_for_screen_ready(self.menu_labels.LBL_SET_RATING_LIMITS_SCREEN)
        self.menu_page.set_tv_rating_limits(self.menu_labels.LBL_TV_RATING_TV_G)
        channel = self.api.get_random_rating_channels(rating=self.menu_labels.LBL_TV_RATING_TV_G)
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=False)
        channel = self.api.get_random_rating_channels(rating=self.menu_labels.LBL_TV_RATING_TV_PG)
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=True)
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_PIN_challenge_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=False)

    # @pytest.mark.p1_regression
    @pytest.mark.infobanner
    # @pytest.mark.test_stabilization
    def test_5595813_check_up_next_show_in_info_banner(self):
        """
        :description:
            Check if up-next program shown in the Info Banner is a correct one
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/5595813
        :return:
        """
        self.home_page.go_to_guide(self)
        channel_number = self.service_api.get_random_live_channel_rich_info(movie=False, transport_type="stream")[0][0]
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.guide_page.press_ok_button()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_livetv_mode()
        up_next_show = self.api.get_up_next_show(channel_number)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_up_next_of_info_baner_header(up_next_show)

    @pytest.mark.infobanner
    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    def test_5595803_check_right_column_of_info_banner_header(self):
        """
        :description:
            To verify the correct information is present in the Info Banner Header
            while watching Live TV.
        :testrail:
            Test Case: https://testrail.corporate.local/index.php?/cases/view/5595803
        :return:
        """
        self.home_page.go_to_guide(self)
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_video_format_icon_of_info_baner_header()
        self.watchvideo_assertions.verify_channel_logo_of_info_baner_header()
        self.watchvideo_assertions.verify_clock_of_info_baner_header()
        self.watchvideo_assertions.verify_up_next_of_info_baner_header()
        self.watchvideo_assertions.verify_channel_number(channel_number)

    # @pytest.mark.p1_regression
    @pytest.mark.infobanner
    # @pytest.mark.test_stabilization
    def test_5596992_info_banner_more_info_message_area(self):
        """
        :description:
            To verify the message area and action when the highlight is in "More Info"
            of the Full Info Banner in Watch Video
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/5596992
        :return:
        """
        self.home_page.go_to_guide(self)
        channel_info = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0]
        self.watchvideo_page.enter_channel_number(channel_info[0], confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        more_info = self.menu_page.get_more_info_name(self)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_page.navigate_by_strip(more_info)
        self.watchvideo_assertions.verify_message_area_of_info_banner_does_not_contain_text(more_info, is_wait=True)
        self.watchvideo_page.select_strip(more_info)
        show_title = self.api.get_offer_search(
            min_start_time=self.service_api.get_middle_mind_time()['currentTime'], station_id=channel_info[2],
            channel_number=channel_info[0], count=1)[0].title
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_ACTION_SCREEN_VIEWMODE)
        self.watchvideo_assertions.verify_screen_title(show_title)

    @pytest.mark.favorite_channels
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    @pytest.mark.usefixtures("cleanup_favorite_channels")
    def test_9916690_1_verify_chup_chdown_buttons_in_confirm_jump_channel_overlay(self):
        """
        To verify ChannelUp/ChannelDown buttons in Confirm Jump Channel overlay
        Testcase: https://testrail.tivo.com//index.php?/cases/view/9916690
        """
        self.home_page.back_to_home_short()
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        jump_channel = list(self.api.get_jump_channels_list().keys())[0]
        if not channel and jump_channel:
            pytest.skip("There are no channels that have next/previous jump channels.")
        self.api.add_favorite_channel([channel, jump_channel])
        self.menu_page.update_favorite_channels_list(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        self.guide_page.wait_for_screen_ready()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_number(channel)
        self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_page.press_channel_down_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_not_shown()
        self.watchvideo_assertions.verify_channel_number(channel)
        self.watchvideo_page.press_channel_down_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_not_shown()
        self.watchvideo_assertions.verify_channel_number(channel)

    @pytest.mark.favorite_channels
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    @pytest.mark.usefixtures("cleanup_favorite_channels")
    def test_9916690_2_verify_launch_app_option_in_confirm_jump_channel_overlay(self):
        """
        To verify OTT app launch from Confirm Jump Channel overlay
        Testcase: https://testrail.tivo.com//index.php?/cases/view/9916690
        """
        self.home_page.back_to_home_short()
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        jump_channel = list(self.api.get_jump_channels_list().keys())[0]
        if not channel and jump_channel:
            pytest.skip("There are no channels that have next/previous jump channels.")
        self.api.add_favorite_channel([channel, jump_channel])
        self.menu_page.update_favorite_channels_list(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        self.guide_page.wait_for_screen_ready()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_LAUNCH_APP)
        self.watchvideo_assertions.verify_app_is_foreground(Settings.app_package, state=False)

    @pytest.mark.favorite_channels
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    @pytest.mark.usefixtures("cleanup_favorite_channels")
    def test_9916690_3_verify_next_channel_option_in_confirm_jump_channel_overlay(self):
        """
        To verify 'Next Channel' option in Confirm Jump Channel overlay
        Testcase: https://testrail.tivo.com//index.php?/cases/view/9916690
        """
        self.home_page.back_to_home_short()
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        jump_channel = list(self.api.get_jump_channels_list().keys())[0]
        if not channel and jump_channel:
            pytest.skip("There are no channels that have next/previous jump channels.")
        self.api.add_favorite_channel([channel, jump_channel])
        self.menu_page.update_favorite_channels_list(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        self.guide_page.wait_for_screen_ready()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.press_channel_down_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_NEXT_CHANNEL)
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_not_shown()

    @pytest.mark.favorite_channels
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    @pytest.mark.usefixtures("cleanup_favorite_channels")
    def test_9916690_4_verify_confirm_jump_channel_overlay_timeout(self):
        """
        To verify Confirm Jump Channel overlay timeout
        Testcase: https://testrail.tivo.com//index.php?/cases/view/9916690
        """
        self.home_page.back_to_home_short()
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        jump_channel = list(self.api.get_jump_channels_list().keys())[0]
        if not channel and jump_channel:
            pytest.skip("There are no channels that have next/previous jump channels.")
        self.api.add_favorite_channel([channel, jump_channel])
        self.menu_page.update_favorite_channels_list(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        self.guide_page.wait_for_screen_ready()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_timeout(
            self.liveTv_labels.LBL_CONFIRM_JUMP_CHANNEL_OVERLAY_TIMEOUT)

    @pytest.mark.favorite_channels
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    @pytest.mark.usefixtures("cleanup_favorite_channels")
    def test_9916690_5_verify_bail_buttons_in_confirm_jump_channel_overlay(self):
        """
        To verify bail buttons in Confirm Jump Channel overlay
        Testcase: https://testrail.tivo.com//index.php?/cases/view/9916690
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        jump_channel = list(self.api.get_jump_channels_list().keys())[0]
        if not channel and jump_channel:
            pytest.skip("There are no channels that have next/previous jump channels.")
        self.api.add_favorite_channel([channel, jump_channel])
        self.menu_page.update_favorite_channels_list(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        for button in self.liveTv_labels.LBL_MANAGED_BAIL_BUTTONS:
            self.home_page.go_to_guide(self)
            self.guide_assertions.verify_guide_title()
            self.guide_page.enter_channel_number(channel)
            self.guide_page.press_ok_button()
            self.watchvideo_assertions.verify_livetv_mode()
            self.watchvideo_page.press_channel_down_button()
            self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
            self.watchvideo_assertions.verify_bail_buttons_in_confirm_jump_channel_overlay(self, button, channel)

    @pytestrail.case("C12792632")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    @pytest.mark.skipif("b-hydra-streamer-1-7" in Settings.branch.lower(), reason="Build does not support the feature")
    def test_10195352_verify_favorite_channels_panel_watch_livetv(self):
        """
        :Description:
            To verify Favorite Cahnnels panel watching LiveTV
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/10195352
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.go_to_favorite_channels()
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()

    # @pytest.mark.p1_regression
    @pytest.mark.infobanner
    # @pytest.mark.test_stabilization
    def test_5595798_verify_episodic_livetv_program_title_in_info_banner(self):
        """
        :description:
            To verify the Series show title is displayed in the Full Info Banner for an episodic LiveTV streaming show
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/5595798
        :return:
        """
        channel = self.api.get_random_live_channel_rich_info(episodic=True, movie=False, entitled=True, filter_channel=True)
        if channel is None:
            pytest.fail("Could not find any episodic channel")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        current_show_title = self.guide_page.get_grid_focus_details()['grid_header_title']
        self.guide_page.start_live_tv_playback(self)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_show_title(current_show_title)

    @pytestrail.case("C12792617")
    # @pytest.mark.p1_regression
    @pytest.mark.p1_reg_stability
    @pytest.mark.iplinear
    @pytest.mark.infobanner
    @pytest.mark.platform_cert_smoke_test
    # @pytest.mark.test_stabilization
    def test_74383986_verify_watching_an_airing_live_show_and_press_pause_replay_buttons(self):
        """
        :description:
            Verify watching an airing live show, pressing Pause,
            and then pressing the Replay button multiple times until reach the begining.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/tests/view/74383986
        :return:
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True,
                                                                        exclude_tplus_channels=True)
        if channels is None:
            pytest.skip("No appropriate channels found")
        self.home_page.goto_live_tv(channels[0])
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.navigate_to_end_of_video()
        self.watchvideo_page.watch_video_for(30)  # watch for sometime to validate replay
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.show_trickplay_if_not_visible(refresh=True)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_page.press_play_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_replay(self, current_position, key_press=10)
        self.my_shows_page.navigate_to_start_of_video_with_replay_button(self)

    # @pytest.mark.test_stabilization
    # @pytestrail.case("C11685253")
    @pytest.mark.ndvr
    # @pytest.mark.e2e
    @pytest.mark.livetv
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-229")
    @pytest.mark.longrun
    @pytest.mark.notapplicable(Settings.is_devhost())
    def test_74367571_verify_playing_nDVR_recording_rewind_to_beginning_resume_playing_and_check_fast_forward(self):
        """
        :description:
            Verify playing a nDVR recording, rewinding to the beginning
            resume playing, fast forwarding, and resume playing.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/tests/view/74367571
        :return:
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True)
        recording = self.api.schedule_single_recording(channels=channels)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(recording[0][0])
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.select_and_wait_for_playback_play()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.navigate_to_start_of_video()
        self.watchvideo_page.press_clear_button()
        self.guide_assertions.verify_play_normal()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.guide_assertions.verify_fast_forward_1(self)

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685254")
    # @pytest.mark.e2e
    @pytest.mark.livetv
    @pytest.mark.longrun
    @pytest.mark.notapplicable(Settings.is_devhost())
    def test_8880427_verify_playing_nDVR_recording_rewind_to_beginning_and_resume_playing(self):
        """
        :description:
            Verify playing a nDVR recording , leaving the recording idle,
            rewinding to the beginning, and then resume playing.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/8880427
        :return:
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True)
        recording = self.api.schedule_single_recording(channels=channels)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(recording[0][0])
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.navigate_to_start_of_video()
        self.guide_assertions.verify_play_normal()

    @pytest.mark.skipif(not Settings.is_android_tv(), reason="Screen recording is applicable only for android")
    @pytest.mark.notapplicable(Settings.is_devhost())
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.compliance
    @pytest.mark.platform_cert_smoke_test
    # pytest.mark.infobanner
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    @pytest.mark.xray("FRUM-843")
    @pytest.mark.msofocused
    def test_10197270_verify_cc_rendered_when_ON(self):
        """
        :description:
            To verify subtitle/closed caption is rendered on live tv when it is ON
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197270
        :return:
        """
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     exclude_jump_channels=True, transport_type="stream")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.close_info_banner()
        self.watchvideo_assertions.record_and_verify_cc(".", 20, Settings.log_path, "ON")

    @pytest.mark.skipif(not Settings.is_android_tv(), reason="Screen recording is applicable only for android")
    @pytest.mark.notapplicable(Settings.is_devhost())
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.compliance
    @pytest.mark.infobanner
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_disable_closed_captioning", "setup_cleanup_disable_closed_captioning")
    def test_10197270_verify_cc_rendered_when_turned_ON_via_LiveTV(self):
        """
        :description:
            To verify subtitle/closed caption is rendered on live tv when it is ON
            This test case is an extension of TC:10197270, wherein CC is turned ON from Live TV
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197270
        :return:
        """
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.turn_on_cc(self)
        self.watchvideo_assertions.record_and_verify_cc(".", 20, Settings.log_path, "ON")

    @pytest.mark.skipif(not Settings.is_android_tv(), reason="Screen recording is applicable only for android")
    @pytest.mark.notapplicable(Settings.is_devhost())
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.subtitle_and_closed_caption
    @pytest.mark.platform_cert_smoke_test
    # @pytest.mark.infobanner
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_disable_closed_captioning")
    def test_10197271_verify_cc_not_rendered_when_OFF(self):
        """
        :description:
            To verify subtitle/closed caption is not rendered on live tv when it is OFF
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197271
        :return:
        """
        self.home_page.back_to_home_short()
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.record_and_verify_cc(None, 20, Settings.log_path, "OFF", os_remove=False)

    @pytest.mark.ipppv
    @pytest.mark.xray("FRUM-840")
    @pytest.mark.timeout(Settings.timeout)
    def test_C5603462_verify_standard_info_banner_ppv_icon(self):
        """
        Verify that the ppv icon is displayed in the Live TV Standard Infobanner
        """
        ppv_rental_channel = self.guide_page.get_ppv_rental_channel(self)
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(ppv_rental_channel)
        self.watchvideo_assertions.verify_ppv_icon_present_info_banner()

    @pytest.mark.ipppv
    @pytest.mark.xray("FRUM-860")
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.msofocused
    @pytest.mark.timeout(Settings.timeout)
    def test_C11400109_verify_full_info_banner_ppv_icon(self):
        """
        Verify that the ppv icon is displayed in the Live TV - full Infobanner
        """
        ppv_rental_channel = self.guide_page.get_ppv_rental_channel(self)
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(ppv_rental_channel)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_ppv_icon_present_info_banner()

    @pytest.mark.ipppv
    @pytest.mark.timeout(Settings.timeout)
    def test_C11400344_verify_ppv_icon_in_program_screen(self):
        """
        Verify that the ppv icon is displayed in the program screen
        """
        channel_number_list = self.service_api.get_ppv_channel_list_current(Settings.tsn)
        if not channel_number_list:
            pytest.skip("Could not find any ppv channel")
        channel_number = channel_number_list[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.home_page.wait_for_screen_ready("GuideListModel")
        self.guide_page.select_and_get_more_info(self)
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_ppv_icon_present_program_screen()

    @pytest.mark.ipppv
    @pytest.mark.xray("FRUM-842")
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_C11402262_verify_blocked_ratings_ppv_livetv(self):
        """
        Verify that the parental control OSD is displayed on the PPV Live TV when the ratings are blocked
        """
        self.menu_page.go_to_parental_controls(self)
        self.menu_page.select_menu_items(self.menu_page.get_parental_controls_menu_item_label())
        self.menu_assertions.verify_create_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_assertions.verify_confirm_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_SET_RATING_LIMITS)
        self.menu_page.set_rating_limits(rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.menu_page.menu_press_back()
        channel_number_list = self.service_api.get_ppv_channel_list_current(Settings.tsn, filter_channel=True)
        if not channel_number_list:
            pytest.skip("Could not find any ppv channel")
        channel_number = channel_number_list[0][0]
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(channel_number)
        self.watchvideo_assertions.verify_livetv_mode()
        tvrating = self.watchvideo_page.check_current_program_has_tvrating(channel_number)
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=True, tvrating=tvrating)
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_PIN_challenge_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_livetv_mode()
        self.guide_assertions.ppv_overlay_confirm()

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout_mid)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_8880249_verify_playing_nDVR_recording_reboot_and_resume_playing(self):
        """
        :description:
            Verify playing a nDVR recording , rebooting the device,
            and then resume playing.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/8880249
        :return:
        """
        recording = self.api.schedule_single_recording()
        program_name = self.home_page.convert_special_chars(recording[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(program_name)
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(300)
        self.watchvideo_assertions.verify_playback_play()
        last_played_position = self.my_shows_page.get_trickplay_position(self)
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_home_title()
        self.home_page.back_to_home_short()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_PAUSED)
        self.my_shows_page.select_menu_by_substring(program_name)
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_assertions.verify_playback_play()
        resume_position = self.my_shows_page.get_trickplay_position(self)
        # below api should be revisited once got clarification
        self.watchvideo_assertions.verify_video_resumed_after_reboot(self, last_played_position, resume_position)

    # @pytestrail.case("C12792618")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    # @pytest.mark.notapplicable(not Settings.is_amino(), reason="Valid for amino only")
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-85")
    @pytest.mark.notapplicable(not Settings.is_amino(), reason="Valid for amino only")
    # @pytest.mark.test_stabilization
    def test_8880428_verify_watching_an_airing_live_show_and_press_pause_advance_buttons(self):
        """
        :description:
            Verify watching an airing live show, pressing Pause,
            and then pressing the Advance button multiple times until caught up to the live cache
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/tests/view/8880428
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_play_pause_button()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_page.watch_video_for(180)
        self.my_shows_page.validate_advance_move(self, current_position)
        self.my_shows_assertions.navigate_to_live_point_using_keys(self, key='advance', count=4)
        live_position = self.my_shows_page.get_trickplay_current_position_time(self)
        time_diff = self.my_shows_page.check_time_diff_min(live_position, current_position)
        self.my_shows_assertions.check_time_different(time_diff, 2, greater=True)

    @pytestrail.case("C12792621")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    def test_C10197202_verify_trickplay_menu_back_button_verification(self):
        """
        :description:
            Verify trickplay menu back button verification.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197202
        :return:
        """
        channel = self.service_api.get_random_live_channel_rich_info(filter_channel=True, exclude_jump_channels=True,
                                                                     transport_type="stream")
        if not channel:
            pytest.skip("Channel Not Found")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.navigate_to_start_of_video()
        self.guide_page.build_cache(180)
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.press_and_verify_back_on_trickplay()
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        # to verify pause mode
        self.guide_page.pause_show(self)
        self.watchvideo_assertions.press_and_verify_back_on_trickplay()
        self.guide_assertions.verify_pause()
        # to verify fast forward
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.guide_page.fast_forward_show(self, 3)
        self.watchvideo_assertions.press_and_verify_back_on_trickplay()
        self.guide_assertions.verify_play_normal()
        # to verify rewind mode
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.guide_page.rewind_show(self, 3)
        self.watchvideo_assertions.press_and_verify_back_on_trickplay()
        self.watchvideo_page.pause(5)
        self.guide_assertions.verify_play_normal()

    @pytestrail.case("C12792619")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    # @pytest.mark.test_stabilization
    def test_C10194980_verify_trickplay_menu_pressing_left_multiple_times(self):
        """
        :description:
            Verify trickplay menu by pressing left multiple times.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10194980
        :return:
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True,
                                                                        exclude_tplus_channels=True)
        if not channels:
            pytest.skip("Channels with no trickplay restriction found.")
        channel = channels[0]
        self.home_page.goto_live_tv(channel)
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_assertions.verify_playback_play()
        playpause_index = self.watchvideo_page.get_strip_focus_index_of_trickplay_icon(refresh=False)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.screen.base.press_left()
        self.watchvideo_assertions.is_rewind_focused(refresh=True)
        self.watchvideo_page.press_left_multiple_times(no_of_times=10)
        self.watchvideo_assertions.verify_mutiple_left_from_play_pause(self, playpause_index=playpause_index)

    @pytestrail.case("C12792620")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    # @pytest.mark.test_stabilization
    def test_C10194982_verify_trickplay_menu_pressing_right_multiple_times(self):
        """
        :description:
            Verify trickplay menu by pressing right multiple times.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10194982
        :return:
        """
        channels = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True,
                                                                                       entitled=True,
                                                                                       exclude_tplus_channels=True)
        if not channels:
            pytest.skip("Channels with no trickplay restriction found.")
        channel = channels[0]
        self.home_page.goto_live_tv()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.tune_to_channel(channel)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.build_cache(60)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.screen.base.press_right()
        self.watchvideo_assertions.is_forward_focused(refresh=True)
        self.watchvideo_page.press_right_multiple_times(no_of_times=10)
        self.watchvideo_assertions.is_guide_focused(refresh=True)

    @pytestrail.case("C12792624")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-92")
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_C10197301_verify_trickplay_menu_pressing_ok_button(self):
        """
        :description:
            Verify trickplay menu by pressing ok button.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197301
        :return:
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(
            recordable=True, filter_channel=True, filter_ndvr=True, is_preview_offer_needed=True)
        programs = self.api.record_currently_airing_shows(number_of_shows=1, includeChannelNumbers=channels,
                                                          is_preview_offer_needed=True, genre="series")
        if not programs:
            pytest.skip("No recordable shows found")
        program = programs[0][0]
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.guide_page.build_cache(15)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.guide_page.pause_show(self)
        self.guide_assertions.verify_pause()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.is_playpause_focused(refresh=False)
        self.guide_assertions.verify_pause()

    @pytestrail.case("C12792622")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    # @pytest.mark.test_stabilization
    def test_C10197211_verify_trickplay_menu_guide_button_selection(self):
        """
        :description:
            Verify trickplay menu by pressing left multiple times.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197211
        :return:
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        if not channel:
            pytest.skip("Channel Not Found")
        self.home_page.goto_live_tv(channel[0][0])
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_right_multiple_times(no_of_times=10)
        self.screen.refresh()
        self.watchvideo_assertions.verify_guide_button_selection(self, refresh=True)

    @pytestrail.case("C12792627")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    def test_C10197309_verify_trickplay_menu_pressing_info_button_on_myshows_recording(self):
        """
        :description:
            Verify trickplay menu by pressing info button.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197309
        :return:
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_ndvr=True)
        if not channel:
            pytest.skip("Test requires a recordable channel")
        check_rec = self.api.record_currently_airing_shows(1, includeChannelNumbers=channel[0][0])
        if len(check_rec) > 0:
            recording = self.my_shows_page.convert_special_chars(check_rec[0][0])
        else:
            pytest.skip("Recordings not available")
        self.home_page.wait_for_screen_ready()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(recording)
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_assertions.verify_playback_play()
        pause = self.watchvideo_page.index_position_of_icon(icon="Pause")
        info = self.watchvideo_page.index_position_of_icon(icon="Info")
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_right_multiple_times(no_of_times=(info - pause))
        self.watchvideo_assertions.verify_info_icon_selection(self)

    @pytestrail.case("C12792625")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_C10197302_verify_trickplay_menu_pressing_left_button_on_myshows_recording(self):
        """
        :description:
            Verify trickplay menu by pressing left button.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197302
        :return:
        """
        channel = self.service_api.get_random_channels_with_no_trickplay_restrictions(recordable=True,
                                                                                      filter_channel=True,
                                                                                      exclude_tplus_channels=True)
        if not channel:
            pytest.skip("No recordable channel without trickplay restrictions found.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel[0])
        recording = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_record_program(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(recording)
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.screen.base.press_left()
        self.watchvideo_assertions.is_rewind_focused(refresh=True)
        self.watchvideo_page.press_left_multiple_times(no_of_times=10)
        self.watchvideo_assertions.is_startover_focused(refresh=True)

    @pytestrail.case("C12792139")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.menu
    def test_11121891_navigate_closed_caption_verify_title(self):
        """
        :description:
            Verify screen title for Subtitles & Closed Caption in Accessibility.
        :testopia:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/11121891
        :return
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_MENU_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_MENU_SHORTCUT)
        self.menu_page.nav_to_top_of_list()
        self.menu_page.select_menu_items(self.menu_labels.LBL_ACCESSIBILITY)
        self.menu_page.select_menu_items(self.menu_labels.LBL_CLOSED_CAPTIONING)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_CLOSED_CAPTIONING_SCREENTITLE)

    @pytestrail.case("C12792138")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.menu
    @pytest.mark.platform_cert_smoke_test
    def test_11680803_language_audio_description_verify_title(self):
        """
        :description:
            Verify screen title for Language & Audio Description in Accessibility.
        :testopia:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/11680803
        :return
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_MENU_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_MENU_SHORTCUT)
        self.menu_page.nav_to_top_of_list()
        self.menu_page.select_menu_items(self.menu_labels.LBL_ACCESSIBILITY)
        self.menu_page.select_menu_items(self.menu_labels.LBL_LANGUAGE_AND_AUDIO_DESCRIPTION)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_LANGUAGE_AND_AUDIO_DESCRIPTION_SCREENTITLE)

    @pytestrail.case("C12792137")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.menu
    def test_11680802_subtitles_closed_caption_language_verify_title(self):
        """
        :description:
            Verify screen title for Subtitles & Closed Caption Language in Accessibility.
        :testopia:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/11680802
        :return
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_MENU_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_MENU_SHORTCUT)
        self.menu_page.nav_to_top_of_list()
        self.menu_page.select_menu_items(self.menu_labels.LBL_ACCESSIBILITY)
        self.menu_page.select_menu_items(self.menu_labels.LBL_SUBTITLE_CLOSED_CAPTION_LANGUAGE)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SUBTITLE_CLOSED_CAPTION_LANGUAGE_SCREENTITLE)

    # @pytest.mark.test_stabilization
    @pytest.mark.infobanner
    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    @pytest.mark.xray("FRUM-672")
    @pytest.mark.msofocused
    def test_10196841_change_Subtitle_CC_Language(self):
        """
               :description:
                   Verify the Change Subtitle & CC Overlay title in LiveTV info banner
               :testopia:
                   Test Case:https://testrail.tivo.com//index.php?/cases/view/10196841
               :return
               """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_full_info_banner_is_shown()
        self.watchvideo_page.select_strip(self.liveTv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_assertions.verify_overlay_shown()
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_CHANGE_SUBTITLE_CC_OVERLAY_TITLE)

    # @pytest.mark.test_stabilization
    @pytest.mark.ndvr
    @pytest.mark.xray("FRUM-822")
    @pytest.mark.msofocused
    @pytest.mark.socu
    @pytest.mark.longrun
    def test_9642947_verify_the_socu_trickyplay_modes(self):
        """
        :description:
            Watch Streaming Video - SOCU - Available TrickPlay Modes - TrickPlay Enabled
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/9642947
        :return:
        """
        self.home_page.back_to_home_short()
        channel_number = self.guide_page.get_trickplay_non_restricted_socu_channel(self, filter_channel=True)[0]
        self.home_page.select_menu_shortcut(self.home_labels.LBL_GUIDE_SHORTCUT)
        self.guide_page.enter_channel_number(channel_number)
        if not Settings.is_altafiber():
            self.menu_page.menu_navigate_left_right(4, 0)
        self.guide_page.wait_for_guide_next_page()
        focused_item = self.guide_page.get_focussed_grid_item(self)
        if Settings.is_altafiber():
            self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        else:
            self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.guide_page.playback_and_verify_trickplay_action(self, forward=True, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, forward=True, speed=2, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, forward=True, speed=3, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, pause=True, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, rewind=True, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, rewind=True, speed=2, socu=False)
        self.guide_page.playback_and_verify_trickplay_action(self, rewind=True, speed=3, socu=False)
        if Settings.is_advance_available():
            self.guide_page.pause_show(self)
            current_position = self.my_shows_page.get_trickplay_current_position_time(self)
            self.my_shows_page.validate_advance_move(self, current_position)
            self.screen.base.press_rewind()
            self.guide_assertions.verify_rewind(1)
            self.screen.base.press_advance()
            self.guide_assertions.verify_play_normal()
            self.watchvideo_page.show_trickplay_if_not_visible()
            previous_position = self.my_shows_page.get_trickplay_current_position_time(self)
            self.watchvideo_page.navigate_to_start_of_video()
            self.screen.base.press_fast_forward()
            self.screen.base.press_advance()
            self.watchvideo_page.show_trickplay_if_not_visible()
            current_position = self.my_shows_page.get_trickplay_current_position_time(self)
            self.my_shows_assertions.validate_trickplay_tickmark_position(previous_position, current_position, advance=True)
        if Settings.is_replay_available():
            current_position = self.my_shows_page.get_trickplay_current_position_time(self)
            self.my_shows_page.validate_replay(self, current_position)
            self.screen.base.press_fast_forward()
            self.guide_assertions.verify_fast_forward(1)
            self.screen.base.press_replay()
            self.guide_assertions.verify_play_normal()
            self.watchvideo_page.show_trickplay_if_not_visible()
            previous_position = self.my_shows_page.get_trickplay_current_position_time(self)
            self.screen.base.press_rewind()
            self.screen.base.press_replay()
            self.watchvideo_page.show_trickplay_if_not_visible()
            current_position = self.my_shows_page.get_trickplay_current_position_time(self)
            self.my_shows_assertions.validate_trickplay_tickmark_position(previous_position, current_position, replay=True)

    @pytestrail.case("C12792626")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_C10197303_verify_trickplay_menu_pressing_right_button_on_myshows_recording(self):
        """
        :description:
            Verify trickplay menu by pressing right button.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197303
        :return:
        """
        recording = self.api.schedule_single_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(recording[0][0])
        self.my_shows_page.select_menu_by_substring(self.my_shows_page.convert_special_chars(recording[0][0]))
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.screen.base.press_right()
        self.watchvideo_assertions.is_forward_focused(refresh=True)
        self.watchvideo_page.press_right_multiple_times(no_of_times=10)
        self.watchvideo_assertions.is_guide_focused(refresh=True)

    @pytestrail.case("C12792623")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    def test_C10197284_verify_trickplay_menu_timeout_verification(self):
        """
        :description:
            Verify trickplay menu timeout verification.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197284
        :return:
        """
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True,
                                                                       exclude_tplus_channels=True)[0]
        if channel is None:
            pytest.skip("Could not find any live channel")
        self.home_page.back_to_home_short()
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        # to verify trickplay dismisses within expected timeout of 6 seconds
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.guide_assertions.verify_play_normal()
        # to verify pause mode
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.guide_page.pause_show(self)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.guide_assertions.verify_pause()
        # to verify fast forward
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.guide_page.fast_forward_show(self, 3)
        self.watchvideo_assertions.press_and_verify_back_on_trickplay()
        self.guide_assertions.verify_play_normal()
        # to verify rewind mode
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.guide_page.rewind_show(self, 3)
        self.watchvideo_assertions.press_and_verify_back_on_trickplay()
        self.watchvideo_page.pause(5)
        self.guide_assertions.verify_play_normal()

    @pytestrail.case("C12792633")
    @pytest.mark.p1_regression
    @pytest.mark.p1_reg_stability
    @pytest.mark.iplinear
    # @pytest.mark.test_stabilization
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10839951_favorites_panel_press_and_hold_ok(self):
        """
        Verify Channel Options overlay
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.screen.base.long_press_enter()
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_CHANNEL_OPTIONS)

    # @pytest.mark.test_stabilization
    @pytest.mark.favoritepanel
    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10839955_remove_favorite_channels(self):
        """
        Favorites Panel - Channel Options overlay - Remove from Favorite Channels
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self, count=5)
        self.home_page.back_to_home_short()
        channel_number = self.api.get_random_encrypted_unencrypted_channels(transportType="stream",
                                                                            filter_channel=True)[0][0]
        if not channel_number:
            pytest.skip("Recordable Channel Not Found")
        self.home_page.goto_live_tv(channel_number)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.remove_favorite_channels_from_favorite_panel(self, 5)
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()

    @pytestrail.case("C12792628")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    # @pytest.mark.test_stabilization
    def test_C10197310_verify_trickplay_menu_guide_button_selection_from_my_shows_recording(self):
        """
        :description:
            VOD - TrickPlay Menu - select Guide and verify one line guide.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197310
        :return:
        """
        recording = self.api.schedule_single_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(self.my_shows_page.convert_special_chars(recording[0][0]))
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_assertions.verify_playback_play()
        pause = self.watchvideo_page.index_position_of_icon(icon="Pause")
        guide = self.watchvideo_page.index_position_of_icon(icon="Guide")
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_right_multiple_times(no_of_times=(guide - pause))
        self.watchvideo_assertions.verify_guide_button_selection(self, refresh=True)

    @pytest.mark.p1_regression
    @pytest.mark.favoritepanel
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10195361_favorites_panel_press_back(self):
        """
        Verify pressing back functionality in favorites panel
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        self.home_page.back_to_home_short()
        channel_number = self.api.get_random_encrypted_unencrypted_channels(transportType="stream",
                                                                            filter_channel=True)[0][0]
        if not channel_number:
            pytest.skip("Recordable Channel Not Found")
        self.home_page.back_to_home_short()
        self.home_page.select_menu_shortcut(self.home_labels.LBL_GUIDE_SHORTCUT)
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.screen.base.press_back()
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.guide_page.pause_show(self)
        self.guide_assertions.verify_pause()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.screen.base.press_back()
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()
        self.guide_assertions.verify_pause()

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.socu
    def test_C10197345_verify_trickplay_menu_info_icon_selection_from_socu_playback(self):
        """
        :description
            SOCU - TrickPlay Menu - select Info
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197345
        :return:
        """
        channel = self.guide_page.get_trickplay_non_restricted_socu_channel(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.screen.base.press_enter()
        # Navigate to start of the video to enable advance.
        self.watchvideo_page.navigate_to_start_of_video()
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_page.pause(10)
        self.guide_assertions.verify_play_normal()
        pause = self.watchvideo_page.index_position_of_icon(icon="Pause")
        info_icon = self.watchvideo_page.index_position_of_icon(icon="Info")
        self.watchvideo_page.show_trickplay_if_not_visible()
        # live point Icon will be disable if its in livetv
        if pause is None or info_icon is None:
            raise AssertionError("Info icon or pause is not there in trickplaybar or it is disabled")
        self.watchvideo_page.press_right_multiple_times(no_of_times=(info_icon - pause))
        self.watchvideo_assertions.verify_info_icon_selection(self)

    @pytestrail.case("C12792631")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.socu
    def test_C10197346_verify_trickplay_menu_guide_button_selection_from_socu_playback(self):
        """
        :description:
            SOCU - TrickPlay Menu - select Guide
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197346
        :return:
        """
        channel = self.api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                   filter_socu=True,
                                                                   restrict=False)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        pause = self.watchvideo_page.index_position_of_icon(icon="Pause")
        guide = self.watchvideo_page.index_position_of_icon(icon="Guide")
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_right_multiple_times(no_of_times=(guide - pause))
        self.watchvideo_assertions.verify_guide_button_selection(self, refresh=True)

    @pytestrail.case("C12792629")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.socu
    @pytest.mark.iplinear
    def test_10197338_verify_trickplay_rewind_icon_is_focused(self):
        """
        :description:
            SOCU - TrickPlay Menu - Invoke by press LEFT
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197338
        :return:
        """
        channel = self.api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                   filter_socu=True, restrict=False)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.screen.base.press_left()
        self.watchvideo_assertions.is_rewind_focused(refresh=True)
        pause = self.watchvideo_page.index_position_of_icon(icon="Pause")
        start_over = self.watchvideo_page.index_position_of_icon(icon="Start Over")
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_left_multiple_times(no_of_times=(pause - start_over))
        self.watchvideo_assertions.is_startover_focused(refresh=True)

    @pytest.mark.p1_regression
    @pytest.mark.socu
    def test_10197337_verify_trickplay_playpause_icon_is_focused(self):
        """
        :description:
            SOCU - TrickPlay Menu - Invoke by press OK
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197337
        :return:
        """
        channel = self.api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                   filter_socu=True, restrict=False)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0][0])
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(channel_number)
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.is_playpause_focused(value="Pause", refresh=True)
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.guide_page.pause_show(self)
        self.guide_assertions.verify_pause()
        self.watchvideo_page.press_clear_button()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.guide_assertions.verify_pause()

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.socu
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10839954_press_ok_on_action_on_channel_options_overlay(self):
        """
        Favorites Panel - Channel Options overlay - Watch Now / Launch app
        """
        channel = self.api.get_random_live_channel_rich_info(episodic=True,
                                                             movie=False, entitled=True, filter_channel=True,
                                                             exclude_jump_channels=True)
        if channel is None:
            pytest.fail("Could not find any episodic channel")
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.go_to_favorite_channels()
        self.guide_page.enter_channel_number(channel[0][0])
        self.home_page.wait_for_screen_ready()
        self.menu_page.add_channel_to_favorites()
        self.home_page.back_to_home_short()
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.screen.base.long_press_enter()
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_CHANNEL_OPTIONS)
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_number(channel[0][0])

    # @pytest.mark.test_stabilization
    @pytest.mark.favoritepanel
    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10195404_verify_favorite_panel_timeout(self):
        """
        Favorites Panel - Timeout
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        self.home_page.back_to_home_short()
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        # Verify Favorite Strip is visible
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        # Added 15 secs wait time for Favorite Strip to get dismissed
        time.sleep(15)
        # Verify Favorite Strip is dismissed after timeout
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()

    @pytestrail.case("C12792630")
    # @pytest.mark.test_stabilization
    @pytest.mark.infobanner
    # @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.socu
    def test_10197339_verify_trickplay_forward_icon_is_focused(self):
        """
        :description:
            SOCU - TrickPlay Menu - Invoke by press RIGHT
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197339
        :return:
        """
        channel = self.guide_page.get_trickplay_non_restricted_socu_channel(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_right_button(refresh=False)
        self.watchvideo_assertions.is_forward_focused(refresh=True)

    @pytest.mark.favoritepanel
    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10195355_favorites_panel_press_ok_selection_for_live_tv(self):
        """
        Verify press ok functionality in favorites panel
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        if channel is None:
            pytest.skip("Channel Not Found")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.get_live_program_name(self)
        self.guide_page.remove_channel_from_favorites(self, channel[0][0])
        self.guide_page.add_channel_to_favorites(channel[0][0])
        self.home_page.back_to_home_short()
        self.home_page.select_menu_shortcut(self.home_labels.LBL_GUIDE_SHORTCUT)
        self.watchvideo_page.enter_channel_number(channel[0][0], confirm=True)
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_page.find_channel_on_favorite_panel(channel[0][0])
        self.watchvideo_page.press_ok_button(refresh=False)
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.verify_standard_info_banner_shown()
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()

    @pytest.mark.p1_regression
    @pytest.mark.socu
    @pytest.mark.favoritepanel
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10195355_favorites_panel_press_ok_selection_socu_channel(self):
        """
        Verify press ok functionality in favorites panel for socu channel
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel = self.api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                   filter_socu=True, restrict=False)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.get_live_program_name(self)
        self.guide_page.remove_channel_from_favorites(self, channel_number)
        self.guide_page.add_channel_to_favorites(channel_number)
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.verify_standard_info_banner_shown()
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()

    # @pytest.mark.test_stabilization
    @pytest.mark.favoritepanel
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10195355_favorites_panel_press_ok_selection_my_shows_recording(self):
        """
        Verify press ok functionality in favorites panel for my shows recording
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        if channel is None:
            pytest.skip("Channel Not Found")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.remove_channel_from_favorites(self, channel[0][0])
        self.guide_page.add_channel_to_favorites(channel[0][0])
        recording = self.api.schedule_single_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(recording[0][0])
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.verify_standard_info_banner_shown()
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()

    @pytestrail.case("C12792634")
    # @pytest.mark.test_stabilization
    @pytest.mark.ndvr
    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_11683500_verify_live_streaming_after_recording_playback(self):
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True, is_preview_offer_needed=True)
        if not channel:
            pytest.skip("No recordable streaming channel found.")
        self.home_page.goto_live_tv(channel)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        program = self.api.record_currently_airing_shows(number_of_shows=1, genre="series", use_cached_grid_row=True)
        if not program:
            pytest.skip("No recordable shows found")
        self.menu_page.go_to_to_do_list(self)
        self.guide_assertions.verify_show_name_present(program[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program[0][0])
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        channel = self.api.get_random_live_channel_rich_info(episodic=True, live=False, filter_channel=True,
                                                             use_cached_grid_row=True)
        if not channel:
            pytest.skip("Channel Not Found")
        self.home_page.goto_live_tv()
        self.watchvideo_assertions.verify_livetv_mode()
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.enter_channel_number(channel[0][0], confirm=True)
        self.watchvideo_assertions.verify_livetv_mode()
        self.guide_assertions.verify_play_normal()

    @pytest.mark.favoritepanel
    @pytest.mark.xray("FRUM-32971")
    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10195355_favorites_panel_press_ok_selection_for_live_tv_jump_channel(self):
        """
        Verify press ok functionality for jump channel in favorites panel
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel_num = list(self.api.get_jump_channels_list().keys())[0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.remove_channel_from_favorites(self, channel_num)
        self.guide_page.add_channel_to_favorites(channel_num)
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                            transportType="stream")[0][0]
        if not channel_number:
            pytest.skip("Recordable Channel Not Found")
        self.home_page.back_to_home_short()
        self.home_page.select_menu_shortcut(self.home_labels.LBL_GUIDE_SHORTCUT)
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_page.find_channel_on_favorite_panel(channel_num)
        jump_layer_shown = self.watchvideo_assertions.verification_of_jump_channel_overlay()
        if jump_layer_shown:
            self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_LAUNCH_APP)
            self.home_page.wait_for_screen_ready()
            self.guide_assertions.verify_jump_channel_launch()
        if self.screen.get_screen_dump_item('viewMode') == self.liveTv_labels.LBL_LIVETV_VIEWMODE:
            self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
            self.watchvideo_assertions.verify_playback_play()
        if self.screen.get_screen_dump_item('viewMode') == self.vod_labels.LBL_BIAXIAL_SCREEN_VIEW_MODE:
            self.vod_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)

    # @pytest.mark.test_stabilization
    @pytest.mark.favoritepanel
    @pytest.mark.socu
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    @pytest.mark.p1_regression
    def test_10195355_favorites_panel_press_ok_selection_socu_channel_jump_channel(self):
        """
        Verify press ok functionality in favorites panel for socu channel
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel_num = list(self.api.get_jump_channels_list().keys())[0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.remove_channel_from_favorites(self, channel_num)
        self.guide_page.add_channel_to_favorites(channel_num)
        channel = self.api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                   filter_socu=True, restrict=False)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_page.find_channel_on_favorite_panel(channel_num)
        jump_layer_shown = self.watchvideo_assertions.verification_of_jump_channel_overlay()
        if jump_layer_shown:
            self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_LAUNCH_APP)
            self.home_page.wait_for_screen_ready()
            self.guide_assertions.verify_jump_channel_launch()
        self.screen.refresh()
        current_view = self.screen.get_screen_dump_item('viewMode')
        if current_view == self.liveTv_labels.LBL_LIVETV_VIEWMODE:
            self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
            self.watchvideo_assertions.verify_playback_play()
        elif current_view == self.vod_labels.LBL_BIAXIAL_SCREEN_VIEW_MODE:
            self.vod_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)

    @pytest.mark.favoritepanel
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_10195355_favorites_panel_press_ok_selection_for_jump_channel_my_shows_recording(self):
        """
        Verify press ok functionality in favorites panel for jump channel in my shows recording
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel_num = list(self.api.get_jump_channels_list().keys())[0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.remove_channel_from_favorites(self, channel_num)
        self.guide_page.add_channel_to_favorites(channel_num)
        recording = self.api.schedule_single_recording()
        self.home_page.log.step("recording variable has {}".format(recording))
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(recording[0][0])
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_page.press_ok_button(refresh=False)
        jump_layer_shown = self.watchvideo_assertions.verification_of_jump_channel_overlay()
        if jump_layer_shown:
            self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_LAUNCH_APP)
            self.home_page.wait_for_screen_ready()
            self.guide_assertions.verify_jump_channel_launch()
        self.screen.refresh()
        current_view = self.screen.get_screen_dump_item('viewMode')
        if current_view == self.liveTv_labels.LBL_LIVETV_VIEWMODE:
            self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
            self.watchvideo_assertions.verify_playback_play()
        elif current_view == self.vod_labels.LBL_BIAXIAL_SCREEN_VIEW_MODE:
            self.vod_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)

    @pytest.mark.p1_regression
    @pytest.mark.favoritepanel
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10839958_adult_content_constraint_verification(self):
        """
        Favorites Panel - Adult content
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.watchvideo_page.set_favorite_channels(self, count=2, adult=True)
        self.menu_page.go_to_parental_controls(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.enter_default_parental_control_password(self)  # to confirm
        self.menu_page.toggle_hide_adult_content()
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        if not channel:
            pytest.skip("Recordable Channel Not Found")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_assertions.verify_adult_content_is_hidden(self)
        self.screen.base.press_enter()  # Tuning to the adult channel
        self.watchvideo_assertions.verify_adult_show_locked_osd()

    @pytestrail.case("C12792136")
    @pytest.mark.p1_regression
    @pytest.mark.menu
    def test_11687643_To_verify_screen_title_Closed_Caption_Preference(self):
        """
        :description:
            Verify screen title for Closed Caption Preference in Accessibility.
        :testopia:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/11687643
        :return
        """
        self.menu_page.go_to_menu_screen(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_ACCESSIBILITY)
        self.menu_page.select_menu_items(self.menu_labels.LBL_CLOSED_CAPTION_PREFERENCES)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_CLOSED_CAPTION_PREFERENCES_SCREENTITLE)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    def test_11683498_verify_livetv_homebackground_streaming_after_reboot(self):
        self.menu_page.enable_full_screen_video_on_home(self)
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(channel, highlight_live_program=False)
        self.watchvideo_assertions.verify_livetv_mode()
        self.guide_assertions.verify_play_normal()
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_assertions.verify_home_title()
        self.home_page.back_to_home_short()
        self.vod_assertions.verify_video_streaming()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Valid for managed devices only")
    def test_10200192_validate_pause_button_behavior(self):
        """
        testopia: https://testrail.tivo.com//index.php?/cases/view/10200192
        """
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True,
                                                                       exclude_tplus_channels=True)[0]
        if channel is None:
            pytest.fail("Could not find any live channel")
        self.home_page.back_to_home_short()
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_playback_play()
        self.vod_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.watch_video_for(60 * 10)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.pause(2)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)
        self.watchvideo_page.press_rewind()
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.pause(2)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)
        self.watchvideo_page.press_ff()
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.pause(2)
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytest.mark.e2e
    # @pytest.mark.test_stabilization
    def test_9643005_verify_jump_channel_overlay_is_dismissed_using_back_button(self):
        """
        Verify behavior for BACK button in "Leaving Live TV" overlay.
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        jump_channel_number = self.api.get_channel_with_jump_channel_near(jump_channel_near=True, nextprev='next')[0]
        self.watchvideo_page.enter_channel_number(jump_channel_number)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_page.press_back_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_not_shown()
        self.watchvideo_assertions.verify_channel_number(jump_channel_number)

    @pytest.mark.e2e
    @pytest.mark.skipif(not Settings.is_amino(), reason="Valid for amino only")
    def test_9643005_verify_jump_channel_overlay_is_dismissed_using_clear_button(self):
        """
        Verify behavior for Clear button in "Leaving Live TV" overlay.
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        jump_channel_number = self.api.get_channel_with_jump_channel_near(jump_channel_near=True, nextprev='next')[0]
        self.watchvideo_page.enter_channel_number(jump_channel_number)
        self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_not_shown()

    #  @pytest.mark.p1_regression
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Valid for managed devices only")
    @pytest.mark.socu
    def test_10200218_validate_stop_button_behavior_pig_enabled(self):
        """
        testopia: https://testrail.tivo.com//index.php?/cases/view/10200218
        """
        channels = self.api.get_random_encrypted_unencrypted_channels(Settings.tsn, socu=True,
                                                                      encrypted=True, filter_channel=True)
        channel = (channels[0][0])
        if channel is None:
            pytest.fail("Could not find any live channel")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.startover_current_show_from_livetv_screen()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_VOD_VIEWMODE)
        self.home_page.back_to_home_short()
        self.watchvideo_page.press_stop_button()
        self.watchvideo_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.socu
    @pytest.mark.usefixtures("disable_video_window")
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Valid for managed devices only")
    def test_10200218_validate_stop_button_behavior_pig_disabled(self):
        """
        testopia: https://testrail.tivo.com//index.php?/cases/view/10200218
        """
        channels = self.api.get_random_encrypted_unencrypted_channels(Settings.tsn, socu=True,
                                                                      encrypted=True, filter_channel=True)
        channel = (channels[0][0])
        if channel is None:
            pytest.fail("Could not find any live channel")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.startover_program_from_livetv_with_socu(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_VOD_VIEWMODE)
        self.home_page.back_to_home_short()
        self.watchvideo_page.press_stop_button()
        self.watchvideo_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)

    @pytest.mark.demo
    def test_123456_throttle_internet_speed(self):
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.restrict_bandwidth()
        self.watchvideo_page.pause(23)  # approximate buffer size
        self.watchvideo_assertions.verify_osd_text(self.watchvideo_labels.LBL_LOADING_VIDEO_OSD)
        self.watchvideo_page.relax_bandwidth_restrictions()

    @pytest.mark.demo
    def test_1234567_limit_download_speed_with_ip(self):
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.set_download_limit_with_ip("mm1.st.tivoservice.com")
        self.watchvideo_page.pause(60)
        self.watchvideo_page.relax_bandwidth_restrictions()

    @pytest.mark.demo
    def test_1234567_update_yukon_url(self):
        """Example of Yukon API usage"""
        url = self.home_page.get_yukon_url(purpose="1.5_throttling",
                                           asset="asset3")
        self.home_page.set_playback_source(url)  # add url to default file - play url
        self.home_page.set_playback_source()  # empty url remove url from default place - play url

    # @pytest.mark.test_stabilization
    @pytest.mark.hospitality
    @pytest.mark.usefixtures("setup_cleanup_bind_hsn")
    @pytest.mark.notapplicable(not Settings.is_technicolor() and not Settings.is_jade() and not Settings.is_jade_hotwire(),
                               "This test is applicable only for Technicolor boxes")
    @pytest.mark.notapplicable(not ExecutionContext.service_api.get_feature_status(FeaturesList.HOSPITALITY),
                               "This test is applicable only for accounts with Hospitality Mode = ON")
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_5413625_hospitality_device_clear_favorite_channel(self):
        """
        Verify TiVo Service settings are cleared after device clearing and login into Hospitality Welcome Screen
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channels = self.api.get_random_live_channel_rich_info(episodic=True, movie=False, live=False,
                                                              channel_count=4, filter_channel=True)
        if channels is None:
            pytest.fail("Could not find the required number of channels")
        self.home_page.go_to_guide(self)
        for channel in channels:
            self.guide_page.add_channel_to_favorites(channel[0])
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.go_to_favorite_channels()
        for channel in channels:
            self.guide_page.enter_channel_number(channel[0])
            self.watchvideo_assertions.verify_checkbox_status(self, channel=channel[0])
        # HSN binding right after device clearing due to https://jira.xperi.com/browse/CA-20547
        self.iptv_prov_api.device_clear(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn))
        self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                    self.service_api.getPartnerCustomerId(Settings.tsn))
        self.menu_page.reconnect_dut_after_reboot(180)
        self.apps_and_games_assertions.select_continue_wait_for_home_screen_to_load(self, is_hospitality_screen_omitted=True)
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.go_to_favorite_channels()
        for channel in channels:
            self.guide_page.enter_channel_number(channel[0])
            self.watchvideo_assertions.verify_checkbox_status(self, channel=channel[0], status=False)

    @pytest.mark.tivo_plus
    @pytest.mark.frumos_11
    @pytest.mark.usefixtures('setup_cleanup_tivo_plus_channels_first_launch')
    @pytest.mark.notapplicable(
        not Settings.is_cc11() and Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
        reason="This test is applicable only for CC11 MSO and builds streamer-1-11 or later.")
    @pytest.mark.xray("FRUM-32933")
    @pytest.mark.msofocused_solutions
    def test_12786358_tivo_plus_terms_of_use_acceptance_overlay(self):
        """
        To verify first launch of TiVo+ channel and Accept User Agreement & Policy
        testrail: https://testrail.tivo.com/index.php?/cases/view/12786358
        """
        self.home_page.go_to_guide(self)
        channel = self.api.get_tivo_plus_channels()[0]
        self.guide_page.enter_channel_number(channel, confirm=True)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.press_ok_button(refresh=False)
        self.guide_page.wait_for_screen_ready("TiVoPlusAcceptanceOverlay")
        self.watchvideo_assertions.verify_tivo_plus_eula_overlay_is_shown(refresh=True)
        self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_CANCEL)
        self.watchvideo_assertions.verify_tivo_plus_eula_overlay_is_not_shown()
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_tivo_plus_eula_overlay_is_shown()
        self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_VIEW_USER_AGREEMENT)
        self.watchvideo_assertions.verify_screen_title(self.liveTv_labels.LBL_TIVO_PLUS_USER_AGREEMENT_SCREENTITLE)
        self.watchvideo_page.press_back_button(refresh=True)
        self.watchvideo_assertions.verify_tivo_plus_eula_overlay_is_shown()
        self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_VIEW_PRIVACY_POLICY)
        self.watchvideo_assertions.verify_screen_title(self.liveTv_labels.LBL_TIVO_PLUS_PRIVACY_POLICY_SCREENTITLE)
        self.watchvideo_page.press_back_button(refresh=True)
        self.watchvideo_assertions.verify_tivo_plus_eula_overlay_is_shown()
        self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_ACCEPT)
        self.watchvideo_assertions.verify_tivo_plus_eula_osd_is_not_shown()
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_assertions.verify_channel_number(channel)

    @pytest.mark.tivo_plus
    @pytest.mark.frumos_11
    @pytest.mark.usefixtures('setup_cleanup_tivo_plus_channels')
    @pytest.mark.notapplicable(
        not Settings.is_cc11() and Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
        reason="This test is applicable only for CC11 MSO and builds streamer-1-11 or later.")
    def test_11678248_tivo_plus_play_xumo_partner_channel(self):
        """
        To verify that channel from Revry partner is playing
        testrail: https://testrail.tivo.com/index.php?/cases/view/11678248
        """
        self.home_page.go_to_guide(self)
        channel = self.api.get_tivo_plus_channels(partner='xumo')[0]
        self.guide_page.tune_to_tivo_plus_channel(self, channel)
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(channel)

    @pytest.mark.tivo_plus
    @pytest.mark.frumos_11
    @pytest.mark.usefixtures('setup_cleanup_tivo_plus_channels')
    @pytest.mark.notapplicable(
        not Settings.is_cc11() and Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
        reason="This test is applicable only for CC11 MSO and builds streamer-1-11 or later.")
    def test_11678249_tivo_plus_play_revry_partner_channel(self):
        """
        To verify that channel from Revry partner is playing
        testrail: https://testrail.tivo.com/index.php?/cases/view/11678249
        """
        self.home_page.go_to_guide(self)
        channel = self.api.get_tivo_plus_channels(partner='revry')[0]
        self.guide_page.tune_to_tivo_plus_channel(self, channel)
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(channel)

    @pytest.mark.tivo_plus
    @pytest.mark.frumos_11
    @pytest.mark.usefixtures('setup_cleanup_tivo_plus_channels')
    @pytest.mark.notapplicable(
        not Settings.is_cc11() and Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
        reason="This test is applicable only for CC11 MSO and builds streamer-1-11 or later.")
    def test_11678250_tivo_plus_play_tastemade_partner_channel(self):
        """
        To verify that channel from Tastemade partner is playing
        testrail:  https://testrail.tivo.com/index.php?/cases/view/11678250
        """
        self.home_page.go_to_guide(self)
        channel = self.api.get_tivo_plus_channels(partner='tastemade')[0]
        self.guide_page.tune_to_tivo_plus_channel(self, channel)
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(channel)

    @pytest.mark.tivo_plus
    @pytest.mark.frumos_11
    @pytest.mark.usefixtures('setup_cleanup_tivo_plus_channels')
    @pytest.mark.notapplicable(
        not Settings.is_cc11() and Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
        reason="This test is applicable only for CC11 MSO and builds streamer-1-11 or later.")
    def test_11678251_tivo_plus_play_loop_partner_channel(self):
        """
        To verify that channel from Loop partner is playing
        testrail: https://testrail.tivo.com/index.php?/cases/view/11678251
        """
        self.home_page.go_to_guide(self)
        channel = self.api.get_tivo_plus_channels(partner='loop')[0]
        self.guide_page.tune_to_tivo_plus_channel(self, channel)
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_page.watch_video_for(180)
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(channel)

    #  @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.frumos_11
    @pytest.mark.socu
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.notapplicable(not Settings.is_arris() or not Settings.is_puck(),
                               reason="This test is applicable only for Arris and Puck devices")
    def test_12777388_verify_yellow_color_button_starts_socu_from_live_tv(self):
        """
        To verify that color button A(yellow) starts SOCU from Live TV
        testrail: https://testrail.tivo.com/index.php?/cases/view/12777388
        """
        channel = self.api.get_random_catch_up_channel_current_air(filter_channel=True,
                                                                   filter_socu=True,
                                                                   restrict=False)
        if channel is None:
            pytest.fail("No channel found")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.startover_program_from_livetv_with_color_button_a()
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)

    @pytest.mark.frumos_11
    @pytest.mark.p1_regression
    @pytest.mark.socu
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="This test is applicable only for managed devices")
    def test_108405148_verify_exit_button_exits_to_live_tv_from_socu(self):
        """
        To verify that EXIT button exits from SOCU to Live TV
        testrail: https://testrail.tivo.com//index.php?/cases/view/10840518
        """
        channel = self.api.get_random_catch_up_channel_current_air(filter_channel=True,
                                                                   filter_socu=True,
                                                                   restrict=False)
        if not channel:
            pytest.skip("No available SOCU programs haven't been found.")
        channel_number = channel[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.watchvideo_assertions.verify_vod_mode()
        self.watchvideo_page.press_exit_button()
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_page.wait_for_infobanner(status="dismissed")
        self.watchvideo_assertions.verify_livetv_mode()

    @pytest.mark.p1_regression
    @pytest.mark.frumos_11
    @pytest.mark.iplinear
    @pytest.mark.socu
    @pytest.mark.notapplicable(
        not Settings.is_managed() or Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-11"))
    def test_299593267_verify_channel_down_button_exits_socu(self):
        """
        To verify that CHDOWN button exits from SOCU to Live TV
        testrail: https://testrail.tivo.com//index.php?/cases/view/299593267
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(Settings.tsn, socu=True, encrypted=True,
                                                                     filter_channel=True)
        if not channel:
            pytest.skip("No available SOCU programs haven't been found.")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.watchvideo_assertions.press_channel_button_and_verify_channel_change('channel down')
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_assertions.press_channel_button_and_verify_channel_change('channel down')

    @pytest.mark.p1_regression
    @pytest.mark.frumos_11
    @pytest.mark.iplinear
    @pytest.mark.socu
    @pytest.mark.notapplicable(
        not Settings.is_managed() or Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-11"))
    def test_299593267_verify_channel_up_button_exits_socu(self):
        """
        To verify that CHUP button exits from SOCU to Live TV
        testrail: https://testrail.tivo.com//index.php?/cases/view/299593267
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(Settings.tsn, socu=True, encrypted=True,
                                                                     filter_channel=True)
        if not channel:
            pytest.skip("No available SOCU programs haven't been found.")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.watchvideo_assertions.press_channel_button_and_verify_channel_change('channel up')
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_assertions.press_channel_button_and_verify_channel_change('channel up')

    @pytest.mark.frumos_11
    @pytest.mark.p1_regression
    @pytest.mark.socu
    def test_299593262_verify_go_to_livetv_trickplay_menu_button_exits_socu(self):
        """
        :description:
            VOD - TrickPlay Menu - select Live TV.
        :testrail: https://testrail.tivo.com//index.php?/cases/view/299593262
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                           filter_socu=True, restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = channel[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=True)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.watchvideo_assertions.verify_vod_mode()
        self.watchvideo_page.watch_video_for(10)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_page.press_pause_in_visual_trickplay(refresh=True)
        play = self.watchvideo_page.index_position_of_icon(icon="Play")
        livetv = self.watchvideo_page.index_position_of_icon(icon="Go to Live TV")
        self.watchvideo_page.press_right_multiple_times(no_of_times=(livetv - play))
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_livetv_mode()

    @pytest.mark.frumos_11
    @pytest.mark.skipif(not Settings.is_cc3(), reason="Audio only feature is supported only on cc3 MSO")
    @pytest.mark.infobanner
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_12782677_change_audio_track_of_audioonly_channel_from_info_banner(self):
        """
         :description:
         To Verify change audio track overlay for audio only channel
         :testrail: https://testrail.tivo.com//index.php?/cases/view/12782677
         Only one audio only channel in headend and there is no multiple audio track available.
         So we can only check change audio track option on info banner
         """
        audio_only_channel = self.service_api.get_random_audioonly_channel()
        if audio_only_channel:
            self.home_page.goto_live_tv(audio_only_channel[0])
            self.watchvideo_page.show_info_banner()
            self.watchvideo_assertions.verify_full_info_banner_is_shown()
            self.watchvideo_page.select_strip(self.liveTv_labels.LBL_CHANGE_AUDIO_TRACK)
            self.watchvideo_assertions.verify_overlay_shown()
            self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_AUDIO_TRACK_OVERLAY_TITLE)
        else:
            pytest.skip("No Audio only channel Available")

    @pytest.mark.frumos_11
    @pytest.mark.skipif(not Settings.is_cc3(), reason="Audio only feature is supported only on cc3 MSO")
    @pytest.mark.infobanner
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_12782655_info_banner_of_audio_only_channel(self):
        """
         :description:
         To Verify info banner for audio only channel
         :testrail:  https://testrail.tivo.com//index.php?/cases/view/12782655
         """
        audio_only_channel = self.service_api.get_random_audioonly_channel()
        if audio_only_channel:
            self.home_page.goto_live_tv(audio_only_channel[0])
            self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
            self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
            self.watchvideo_page.show_info_banner()
            self.watchvideo_assertions.verify_full_info_banner_is_shown()
        else:
            pytest.skip("No Audio only channel Available")

    @pytest.mark.frumos_11
    @pytest.mark.audioonly
    @pytest.mark.notapplicable(not Settings.is_cc3(), "Audio only feature is supported only on cc3 and Telus MSO")
    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.xray("FRUM-978")
    @pytest.mark.msofocused
    def test_12782657_verify_audio_only_trickplay_restrictions_pause(self):
        """
        To verify Pause restriction message for audio only channel

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/12782657
        """
        audio_only_channel = self.service_api.get_random_audioonly_channel()
        if audio_only_channel:
            self.home_page.goto_live_tv(audio_only_channel[0])
            self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
            self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
            self.watchvideo_page.show_trickplay_if_not_visible()
            self.watchvideo_page.press_pause_in_visual_trickplay()
            self.watchvideo_assertions.verify_trickplay_restriction_message_shown(
                self.liveTv_labels.LBL_PAUSE_NOT_SUPPORTED)
            self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)
            self.watchvideo_assertions.verify_ff__status("disabled")
            self.watchvideo_assertions.verify_rewind__status("disabled")
        else:
            pytest.skip("No Audio only channel Available")

    @pytest.mark.p1_regression
    @pytest.mark.compliance
    @pytest.mark.iplinear
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Test case is seperated for managed and unmanaged devices")
    def test_312064627_managed_verify_audio_video_present_for_entitled_channels(self):
        """
        To verify Audio and video are present for entitled channels only on managed devices
        Testrail: https://testrail.tivo.com//index.php?/tests/view/312064627
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        if channel is None:
            pytest.skip("Could not find any good channel")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_channel_up_multiple_times()
        jump_overlay = self.watchvideo_page.get_confirm_jump_channel_overlay_visibility()
        if not jump_overlay:
            if not self.watchvideo_page.osd_shown():
                self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
                self.watchvideo_assertions.verify_playback_play()
        else:
            self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_NEXT_CHANNEL)

    @pytest.mark.p1_regression
    @pytest.mark.compliance
    @pytest.mark.iplinear
    @pytest.mark.skipif(Settings.is_managed(), reason="Test case is seperated for managed and unmanaged devices")
    def test_312064627_unmanaged_verify_audio_video_present_for_entitled_channels(self):
        subscribed_channels = self.service_api.get_random_live_channel_rich_info(movie=False, episodic=True, channel_count=1,
                                                                                 transport_type="stream")
        if not subscribed_channels:
            pytest.skip("Could not find any entitled channel")
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(subscribed_channels[0][0])
        for i in range(2):
            self.guide_page.goto_one_line_guide_from_live(self)
            self.watchvideo_assertions.verify_channel_change_from_olg()
            channel_subscribe = self.guide_labels.CHANNEL_NOT_SUBSCRIBED
            if self.watchvideo_page.is_overlay_shown() and self.watchvideo_page.get_overlay_title() == channel_subscribe:
                self.watchvideo_page.press_ok_button()
                self.watchvideo_assertions.verify_one_line_guide()
            else:
                self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
                self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_C14379826_red_dot_displayed_on_trickplay_after_creating_recording(self):
        channel = self.service_api.get_random_channels_with_no_trickplay_restrictions(recordable=True,
                                                                                      filter_channel=True,
                                                                                      entitled=True,
                                                                                      exclude_tplus_channels=True)
        if channel is None:
            pytest.skip("Recordable Channel Not Found")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.my_shows_page.create_recording_from_live_tv(self, channel[0])
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.screen.refresh()
        self.watchvideo_assertions.verify_red_dot_is_displayed_on_trickplay()

    @pytest.mark.p1_regression
    @pytest.mark.socu
    def test_20933793_verify_play_mode_after_rewind(self):
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                           filter_socu=True, restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_view_mode(self.guide_labels.LBL_VIEW_MODE)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_playback_play()
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.watch_video_for(60 * 2)
        self.watchvideo_page.navigate_to_start_of_video()
        self.guide_assertions.verify_play_normal()
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(value, value1, rewind=True)

    @pytestrail.case("C14386461")
    @pytest.mark.xray("FRUM-1091")
    @pytest.mark.msofocused
    @pytest.mark.compliance
    @pytest.mark.p1_regression
    def test_14386461_trigger_EAS_alert_on_livtev(self):
        """
        Xray: https://jira.xperi.com/browse/FRUM-1091
        """
        channel = self.api.get_eas_non_interrupted_channels()
        if not channel:
            pytest.skip("None of the channels allow EAS interruption. Hence Skipping")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.screen.base.press_back()
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.bat
    @pytest.mark.frumos_13
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.timeout(Settings.timeout)
    @pytestrail.case("C11688096")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.skipif("telus" in Settings.mso.lower(), reason="TV-G rating is not available for telus MSO")
    def test_C11688096_verify_user_can_watch_same_or_lower_rating_content_in_livetv(self):
        """
        Description:
        To verify the correct behavior for lower or same ratings in Live TV when the Movie Rating Limit is set to AO.
        """
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_page.select_menu(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_assertions.verify_create_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_assertions.verify_confirm_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.select_menu(self.menu_labels.LBL_SET_RATING_LIMITS)
        self.menu_page.wait_for_screen_ready(self.menu_labels.LBL_SET_RATING_LIMITS_SCREEN)
        self.menu_page.set_rating_limits(rated_movie=self.menu_page.get_movie_rating(),
                                         rated_tv_show=self.menu_page.get_tv_rating(),
                                         unrated_tv_show=self.menu_labels.LBL_ALLOW_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_ALLOW_ALL_UNRATED)

        self.menu_page.press_back_button(refresh=True)
        channel = self.api.get_random_rating_channels(rating="TV-G", filter_channel=True)
        self.home_page.goto_live_tv(channel[0][0], confirm=False)
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=False)
        channel = self.api.get_random_rating_channels(rating="PG", filter_channel=True)
        self.home_page.goto_live_tv(channel[0][0], confirm=False)
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=False)

    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_c14391035_verify_playmode_after_rewind_for_inprogress_recording(self):
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True)
        recording = self.api.schedule_single_recording(channels=channels)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(self.my_shows_page.convert_special_chars(recording[0][0]))
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(120)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.navigate_to_start_of_video()
        self.guide_assertions.verify_play_normal()

    @pytest.mark.p1_regression
    def test_19782350_part1_verify_trickplay_timeout_while_FFWDx1(self):
        """
        Verify if Trickplay bar is getting timed out while doing FFWDx1 in Live TV.

        https://testrail.tivo.com/index.php?/cases/view/19782350
        """
        channel = self.service_api.get_random_channels_with_no_trickplay_restrictions(filter_channel=True,
                                                                                      exclude_tplus_channels=True)
        self.home_page.goto_live_tv(channel[0])
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.guide_page.fast_forward_show(self, 1)
        self.watchvideo_page.pause(1)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        mode = self.watchvideo_page.get_trickplay_text_play_or_pause()
        if mode == self.watchvideo_labels.LBL_PLAY_OPTION:
            self.screen.base.press_left()
            self.watchvideo_assertions.is_playpause_focused(refresh=True)
            self.watchvideo_page.press_ok_button()
            self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    # @pytest.mark.test_stabilization
    @pytest.mark.socu
    @pytest.mark.p1_regression
    def test_19782350_part2_verify_trickplay_timeout_while_FFWDx1(self):
        """
        Verify if Trickplay bar is getting timed out while doing FFWDx1 for Socu

        https://testrail.tivo.com/index.php?/cases/view/19782350
        """
        channel = self.api.get_random_catch_up_channel_current_air()
        if not channel:
            pytest.skip("No available SOCU programs haven't been found.")
        channel_number = channel[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.fast_forward_show(self, 1)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        mode = self.watchvideo_page.get_trickplay_text_play_or_pause()
        focus = self.watchvideo_page.get_strip_focus_of_trickplay_bar()
        if mode == self.watchvideo_labels.LBL_PLAY_OPTION and focus == self.watchvideo_labels.LBL_FORWARD_BUTTON:
            self.screen.base.press_left()
            self.watchvideo_assertions.is_playpause_focused(refresh=True)
            self.watchvideo_page.press_ok_button()
            self.guide_page.wait_for_screen_ready()
        elif mode == self.watchvideo_labels.LBL_PLAY_OPTION and focus == self.watchvideo_labels.LBL_PLAY_OPTION:
            self.watchvideo_assertions.is_playpause_focused(refresh=True)
            self.watchvideo_page.press_ok_button()
            self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytest.mark.p1_regression
    def test_19782350_part3_verify_trickplay_timeout_while_FFWDx1(self):
        """
        Verify if Trickplay bar is getting timed out while doing FFWDx1 in VOD

        https://testrail.tivo.com/index.php?/cases/view/19782350
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(600, 7200)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.skip_hdmi_connection_error()
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX1)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        mode = self.watchvideo_page.get_trickplay_text_play_or_pause()
        if mode == self.watchvideo_labels.LBL_PLAY_OPTION:
            self.screen.base.press_left()
            self.watchvideo_assertions.is_playpause_focused(refresh=True)
            self.watchvideo_page.press_ok_button()
            self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.LINEAR,
                                                        FeAlacartePackageTypeList.NATIVE)])
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_C12947446_drm_type_iplinear_native_playback(self, request, feature, package_type):
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_guide(self)
        self.guide_page.verify_channel(self, self.guide_page.guide_encrypted_streaming_channel_number(self))
        self.watchvideo_assertions.verify_playback_play()

    # @pytest.mark.test_stabilization
    @pytest.mark.longrun
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-1137")
    def test_19782408_verify_FFWD_to_live_resumes_playback(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/19782408
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.goto_live_tv(channel[0][0])
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.watch_video_for(60 * 30)  # build cache for 30 minutes
        value0 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.guide_page.rewind_show(self, 3)
        self.watchvideo_assertions.verify_rewind_with_time(self, value0)
        focus = self.watchvideo_page.get_strip_focus_of_trickplay_bar()
        if focus == self.watchvideo_labels.LBL_REWIND_BUTTON:
            self.screen.base.press_right()
        focus = self.watchvideo_page.get_strip_focus_of_trickplay_bar()
        if focus == self.watchvideo_labels.LBL_PLAY_OPTION:
            self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.is_playpause_focused(value="Pause", refresh=True)
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete()
        self.watchvideo_page.wait_for_screen_ready()
        self.guide_assertions.verify_play_normal()

    @pytest.mark.infobanner
    @pytest.mark.parametrize("is_relaunch_needed,is_package_add_needed", [(True, True)])
    @pytest.mark.usefixtures("setup_cleanup_inactivity_timeout")
    @pytest.mark.notapplicable(Settings.is_fire_tv() or Settings.is_apple_tv(),
                               reason="FireTV and AppleTV are not supported.")
    @pytest.mark.notapplicable(not Settings.is_cc3() or not Settings.is_cc11(),
                               reason="CableCo3 and CableCo11 are only supported.")
    def test_20930780_inactivity_timeout_in_live_tv(self, is_relaunch_needed, is_package_add_needed):
        """
        Testopia: https://testrail.tivo.com//index.php?/cases/view/20930780
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(
            filter_channel=True, encrypted=True, transportType="stream")
        if channel is None:
            pytest.skip("Recordable Channel Not Found")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.pause(430)
        # to show inactivity OSD - 5 minutes
        # OSD timeout - 2 minutes
        # additional timeout to let the box start screensaver - 10 seconds
        self.watchvideo_assertions.verify_foreground_package_name(Settings.screen_saver_package)

    @pytest.mark.usefixtures("reset_bandwidth_rule")
    def test_c14094140_throttle_bandwidth_2_5_mbps(self):
        channels = self.api.get_random_encrypted_unencrypted_channels(Settings.tsn, socu=True,
                                                                      encrypted=True, filter_channel=True)
        channel = (channels[0][0])
        if channel is None:
            pytest.fail("Could not find any live channel")

        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(channel)
        self.watchvideo_page.show_network_osd()
        self.watchvideo_page.init_ssh()
        self.watchvideo_page.wonder_restrict_bandwidth(2560, 2560)
        self.watchvideo_page.pause_with_video_buffer()
        self.watchvideo_assertions.verify_throttle_network(self, 2560)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_14379319_verify_no_dimming_screen_while_watching_video(self):
        """
        Appearing of Dimming screen - in Streaming Watch Video screen (negative case)

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/14379319
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, encrypted=True,
                                                                             transportType="stream")[0][0]
        self.home_page.update_test_conf_and_reboot(TIMEOUT_TO_DIMMING_SCREEN=60000)
        self.home_page.goto_live_tv(channel)
        self.watchvideo_page.wait_for_LiveTVPlayback("PLAYING")
        self.watchvideo_assertions.verify_view_mode()
        self.watchvideo_assertions.verify_error_overlay_not_shown()
        self.watchvideo_page.pause(120, "Waiting for the Dimming screen to appear")
        self.watchvideo_assertions.verify_view_mode()

    @pytest.mark.stop_streaming
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_cleanup_turn_on_device_power")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("setup_enable_full_screen_video_on_home")
    def test_14391793_verify_stop_streaming_tv_on_off_while_socu_playback(self):
        """
        Stop Streaming - SOCU streaming - Pause - TV(HDMI Adapter) Power OFF/ON

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/14391793
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0][0])
        self.home_page.goto_live_tv(channel_number)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_page.press_left_multiple_times(no_of_times=4)
        self.watchvideo_assertions.is_startover_focused(refresh=True)
        self.vod_page.press_ok()  # Press 'Start Over' button
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.turn_off_device_power(Settings.equipment_id)
        self.home_page.wait_for_screen_saver(time=self.guide_labels.LBL_SCREEN_SAVER_WAIT_TIME)
        self.watchvideo_assertions.verify_video_playback_stopped()
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.watchvideo_page.turn_on_device_power(Settings.equipment_id)
        self.screen.base.press_right()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=900000)
        time.sleep(self.guide_labels.LBL_TEN_SECONDS)
        self.home_assertions.verify_home_title()
        self.watchvideo_assertions.verify_video_playback_started()
        self.home_page.goto_live_tv()
        self.watchvideo_assertions.verify_channel_number(channel_number)

    @pytest.mark.p1_regression
    @pytest.mark.p1_reg_stability
    @pytest.mark.livetv
    def test_20941110_verify_ffwd_and_rwd_when_paused(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20941110
        """
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True, exclude_tplus_channels=True)
        if channel is None:
            pytest.skip("No appropriate channels found.")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 30)  # build cache for REW modes verification
        self.watchvideo_page.navigate_to_end_of_video()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.screen.base.press_left()  # RWD
        self.watchvideo_assertions.is_rewind_focused(refresh=True)
        value0 = self.my_shows_page.get_trickplay_current_position_time(self, refresh=False)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(10)
        self.watchvideo_assertions.verify_rewind_with_time(self, value0)
        self.menu_page.press_back_button(refresh=True)  # To dismiss trickplay and resume playback
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        value1 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.screen.base.press_right()  # FWD
        self.watchvideo_assertions.is_forward_focused(refresh=True)
        self.watchvideo_page.press_ok_button()  # FWD
        self.watchvideo_page.pause(10)
        self.watchvideo_assertions.verify_forward_with_time(self, value1)
        self.menu_page.press_back_button(refresh=True)  # To dismiss trickplay and resume playbacki
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.is_playpause_focused(value="Pause")
        self.watchvideo_page.press_ok_button()
        self.guide_assertions.verify_pause()
        value2 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.screen.base.press_left()  # RWD
        self.watchvideo_assertions.is_rewind_focused(refresh=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(10)
        self.watchvideo_assertions.verify_rewind_with_time(self, value2)
        self.screen.base.press_right()  # play/pause
        self.screen.base.press_right()  # FWD
        self.watchvideo_assertions.is_forward_focused(refresh=True)
        self.watchvideo_page.press_ok_button()
        value3 = self.my_shows_page.get_trickplay_current_position_time(self, refresh=False)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(10)
        self.watchvideo_assertions.verify_forward_with_time(self, value3)
        # TC should not leave playback on FF mode
        self.menu_page.press_back_button(refresh=True)  # To dismiss trickplay and resume playbacki
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.longrun
    @pytest.mark.livetv
    def test_20941218_verify_rewind(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20941110
        """
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True, exclude_tplus_channels=True)
        if channel is None:
            pytest.skip("No appropriate channels found.")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 30)  # build cache for 30 minutes
        value0 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.screen.base.press_left()  # RWD
        self.watchvideo_assertions.is_rewind_focused(refresh=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(20)
        self.watchvideo_assertions.verify_rewind_with_time(self, value0)
        value1 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(5)
        self.watchvideo_assertions.verify_rewind_with_time(self, value1)
        value2 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_rewind_with_time(self, value2)

    @pytest.mark.p1_regression
    @pytestrail.case("C20931416")
    @pytest.mark.platform_cert_smoke_test
    def test_C20931416_verify_last_played_channel_on_LiveTV(self):
        """
        Description: This test case will verify if after restarting the Tivo app, the Livetv channel remains same as
        the channel being played before restarting the app.
        """
        self.home_page.go_to_guide(self)
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                            transportType="stream")[0][0]
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_channel_number(channel_number)
        self.home_page.relaunch_hydra_app(reboot=True)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_home_title()
        self.guide_page.go_to_live_tv(self)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_channel_number(channel_number)

    @pytest.mark.p1_regression
    @pytest.mark.livetv
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_4866167_verify_thuuz_ratings_on_livetv_when_thuuz_rating_is_ON(self):
        self.api.cancel_all_recordings()
        thuuz_channel = self.service_api.get_sports_with_thuuz_rating(filter_good_channels=True)
        if not thuuz_channel:
            pytest.skip("Did not find any channels with Thuuz Rating. Hence Skipping")
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.select_menu(self.menu_labels.LBL_THUUZ_SPORTS_RATING)
        self.menu_page.select_menu(self.menu_labels.LBL_YES)  # Thuuz rating ON
        self.home_page.goto_live_tv(thuuz_channel[0]['channelNumber'])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_assertions.verify_critic_ratings_on_livetv()
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_full_info_banner_is_shown()
        self.watchvideo_assertions.verify_critic_ratings_on_livetv()

    @pytest.mark.p1_regression
    @pytest.mark.livetv
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_4866162_verify_thuuz_ratings_on_livetv_when_thuuz_rating_is_OFF(self):
        self.api.cancel_all_recordings()
        thuuz_channel = self.service_api.get_sports_with_thuuz_rating(filter_good_channels=True)
        if not thuuz_channel:
            pytest.skip("Did not find any channels with Thuuz Rating. Hence Skipping")
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.select_menu(self.menu_labels.LBL_THUUZ_SPORTS_RATING)
        self.menu_page.select_menu(self.menu_labels.LBL_NO)  # Thuuz rating OFF
        self.home_page.goto_live_tv(thuuz_channel[0]['channelNumber'])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_assertions.verify_critic_ratings_on_livetv(visible=False)
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_full_info_banner_is_shown()
        self.watchvideo_assertions.verify_critic_ratings_on_livetv(visible=False)

    @pytest.mark.stop_streaming
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.usefixtures("setup_enable_full_screen_video_on_home")
    def test_C14391801_verify_recording_when_tv_off(self):
        """
    Stop Streaming -  Record a show - TV Power OFF

    Testrail:
        https://testrail.tivo.com//index.php?/cases/view/14391801
        """

        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.watchvideo_page.turn_off_device_power(Settings.equipment_id)
        self.home_page.wait_for_screen_saver(time=self.guide_labels.LBL_SCREEN_SAVER_WAIT_TIME)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.watchvideo_page.turn_on_device_power(Settings.equipment_id)
        self.screen.base.press_right()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=900000)
        time.sleep(self.guide_labels.LBL_TEN_SECONDS)
        self.home_assertions.verify_home_title(label=self.guide_labels.LBL_SCREENTITLE)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytest.mark.stop_streaming
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.usefixtures("setup_enable_full_screen_video_on_home")
    def test_C14391800_verify_OnePass_when_tv_off(self):
        """
        Stop Streaming -  Create OnePass - TV Power OFF

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/14391800
        """
        self.home_page.log.step("Step 0")
        channel = self.service_api.get_recordable_non_movie_channel()
        if channel is None:
            pytest.fail("Could not find any episodic channel")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        program = self.guide_page.create_one_pass_on_record_overlay(self)
        self.watchvideo_page.turn_off_device_power(Settings.equipment_id)
        self.home_page.wait_for_screen_saver(time=self.guide_labels.LBL_SCREEN_SAVER_WAIT_TIME)
        self.watchvideo_assertions.verify_video_playback_stopped()
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.watchvideo_page.turn_on_device_power(Settings.equipment_id)
        self.screen.base.press_right()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=900000)
        time.sleep(self.guide_labels.LBL_TEN_SECONDS)
        self.home_assertions.verify_home_title(label=self.guide_labels.LBL_SCREENTITLE)
        self.menu_page.go_to_one_pass_manager(self)
        self.home_assertions.verify_show_in_one_pass_manager(self, program)

    @pytest.mark.stop_streaming
    @pytest.mark.livetv
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    def test_20932944_verify_livetv_stop_streaming_videowindow_off(self):
        """
        Stop Streaming - Video Window OFF - Live TV - Power TV OFF/ON

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/20932944
        """
        self.menu_page.disable_full_screen_video_on_home(self)
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, live=False, filter_channel=True)
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=True)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.turn_off_device_power(Settings.equipment_id)
        self.home_page.wait_for_screen_saver(time=self.guide_labels.LBL_SCREEN_SAVER_WAIT_TIME)
        self.watchvideo_assertions.verify_video_playback_stopped()
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.watchvideo_page.turn_on_device_power(Settings.equipment_id)
        self.screen.base.press_right()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=900000)
        time.sleep(self.guide_labels.LBL_TEN_SECONDS)
        self.home_assertions.verify_home_title()
        self.vod_assertions.verify_video_blanking_status(state="true")
        self.menu_page.enable_full_screen_video_on_home(self)

    @pytest.mark.ipppv
    @pytest.mark.msofocused
    @pytest.mark.cloud_core_rent_ppv
    def test_389366311_verify_EAS_on_ppv(self):
        ppv_rental_channel = self.guide_page.get_ppv_rental_channel(self)
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(ppv_rental_channel)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_text_in_watch_video_osd(self.liveTv_labels.LBL_IPPPV_RENTING_ALLOWED)
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.press_select_verify_confirm_purchase_overlay()
        self.guide_assertions.press_select_verify_ppv_purchase_confirm_overlay()
        self.screen.base.press_back()
        self.watchvideo_assertions.verify_livetv_mode()
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        time.sleep(5)
        self.watchvideo_assertions.press_exit_and_verify_streaming(self)

    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.longrun_2
    def test_14095628_verify_ndvr_ccm_long_term_storage_recording_playback(self):
        icm_ch, ccm_ch = self.service_api.get_CCM_or_ICM_channel(filter_channel=True, filter_ndvr=True)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(ccm_ch[0])
        self.guide_page.wait_for_screen_ready('GridGuide')
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_record_program(self)
        self.watchvideo_assertions.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.nav_to_menu_by_substring(program)
        self.my_shows_assertions.verify_recording_icon()
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.live_tv_assertions.verify_view_mode(self.my_shows_page.get_watch_or_video_recording_view_mode(self))
        self.my_shows_assertions.verify_recording_playback(self)
        self.guide_page.wait_for_24_hours()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.nav_to_menu_by_substring(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.live_tv_assertions.verify_view_mode(self.my_shows_page.get_watch_or_video_recording_view_mode(self))
        self.my_shows_assertions.verify_recording_playback(self)
        self.watchvideo_page.watch_video_for(60 * 5)

    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    @pytest.mark.subtitle_tests
    @pytest.mark.timeout(Settings.timeout)
    def test_312064635_verify_subtitle_and_cc_order(self):
        '''
        https://testrail.tivo.com/index.php?/tests/view/312064635
        '''
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(self.watchvideo_labels.LBL_CH_NO_8124)
        self.guide_page.wait_for_screen_ready('GridGuide')
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.press_info_button()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_page.navigate_by_strip(self.live_tv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.menu_page.select_menu_items(self.watchvideo_labels.LBL_SPANISH_1)
        self.guide_page.wait_for_screen_ready()
        self.home_page.press_info_button()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_page.navigate_by_strip(self.live_tv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_language_with_blue_tick(self.watchvideo_labels.LBL_SPANISH_1)
        self.watchvideo_assertions.verify_subtitle_language_order(self, self.watchvideo_labels.LBL_SPANISH_1)
        self.screen.base.press_back()
        self.guide_page.wait_for_screen_ready()
        self.home_page.press_info_button()
        self.watchvideo_page.navigate_by_strip(self.live_tv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.menu_page.select_menu_items(self.watchvideo_labels.LBL_SPANISH_2)
        self.guide_page.wait_for_screen_ready()
        self.home_page.press_info_button()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_page.navigate_by_strip(self.live_tv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_language_with_blue_tick(self.watchvideo_labels.LBL_SPANISH_2)
        self.watchvideo_assertions.verify_subtitle_language_order(self, self.watchvideo_labels.LBL_SPANISH_2)

    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-1403")
    @pytest.mark.msofocused
    @pytest.mark.livetv
    def test_14391024_verify_livetv_playback_when_cache_advances_past_pause_point(self):
        """
        To verify Live tv should start playback in 6-8 sec when cache advances past the pause point

        https://testrail.tivo.com/index.php?/cases/view/14391024
        """
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True, exclude_tplus_channels=True)
        if channel is None:
            pytest.skip("No appropriate channels found.")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.navigate_to_start_of_video()
        self.home_page.wait_for_screen_ready()
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.pause(5)
        self.guide_assertions.verify_play_normal()

    @pytest.mark.p1_regression
    @pytest.mark.livetv
    @pytest.mark.cloud_core_liveTV
    def test_21557979_verify_metacritic_rating_on_livetv(self):
        """
        Verify Metacritic rating on Livetv
        """
        self.api.cancel_all_recordings()
        metacritic_channel = self.service_api.get_movies_with_metacritic_ratings(collection_type='movie',
                                                                                 filter_good_channels=True)
        if not metacritic_channel:
            pytest.skip("Did not find any channel with Metacritic Rating. Hence Skipping")
        self.home_page.goto_live_tv(metacritic_channel[0]['channelNumber'])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_assertions.verify_critic_ratings_on_livetv()
        self.watchvideo_page.press_clear_button()
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_assertions.verify_full_info_banner_is_shown()
        self.watchvideo_assertions.verify_critic_ratings_on_livetv()

    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.longrun_2
    def test_14378735_verify_ndvr_icm_long_term_storage_recording_playback(self):
        icm_ch, ccm_ch = self.service_api.get_CCM_or_ICM_channel(filter_channel=True, filter_ndvr=True)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(icm_ch[0])
        self.guide_page.wait_for_screen_ready('GridGuide')
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_record_program(self)
        self.watchvideo_assertions.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.nav_to_menu_by_substring(program)
        self.my_shows_assertions.verify_recording_icon()
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.live_tv_assertions.verify_view_mode(self.my_shows_page.get_watch_or_video_recording_view_mode(self))
        self.my_shows_assertions.verify_recording_playback(self)
        self.guide_page.wait_for_24_hours()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.nav_to_menu_by_substring(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.live_tv_assertions.verify_view_mode(self.my_shows_page.get_watch_or_video_recording_view_mode(self))
        self.my_shows_assertions.verify_recording_playback(self)
        self.watchvideo_page.watch_video_for(60 * 5)

    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    @pytest.mark.subtitle_tests
    @pytest.mark.timeout(Settings.timeout)
    def test_10196843_verify_description_of_change_subtitle_and_cc_language(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/10196843
        """
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(self.watchvideo_labels.LBL_CH_NO_8124)
        self.guide_page.wait_for_screen_ready('GridGuide')
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.press_info_button()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_page.navigate_by_strip(self.live_tv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_overlay_shown()
        self.menu_page.select_menu_items(self.watchvideo_labels.LBL_SPANISH_1)
        self.guide_page.wait_for_screen_ready()
        self.home_page.press_info_button()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_page.navigate_by_strip(self.live_tv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_description_of_change_subtitle_and_cc_language(self,
                                                                                         self.watchvideo_labels.LBL_SPANISH_1)

    @pytest.mark.nDVR_showing_restriction
    @pytest.mark.p1_regression
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.frumos_15
    def test_20932938_recording_not_permitted_on_info_banner_for_nDVR_restricted_offer(self):
        """
        To verify recording not permitted button on info banner of nDVR restricted live offer
        https://testrail.tivo.com//index.php?/cases/view/20932938
        """
        channels = self.service_api.get_recording_channel_with_live_offer_restricted()
        if not channels:
            pytest.skip("Failed to call station_search")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number((random.sample(channels, 1))[0], confirm=True)
        self.home_page.wait_for_screen_ready()
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_recording_not_permitted_button_on_info_banner(self)

    @pytest.mark.nDVR_showing_restriction
    @pytest.mark.p1_regression
    @pytest.mark.frumos_15
    def test_20932937_recording_not_permitted_on_info_banner_for_nDVR_restricted_channel(self):
        """
        To verify recording not permitted button on info banner of nDVR restricted live channel
        https://testrail.tivo.com//index.php?/cases/view/20932937
        """
        channels = self.service_api.get_nonrecordable_channels()
        if not channels:
            pytest.skip("No non-recordable channels found.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number((random.sample(channels, 1))[0], confirm=True)
        self.home_page.wait_for_screen_ready()
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_recording_not_permitted_button_on_info_banner(self)

    @pytest.mark.nDVR_showing_restriction
    @pytest.mark.p1_regression
    @pytest.mark.frumos_15
    @pytest.mark.cloud_core_guide_preview
    def test_20932928_status_message_in_upcoming_airing_for_nDVR_restricted_offer_in_content_screen(self):
        """
        To Verfiy status message on preview in upcoming Airing strips for nDVR restricted live channel
        https://testrail.tivo.com//index.php?/cases/view/20932928
        """
        channels = self.service_api.get_recording_channel_with_live_offer_restricted()
        if not channels:
            pytest.skip("Failed to call station_search")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready("GridGuide")
        self.guide_page.enter_channel_number((random.sample(channels, 1))[0], confirm=True)
        self.home_page.wait_for_screen_ready("GridGuide")
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_info_banner()
        self.watchvideo_page.select_strip(self.menu_page.get_more_info_name(self))
        self.home_page.wait_for_screen_ready()
        self.menu_page.select_menu_items(self.guide_labels.LBL_UPCOMING_AIRINGS)
        self.screen.base.press_back()
        time.sleep(Settings.SHORTEST_WAIT_TIME)
        self.guide_assertions.verify_status_message_in_upcoming_airing_for_nDVR_restricted_offer_in_content_screen()

    @pytest.mark.nDVR_showing_restriction
    @pytest.mark.p1_regression
    @pytest.mark.frumos_15
    def test_20932936_status_message_in_one_line_guide_for_nDVR_restricted_offer(self):
        """
        To Verify status message on one line guide preview for nDVR restricted offer
        https://testrail.tivo.com//index.php?/cases/view/20932936
        """
        channels = self.service_api.get_recording_channel_with_live_offer_restricted()
        if not channels:
            pytest.skip("Failed to call station_search")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number((random.sample(channels, 1))[0], confirm=True)
        self.home_page.wait_for_screen_ready()
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.goto_one_line_guide_from_live(self)
        self.watchvideo_assertions.verify_status_message_in_one_line_guide_for_nDVR_restricted_offer(self)

    @pytest.mark.usefixtures("cleanup_favorite_channels")
    # @pytest.mark.test_stabilization
    @pytest.mark.favorite_channels
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    def test_21558383_leave_liveTv_overlay(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/21558383
        """
        self.home_page.back_to_home_short()
        channel = self.api.get_random_encrypted_unencrypted_channels(channel_count=3, filter_channel=True)
        jump_channel = list(self.api.get_jump_channels_list().keys())[0]
        if not channel and jump_channel:
            pytest.skip("There are no channels that have next/previous jump channels.")
        channel_list = [channel[0][0], channel[1][0]]
        self.api.add_favorite_channel([channel[0][0], jump_channel, channel[1][0]])
        self.menu_page.update_favorite_channels_list(self)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_title()
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        self.guide_page.wait_for_screen_ready()
        self.home_page.go_to_guide(self)
        max_channel_number = max(channel_list)
        min_channel_number = min(channel_list)
        self.guide_page.enter_channel_number(max_channel_number)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_channel_number(max_channel_number)
        self.watchvideo_page.press_channel_up_button()
        if jump_channel > channel[1][0] and jump_channel < channel[0][0]:
            self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
            self.watchvideo_page.pause(300)  # dismiss overlay
            self.guide_page.wait_for_screen_ready()
            self.watchvideo_assertions.verify_livetv_mode()
            self.watchvideo_assertions.verify_channel_number(min_channel_number)
        elif (jump_channel > channel[1][0] and jump_channel > channel[0][0]) or \
             (jump_channel < channel[1][0] and jump_channel < channel[0][0]):
            self.watchvideo_assertions.verify_livetv_mode()

    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    @pytest.mark.subtitle_tests
    @pytest.mark.compliance
    @pytest.mark.timeout(Settings.timeout)
    def test_312064642_cc_language_unknown(self):
        """
        https://testrail.tivo.com/index.php?/tests/view/312064642

        removed description verification as it is alredy being done in below case
        test_10196843_verify_description_of_change_subtitle_and_cc_language
        """
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.goto_live_tv(channel[0][0])
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.press_info_button()
        self.watchvideo_page.navigate_by_strip(self.live_tv_labels.LBL_CHANGE_SUBTITLE_CC_LANGUAGE)
        self.watchvideo_page.press_ok_button()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_overlay_shown()
        self.watchvideo_assertions.verify_cc_track()

    @pytest.mark.internal_storage
    @pytest.mark.usefixtures("free_up_internal_memory_by_uninstalling")
    @pytest.mark.usefixtures("fill_internal_storage_by_installing_apps")
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_21568606_fill_storage_and_press_exit_on_livetv(self):
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        available_data = self.home_page.get_data_in_mb()
        if int(available_data) > self.home_labels.LBL_MINIMUM_MEMORY:
            pytest.fail("Internal storage is not full. install some apps")
        channel = self.service_api.get_recordable_non_movie_channel(filter_ndvr=True)
        if not channel:
            pytest.skip("Recordable episodic channels are not found.")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 3)
        program = self.api.record_currently_airing_shows(1, includeChannelNumbers=channel[0][0])
        if not program:
            pytest.skip("Failed to schedule recording")
        recording = program[0][0]
        if not Settings.is_managed():
            self.screen.base.press_back()
        if Settings.is_managed():
            self.home_page.press_home_button()  # Press Home button
        self.home_page.wait_for_screen_ready()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(recording)
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.longrun
    @pytest.mark.socu
    @pytest.mark.usefixtures("enable_video_providers")
    def test_21570241_test_verify_asset_is_played_in_order_part_2(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/21570241

        SOCU & OTT
        """
        channel = self.api.get_random_catch_up_channel_current_air(filter_channel=True,
                                                                   filter_socu=True,
                                                                   restrict=False)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        desc = self.guide_page.get_grid_focus_details()['description']
        self.my_shows_page.play_socu_program_multiple_times(self, expected_program_name=program, expected_desc=desc,
                                                            channel=channel[0][0], count=40)
        self.home_page.back_to_home_short()
        self.home_page.wait_for_screen_ready()
        self.home_page.goto_prediction()
        self.home_page.wait_for_screen_ready()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        shows = self.home_page.get_prediction_bar_shows(self)
        status = self.home_assertions.is_content_available_in_prediction(self, program, shows)
        if status:
            self.home_page.nav_to_show_on_prediction_strip(program)
            self.watchvideo_assertions.press_select_and_verify_streaming(self)
        else:
            pytest.skip("SOCU asset not found in prediction bar")

    @pytest.mark.frumos_15
    @pytest.mark.resiliency_mode
    @pytest.mark.usefixtures("restore_mind_availability")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @ pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    def test_21558056_verify_livetv_channel_change_when_tivo_service_is_down(self):
        """
        testrail: https://testrail.tivo.com/index.php?/cases/view/21558056
        """
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.toggle_mind_availability()
        self.watchvideo_page.press_back_button()
        self.watchvideo_assertions.press_channel_button_and_verify_channel_change('channel up')
        self.watchvideo_assertions.verify_playback_play(disconnected_state=True)
        self.watchvideo_assertions.press_channel_button_and_verify_channel_change('channel down')
        self.watchvideo_assertions.verify_playback_play(disconnected_state=True)

    @pytest.mark.internal_storage
    @pytest.mark.usefixtures("free_up_internal_memory_by_uninstalling")
    @pytest.mark.usefixtures("fill_internal_storage_by_installing_apps")
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_21568607_fill_internal_storage_and_play_exit_button(self):
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_home_title()
        available_data = self.home_page.get_data_in_mb()
        if int(available_data) > self.home_labels.LBL_MINIMUM_MEMORY:
            pytest.fail("Internal storage is not full. install some apps")
        self.home_page.back_to_home_short()
        channels = self.api.get_channels_with_no_trickplay_restrictions(
            recordable=True, filter_channel=True, filter_ndvr=True, is_preview_offer_needed=True)
        program = self.api.record_currently_airing_shows(number_of_shows=1, includeChannelNumbers=channels,
                                                         genre="series", use_cached_grid_row=True)[0][0]
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_recording_playback(self)
        self.watchvideo_page.watch_video_for(60 * 5)
        self.watchvideo_assertions.verify_playback_play()
        socu_channel = self.guide_page.get_encrypted_socu_channel(self, filter_socu=True)
        self.watchvideo_page.enter_channel_number(socu_channel[0][0])
        self.watchvideo_page.watch_video_for(60 * 5)
        self.watchvideo_assertions.verify_playback_play()
        self.screen.refresh()
        channel1 = self.watchvideo_page.get_channel_number()
        self.watchvideo_page.press_exit_button()
        self.home_page.wait_for_screen_ready()
        self.watchvideo_page.watch_video_for(30)
        self.watchvideo_assertions.verify_playback_play()
        self.screen.refresh()
        channel2 = self.watchvideo_page.get_channel_number()
        self.watchvideo_assertions.verify_channel_change_after_pressing_exit_button(channel1, channel2)

    # @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures(
        "toggle_guide_rows_service_availability"
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18) else "switch_tivo_service_rasp")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Enter to Disconnected State. NoNetworkScreen is shown")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    def test_21558353_21558361_21558377_21558363_21558365_21558366_21558369_fail_open_olg_feature_mind_is_down(self):
        """
        This test covers 7 cases (https://jira.tivo.com/browse/IPTV-21875)

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/21558353 - entering the OLG
            https://testrail.tivo.com/index.php?/cases/view/21558361 - tile displaying
            https://testrail.tivo.com/index.php?/cases/view/21558377 - selecting a tile
            https://testrail.tivo.com/index.php?/cases/view/21558363 - tuning to a channel
            https://testrail.tivo.com/index.php?/cases/view/21558365 - blocking the Future Guide
            https://testrail.tivo.com/index.php?/cases/view/21558366 - blocking the Past Guide
            https://testrail.tivo.com/index.php?/cases/view/21558369 - scrolling up and down
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True, channel_count=1)[0][0]
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.open_olg(refresh=False, wait_olg_event=False, wait_olg_content=False)
        # Step #1: Checking disconnected Guide service whisper when entering One Line Guide
        self.guide_assertions.smart_verify_guide_service_down_whisper(is_olg=True)
        # Step #2: Scrolling vertically and checking only one fallback tile subtitle (text in the bottom of a tile) in a row.
        # Also, checking tiles count to ensure that Future Guide is not available
        self.guide_assertions.verify_olg_tiles_with_disconnected_service(self.guide_labels.LBL_DS_PROGRAM_CELL, 1, 5, True)
        self.guide_page.waiting_fail_open(is_olg=True)
        is_1_18_or_higher = True if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18) else False
        self.watchvideo_assertions.verify_transition_to_past_olg_is_blocked(expected=not is_1_18_or_higher)
        if not is_1_18_or_higher:
            self.watchvideo_page.open_olg(refresh=False, wait_olg_event=False, wait_olg_content=False)
            self.watchvideo_assertions.verify_channel_cell_is_currently_focused()
        else:
            self.guide_page.get_to_channel_tab(is_olg=True)
        self.watchvideo_page.press_right_button()
        # Step #4: tuning to a channel and checking if entered WatchVideo screen
        self.watchvideo_page.enter_channel_number(channel, confirm=False, olg=True)
        self.guide_page.waiting_fail_open(is_olg=True)
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_number(channel)

    # @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures(
        "toggle_guide_rows_service_availability"
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18) else "switch_tivo_service_rasp")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Enter to Disconnected State. NoNetworkScreen is shown")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    def test_21558362_fail_open_olg_feature_channels_option_overlay_when_mind_is_down(self):
        """
        Fail Open One Line Guide - Channel options

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/21558362
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.open_olg(refresh=False)
        self.watchvideo_page.enter_channel_number(channel, olg=True)
        self.guide_page.waiting_fail_open(is_olg=True)
        self.guide_page.get_to_channel_tab(is_olg=True)
        self.watchvideo_assertions.verify_channel_cell_is_currently_focused()
        self.watchvideo_page.press_ok_button(refresh=False)  # opening Channel Options overlay
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_CHANNEL_OPTIONS)
        self.watchvideo_page.select_menu(self.liveTv_labels.LBL_WATCH_NOW)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_number(channel)

    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    @pytest.mark.usefixtures("reset_bandwidth_rule")
    def test_389366296_verify_subtitle_in_low_bandwidth(self):
        """
        https://testrail.tivo.com//index.php?/tests/view/389366296
        """
        self.home_page.back_to_home_short()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_network_osd()
        self.watchvideo_page.init_ssh()
        self.watchvideo_page.wonder_restrict_bandwidth(2560, 2560)
        self.watchvideo_assertions.record_and_verify_cc(".", 20, Settings.log_path, "ON")
        self.watchvideo_page.wonder_relax_bandwidth_restrictions()
        self.menu_page.disable_closed_captioning(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_network_osd()
        self.watchvideo_page.init_ssh()
        self.watchvideo_page.wonder_restrict_bandwidth(2560, 2560)
        self.watchvideo_assertions.record_and_verify_cc(".", 20, Settings.log_path, "OFF")

    @pytest.mark.yukon
    @pytest.mark.usefixtures("setup_cleanup_remove_playback_source")
    def test_13530290_verify_download_error_yukon_server(self):
        """
        Verify "Download Error" using url from Yukon Server
        """
        self.guide_assertions.set_playback_to_yukon_url(purpose="404",
                                                        asset="asset3")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.guide_assertions.verify_download_error()

    @pytest.mark.yukon
    @pytest.mark.usefixtures("setup_cleanup_remove_playback_source")
    def test_c13533955_throttle_bandwidth_1_5_Mbps(self):
        """
        Verify Yukon Server - Throttle the bandwidth to 1.5 Mbps
        """
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_assertions.set_playback_to_yukon_url(purpose="1.5_throttling",
                                                        asset="asset1")
        self.watchvideo_page.pause(23)  # approximate buffer size
        self.watchvideo_assertions.verify_text_in_watch_video_osd(self.watchvideo_labels.LBL_LOADING_VIDEO_OSD)

    @pytest.mark.yukon
    @pytest.mark.usefixtures("setup_cleanup_remove_playback_source")
    def test_c13533957_throttle_bandwidth_5_0_Mbps(self):
        """
        Verify Yukon Server - Throttle the bandwidth to 5.0 Mbps
        """
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_assertions.set_playback_to_yukon_url(purpose="5_throttling",
                                                        asset="asset1")
        self.watchvideo_page.pause(23)  # approximate buffer size
        self.watchvideo_assertions.verify_text_in_watch_video_osd(self.watchvideo_labels.LBL_LOADING_VIDEO_OSD)

    @pytest.mark.yukon
    @pytest.mark.usefixtures("setup_cleanup_remove_playback_source")
    def test_yukon_server_nothrottling(self):
        """
        Verify Yukon Server - expose all media with zero Throttling the bandwidth
        """
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_assertions.set_playback_to_yukon_url(purpose="no_throttling",
                                                        asset="asset1")
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()

    @pytest.mark.yukon
    @pytest.mark.usefixtures("setup_cleanup_remove_playback_source")
    def test_C13533958_verify_reject_download_error_yukon_server(self):
        """
        Verify "Download Error" using url from Yukon Server
        Testrail: https://testrail.tivo.com//index.php?/cases/view/13533958&group_by=cases:section
        _id&group_id=1296449&group_order=asc
        """
        self.guide_assertions.set_playback_to_yukon_url(purpose="reject",
                                                        asset="asset3")
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.guide_assertions.verify_download_error()

    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.audioonly
    @pytest.mark.parental_control
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_389366335_389366336_parental_controls_audio_only_channel(self, request):
        self.home_page.back_to_home_short()
        request.getfixturevalue('setup_lock_parental_and_purchase_controls')
        audio_only_channel = self.service_api.get_random_audioonly_channel()
        if not audio_only_channel:
            pytest.skip("No audio only channel found")
        self.home_page.goto_live_tv(audio_only_channel[0])
        self.home_page.wait_for_screen_ready()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_osd()
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_PIN_challenge_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_no_osd_on_screen()

    @pytest.mark.frumos_15
    @pytest.mark.tivo_plus
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @ pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.usefixtures("setup_cleanup_pluto_tv_app")
    @pytest.mark.usefixtures("cleanup_favorite_channels")
    def test_21572360_verify_pluto_tv_by_navigate_using_channelup_button_in_livetv(self):
        """
        To verify ChannelUp/ChannelDown buttons in Confirm Jump Channel overlay
        Testcase: https://testrail.tivo.com//index.php?/cases/view/21572360
        """
        self.home_page.back_to_home_short()
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        pluto_channel = self.api.get_pluto_tv_channels()[0]
        if not channel or not pluto_channel:
            pytest.skip("There are no channels that have next/previous jump channels.")
        self.api.add_favorite_channel([channel, pluto_channel])
        self.menu_page.update_favorite_channels_list(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        self.guide_page.wait_for_screen_ready()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_number(channel)
        self.watchvideo_page.press_channel_up_button()
        self.watchvideo_assertions.verify_confirm_jump_channel_overlay_shown()
        self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_LAUNCH_APP)
        self.apps_and_games_assertions.verify_google_play_is_foreground()

    @pytest.mark.xray("FRUM-91279")
    @pytest.mark.p1_regression
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_91279_open_netflix_from_olg(self):
        channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=channels, app=self.menu_labels.LBL_NETFLIX)
        if channel_num is None:
            pytest.skip("Device does not have netflix app")
        channels = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True)
        if not channels:
            pytest.skip("Channels with no trickplay restriction found.")
        channel = channels[0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.open_olg()
        self.guide_page.enter_channel_number(channel_num)
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN, timeout=4000)
        self.watchvideo_page.press_ok_button()
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_17)

    @pytest.mark.xray("FRUM-91280")
    @pytest.mark.p1_regression
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_91280_launch_netflix_from_channel_surf(self):
        channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=channels, app=self.menu_labels.LBL_NETFLIX)
        if channel_num is None:
            pytest.skip("Device does not have netflix app")
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True)
        if channel is None:
            pytest.skip("No appropriate channels found.")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.enter_channel_number(channel_num)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_18)

    @pytest.mark.xray("FRUM-91284")
    @pytest.mark.test_stabilization
    def test_frum_91284_launch_netflix_from_prediction_bar(self):
        see_more_info = self.wtw_labels.LBL_WTW_INFO_CARDS_SEE_MORE_INFO
        self.home_page.back_to_home_short()
        show = self.service_api.get_show_from_feed_item_with_ott(ott_partner_id="tivo:pt.3455",
                                                                 feed_name="/predictions")
        self.home_page.log.info("Show name {}".format(show))
        if not show:
            pytest.skip("No show in prediction with OTT")
        show_name = show[0][0]
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show_name)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.wtw_page.select_menu(see_more_info)
        self.home_page.nav_to_all_episodes_listview()
        self.ott_deeplinking_page.nav_to_more_option()
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.ott_deeplinking_assertions.verify_ott_screen_with_package(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME,
                                                                       "NETFLIX")
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_21)

    @pytest.mark.livetv
    @pytest.mark.stop_streaming
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.usefixtures("setup_enable_full_screen_video_on_home")
    def test_t389366309_unplug_hdmi_whileon_LiveTV(self):
        """
        testrail: https://testrail.tivo.com//index.php?/tests/view/389366309
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, live=False, filter_channel=True)
        if channel is None:
            pytest.skip("No appropriate channels found.")
        self.home_page.goto_live_tv(channel[0][0])
        self.home_page.wait_for_screen_ready()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.turn_off_device_power(Settings.equipment_id)
        self.watchvideo_page.turn_on_device_power(Settings.equipment_id)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.tivo_plus
    @pytest.mark.parental_control
    def test_389366320_parental_controls_tivoplus_channel(self, request):
        self.home_page.back_to_home_short()
        request.getfixturevalue('setup_lock_parental_and_purchase_controls')
        tivoplus_channel = self.service_api.get_tivo_plus_channels()
        self.home_page.goto_live_tv(tivoplus_channel[0])
        self.home_page.wait_for_screen_ready()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_osd()
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_PIN_challenge_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_no_osd_on_screen()

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k_network_throttle
    @pytest.mark.usefixtures("reset_bandwidth_rule")
    def test_FRUM_15_throttle_bandwidth_during_4k_playback(self, request):
        channel = self.service_api.get_4k_channel()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(20)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_screen_resolution(self)
        self.watchvideo_page.init_ssh()
        self.watchvideo_page.wonder_restrict_bandwidth(2560, 2560)
        self.watchvideo_page.watch_video_for(20)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_screen_resolution_not_uhd(self)
        request.getfixturevalue('reset_bandwidth_rule')
        self.watchvideo_page.watch_video_for(20)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.ipppv
    @pytest.mark.cloud_core_rent_ppv
    def test_389366311_EAS_on_no_purchase_ppv(self):
        ppv_rental_channel = self.guide_page.get_ppv_rental_channel(self)
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(ppv_rental_channel)
        rented = \
            self.watchvideo_assertions.verify_current_program_of_ppv_channel_is_already_rented(self, ppv_rental_channel)
        if rented:
            self.guide_page.wait_for_current_show_to_finish()
        self.watchvideo_assertions.verify_text_in_watch_video_osd(self.liveTv_labels.LBL_IPPPV_RENTING_ALLOWED)
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.screen.base.press_exit_button(5)
        self.watchvideo_assertions.verify_text_in_watch_video_osd(self.liveTv_labels.LBL_IPPPV_RENTING_ALLOWED)

    @pytest.mark.live_tv_pause_timeout
    @pytest.mark.test_stabilization
    def test_live_tv_pause_time_out(self):
        """
        https://testrail.tivo.com//index.php?/cases/view/22764638
        Device resumes the playback when rolling buffer reaches to  pause time.
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        if not channel:
            pytest.skip("channel not found.")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.watchvideo_page.enter_channel_number(channel, confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING", timeout=(30 * 1000))
        self.watchvideo_page.show_info_banner()
        self.watchvideo_page.navigate_to_start_of_video()
        self.watchvideo_page.pause(30, "waiting for playback start")
        self.watchvideo_page.press_pause_button()
        self.watchvideo_page.pause(60, "waiting for device to resume the playback from pause")
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k_device_not_support
    def test_FRUM_20_device_not_support_4k_lower_resolution_playback(self):
        channel = self.service_api.get_4k_channel()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(20)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_screen_resolution_not_uhd(self)

    @pytest.mark.tivo_plus
    @pytest.mark.notapplicable(Settings.is_unmanaged(), reason="This test is only for managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11))
    @pytest.mark.xray("FRUM-33049")
    @pytest.mark.msofocused
    def test_tivoplus_switch_between_channels(self):
        '''
            :description: TiVo+ channels - switch between last watched channels
            Test Rail id: https://testrail.tivo.com//index.php?/tests/view/514088586
        '''

        tivo_plus_channel_list = self.api.get_tivo_plus_channels()
        if tivo_plus_channel_list == [] and len(tivo_plus_channel_list) < 2:
            pytest.skip("No Tivo plus channels or enough channels found")

        tivoplus_channel = tivo_plus_channel_list[0]
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(tivoplus_channel, confirm=True)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.press_ok_button()
        if self.watchvideo_page.is_tivo_plus_eula_overlay_shown():
            self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_ACCEPT)
            self.watchvideo_assertions.verify_tivo_plus_eula_osd_is_not_shown()
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(tivoplus_channel)
        self.guide_page.goto_one_line_guide_from_live(self)
        another_tivoplus_channel = tivo_plus_channel_list[1]
        self.guide_page.enter_channel_number(another_tivoplus_channel, confirm=True)
        self.guide_page.press_ok_button()
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(another_tivoplus_channel)
        self.watchvideo_page.press_exit_button()
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(tivoplus_channel)

    def test_C11678413_scroll_through_tivo_plus_channels(self):
        """
        https://testrail.tivo.com//index.php?/cases/view/11678413
        """
        self.home_page.go_to_guide(self)
        tivo_plus_channel_list = self.api.get_tivo_plus_channels()
        if tivo_plus_channel_list == []:
            pytest.skip("No Tivo plus channels found")
        if len(tivo_plus_channel_list) > 7:
            index = 7
        else:
            index = len(tivo_plus_channel_list)
        channel = tivo_plus_channel_list[0]
        self.guide_page.tune_to_tivo_plus_channel(self, channel)
        if self.watchvideo_page.is_tivo_plus_eula_overlay_shown():
            self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_ACCEPT)
            self.watchvideo_assertions.verify_tivo_plus_eula_osd_is_not_shown()
        for channel in tivo_plus_channel_list[:index]:
            self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
            self.watchvideo_page.watch_video_for(180)
            self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
            self.watchvideo_assertions.verify_channel_number(channel)
            self.screen.base.press_channel_up()
        for channel in tivo_plus_channel_list[index:0:-1]:
            self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
            self.watchvideo_page.watch_video_for(180)
            self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
            self.watchvideo_assertions.verify_channel_number(channel)
            self.watchvideo_page.press_channel_down_button()

    @pytest.mark.tivo_plus
    @pytest.mark.usefixtures('setup_cleanup_tivo_plus_channels')
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_C11678230_tivoplus_from_favorites(self):
        """
        https://testrail.tivo.com//index.php?/cases/view/11678230
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel = self.api.get_random_catch_up_channel_current_air(filter_channel=True,
                                                                   filter_socu=False,
                                                                   restrict=False)
        tivoplus_channel_list = self.api.get_tivo_plus_channels()
        if (tivoplus_channel_list == []) or (not channel):
            pytest.fail("Could not find desired channels")
        tivoplus_channel = random.choice(tivoplus_channel_list)
        self.api.add_favorite_channel([channel, tivoplus_channel])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=True)
        self.guide_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_page.find_channel_on_favorite_panel(tivoplus_channel)
        if self.watchvideo_page.is_tivo_plus_eula_overlay_shown():
            self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_ACCEPT)
            self.watchvideo_assertions.verify_tivo_plus_eula_osd_is_not_shown()
        self.watchvideo_assertions.verify_standard_info_banner_shown()
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()
        self.screen.base.press_channel_down()

    @pytest.mark.xray("FRUM-21978")
    @pytest.mark.usefixtures(
        "toggle_guide_rows_service_availability"
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18) else "switch_tivo_service_rasp")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Enter to Disconnected State. NoNetworkScreen is shown")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    def test_frum_21978_verify_olg_channel_options_overlay_when_servive_is_down_after_reboot(self):
        """
        Resiliency Mode - One Line Guide - Channel Options overlay
            Verify OLG functionality when service is down and then device rebooted
        Xray:
            https://jira.tivo.com/browse/FRUM-21978
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.open_olg(refresh=False, wait_olg_event=False, wait_olg_content=False)
        self.guide_assertions.smart_verify_guide_service_down_whisper(is_olg=True)
        self.watchvideo_page.enter_channel_number(channel, olg=True)
        self.guide_page.waiting_fail_open(is_olg=True)
        self.guide_page.get_to_channel_tab(is_olg=True)
        self.watchvideo_assertions.verify_channel_cell_is_currently_focused()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_CHANNEL_OPTIONS)
        self.watchvideo_page.select_menu(self.liveTv_labels.LBL_WATCH_NOW)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_number(channel)

    @pytest.mark.tivo_plus
    @pytest.mark.xray("FRUM-32852")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11))
    @pytest.mark.msofocused
    def test_514088581_tune_to_tivoplus_channel_from_guide(self):
        '''
        https://testrail.tivo.com//index.php?/tests/view/514088581
        TiVo+ channels - Tune to channel from Guide
        '''
        tivoplus_channel = self.api.get_tivo_plus_channels()[0]
        if not tivoplus_channel:
            pytest.skip("No Tivoplus channel found")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(tivoplus_channel, confirm=True)
        self.guide_page.press_ok_button()
        self.guide_page.wait_for_screen_ready()
        if self.watchvideo_page.is_tivo_plus_eula_overlay_shown():
            self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_ACCEPT)
            self.watchvideo_assertions.verify_tivo_plus_eula_osd_is_not_shown()
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(tivoplus_channel)

    @pytest.mark.internal_storage
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_486395024_low_memory_killer_case1(self):
        """
        RAM Status: ['Total', 'Free', 'used']
        Mem info will be displayed in KB.
        Play any playback beyond 3 hours
        Expected Result:
        TiVo app should not be crashing
        Screen transition is smooth and there is no delay or stalling when navigate within TiVo app.
        """
        ram, zram, lostram = self.home_page.screen.base.driver.meminfo_stats()
        self.home_page.log.info(f"RAM at Start: {ram} ZRAM {zram} LOSTRAM {lostram}")
        program = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True)
        if program is None:
            pytest.skip("Could not get any channel")
        channel_number = (program[0][0])
        channel = self.api.map_channel_number_to_currently_airing_offers(
            self.api.get_random_recordable_channel(channel_count=-1, filter_channel=True, use_cached_grid_row=True),
            self.api.channels_with_current_show_start_time(transport_type="stream", use_cached_grid_row=True), count=1)
        if not channel:
            pytest.skip("Recordable Channel Not Found")
        self.home_page.goto_live_tv(channel[0][1])
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.check_RAM_every_hour(self, channel_number)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.menu_page.go_to_accessibility(self)
        self.menu_assertions.verify_accessibility_screen_title(self)
        self.menu_page.go_to_one_pass_manager(self)
        self.home_assertions.verify_screen_title("ONEPASS MANAGER")
        self.vod_page.go_to_vod(self)
        self.home_page.go_to_what_to_watch(self)
        self.home_assertions.verify_view_mode(self.home_labels.LBL_WTW_SCREEN_MODE)

    @pytest.mark.tivo_plus
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11))
    @pytest.mark.xray("FRUM-33139")
    @pytest.mark.msofocused
    def test_tivoplus_tune_to_channel_from_OLG(self):
        '''
            :description: TiVo+ channels - Tune to TivoPlus channel from OLG
            TestrailID:https://testrail.tivo.com//index.php?/tests/view/514088582
        '''
        tivoplus_channel = self.api.get_tivo_plus_channels()[0]
        if not tivoplus_channel:
            pytest.skip("No Tivoplus channel found")
        self.home_page.go_to_guide(self)
        channel_number = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True)[0][0]
        self.watchvideo_page.enter_channel_number(channel_number, confirm=True)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.goto_one_line_guide_from_live(self)
        self.guide_page.enter_channel_number(tivoplus_channel, confirm=True)
        self.guide_page.press_ok_button()
        if self.watchvideo_page.is_tivo_plus_eula_overlay_shown():
            self.watchvideo_page.select_menu_by_substring(self.liveTv_labels.LBL_ACCEPT)
            self.watchvideo_assertions.verify_tivo_plus_eula_osd_is_not_shown()
        self.watchvideo_page.wait_for_LiveTVPlayback(status='PLAYING')
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(tivoplus_channel)

    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_enable_video_window")
    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k_stop_streaming
    def test_FRUM_427_watch_4k_stop_streaming(self):
        channel = self.service_api.get_4k_channel()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(20)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.turn_off_device_power(Settings.equipment_id)
        # need sleep for stop streaming for 5 minutes
        time.sleep(350)
        self.watchvideo_page.turn_on_device_power(Settings.equipment_id)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.screen.base.press_right()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=900000)
        self.home_assertions.verify_home_title()
        self.vod_assertions.verify_video_streaming()
        self.home_page.press_back_from_home_to_livetv(self)
        self.watchvideo_page.watch_video_for(30)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.internal_storage
    @pytest.mark.usefixtures("free_up_internal_memory_by_uninstalling")
    @pytest.mark.usefixtures("fill_internal_storage_by_installing_apps")
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_486395024_low_memory_killer_case2(self):
        ram, zram, lostram = self.home_page.screen.base.driver.meminfo_stats()
        self.home_page.log.info(f"RAM after installing few apps: {ram} ZRAM {zram} LOSTRAM {lostram}")
        program = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True)
        if program is None:
            pytest.skip("Could not get any channel")
        channel_number = (program[0][0])
        channel = self.api.map_channel_number_to_currently_airing_offers(
            self.api.get_random_recordable_channel(channel_count=-1, filter_channel=True, use_cached_grid_row=True),
            self.api.channels_with_current_show_start_time(transport_type="stream", use_cached_grid_row=True), count=1)
        if not channel:
            pytest.skip("Recordable Channel Not Found")
        self.home_page.goto_live_tv(channel[0][1])
        self.watchvideo_page.watch_video_for(60 * 240)
        ram, zram, lostram = self.home_page.screen.base.driver.meminfo_stats()
        self.home_page.log.info(f"RAM status after 4hr: RAM {ram} ZRAM {zram} LOSTRAM {lostram}")
        self.watchvideo_page.tune_to_channel(channel_number)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.perform_trickplay_operation(self, channel_number, 5)
        self.watchvideo_page.launch_installed_apps_and_check_RAM(self)
        ram, zram, lostram = self.home_page.screen.base.driver.meminfo_stats()
        self.home_page.log.info(f"RAM status: after launching few apps: RAM {ram} ZRAM {zram} LOSTRAM {lostram}")
        if Settings.is_managed():
            self.home_page.press_home_button()
        else:
            self.screen.base.press_back()

    @pytest.mark.iplinear
    # @pytest.mark.test_stabilization
    def test_demo_verify_video_quality(self):
        """
            Test to verify video quality
        """
        self.home_page.back_to_home_short()
        channels = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True)
        if not channels:
            pytest.skip("No appropriate channels found.")
        channel = channels[0]
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.enter_channel_number(channel, confirm=True)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.enter_channel_number(channels[1], confirm=True)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.fetch_video_quality_details(channel)

    @pytest.mark.msofocused
    @pytest.mark.lite_branding
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_43807_livetv_png_validation_lite_branding(self):
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        if not channel:
            pytest.skip("Failed to find any episodic channels")
        branding_image = self.guide_page.get_image_detail_from_branding_bundle_response(item="imageUrl",
                                                                                        item_value="primary_branding")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(20)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        dump_image = self.screen.get_screen_dump_item('brandingLogo')
        self.watchvideo_assertions.verify_branding_ui_bundle_logos(branding_image, dump_image)

    @pytest.mark.xray('FRUM-39241', 'FRUM-39267')
    @pytest.mark.msofocused
    @pytest.mark.parametrize("enable,is_relaunch_needed,is_package_add_needed", [(True, False, False), (False, False, True)])
    @pytest.mark.usefixtures("setup_cleanup_inactivity_timeout")
    @pytest.mark.usefixtures("cleanup_clear_app_data")  # adding this fixture due to https://jira.xperi.com/browse/IPTV-24982
    @pytest.mark.notapplicable(Settings.is_external_mso(), "Used IptvProvApi calls are not supported by external MSOs")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    def test_frum_39241_device_feature_search_update(self, enable, is_relaunch_needed, is_package_add_needed):
        """
        deviceFeatureSearch update when RemoteCommands.FEATURE_STATUS Command received:
        Feature Enabling: Configurable Inactivity Time

        Xray:
            https://jira.xperi.com/browse/FRUM-39241 (inactivityTime feature enabling)
            https://jira.xperi.com/browse/FRUM-39267 (inactivityTime feature disabling)
        """
        # Case (False, False, True) fails due to https://jira.xperi.com/browse/IPTV-24982
        channel = self.service_api.get_random_encrypted_unencrypted_channels(
            filter_channel=True, encrypted=True, transportType="stream")
        package = self.iptv_prov_api.get_fe_operator_name() + "-inactivityTime-5Minutes"
        self.home_page.back_to_home_short()
        self.iptv_prov_api.update_device_alacarte_package(package, is_add=enable)
        self.home_page.pause(5, "Waiting a bit for data to be updated on service side")
        param = {"autoStandbyInactivityTimeoutMinutes": "5"}
        self.api_assertions.verify_device_feature_search(DeviceFeatureSearchFeatures.INACTIVITY_TIME, param, enable)
        self.home_page.send_fcm_or_nsr_notification(NotificationSendReqTypes.NSR, RemoteCommands.FEATURE_STATUS)
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        # Inactivity OSD is shown after 5 minutes with no action + 30 seconds to catch OSD in log
        result = self.watchvideo_page.wait_for_osd_text(self.watchvideo_labels.LBL_INACTIVITY_TIME_OSD_TEXT, 330000)
        self.watchvideo_assertions.verify_error_overlay_not_shown()
        assert_that(result and enable or not result and not enable,
                    f"OSD text is {result} while it's expected to be {enable}")

    @pytestrail.case("C12786348")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.parametrize("feature, package_type", [(Settings.mdrm_ndvr_feature(),
                                                        FeAlacartePackageTypeList.NATIVE)])
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_12786348_nDVR_Completed_Recordings_Verimatrixordefault(self, request, feature, package_type):
        """
                    Test rail:
                    https://testrail.tivo.com/index.php?/cases/view/12786348
                    """
        recordable_channellist = self.api.get_recordable_channels()
        encrypted_channellist = self.api.get_encrypted_channel_list()
        intersection = set(recordable_channellist).intersection(encrypted_channellist)
        channel_list = list(intersection)
        if not channel_list:
            pytest.skip("No recordable encrpyted channel found")
        drm_type = self.api.provisioning_info_type(self.home_labels.LBL_NDVR_PROVISIONING_INFO_SEARCH)
        self.home_page.check_drmtype(self, request, drm_type, self.home_labels.KEY_DRM_ANDROID_DEFAULT,
                                     feature, FeAlacartePackageTypeList.VERIMATRIX)
        channel_number = random.choice(channel_list)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.VERIMATRIX, is_add=False)
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytestrail.case("C12786351" and "C12787148")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("cleanup_package_names_native")
    @pytest.mark.parametrize("feature, package_type",
                             [(Settings.mdrm_ndvr_feature(), FeAlacartePackageTypeList.VERIMATRIX)])
    def test_C12786351_C12787148_nDVR_Completed_Recordings_Widevineornative_to_Verimatrixordefault(self, request,
                                                                                                   feature, package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/12786351
        """
        recordable_channellist = self.api.get_recordable_channels()
        encrypted_channellist = self.api.get_encrypted_channel_list()
        intersection = set(recordable_channellist).intersection(encrypted_channellist)
        channel_list = list(intersection)
        if not channel_list:
            pytest.skip("No recordable encrpyted channel found")
        self.home_page.drm_update(self, request, feature, FeAlacartePackageTypeList.NATIVE)
        channel_number = random.choice(channel_list)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.NATIVE, is_add=False)
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytestrail.case("C12786349")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.usefixtures("cleanup_package_names_native")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.parametrize("feature, package_type",
                             [(Settings.mdrm_ndvr_feature(), FeAlacartePackageTypeList.NATIVE)])
    def test_C12786349_nDVR_Onepass_Recordings_Verimatrixordefault_to_Widevineornative(self, request, feature,
                                                                                       package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/12786348
        """
        recordable_channellist = self.api.get_recordable_channels()
        encrypted_channellist = self.api.get_encrypted_channel_list()
        intersection = set(recordable_channellist).intersection(encrypted_channellist)
        channel_list = list(intersection)
        if not channel_list:
            pytest.skip("No recordable encrpyted channel found")
        self.home_page.drm_update(self, request, feature, FeAlacartePackageTypeList.VERIMATRIX)
        self.api.cancel_all_onepass(Settings.tsn)
        nonrecordable_channellist = self.service_api.get_nonrecordable_channels()
        onepass_showlist = self.api.one_pass_currently_airing_shows(
            1, excludeChannelNumbers=nonrecordable_channellist)
        if not onepass_showlist:
            pytest.skip("No onepass channel found")
        onepass_showname = onepass_showlist[0][0]
        onepass_channel = onepass_showlist[0][1]
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready("GridGuide")
        self.guide_page.enter_channel_number(onepass_channel)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(onepass_showname)
        self.my_shows_page.select_show(onepass_showname)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.VERIMATRIX, is_add=False)
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(onepass_showname)
        self.my_shows_page.select_show(onepass_showname)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytestrail.case("C12786352")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.usefixtures("cleanup_package_names_native")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.parametrize(
        "feature, package_type", [(Settings.mdrm_ndvr_feature(), FeAlacartePackageTypeList.VERIMATRIX)])
    def test_C12786352_nDVR_Onepass_Recordings_Widevineornative_to_Verimatrixordefault(self, request, feature,
                                                                                       package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/12786351
        """
        self.home_page.drm_update(self, request, feature, FeAlacartePackageTypeList.NATIVE)
        self.api.cancel_all_onepass(Settings.tsn)
        nonrecordable_channellist = self.service_api.get_nonrecordable_channels()
        onepass_showlist = self.api.one_pass_currently_airing_shows(
            1, excludeChannelNumbers=nonrecordable_channellist)
        if not onepass_showlist:
            pytest.skip("No onepass channel found")
        onepass_showname = onepass_showlist[0][0]
        onepass_channel = onepass_showlist[0][1]
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready("GridGuide")
        self.guide_page.enter_channel_number(onepass_channel)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(onepass_showname)
        self.my_shows_page.select_show(onepass_showname)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.home_page.update_drm_package_names_native(feature, FeAlacartePackageTypeList.NATIVE, is_add=False)
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        self.home_page.relaunch_hydra_app()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(onepass_showname)
        self.my_shows_page.select_show(onepass_showname)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_59064_verify_user_to_play_three_hour_movies(self):
        """
        To verify user has ability to play 3 hour movies or shows without interruption in LiveTv
        FRUM-59064
        :return:
        """
        self.home_page.back_to_home_short()
        channel = self.api.get_random_encrypted_unencrypted_channels(duration=10800)[0][0]
        if not channel:
            pytest.skip("No appropriate channels found")
        self.home_page.goto_live_tv(channel)
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 60)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 60)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 58)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.usefixtures("enable_disable_stay_awake")
    @pytest.mark.stability
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_frum_71767_verify_twenty_four_hours_continuous_playback(self):
        """
        FRUM-71767
        Verify twenty four hours continuous playback
        :return:
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(transportType="stream", filter_channel=True)
        if not channel:
            pytest.skip("No appropriate channels found.")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.verify_long_hours_playback(self, no_of_hrs=6)

    @pytest.mark.p1_regression
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Managed Android only.")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16),
                               reason="Supported starting from frumos-1-16.")
    @pytest.mark.ndvr
    def test_frum64672_verify_recordings_button_in_watchvideo_screen(self):
        """
        testcase: https://jira.xperi.com/browse/FRUM-64672
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.home_page.press_recordings_button()
        self.my_shows_assertions.verify_recordings_menu_is_selected()

    @pytest.mark.p1_regression
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not Settings.is_managed(), reason="Managed Android only.")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16),
                               reason="Supported starting from frumos-1-16.")
    @pytest.mark.ndvr
    def test_frum76507_verify_accessibility_button_in_watchvideo_screen(self):
        """
        testcase: https://jira.xperi.com/browse/FRUM-76507
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.press_accessibility_button()
        self.watchvideo_assertions.verify_option_in_accessibility_strip(self.home_labels.TURN_SCREEN_READER_ON)

    @pytest.mark.full_regression_tests
    def test_frum_94800_verify_rewind_speed(self):
        """
        https://jira.xperi.com/browse/FRUM-94800
        """
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True)
        if channel is None:
            pytest.skip("No appropriate channels found.")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.navigate_to_end_of_video()
        self.watchvideo_page.watch_video_for(60 * 30)  # build cache for 30 minutes
        value0 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.screen.base.press_left()  # RWD
        self.watchvideo_assertions.is_rewind_focused(refresh=True)
        self.watchvideo_page.press_ok_button()
        value1 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_assertions.verify_time_diff_for_all_forward_or_rewind_speeds(self, False, 1, value0, value1)
        value2 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(0.5)
        value3 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_assertions.verify_time_diff_for_all_forward_or_rewind_speeds(self, False, 2, value2, value3)
        value4 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(0.5)
        value5 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_assertions.verify_time_diff_for_all_forward_or_rewind_speeds(self, False, 3, value4, value5)

    @pytest.mark.full_regression_tests
    def test_frum_99834_verify_forward_speed(self):
        """
        https://jira.xperi.com/browse/FRUM-99834
        """
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True)
        if channel is None:
            pytest.skip("No appropriate channels found.")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 30)  # build cache for 30 minutes
        self.watchvideo_page.navigate_to_start_of_video()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.home_page.log.info("verified playback...")
        value0 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.screen.base.press_right()  # FWD
        self.watchvideo_assertions.is_forward_focused(refresh=True)
        self.watchvideo_page.press_ok_button()
        value1 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_assertions.verify_time_diff_for_all_forward_or_rewind_speeds(self, True, 1, value0, value1)
        value2 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(0.5)
        value3 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_assertions.verify_time_diff_for_all_forward_or_rewind_speeds(self, True, 2, value2, value3)
        value4 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.pause(0.5)
        value5 = self.my_shows_page.get_trickplay_current_position_time(self)
        self.watchvideo_assertions.verify_time_diff_for_all_forward_or_rewind_speeds(self, True, 3, value4, value5)

    @pytest.mark.ipppv
    @pytest.mark.cloud_core_rent_ppv
    @pytest.mark.msofocused
    @pytest.mark.xray('FRUM-66504')
    def test_frum66504_tune_to_unpurchased_show(self):
        ppv_rental_channel = self.guide_page.get_ppv_rental_channel(self)
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(ppv_rental_channel)
        rented = \
            self.watchvideo_assertions.verify_current_program_of_ppv_channel_is_already_rented(self, ppv_rental_channel)
        if rented:
            self.guide_page.wait_for_current_show_to_finish()
        self.watchvideo_assertions.verify_text_in_watch_video_osd(self.liveTv_labels.LBL_IPPPV_RENTING_ALLOWED)

    @pytest.mark.parametrize("is_olg", [(True)])
    @pytest.mark.parametrize("icon, expected",
                             [("new", True), ("new", False), ("ppv", True), ("ppv", False), ("socu", True), ("socu", False),
                              ("non_rec_pg", True), ("non_rec_pg", False), ("non_req_crr", True), ("non_req_crr", False)])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/oneLineGuideCells are supported since Hydra v1.18")
    @pytest.mark.usefixtures("setup_prepare_params_for_guide_cells_test")
    @pytest.mark.socu
    def test_frum_32627_checking_olg_tile_icons_olg_req(self, request, icon, expected, is_olg):
        """
        Verifying NEW, PPV, SOCU, non-recordable icons on OLG Tiles basing on /v1/oneLineGuideCells (OpenAPI request)

        Xray:
            https://jira.xperi.com/browse/FRUM-32627
            https://jira.xperi.com/browse/FRUM-26521
        """
        params_for_test = request.config.cache.get("params_for_test", None)
        if icon == "ppv" and expected:
            # Let's tune to playable channel and then find PPV one to avoid PPV playback failures
            channel = self.service_api.get_random_channel_from_guide_rows(
                get_playable_live_tv=True, is_ppv=False, exclude_tplus_channels=True, exclude_plutotv_channels=True)[0][2]
        tune_to_chan = params_for_test["channel_number"] if not (icon == "ppv" and expected) else channel.channel_number
        self.home_page.goto_live_tv(tune_to_chan, confirm=True, highlight_live_program=False)
        if icon != "ppv":
            self.watchvideo_assertions.verify_video_playback_started()
        self.watchvideo_page.open_olg()
        self.watchvideo_page.enter_channel_number(params_for_test["channel_number"], confirm=False)
        # To avoid OLG disappearing due to 15 seconds timeout due to inactivity
        self.watchvideo_page.press_up_button(refresh=False)
        self.watchvideo_page.press_down_button(refresh=False)
        self.guide_page.get_to_channel_tab(is_olg=True)
        self.guide_page.move_highlight_to_a_cell(params_for_test["steps"])
        icon_tmp = "socu_guide_header" if icon == "socu" else params_for_test["icon"]
        self.guide_assertions.verify_icon_olg_highilighted_tile(self, icon_tmp, expected)

    @pytest.mark.xray('FRUM-103562')
    @pytest.mark.test_stabilization
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    def test_frum_103562_verify_program_time_on_info_bar_and_system_time(self):
        """
        https://jira.xperi.com/browse/FRUM-103562
        """
        channel = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True)
        if channel is None:
            pytest.skip("No appropriate channels found.")
        self.home_page.goto_live_tv(channel[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_program_time_and_system_time(self)
        self.watchvideo_page.verify_program_time_and_sys_time_for_next_few_channels(self)

    @pytest.mark.xray('FRUM-18687')
    @pytest.mark.notapplicable(not Settings.is_hotwire())
    def test_frum_18687_switch_btw_aac_and_ac3(self):
        audio_ac3_channel = self.service_api.get_random_ac3_audio_channel()
        audio_aac_channel = self.service_api.get_random_aac_audio_channel()
        audios = [audio_ac3_channel, audio_aac_channel]
        for audio in audios:
            self.home_page.goto_live_tv(audio)
            self.watchvideo_page.show_info_banner()
            self.watchvideo_assertions.verify_full_info_banner_is_shown()
            self.watchvideo_page.select_strip(self.liveTv_labels.LBL_CHANGE_AUDIO_TRACK)
            self.watchvideo_assertions.verify_overlay_shown()
            self.watchvideo_assertions.verify_overlay_title(self.liveTv_labels.LBL_AUDIO_TRACK_OVERLAY_TITLE)
            self.home_page.back_to_home_short()

    @pytest.mark.xray('FRUM-108796')
    @pytest.mark.test_stabilization
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_frum_108796_verify_parental_control_message_is_not_shown_when_it_is_not_blocked(self):
        """
        https://jira.xperi.com/browse/FRUM-108796
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.go_to_set_rating_limit(self)
        self.menu_page.set_rating_limits(rated_movie=self.menu_labels.LBL_ALLOW_ALL_HIGHEST_ALLOWED_RATING,
                                         rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         unrated_tv_show=self.menu_labels.LBL_ALLOW_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_ALLOW_ALL_UNRATED)
        self.menu_page.menu_press_back()
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        channel = self.api_parser.get_streamable_channel_list_with_unrated_shows()
        if not channel:
            pytest.skip("could not find unrated channel")
        self.home_page.goto_live_tv(random.choice(channel))
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=False)
        channel = self.guide_page.get_streamable_rating_content(self)
        if not channel:
            pytest.skip("could not find rating channel")
        self.home_page.goto_live_tv(random.choice(channel))
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=True)
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_PIN_challenge_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(shown=False)

    @pytest.mark.cloud_core_liveTV
    @pytest.mark.frumos_18
    @pytest.mark.infobanner
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/airing is supported since Hydra v1.18")
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_frum_96502_verify_banner_title_and_up_next_info(self):
        """
        Watch asset 90 minutes in a row on a single channel checking each 15 minutes that show current info
        and up next data is correct
        """
        # TODO filter out device type restricted channels (restrictedDeviceType)
        items = self.service_api.get_random_channel_from_guide_rows(get_playable_live_tv=True,
                                                                    exclude_tplus_channels=True,
                                                                    exclude_plutotv_channels=True,
                                                                    is_ppv=False,
                                                                    duration_gt=1800,
                                                                    duration_lt=1800
                                                                    )
        if not items:
            pytest.skip("No appropriate channels found")
        item = items[0]
        self.home_page.log.info(f"Channel selected: {item[0]}")
        self.home_page.goto_live_tv(item[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_page.navigate_to_end_of_video()
        for i in range(8):
            self.home_page.log.info(f"Iteration {i} has started")
            airing_dict = self.service_api.get_airing(item[2].station_id)
            current_title = airing_dict["airing_show"].title
            up_next_title = airing_dict["upcoming_list"][0].title
            self.home_page.log.info(f"Expected current title: {current_title}  Expected next: {up_next_title}")
            self.watchvideo_page.show_trickplay_if_not_visible(refresh=True)
            self.watchvideo_assertions.verify_show_title(current_title)
            self.watchvideo_assertions.verify_up_next_of_info_baner_header(up_next_title)
            self.watchvideo_page.pause(900, "Watching LiveTV without any actions during 15 min")

    @pytest.mark.cloud_core_liveTV
    @pytest.mark.frumos_18
    @pytest.mark.infobanner
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/airing is supported since Hydra v1.18")
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_97188_verify_banner_title_and_up_next_info_for_past_show(self):
        """
        Rewind to the back of the cache and verify that information about current show and up next is correct.
        Then return back to current time and check title and "up next" again.
        """
        # TODO filter out trickplay restricted channels (trickplayRestriction)
        # TODO filter out device type restricted channels (restrictedDeviceType)
        items = self.service_api.get_random_channel_from_guide_rows(get_playable_live_tv=True,
                                                                    exclude_tplus_channels=True,
                                                                    exclude_plutotv_channels=True,
                                                                    is_ppv=False,
                                                                    duration_gt=1800
                                                                    )
        if not items:
            pytest.skip("No appropriate channel found")
        item = items[0]
        self.home_page.log.info(f"Channel selected: {item}")
        self.home_page.goto_live_tv(item[0])
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
        self.watchvideo_assertions.verify_livetv_mode()
        # Rewind to the beginning of the cache and check title and up next info
        self.watchvideo_page.fast_navigate_to_start_of_video()
        self.watchvideo_page.show_trickplay_if_not_visible(refresh=True)
        airing_time_utc_open_api_format = self.watchvideo_page.get_cache_start_time_utc_open_api_str()
        airing_dict = self.service_api.get_airing(item[2].station_id, airing_time_utc_open_api_format)
        title = airing_dict["airing_show"].title
        up_next_title = airing_dict["upcoming_list"][0].title
        self.home_page.log.info(f"Back in cache verify expect title: {title} next: {up_next_title}")
        self.watchvideo_assertions.verify_show_title(title)
        self.watchvideo_assertions.verify_up_next_of_info_baner_header(up_next_title)
        # Fast forward to live point and verify title and up next again
        self.watchvideo_page.fast_navigate_to_end_of_video()
        airing_dict = self.service_api.get_airing(item[2].station_id)
        title = airing_dict["airing_show"].title
        up_next_title = airing_dict["upcoming_list"][0].title
        self.home_page.log.info(f"Live point again verify expect title: {title}  Expect next: {up_next_title}")
        self.watchvideo_assertions.verify_show_title(title)
        self.watchvideo_assertions.verify_up_next_of_info_baner_header(up_next_title)

    @pytest.mark.stop_streaming
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.usefixtures("setup_enable_full_screen_video_on_home")
    def test_device_to_be_remain_in_standby_mode(self):
        self.home_page.go_to_home_screen(self)
        self.watchvideo_page.turn_off_device_power(Settings.equipment_id)
        self.home_page.wait_for_screen_saver(time=self.guide_labels.LBL_SCREEN_SAVER_WAIT_TIME)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        # waiting for 10 minutes  to make sure app is not going out of standby on its own
        time.sleep(600)
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.watchvideo_page.turn_on_device_power(Settings.equipment_id)
        self.screen.base.press_right()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=900000)

    @pytest.mark.infobanner
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.notapplicable(Settings.is_apple_tv(),
                               reason="AppleTV are not supported intents.")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/airing is supported since Hydra v1.18")
    def test_frum_117520_verify_full_info_banner_after_screensaver(self):
        """
        FRUM-117520
        Verify data in Full Info Banner is correct after returning from Screensaver to LiveTV
        (comparing screendump data and v1/airing data)
        """
        items = self.service_api.get_random_channel_from_guide_rows(get_playable_live_tv=True,
                                                                    exclude_tplus_channels=True,
                                                                    exclude_plutotv_channels=True,
                                                                    is_ppv=False,
                                                                    duration_gt=1800,
                                                                    duration_lt=1800
                                                                    )
        item = items[0]
        self.home_page.log.info(f"Channel selected for tuning: {item}")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(item[0])
        self.screen.base.start_screensaver()
        self.watchvideo_assertions.verify_foreground_package_name(Settings.screen_saver_package)
        self.screen.base.press_enter()
        airing_dict = self.service_api.get_airing(item[2].station_id)
        current_title = airing_dict["airing_show"].title
        up_next_title = airing_dict["upcoming_list"][0].title
        self.home_page.log.info(f"Expected current title: {current_title}  Expected next: {up_next_title}")
        self.watchvideo_page.show_trickplay_if_not_visible(refresh=True)
        self.watchvideo_assertions.verify_show_title(current_title)
        self.watchvideo_assertions.verify_up_next_of_info_baner_header(up_next_title)

    @pytest.mark.frumos_19
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.infobanner
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guide_rows is supported since Hydra v1.18")
    def test_frum_119008_stop_recording_from_info_banner(self,
                                                         get_and_restore_tcdui_test_conf,  # noqa: F811
                                                         increase_timeout_of_widgets_in_watch_video_screen,  # noqa: F811
                                                         ):
        """
        Verify behavior when cancelling an in-progress recording from Action in Full Info Banner,
        in this test case overrided timeout for Info Banner is used
        """
        items = self.service_api.get_random_channel_from_guide_rows(get_playable_live_tv=True,
                                                                    is_recordable_show=True
                                                                    )
        item = items[0]
        self.home_page.log.info(f"Channel selected for tuning: {item}")
        # Schedule recording by using service api request
        self.service_api.record_this_content(item[1].content_id, item[1].offer_id)
        # Select 'Stop Recording' action in Full Info Banner
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(item[0])
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout + 12)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.press_down_button()
        self.screen.get_json()
        self.watchvideo_page.select_strip(self.liveTv_labels.LBL_STOP_RECORDING)
        self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_STOP_RECORDING_OVERLAY)
        self.watchvideo_page.nav_to_menu_by_substring(self.liveTv_labels.LBL_STOP_AND_DELETE)
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_page.pause(4)
        # Verify red dot is not visible
        self.watchvideo_page.show_trickplay_if_not_visible(refresh=True)
        self.watchvideo_assertions.verify_red_dot_is_displayed_on_trickplay(status=False)

    @pytest.mark.frumos_19
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.infobanner
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guide_rows is supported since Hydra v1.18")
    def test_frum_122309_start_over_action_from_info_banner(self,
                                                            get_and_restore_tcdui_test_conf,  # noqa: F811
                                                            increase_timeout_of_widgets_in_watch_video_screen,  # noqa: F811
                                                            ):
        """
        Verify SOCU is started successfully from Full Info Banner action strip,
        in this test case overrided timeout for Info Banner is used
        """
        items = self.service_api.get_random_channel_from_guide_rows(get_playable_live_tv=True,
                                                                    get_playable_socu=True
                                                                    )
        item = items[0]
        self.home_page.log.info(f"Channel selected for tuning: {item}")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(item[0])
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout + 12)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.press_down_button()
        self.screen.get_json()
        self.watchvideo_page.select_strip(self.liveTv_labels.LBL_START_OVER)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_VOD_VIEWMODE)

    @pytest.mark.frumos_19
    @pytest.mark.cloud_core_rent_ppv
    def test_frum_119593_purchase_on_ppv_show_from_action_screen(self,
                                                                 refresh_ppv_credit_limit,  # noqa: F811
                                                                 ):
        """
        Verify user can purchase on ppv show from LiveTV by pressing OK on PPV OSD
        """
        ppv_rental_channel = self.api.get_ppv_channel_which_can_be_rented_soon()
        self.home_page.log.info(f"Channel selected for tuning and wait time for offer: {ppv_rental_channel}")
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.home_page.goto_livetv_short(self)
        self.watchvideo_page.tune_to_channel(ppv_rental_channel[0]["channel_number"])
        self.watchvideo_page.pause(ppv_rental_channel[0]["wait_time_sec"], reason="waiting time for purchase window")
        self.watchvideo_assertions.verify_text_in_watch_video_osd(self.liveTv_labels.LBL_IPPPV_RENTING_ALLOWED)
        # verify video is blanked
        self.vod_assertions.verify_video_blanking_status(state="true")
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.press_select_verify_confirm_purchase_overlay()
        self.guide_assertions.press_select_verify_ppv_purchase_confirm_overlay()
        # verify video is unblanked after renting
        self.vod_assertions.verify_video_blanking_status(state="false")
        self.screen.base.press_back()
        self.watchvideo_assertions.verify_osd_text(self.liveTv_labels.LBL_IPPPV_RENTING_ALLOWED, expected=False)
        self.watchvideo_assertions.verify_livetv_mode()

    @pytest.mark.reference_4k
    def test_128880_check_livetv_4k_resolution(self):
        """
        FRUM-128880
        Test to check resolution on 4k devices
        """
        channel = self.service_api.get_4k_channel()
        if not channel:
            pytest.skip("No channel found")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.show_network_osd()
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.test_stabilization
    @pytest.mark.hevc
    @pytest.mark.notapplicable(
        not (Settings.is_puck and Settings.is_cc3), reason="HEVC is currently supported in cc3 sei managed device")
    def test_frum_130428_hevc_linear_playback(self):
        """
        Verify linear playback of hevc channel
        """
        channel_list = self.watchvideo_page.get_channel_list_from_open_api()
        hevc_channel = self.service_api.get_hevc_channel(channel_list)
        if not hevc_channel:
            pytest.skip("No HEVC channel found")
        self.home_page.goto_live_tv(hevc_channel[0], confirm=False)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.test_stabilization
    @pytest.mark.hevc
    @pytest.mark.notapplicable(
        not (Settings.is_puck and Settings.is_cc3), reason="HEVC is currently supported in cc3 sei managed device")
    def test_frum_130431_hevc_socu_playback(self):
        """
        Verify SoCu playback on hevc channel
        """
        channel_list = self.watchvideo_page.get_channel_list_from_open_api()
        hevc_channel = self.service_api.get_hevc_channel(channel_list, SoCu=True)
        if not hevc_channel:
            pytest.skip("No HEVC channel found with socu")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(hevc_channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.guide_assertions.verify_play_normal()

    @pytest.mark.test_stabilization
    @pytest.mark.hevc
    @pytest.mark.notapplicable(
        not (Settings.is_puck and Settings.is_cc3), reason="HEVC is currently supported in cc3 sei managed device")
    def test_frum_130432_hevc_nDVR_playback(self):
        """
        Verify nDVR playback on hevc channel
        """
        channel_list = self.watchvideo_page.get_channel_list_from_open_api()
        hevc_channel = self.service_api.get_hevc_channel(channel_list, nDVR=True)
        if not hevc_channel:
            pytest.skip("No recordable HEVC channel")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(hevc_channel[0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    def test_FRUM_136725_trickplay_actions_on_4k_socu_content(self, record_property):
        """
        Verify trickplay actions on 4k socu content
        """
        channel_4k = self.service_api.get_4k_channel(socu=True)
        no_trickplay_restriction_channellist = self.api.get_channels_with_no_trickplay_restrictions()
        intersection = set(channel_4k).intersection(no_trickplay_restriction_channellist)
        channel = list(intersection)
        if not channel:
            pytest.skip("No 4k content available without trickplay restrictions")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        record_property("channel_number", channel)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_TEN_SECONDS)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_screen_resolution(self)
        if not self.guide_page.get_trickplay_visible():
            self.guide_page.screen.base.press_enter()
        # to verify fast forward
        self.guide_page.fast_forward_show(self, 1)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX1)
        self.vod_page.press_play_pause_button()
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_THIRTY_SECONDS)
        self.watchvideo_assertions.verify_playback_play()
        if not self.guide_page.get_trickplay_visible():
            self.guide_page.screen.base.press_enter()
        # to verify rewind
        self.guide_page.rewind_show(self, 1)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX1)
        self.vod_page.press_play_pause_button()
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_TEN_SECONDS)
        self.watchvideo_assertions.verify_playback_play()
        # to verify advance
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_TEN_SECONDS)
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_advance_move(self, current_position)
        # to verify replay
        self.watchvideo_page.watch_video_for(60 * 2)
        current_position = self.my_shows_page.get_trickplay_current_position_time(self)
        self.my_shows_page.validate_replay(self, current_position, key_press=15)
        self.watchvideo_page.watch_video_for(self.guide_labels.LBL_TEN_SECONDS)
        self.watchvideo_assertions.verify_screen_resolution(self)
