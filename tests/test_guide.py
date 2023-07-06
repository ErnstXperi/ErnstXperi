"""
Created on Sept 7, 2017

@author: tboroffice
"""

import time
import json
import random
from datetime import datetime, timedelta

import pytest
from hamcrest import assert_that, is_, has_entries

from set_top_box.test_settings import Settings
from set_top_box.conftest import get_and_restore_tcdui_test_conf
from set_top_box.conf_constants import FeAlacarteFeatureList, FeAlacartePackageTypeList, HydraBranches, \
    DeviceInfoStoreFeatures, FeaturesList, BodyConfigFeatures, DateTimeFormats, NotificationSendReqTypes, \
    RemoteCommands, LongevityConstants
from set_top_box.client_api.home.conftest import cleanup_package_names_native,\
    preserve_initial_package_state, remove_packages_if_present_before_test, setup_cleanup_return_initial_feature_state, \
    decrease_screen_saver, setup_disable_stay_awake, cleanup_sign_in_and_skip_ftux, back_to_home
from set_top_box.client_api.guide.conftest import setup_guide, setup_prepare_params_for_guide_cells_test, \
    switch_tivo_service_rasp, remove_channel_package_sports, setup_cleanup_list_favorite_channels_in_guide, \
    setup_add_favorite_channels_in_guide, toggle_mind_availability, toggle_guide_rows_service_availability, \
    unsubscribed_channel_check
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_bind_hsn
from set_top_box.shared_context import ExecutionContext
from set_top_box.client_api.my_shows.conftest import setup_cleanup_myshows, setup_delete_book_marks, \
    setup_my_shows_sort_to_date, setup_myshows_delete_recordings
from set_top_box.client_api.Menu.conftest import disable_parental_controls, \
    setup_cleanup_parental_and_purchase_controls, setup_enable_closed_captioning, setup_parental_control, \
    disable_video_providers, enable_video_providers, setup_disable_closed_captioning, \
    set_one_pass_record_option_to_new_only, remove_parental_controls__from_pps
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions  # noqa: F401
from pytest_testrail.plugin import pytestrail
from set_top_box.client_api.account_locked.conftest import cleanup_enabling_internet
from tools.utils import DateTimeUtils
from mind_api.dependency_injection.entities.branding import Branding
from mind_api.middle_mind.field import tivo_partner_stations_backup


@pytest.mark.usefixtures("setup_guide")
@pytest.mark.usefixtures("is_service_guide_alive")
@pytest.mark.guide
@pytest.mark.timeout(Settings.timeout)
class TestGuideScreen(object):

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_323719_guide_verify_overlay(self):
        self.home_page.go_to_guide(self)
        self.guide_assertions.press_select_and_verify_overlay()

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_323740_guide_nav_to_channel(self):
        channel_number = self.service_api.get_random_channel(Settings.tsn, "entitled", mso=Settings.mso)
        if not channel_number:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_assertions.verify_channel_found(channel_number)

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_323720_guide_watch_channel(self):
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_watch_channel(self, "105")
        self.watchvideo_assertions.verify_live_tv_details(self)

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_326330_guide_nav_to_on_now_on_channel(self):
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_focus_on_channel_airing_now_program(self, "105")
        self.guide_page.select_and_watch_program(self)

    @pytest.mark.timeout(Settings.timeout)
    def test_326332_guide_record_from_on_now_on_channel(self):
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_focus_on_channel_airing_now_program(self, "7105")
        self.guide_page.select_and_record_program(self)
        self.guide_page.select_and_cancel_program_recording()

    @pytestrail.case("C11123831")
    @pytest.mark.favorite_channels
    @pytest.mark.xray("FRUM-279")
    @pytest.mark.msofocused
    @pytest.mark.devhost
    @pytest.mark.iplinear
    @pytest.mark.usefixtures("setup_parental_control",
                             "setup_add_favorite_channels_in_guide",
                             "setup_cleanup_list_favorite_channels_in_guide")
    @pytest.mark.timeout(Settings.timeout)
    def test_328476_list_favorite_channels_in_guide(self):
        """
        328476
        Go to Guide and change channel options to view only Favorite Channels
        :return:
        """
        self.home_page.go_to_guide(self)
        self.guide_page.get_live_program_name(self)
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        # The Telus Box does not show that guide has been switched to favortite channels
        # unless you go back home and then go back to guide
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_channel_option(self.guide_labels.LBL_FAVORITE_CHANNELS_TIP_TEXT)

    # @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_326330_launch_guide_and_watch_live_tv(self):
        """
        326330
        Verify User is able to stream live programs by selecting any program in Guide
        :return:
        """
        self.home_page.go_to_guide(self)
        self.guide_page.select_and_watch_program(self)

    @pytestrail.case("C10838517")
    @pytest.mark.xray("FRUM-44")
    @pytest.mark.devhost
    @pytest.mark.msofocused
    @pytest.mark.sanity
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    def test_289569_one_line_guide_entry(self):
        """
        289569
        Verify OneLineGuide displays and highlight tile.
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                             transportType="stream")[0][0]
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.goto_live_tv(channel, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.timestamp_test_start()
        self.guide_page.goto_one_line_guide_from_live(self)
        self.guide_page.exit_one_line_guide()
        self.guide_page.timestamp_test_end()

    @pytestrail.case("C11123836")
    @pytest.mark.devhost
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.xray("FRUM-281")
    @pytest.mark.msofocused
    def test_365014_channel_up_down(self):
        """
        365014
        To verify channel up/down
        :return:
        """
        self.home_page.go_to_guide(self)
        self.guide_page.select_and_watch_program(self)
        self.guide_page.go_up_down_channels_on_guide(2)
        self.guide_page.exit_one_line_guide()

    @pytestrail.case("C10838516")
    @pytest.mark.xray('FRUM-45')
    @pytest.mark.sanity
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings", "setup_parental_control", "setup_cleanup_myshows")
    def test_328268_create_one_pass_and_verify(self):
        """
        328268
        Creating OnePass and checking that the created onepass is listing under onepass manager or not.
        :return:
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if channel is None:
            pytest.fail("Could not find any episodic channel")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        program = self.guide_page.create_one_pass_on_record_overlay(self)
        self.menu_page.go_to_one_pass_manager(self)
        self.home_assertions.verify_show_in_one_pass_manager(self, program)

    @pytestrail.case("C11123825")
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-272")
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device does not have Jump Channels")
    @pytest.mark.notapplicable(Settings.is_ruby() or Settings.is_jade(), reason="Netflix is not supported")
    def test_204422_jump_channel(self):
        """
        204422
        Verify that the assigned channel given for the TiVo application launches that application
        :return:
        """
        channels = self.service_api.get_jump_channels_list()
        if not channels:
            pytest.skip("Could not find any channel.")
        channel_num = random.choice(self.guide_page.check_channel_availability(self, channels))
        channel = self.service_api.get_random_encrypted_unencrypted_channels(Settings.tsn, filter_channel=True,
                                                                             transportType="stream")
        if channel is None:
            pytest.skip("Could not find any channel. hence skipping")
        self.home_page.goto_live_tv(channel[0][0])
        self.home_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        dump = False if Settings.is_apple_tv() else True
        olg = True if Settings.is_apple_tv() else False
        if Settings.is_apple_tv():
            self.watchvideo_page.open_olg()
        self.guide_page.enter_channel_number(channel_num, confirm=True, dump=dump, olg=olg)
        self.guide_page.pause(10)
        self.guide_assertions.verify_jump_channel_launch(Settings.app_package, enter=False)

    @pytestrail.case("C12790639")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-176")
    @pytest.mark.msofocused
    @pytest.mark.guide
    # @pytest.mark.test_stabilization
    def test_5424269_grid_guide_entry_default_program_channel_time(self):
        """
        Verify default program, channel and time in Grid Guide.

        Testrail:
            https://testrail.corporate.local/index.php?/cases/view/5424269
        """
        channel_number = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                                    transportType="stream")[0][0]
        if not channel_number:
            pytest.skip("Could not find any channel.")
        self.home_page.goto_live_tv(channel_number)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        current_show_title = self.watchvideo_page.get_show_title()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.wait_for_guide_next_page()
        self.guide_page.wait_for_header_rendering()
        data = self.guide_page.screen.get_json()
        self.guide_page.get_grid_focus_details(data)
        self.guide_assertions.verify_in_current_guide(data)
        self.guide_assertions.verify_channel_of_highlighted_program_cell(channel_number, data)
        self.guide_assertions.verify_show_title(current_show_title, "guide_cell")

    @pytestrail.case("C12790644")
    @pytest.mark.p1_regression
    @pytest.mark.guide
    @pytest.mark.timeout(Settings.timeout)
    def test_289570_one_line_guide_option_menu_item_check(self):
        """
        289570
        Verify pressing SELECT and PLAY on OneLineGuide displays RecordingOptions when no recording exists for the show.
        :return:
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.back_to_home_short()
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.one_line_guide_options(self)

    @pytestrail.case("C11123844")
    @pytest.mark.devhost
    @pytest.mark.xray("FRUM-289")
    @pytest.mark.msofocused
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_94988_trickplay_bar_live_tv(self):
        """
        94988
        To verify correct status bar icon displays during various TrickPlay modes/speeds while in watching Live TV.
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("Could not get any channel")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_assertions.verify_play_normal()
        self.guide_page.rewind_show(self, 3)
        self.screen.base.press_playpause()
        self.guide_page.fast_forward_show(self, 3)
        self.screen.base.press_playpause()
        self.guide_page.pause_show(self)
        self.screen.base.press_playpause()

    @pytestrail.case("C11123829")
    @pytest.mark.devhost
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout_mid)
    def test_323714_verify_2_weeks_of_upcoming_guide_data(self):
        """
        323714
        Verify the amount of Guide data displayed in from the current time into to the future
        (displayed to the right side of the channel column).
        :return:
        """
        self.home_page.go_to_guide(self)
        self.guide_page.move_days_forward(self, days=12)

    @pytestrail.case("C11123830")
    @pytestrail.case("C21566943")
    @pytest.mark.devhost
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.frumos_15
    def test_323715_C21566943_verify_previous_guide_data_days_grid_guide(self):
        """
        323715
        Verify that past content available on guide is for no. of days equal to that published from brandingbubdle.
        Fallback is to 3 days of program data if epg value is not published in bundle or if bundle get fails.
        Publishing of epglookbackhours (further converted to number of days) is done from service console because
        repetitive publishing through automation cases is not recommended on all environments.
        :return:
        """
        Epg_Past_Number_of_Days = self.guide_page.get_epgLookBackHours(self)
        self.home_page.go_to_guide(self)
        self.guide_page.move_days_backward(self, days=Epg_Past_Number_of_Days)

    @pytestrail.case("C11123832")
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.xray("FRUM-280")
    @pytest.mark.msofocused
    def test_355106_verify_alternate_audio(self):
        """
        355106
        Verify alternate audio on Full Info Banner in Live TV
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(Settings.tsn, filter_channel=True,
                                                                             transportType="stream")
        if channel is None:
            pytest.skip("Could not get any channel")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.change_audio(self)

    @pytestrail.case("C10838515")
    @pytest.mark.xray("FRUM-47")
    @pytest.mark.sanity
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused
    def test_355038_verify_encrypted(self):
        """
        355038 - Part1
        Verify Encrypted content playback on Live TV for HD and SD content.
        :return:
        """
        if Settings.mso.lower() == "rcn":
            channel_number = self.service_api.get_random_channel(Settings.tsn,
                                                                 "entitled", mso=Settings.mso, filter_channel=True)
        else:
            channel = self.service_api.get_random_encrypted_unencrypted_channels(Settings.tsn,
                                                                                 encrypted=True, filter_channel=True)
            channel_number = (channel[0][0])
        if not channel_number:
            pytest.skip("Could not find any channel.")
        self.guide_page.verify_channel(self, channel_number)

    @pytestrail.case("C10840399")
    @pytest.mark.xray('FRUM-47')
    @pytest.mark.sanity
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif("rcn" in Settings.mso.lower() or "tds" in Settings.mso.lower() or "usqe1" in
                        Settings.test_environment.lower(),
                        reason="Case is skipped as there are no uncnrypted channels in mso-rcn,tds or test_environment-usqe1")
    def test_355038_verify_unencrypted(self):
        """
         355038 - Part2
        Verify unencrypted content playback on Live TV for HD and SD content.
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(Settings.tsn,
                                                                             encrypted=False,
                                                                             )
        if not channel:
            pytest.skip("Could not find any channel.")
        channel_number = channel[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.watch_channel(self, channel_number)
        self.vod_assertions.verify_view_mode(self.guide_labels.LBL_LIVE_TV_VIEW_MODE, dump=False)

    # @pytestrail.case("C11116856")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.xray('FRUM-62292')
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    def test_355570_guide_catchup_icon_past(self):
        """
        355570
        Check the Catchup icon display on program cell for the show in past in the Grid Guide
        :return:S
        """
        channels = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                            filter_channel=True,
                                                                            filter_socu=True,
                                                                            restrict=False)
        if channels is None:
            pytest.skip("No channel found")
        channel = (channels[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.menu_page.menu_navigate_left_right(2, 0)
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell", True)

    @pytestrail.case("C10838520")
    @pytest.mark.xray('FRUM-42')
    @pytest.mark.sanity
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.cloud_core_vod_socu
    @pytest.mark.timeout(Settings.timeout)
    def test_355719_guide_socu_playback_past(self):
        """
        355719
        Verify actions from Record Overlay to playback of a past SOCU offer from the Guide
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.menu_page.menu_navigate_left_right(4, 0)
        self.guide_page.wait_for_guide_next_page()
        focused_item = self.guide_page.get_focussed_grid_item(self)
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)

    @pytestrail.case("C10838521")
    @pytest.mark.xray('FRUM-40')
    @pytest.mark.sanity
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.cloud_core_vod_socu
    @pytest.mark.timeout(Settings.timeout)
    def test_355718_guide_socu_playback(self):
        """
        355718
        Verify the behavior when pressing OK/SELECT on the "Watch now from CATCHUP_NAME"
        action in the Record overlay  from the Guide.
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
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

    # MOVED to BAT from SANITY
    @pytestrail.case("C11123826")
    @pytest.mark.devhost
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures("setup_parental_control",
                             "setup_my_shows_sort_to_date",
                             "setup_myshows_delete_recordings",
                             "setup_cleanup_myshows")
    @pytest.mark.timeout(Settings.timeout)
    def test_309176_guide_recording_myshows(self):
        """
        309176
        To verify the scheduled in progress recording from Guide show up in MyShows
        :return:
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_ndvr=True)
        if not channel:
            pytest.skip("Could not find recordable non movie channel.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_content_in_any_category(self, program)

    @pytestrail.case("C11124021")
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-244")
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_393695_onelineguide_socu_playback_past(self):
        """
        393695
        Verify actions from Record Overlay to playback of a past SOCU offer from the One Line Guide
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                           filter_socu=True, restrict=False)
        if not channel or len(channel) <= 0:
            pytest.skip("could not find any socu channel")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=False)
        self.guide_page.goto_one_line_guide_from_live(self)
        self.menu_page.menu_navigate_left_right(2, 0)
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        title = self.guide_page.get_overlay_title()
        self.guide_assertions.press_select_verify_watch_screen(self, title)

    @pytestrail.case("C11124022")
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-245")
    @pytest.mark.bvt
    @pytest.mark.devhost
    @pytest.mark.socu
    @pytest.mark.cloud_core_vod_socu
    @pytest.mark.timeout(Settings.timeout)
    def test_393696_onelineguide_socu_playback(self):
        """
        393696
        One Line Guide - In Progress - Startover Icon - SOCU Show - Record Overlay - Watch now from CATCHUP_NAME - Press OK
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True,
                                                                           filter_socu=True, restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=False)
        self.guide_page.goto_one_line_guide_from_live(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True, inprogress=True)
        title = self.guide_page.get_overlay_title()
        self.guide_assertions.press_select_verify_watch_screen(self, title)

    @pytestrail.case("C11123913")
    # @pytest.mark.bat
    @pytest.mark.xray("FRUM-240")
    @pytest.mark.infobanner
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_disable_closed_captioning")
    def test_358250_socu_playback_closed_captioning(self):
        """
        358250
        To verify a user is able to turn on closed captioning while watching a socu asset with closed caption available.
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                             filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.turn_on_cc(self)
        self.watchvideo_page.turn_on_cc(self, ON=False)

    @pytestrail.case("C11116835")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_111159_record_overlay_movie(self):
        channel = self.service_api.get_random_live_channel_rich_info(movie=True, live=False, transport_type="stream")
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.screen.base.press_right()
        self.guide_page.open_record_overlay()
        self.guide_assertions.verify_year_in_title()
        self.guide_assertions.verify_bookmark_and_moreInfo_available(self)

    @pytestrail.case("C11116868")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_77020_record_overlay_episodic(self):
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, live=False)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.screen.base.press_right()
        self.guide_page.open_record_overlay()
        self.guide_assertions.verify_year_in_title(converse=True)

    @pytestrail.case("C11116834")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_114073_verify_past_guide(self):
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                             transportType="stream")
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_assertions.verify_transition_past_guide_and_back()

    @pytestrail.case("C11116831")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_103091_guide_guidebutton(self):
        api = self.service_api
        grid_row = api.channels_with_current_show_start_time()
        channel_num = api.get_random_encrypted_unencrypted_channels(grid_row=grid_row, filter_channel=True)[0][0]
        if not channel_num:
            pytest.skip("Could not find channel with current show start time.")
        channel = self.service_api.get_random_live_channel_rich_info(use_cached_grid_row=True,
                                                                     episodic=True,
                                                                     filter_channel=True)
        if not channel:
            pytest.skip("Could not find live channel rich info.")
        self.home_page.goto_live_tv(channel_num)
        self.watchvideo_assertions.verify_livetv_mode()
        self.home_page.press_guide_button()
        self.guide_assertions.verify_guide_title()
        # Let's get cached get_grid_row() since it's already called above
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.wait_for_screen_ready()
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_channel_number(channel[0][0])

    @pytestrail.case("C11116847")
    @pytest.mark.p1_regression
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_76980_guide_tune_to_channel(self):
        channel_number = self.service_api.get_random_encrypted_unencrypted_channels(
            grid_row=self.service_api.channels_with_current_show_start_time(), filter_channel=True)[0][0]
        if not channel_number:
            pytest.skip("Could not find channel with current show start time.")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.wait_for_screen_ready()
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_channel_number(channel_number)
        self.guide_page.pause(300, "Waiting for Media Health Events")
        self.watchvideo_assertions.verify_channel_video_quality_score(self, channel_number)

    @pytestrail.case("C11123843")
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-288")
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.msofocused
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_393714_schedule_recording_and_verify_todo_list(self):
        """
        393714
        To Verify recording is created and listed under To Do list.
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(channel)
        self.guide_page.wait_for_screen_ready("GridGuide")
        self.guide_page.get_live_program_name(self)
        self.menu_page.menu_navigate_left_right(0, 4)
        self.guide_page.wait_for_guide_next_page()
        self.guide_page.get_live_program_name(self)
        show_name = self.guide_page.get_focussed_grid_item(self)
        self.guide_page.select_and_record_program(self)
        self.guide_assertions.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.menu_page.go_to_to_do_list(self)
        self.guide_assertions.verify_show_name_present(show_name)

    @pytestrail.case("C11123828")
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-276")
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    def test_310882_cancel_recording_guide(self):
        """
        :description:
            To verify the recording/cancellation of an upcoming recording from Guide Screen
        :testopia:
            Test Case: https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=310882
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(channel)
        self.guide_page.select_cancel_recording(self)

    @pytestrail.case("C11123841")
    @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.devhost
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_393707_record_on_a_ICM_channel(self):
        """
        393707
        Record individual copy
        :return:
        """
        icm_ch, ccm_ch = self.service_api.get_CCM_or_ICM_channel(filter_channel=False, filter_ndvr=True)
        if not icm_ch:
            pytest.skip("Did not find ICM Channels")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(icm_ch[0])
        self.guide_page.select_and_record_program(self)
        self.watchvideo_assertions.verify_whisper_shown("")

    @pytestrail.case("C11123840")
    @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_393706_record_on_a_CCM_channel(self):
        """
        393706
        Record common copy channel
        :return:
        """
        icm_ch, ccm_ch = self.service_api.get_CCM_or_ICM_channel(filter_channel=True, filter_ndvr=True)
        if not ccm_ch:
            pytest.skip("Did not find CCM Channels")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(ccm_ch[0])
        self.guide_page.wait_for_screen_ready('GridGuide')
        self.guide_page.select_and_record_program(self)
        self.watchvideo_assertions.verify_whisper_shown("")

    @pytestrail.case("C11123842")
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-285")
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="TODO: to investigate Logger error")
    def test_393708_create_5_one_pass_from_guide(self):
        """
        393708
        Creating OnePass and checking that the created onepass is listing under onepass manager or not.
        :return:
        """
        self.api.cancel_all_onepass(Settings.tsn)
        non_recordable_channellist = self.service_api.get_nonrecordable_channels()
        if non_recordable_channellist is False:
            non_recordable_channellist = None
        onepass_showlist = self.api.one_pass_currently_airing_shows(5, excludeChannelNumbers=non_recordable_channellist)
        if not onepass_showlist:
            pytest.skip("No one pass channel found")
        self.menu_page.go_to_one_pass_manager(self)
        for i in range(len(onepass_showlist)):
            show = self.my_shows_page.remove_service_symbols(onepass_showlist[i][0])
            self.home_assertions.verify_show_in_one_pass_manager(self, show)

    @pytestrail.case("C11123837")
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-282")
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_devhost())
    def test_393668_channel_entitlement_matches_assigned_linear_packages(self):
        """
          393668
           Verify that IP Linear channel entitlement matches the assigned Linear Packages.
          :return:
        """
        status = self.api.check_unentitled_channel_availability()
        if status:
            pytest.skip("Device does not have unentitled channels")
        else:
            not_subscribed_channels = self.service_api.get_unentitled_channels(exclude_jump_channels=True, offer_check=True)
            if len(not_subscribed_channels) <= 0:
                pytest.skip("Test requires not subscribed channels: {}".format(not_subscribed_channels))

        subscribed_channels = self.service_api.get_random_encrypted_unencrypted_channels(socu=True, encrypted=True,
                                                                                         filter_channel=True)
        if not subscribed_channels:
            pytest.skip("Test requires subscribed channels")

        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(subscribed_channels[0][0])
        self.guide_assertions.verify_channel_text_color(self.guide_labels.SUBSCRIBED_CHANNEL_COLOR)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(6)
        self.menu_page.menu_press_back()
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_view_mode(self.guide_labels.LBL_VIEW_MODE)
        if Settings.mso.lower() != "cableco3":
            self.guide_page.enter_channel_number(not_subscribed_channels[0])
            self.guide_page.get_live_program_name(self)
            self.screen.refresh()
            self.guide_assertions.verify_channel_text_color(self.guide_labels.NOT_SUBSCRIBED_CHANNEL_COLOR)
            if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_13):
                self.screen.base.press_enter()
                self.watchvideo_assertions.verify_livetv_mode()
                self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")
            else:
                self.guide_assertions.press_select_verify_channel_not_subscribed_overlay()

    @pytestrail.case("C11123827")
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_my_shows_sort_to_date", "setup_myshows_delete_recordings", "setup_cleanup_myshows")
    @pytest.mark.timeout(Settings.timeout)
    def test_310875_encrypted_channel_recording(self):
        """
        310875
        Create in-progress recording on an encrypted channel and validate the recording is scheduled
        :return:
        """
        if Settings.mso.lower() == "rcn":
            channel_number = self.service_api.get_random_channel(Settings.tsn, "entitled", mso=Settings.mso)
        else:
            channel_number = self.guide_page.guide_encrypted_streaming_channel_number(self)
        if not channel_number:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_content_in_any_category(self, program)

    @pytestrail.case("C11116840")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings", "setup_parental_control")
    def test_124712_recording_options_validations(self):
        """
          124712
          To validate the recording overlay options for a future recording
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        for i in range(2):
            self.guide_page.screen.base.press_right()
            self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.wait_for_guide_next_page()
        self.guide_page.select_and_record_program(self)
        self.guide_page.tab_refresh_explicit_recording_icon(icon_validation=False)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.open_record_overlay()
        program = self.guide_page.get_overlay_title()
        self.guide_page.select_verify_modify_recording(self)
        self.menu_page.go_to_to_do_list(self)
        self.guide_assertions.verify_show_name_present(program)

    @pytestrail.case("C11116841")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-406")
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_291969_single_explicit_validation_recording(self):
        """
        291969
        To test the Guide Decoration for a Future Show available for nPVR.
        :return:
        """
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(channel_count=-1, is_preview_offer_needed=True),
            self.service_api.channels_with_current_show_start_time(duration=5400, use_cached_grid_row=True),
            genre="series", count=1, future=1, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][1])
        self.guide_page.get_live_program_name(self)
        self.guide_page.screen.base.press_right()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.wait_for_guide_next_page()
        program = self.guide_page.get_focussed_grid_item(self)
        self.guide_page.select_and_record_program(self)
        self.guide_page.tab_refresh_explicit_recording_icon()
        recordingicon_info = self.guide_page.get_the_recording_icon_details()
        self.guide_page.validate_explicit_recording_icon(self, recordingicon_info['recordingicon_images']['imagename'])
        self.menu_page.go_to_to_do_list(self)
        self.guide_assertions.verify_show_name_present(program)

    @pytestrail.case("C11116862")
    @pytest.mark.xray("FRUM-69")
    @pytest.mark.longrun_2
    @pytest.mark.ndvr
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_393718_cancel_onepass_from_onepassmanager(self):
        """
        393718
        To Verify OnePass is getting cancel from OnePass manager.
        This Script has been enhanced to check Longevity https://testrail.tivo.com//index.php?/cases/view/21259772
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(genre="series", transportType="stream")
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        program = self.guide_page.create_one_pass_on_record_overlay(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.wait_for_screen_ready()
        self.menu_page.go_to_one_pass_manager(self)
        self.home_assertions.verify_show_in_one_pass_manager(self, program)
        next_episode = self.guide_page.get_upcoming_episode(self)
        self.screen.base.press_back()
        self.wtw_page.pause(5)
        self.guide_page.select_validate_onepass(self)
        self.menu_page.go_to_one_pass_manager(self)
        self.menu_assertions.verify_onepass_manager_empty_screen()
        self.guide_page.wait_for_upcoming_episode_to_air(self, program, next_episode[0], next_episode[1], next_episode[3])
        self.menu_page.go_to_one_pass_manager(self)
        self.menu_assertions.verify_onepass_manager_empty_screen()

    @pytestrail.case("C11124020")
    @pytest.mark.bat
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    def test_363174_play_encrypted_socu_from_guide(self):
        """
        Test Case 363174: SOCU - E2E - Encrypted playback
        Attempt to playback the encrypted SOCU offer from Guide.
        :return:
        """
        channel = self.guide_page.get_encrypted_socu_channel(self, filter_socu=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.home_assertions.verify_socu_playback(self)

    @pytestrail.case("C11116832")
    @pytest.mark.p1_regression
    @pytest.mark.guide
    @pytest.mark.timeout(Settings.timeout)
    def test_102629_grid_Guide_GUIDE(self):
        """
        102629
        Check the GUIDE button
        :return:
        """
        self.home_page.back_to_home()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.guide_page.screen.base.press_guide()
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_view_mode(self.guide_labels.LBL_VIEW_MODE)
        self.guide_page.screen.base.press_guide()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_LIVETV_VIEWMODE)

    @pytestrail.case("C12792605")
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_355711_verify_socu_record_overlay(self):
        """
        355711
        To verify "Watch" actions in Record overlay for a show that is available only from SOCU catalog in Past Guide
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.menu_page.menu_navigate_left_right(4, 0)
        self.guide_page.wait_for_guide_next_page()
        self.guide_page.open_record_overlay()
        catchup_name = self.guide_page.get_watch_now_catchup_name(self, inprogress=False)
        image_name = self.guide_labels.LBL_RECORD_OVERLAY_CATCHUP_ICON
        self.guide_assertions.verify_text_image_from_screen(catchup_name, image_name)

    @pytestrail.case("C11116858")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-418")
    @pytest.mark.msofocused
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    def test_355569_guide_catchup_icon_inprogress(self):
        """
        355569
        Check the catchup icon displayed on program cell for the in progress show
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell", True)

    @pytestrail.case("C11116860")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-67")
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    def test_363100_search_past_socu_asset_source_icon(self):
        """
        363100
        Verify CatchUp asset in past is available in Search results
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("No channels found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(channel_number)
        self.menu_page.menu_navigate_left_right(3, 0)
        self.guide_page.wait_for_screen_ready()
        focused_program = self.guide_page.get_focussed_grid_item(self)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(focused_program, focused_program, select=False)
        self.guide_assertions.verify_catchup_socu_icon_on_search_screen()

    @pytestrail.case("C11116848")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-408")
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    def test_355571_future_socu_program_source_icon(self):
        """
        355571
        Verify that the Catchup icon is not displayed on program cell for a future show
        in the Guide that will later be available through SOCU
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(channel_number)
        self.menu_page.menu_navigate_left_right(0, 2)
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell", False)

    @pytestrail.case("C11116853")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    def test_355573_SOCU_source_icon_guide_header(self):
        program = self.service_api.get_random_encrypted_unencrypted_channels(socu=True,
                                                                             encrypted=True,
                                                                             filter_channel=True,
                                                                             filter_socu=True,
                                                                             restrict=False)
        if program is None:
            pytest.skip("No channel found")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(program[0][0])
        program_name = self.guide_page.get_live_program_name(self)
        self.guide_assertions.verify_socu_icon_in_guide_header(self, program_name)

    @pytestrail.case("C11116852")
    @pytest.mark.bvt
    @pytest.mark.socu
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_355625_verify_socu_playback_from_onelineguide(self):
        """
        355625
        To check and verify the catchup icon is displayed on tile for the in progress show
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.guide_page.goto_one_line_guide_from_live(self)
        image_name = self.guide_labels.LBL_RECORD_OVERLAY_CATCHUP_ICON
        self.guide_assertions.verify_socu_onlineguide(image_name, refresh=False)

    @pytestrail.case("C11116855")
    @pytest.mark.bvt
    @pytest.mark.socu
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_355626_verify_socu_playback_from_onelineguide_past(self):
        """
        355626
        To check and verify the catchup icon is displayed on tile for show in Past Guide
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.guide_page.goto_one_line_guide_from_live(self)
        image_name = self.guide_labels.LBL_RECORD_OVERLAY_CATCHUP_ICON
        self.menu_page.menu_navigate_left_right(4, 0)
        self.guide_assertions.verify_socu_onlineguide(image_name)

    @pytestrail.case("C11123914")
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-241")
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.cloud_core_vod_socu
    @pytest.mark.devhost
    @pytest.mark.timeout(Settings.timeout)
    def test_358254_socu_partially_watched_resume_playing(self):
        """
        358254
        To verify user is able to resume playing a partially watched SOCU asset
        Per discussion, decided to watch for at least 1 minute instead of PAUSE
        because a lot of SOCU assets have trickplay restrictions for PAUSE
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, channel_count=1, filter_channel=True,
                                                                           filter_socu=True, restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60 * 2)
        last_played_position = self.watchvideo_page.get_trickplay_current_position()
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        # self.guide_page.get_live_program_name(self)  # Do not add this api. causing CA-20228
        self.guide_page.select_and_watch_program(self, socu=True, resume=True)
        self.watchvideo_assertions.verify_socu_playback_started()
        resume_position = self.watchvideo_page.get_trickplay_current_position()
        self.watchvideo_assertions.verify_video_resumed(last_played_position, resume_position)

    @pytestrail.case("C11116833")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-154")
    @pytest.mark.msofocused
    @pytest.mark.guide
    @pytest.mark.timeout(Settings.timeout)
    def test_113479_guide_default_channel_is_highlighted(self):
        """
        113479
        Check the GUIDE button
        :return:
        """
        self.home_page.back_to_home()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_playback_play()
        channel_number = self.watchvideo_assertions.get_channel_number()
        self.guide_page.screen.base.press_guide()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_default_channel_is_highlighted(self, channel_number)

    @pytestrail.case("C12792604")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    def test_361368_playback_socu_livetv(self):
        """
        361368
        To verify SOCU playback functionality works as expected for IP Linear channels.
        :return:
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.guide_assertions.verify_play_normal()
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.guide_assertions.verify_play_normal()

    @pytestrail.case("C11116851")
    @pytest.mark.p1_regression
    @pytest.mark.bvt
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    def test_355671_watch_options_on_record_overlay(self):
        """
        355671
        This case verifies "Watch" actions in Record overlay for a show that is available
        from SOCU catalog and is in progress now on LiveTV
        Part2 of this case will cover "Watch" actions in Record overlay
        for a show that is available from OTT and SOCU catalog
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.verify_watch_live_option_on_record_overlay(self)

    @pytestrail.case("C11116849")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.guide
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_339633_cancel_ONE_PASS_NAME_from_onepass_options_strip(self):
        """
        339633
        Verify Cancel ONE_PASS_NAME from OnePass Options strip displays Cancel OnePass Overlay.
        :return:
        """
        channel = self.service_api.get_recordable_non_movie_channel()
        if not channel:
            pytest.skip("Recordable episodic channels are not found.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.wait_for_channel_change()
        self.guide_page.get_live_program_name(self)
        self.guide_page.create_one_pass_on_record_overlay(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.select_and_get_more_info(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.cancel_one_pass_and_verify(self)

    @pytestrail.case("C11116830")
    @pytest.mark.p1_regression
    @pytest.mark.onepass
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_309094_schedule_a_one_pass_from_one_line_guide(self):
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if not channel:
            pytest.skip("Recordable episodic channels are not found.")
        self.home_page.goto_live_tv(channel[0][0])
        self.guide_page.open_olg()
        self.watchvideo_assertions.verify_one_line_guide()
        self.guide_page.create_one_pass_on_record_overlay(self)

    @pytestrail.case("C11116859")
    @pytest.mark.p1_regression
    @pytest.mark.socu
    @pytest.mark.xray("FRUM-419")
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_358255_socu_ffwX1_mode(self):
        """
        358255
        To Verify the trickplay action FFWx1 for SOCU
        :return:
        """
        channels = self.guide_page.get_trickplay_non_restricted_socu_channel(self, filter_channel=True)
        if not channels:
            pytest.skip("There are no SOCU channels without trickplay restriction")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channels[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.playback_and_verify_trickplay_action(self, forward=True)

    @pytestrail.case("C11116854")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-414")
    @pytest.mark.socu
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_358316_socu_rwX1_mode(self):
        """
        358316
        To Verify the trickplay action RWx1 for SOCU
        :return:
        """
        channels = self.guide_page.get_trickplay_non_restricted_socu_channel(self, filter_channel=True)
        if not channels:
            pytest.skip("There are no SOCU channels without trickplay restriction")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channels[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.playback_and_verify_trickplay_action(self, rewind=True)

    @pytestrail.case("C11116857")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-417")
    @pytest.mark.socu
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_358283_socu_pause_mode(self):
        """
        358283
        To Verify the trickplay action pause for SOCU
        :return:
        """
        channels = self.guide_page.get_trickplay_non_restricted_socu_channel(self, filter_channel=True)
        if not channels:
            pytest.skip("There are no SOCU channels without trickplay restriction")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channels[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.playback_and_verify_trickplay_action(self, pause=True)

    @pytestrail.case("C11116850")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-410")
    @pytest.mark.socu
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_359401_socu_play_mode(self):
        """
        359401
        To Verify the trickplay action pause and play for SOCU
        :return:
        """
        channels = self.guide_page.get_trickplay_non_restricted_socu_channel(self, filter_channel=True)
        if not channels:
            pytest.skip("There are no SOCU channels without trickplay restriction")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channels[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.playback_and_verify_trickplay_action(self, playpause=True)

    @pytestrail.case("C11116837")
    @pytest.mark.p1_regression
    @pytest.mark.actionscreen
    @pytest.mark.may_also_like_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_271830_non_episodic_screen_strips_validation(self):
        channel = self.service_api.get_random_live_channel_rich_info(movie=False, episodic=False,
                                                                     transport_type="stream")
        if channel is None:
            pytest.fail("Could not find any channel with non episodic program airing live")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_validate_program_screen_strips(self, self.guide_labels.LBL_NON_EPISODIC_STRIP_ORDER)

    @pytestrail.case("C11116836")
    @pytest.mark.p1_regression
    @pytest.mark.p1_reg_stability
    @pytest.mark.actionscreen
    @pytest.mark.may_also_like_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_271379_episode_screen_strip_order(self):
        """
        271379
        Verify Episode Screen strip order.
        """
        channel_details = self.service_api.get_random_live_channel_rich_info(movie=False, episodic=True,
                                                                             transport_type="stream")
        if channel_details is None:
            pytest.fail("Could not find any channel with episodic program airing live")
        channel_number = channel_details[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_validate_program_screen_strips(self, self.guide_labels.LBL_EPISODIC_STRIP_ORDER)

    @pytestrail.case("C11116839")
    @pytest.mark.p1_regression
    @pytest.mark.actionscreen
    @pytest.mark.may_also_like_ccu
    @pytest.mark.timeout(Settings.timeout)
    def test_274053_episodic_may_also_like_gallery_screen_validation(self):
        """
        TC 274053 - Episodic - May also like Gallery screen validation
        :return:
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if channel is None:
            pytest.fail("Could not find any episodic channel")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.goto_episode_screen(self)
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE)
        titles = self.guide_page.get_strip_items_title(self)
        if titles is None:
            pytest.fail("Strip is empty")
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_MAY_ALSO_LIKE,
                                                                        select_view_all=True)
        self.guide_assertions.verify_gallery_screen_and_tiles_order(self, titles, program,
                                                                    self.my_shows_labels.LBL_MAY_ALSO_LIKE)

    @pytestrail.case("C12790644")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.onepass
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_328459_verify_recording_related_options(self):
        channel_details = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if channel_details is None:
            pytest.fail("Could not find any channel with episodic program airing live")
        channel = channel_details[0][0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel, confirm=False)
        self.guide_page.open_record_overlay()
        self.guide_page.select_verify_onepass_overlay_menu_item(self)

    @pytest.mark.guide
    @pytest.mark.xray("FRUM-921")
    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    def test_9919698_grid_guide_guide_banner_press_down_on_the_bottommost_cell(self):
        """
        9919698
         Verify pressing DOWN on the bottommost cell in Guide.
        :return:
        """
        self.home_page.go_to_guide(self)
        self.guide_page.go_to_bottom_cell_in_guide()
        self.screen.base.press_down()
        self.guide_assertions.verify_guide_banner_is_focused()

    @pytest.mark.ipppv
    @pytest.mark.timeout(Settings.timeout)
    def test_C5603442_verify_ppv_channel_in_guide_check_ppv_overlay(self):
        """
                C5603442
                get a Random PPV channel using Grid Row Search
                Use Middle Mind payload response  to get the channels
                pick the first channel in the Channel list from grid row response which has transport Type -ppv
                Enter the first PPV channel
                Verify PPV Icon is present
                select to watch the PPV channel and confirm PPV Overlay

        """
        ppv_rental_channel = self.guide_page.get_ppv_rental_channel(self)
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(ppv_rental_channel)
        self.guide_page.select_and_watch_program(self)
        self.guide_assertions.ppv_overlay_confirm()

    @pytestrail.case("C11116838")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-403")
    @pytest.mark.msofocused
    @pytest.mark.actionscreen
    @pytest.mark.timeout(Settings.timeout)
    def test_274042_episodic_upcoming_airings_screen_validation(self):
        """
        274042
         Verify upcoming airings screen validation.
        :return:
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, movie=False)
        if channel is None:
            pytest.fail("Could not find any episodic channel")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.goto_episode_screen(self)
        strip = self.guide_assertions.verify_upcoming_menu_episode_screen(channel[0][0])
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, strip[0],
                                                                        select_view_all=True)
        self.guide_page.wait_for_screen_ready(strip[1], timeout=10000)
        self.guide_assertions.verify_upcoming_airings_screen(self)

    @pytest.mark.ui_promotions
    @pytest.mark.guidebanner
    @pytest.mark.xray("FRUM-682")
    @pytest.mark.timeout(Settings.timeout)
    def test_9919679_grid_guide_banner_press_select_no_action(self):
        """
        9919679
         Grid Guide - Guide Banner - Focused - Press SELECT - No Action
        :return:
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_NO_ACTION
        self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                           feed_name='/promotions/guideBanner',
                                                           action_type=action_type_lbl)
        self.screen.base.press_enter()
        self.guide_assertions.verify_guide_title()
        self.guide_assertions.verify_guide_banner_is_focused()

    @pytest.mark.ui_promotions
    @pytest.mark.xray("FRUM-748")
    @pytest.mark.timeout(Settings.timeout)
    def test_9919676_grid_guide_banner_press_select_no_action_deeplink_into(self):
        """
        9919676
         Guide Banner - Focused - Press SELECT - Deeplink into
        :return:
        """
        self.home_page.go_to_guide(self)
        lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE
        guide_banner = self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                                          feed_name='/promotions/guideBanner',
                                                                          action_type=lbl,
                                                                          streamer_only=True,
                                                                          need_deeplink=True,
                                                                          is_filter=True,
                                                                          is_app=True,
                                                                          is_top_lvl=False)
        self.guide_assertions.press_select_and_verify_app_running(guide_banner)

    @pytest.mark.ui_promotions
    @pytest.mark.xray("FRUM-994")
    @pytest.mark.timeout(Settings.timeout)
    def test_9919678_grid_guide_banner_press_select_top_level_app(self):
        """
        9919678
         Grid Guide - Guide Banner - Focused - Press SELECT - Top level app
        :return:
        """
        self.home_page.go_to_guide(self)
        lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE
        guide_banner = self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                                          feed_name='/promotions/guideBanner',
                                                                          action_type=lbl,
                                                                          streamer_only=True,
                                                                          is_filter=True,
                                                                          is_app=True,
                                                                          is_top_lvl=True)
        self.guide_assertions.press_select_and_verify_app_running(guide_banner)

    # @pytest.mark.test_stabilization
    @pytest.mark.longrun
    @pytest.mark.timeout(Settings.timeout)
    def test_358253_socu_playback_until_end(self):
        """
        358253
        SOCU playback behavior when watched until the end.
        :return:
        """
        self.menu_page.autoplay_next_episode_settings(self, self.menu_labels.LBL_ON)
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True)
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.wait_and_watch_until_end_of_program(self)
        self.guide_page.verify_episode_panel_and_playback_of_upcoming_episode(self)

    # @pytest.mark.test_stabilization
    @pytest.mark.longrun
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_393694_catchup_until_end_autoplay_next_episode(self):
        """
        393694
        Verify the CU playback behavior when watched until the end when Autoplay Next Episode is ON.
        SOCU playback behavior when watched until the end.
        :return:
        """
        self.menu_page.autoplay_next_episode_settings(self, self.menu_labels.LBL_ON)
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        self.menu_page.menu_navigate_left_right(6, 0)
        self.guide_page.wait_for_guide_next_page()
        focused_item = self.guide_page.get_focussed_grid_item(self)
        self.guide_page.create_one_pass_on_record_overlay(self)
        self.guide_assertions.press_select_verify_record_overlay(self, inprogress=False)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
        self.guide_page.wait_and_watch_until_end_of_program(self)
        self.guide_page.verify_episode_panel_and_playback_of_upcoming_episode(self)

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.longrun
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.usefixtures("disable_video_providers")
    @pytest.mark.timeout(Settings.timeout)
    def test_368335_socu_playback_through_myshow_options(self):
        """
        368335
        Verify SOCU and nDVR playback both work as expected for a program available through both options.
        :return:
        """
        channel = self.service_api.get_random_recordable_channel(channel_count=3, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        for i in range(len(channel)):
            self.guide_page.log.info("Checking for channel: {}".format(channel[i][0]))
            channel_number = (channel[i][0])
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(channel_number)
            focused_item = self.guide_page.get_live_program_name(self)
            record_status = self.guide_page.create_live_recording()
            if record_status:
                self.guide_page.select_and_watch_program(self)
                self.guide_page.wait_and_watch_until_end_of_program(self)
                if not self.guide_page.go_to_recorded_program_in_guide(self, focused_item, channel_number):
                    pytest.fail("Highlighted program is not as expected program")
                self.guide_page.watch_past_scou_program_from_replay_and_myshow(self)
                break

    @pytestrail.case("C11116861")
    @pytest.mark.p1_regression
    @pytest.mark.socu
    @pytest.mark.usefixtures("setup_delete_book_marks", "setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_393518_socuicon_on_programscreen_infobanner_predictionbar(self):
        """
        393518
        Verify SOCU Icons in Guide, Search, My Shows->Program screen, Info Banner, and Predictions Bar
        NOTE: SOCU Icons in search,guide,one line guide is already validated in TC363100,355573,355569,355571,355625
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1, encrypted=True, socu=True,
                                                                             bookmark=True, genre='series',
                                                                             filter_channel=True,
                                                                             filter_socu=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.service_api.bookmark_show(*channel[0][2])
        self.guide_page.wait_for_screen_ready()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.guide_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_content_in_category(channel[0][1])
        self.my_shows_page.select_show(channel[0][1])
        self.my_shows_page.select_socu_playback(self)
        self.home_assertions.verify_socu_playback(self)
        self.vod_page.resume_socu_playback(self)
        self.watchvideo_page.show_info_banner()
        self.guide_assertions.verify_catchup_icon(self)
        self.home_page.back_to_home_short()
        self.guide_page.navigate_and_verify_socu_icon_on_prediction_bar(self)

    @pytestrail.case("C11685255")
    @pytest.mark.livetv
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.e2e
    @pytest.mark.timeout(Settings.timeout)
    def test_74567136_system_behavior_on_tuning_subscribed_channel(self):
        """
        Verify system behavior when attempting to tune to subscribed channels.
        """
        subscribed_channels = self.service_api.get_random_live_channel_rich_info(channel_count=1, episodic=True,
                                                                                 filter_channel=True, transport_type="stream")
        if not subscribed_channels:
            pytest.skip("Could not find any channel. hence skipping")
        channel = subscribed_channels[0][0]
        channel_list = self.api.get_channels_list(self.service_api.GCL_CHANNEL_LIST)
        x = self.guide_assertions.channel_index_value_from_channel_list(channel_list, channel)
        ch = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(ch)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.guide_assertions.verify_tuned_channel_is_subscribed_or_not_subscribed(self, channel_list[x - 1],
                                                                                   subscribed_channels[0][0])
        self.guide_assertions.verify_tuned_channel_is_subscribed_or_not_subscribed(self, subscribed_channels[0][0],
                                                                                   channel_list[x - 1])
        self.watchvideo_page.open_olg()
        self.watchvideo_page.enter_channel_number(subscribed_channels[0][0], confirm=True)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.guide_assertions.verify_play_normal()
        if not Settings.is_apple_tv():
            self.guide_page.go_to_live_tv(self)
            self.guide_page.enter_channel_number(subscribed_channels[0][0])
            self.guide_assertions.verify_play_normal()

    @pytestrail.case("C11685255")
    @pytest.mark.livetv
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.e2e
    @pytest.mark.timeout(Settings.timeout)
    def test_74567136_system_behavior_on_tuning_unsubscribed_channel(self):
        """
        Verify system behavior when attempting to tune to unsubscribed channels.
        """
        status = self.api.get_show_entitled_channels_status(tsn=Settings.tsn)
        if status:
            pytest.skip("Device does not have unentitled channels")
        unsubscribed_channels = self.service_api.get_unentitled_channels(exclude_jump_channels=True)
        unsubscribed_channel = unsubscribed_channels[0]
        ch = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(ch)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.open_olg()
        self.screen.base.press_left()  # to be on a channel cell after entering channel number
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_13):
            self.watchvideo_page.enter_channel_number(channel=unsubscribed_channel, confirm=True, olg=True)
            time.sleep(2)
            self.guide_page.check_for_overlay_watchnow_or_watchlive()
            self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")
        else:
            self.watchvideo_page.enter_channel_number(channel=unsubscribed_channel, confirm=False, olg=True)
            self.guide_assertions.press_select_verify_channel_not_subscribed_overlay()
        self.guide_page.go_to_live_tv(self)
        self.guide_page.enter_channel_number(unsubscribed_channel)
        self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")
        self.guide_assertions.verify_channel_not_subscribed_osdtext(self)

    @pytestrail.case("C11685249")
    @pytest.mark.e2e
    # @pytest.mark.livetv
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    def test_74108904_tune_subscribed_and_unsubscribed_channel_from_liveTv_with_different_actions(self):
        """
        To Verify tuning to subscribed and unsubscribed channel from Live Tv with different actions and sources
        """
        status, result = self.vod_api.get_offer_playable()
        subscribed_channels = self.service_api.get_random_live_channel_rich_info(movie=False, episodic=True, channel_count=1)
        if not subscribed_channels:
            pytest.skip("Could not find any channel.")
        channel = subscribed_channels[0][0]
        channel_list = self.api.get_channels_list(self.service_api.GCL_CHANNEL_LIST)
        x = self.guide_assertions.channel_index_value_from_channel_list(channel_list, channel)
        self.guide_page.go_to_live_tv(self)
        self.guide_assertions.verify_tuned_channel_is_subscribed_or_not_subscribed(self, subscribed_channels[0][0],
                                                                                   channel_list[x - 1], key='pause')
        self.guide_assertions.verify_channel_up_or_down_behaviour_in_one_line_guide(self, channel, channel_up=True)
        self.home_page.press_guide_button()
        self.guide_assertions.verify_guide_title()
        self.home_page.press_guide_button()
        self.watchvideo_assertions.verify_livetv_mode()
        if result:
            self.home_page.back_to_home_short()
            self.vod_page.goto_vodoffer_program_screen(self, result)
            self.vod_page.play_any_playable_vod_content(self, result)
            self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
            self.guide_page.go_to_live_tv(self)
            self.watchvideo_assertions.verify_live_tv_details(self)

    @pytestrail.case("C11685249")
    @pytest.mark.e2e
    @pytest.mark.livetv
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout_mid)
    def test_74108904_tune_unsubscribed_channel_from_liveTv_with_different_actions(self):
        """
        To Verify tuning to subscribed and unsubscribed channel from Live Tv with different actions and sources
        """
        subscribed_channels = self.api.get_channels_with_no_trickplay_restrictions(filter_channel=True)
        if not subscribed_channels:
            pytest.skip("No trickplay non restrictions channels found.")
        subscribed_channel = subscribed_channels[0]
        status = self.api.get_show_entitled_channels_status(tsn=Settings.tsn)
        if status:
            pytest.skip("Device does not have unentitled channels")
        unsubscribed_channels = self.service_api.get_unentitled_channels(exclude_jump_channels=True)
        unsubscribed_channel = random.choice(unsubscribed_channels)
        channel_list = self.api.get_channels_list(self.service_api.GCL_CHANNEL_LIST)
        ch = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True, transportType="stream")[0][0]
        self.home_page.goto_live_tv(ch)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        x = self.guide_assertions.get_channel_index_value_difference_between_channels(channel_list,
                                                                                      unsubscribed_channel, subscribed_channel)
        self.guide_assertions.verify_tuned_channel_is_subscribed_or_not_subscribed(self, unsubscribed_channel,
                                                                                   subscribed_channel,
                                                                                   key='fastforward', count=x)
        self.home_page.goto_live_tv(ch)
        self.guide_assertions.verify_tuned_channel_is_subscribed_or_not_subscribed(self, unsubscribed_channel,
                                                                                   subscribed_channel, key='rewind', count=x)
        self.guide_assertions.verify_channel_up_or_down_behaviour_in_one_line_guide(self, unsubscribed_channel)
        self.home_page.press_guide_button()
        self.guide_assertions.verify_guide_title()
        self.home_page.press_guide_button()
        self.watchvideo_assertions.verify_livetv_mode()

    @pytestrail.case("C12792603")
    @pytest.mark.p1_regression
    @pytest.mark.socu
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    @pytest.mark.skipif("b-hydra-streamer-1-7" in Settings.branch.lower(), reason="Build does not support the feature")
    def test_10195352_verify_favorite_channels_panel_watch_socu(self):
        """
        :Description:
            To verify Favorite Cahnnels panel watching SOCU
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/10195352
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.go_to_favorite_channels()
        channels = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                            filter_channel=True,
                                                                            filter_socu=True,
                                                                            restrict=False)
        if channels is None:
            pytest.skip("No channel found")
        channel = channels[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()

    @pytestrail.case("C12790640")
    @pytest.mark.bc_to_fss
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.SOCU)])
    @pytest.mark.parametrize("body_config_feature", [(BodyConfigFeatures.SOCU)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.SOCU)])
    @pytest.mark.parametrize("req_type", ["NO_REQ"])
    @pytest.mark.parametrize("bc_state, fs_state", [(False, False), (False, True), (True, False), (True, True)])
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.notapplicable(Settings.is_devhost(), reason="Does not support reboot")
    @pytest.mark.notapplicable(not Settings.is_internal_mso(), reason="Not allowed for External MSOs")
    def test_10464412_socu_from_body_config_to_feature_status(self, request, feature_status_feature,
                                                              device_info_store_feature, body_config_feature,
                                                              req_type, bc_state, fs_state):
        """
        Verify catchup icon in Guide Program Cell.
        Only feature state in featureStatus should affect feature enabling/disabling.
        bc_state = feature state in bodyConfig, fs_state = feature state in featureStatus.

        Xray:
            https://jira.tivo.com/browse/FRUM-8101
            https://jira.tivo.com/browse/FRUM-8100
            https://jira.tivo.com/browse/FRUM-1001
            https://jira.tivo.com/browse/FRUM-929

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/10464413
            https://testrail.tivo.com//index.php?/cases/view/10464412
            https://testrail.tivo.com//index.php?/cases/view/11124434
            https://testrail.tivo.com//index.php?/cases/view/11124433
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        request.config.cache.set("is_relaunch_needed", True)
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, fs_state)
        self.service_api.update_features_in_body_config(body_config_feature, is_add=bc_state)
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.service_api.check_feature_with_body_search(body_config_feature, expected=bc_state)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, expected=fs_state)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell", fs_state)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True, socu_on=fs_state)
        if fs_state:
            self.guide_page.select_and_watch_program(self, socu=True, open_rec_overlay=False)
            self.watchvideo_assertions.verify_socu_playback_started()

    @pytest.mark.fast_fs_update
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.SOCU)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.SOCU)])
    @pytest.mark.parametrize("req_type,enable", [
        (NotificationSendReqTypes.FCM, True), (NotificationSendReqTypes.NSR, True),
        (NotificationSendReqTypes.FCM, False), (NotificationSendReqTypes.NSR, False)])
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(not Settings.is_internal_mso(), reason="Not allowed for External MSOs")
    @pytest.mark.notapplicable(
        Settings.is_unmanaged() and Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16),
        "NSR featureStatus is enabled starting from Hydra v1.16")
    def test_20959896_socu_fast_feature_status_update(self, request, feature_status_feature,
                                                      device_info_store_feature, req_type, enable):
        """
        Fast featureStatus Update.
        Feature Enabling: Set SOCU = TRUE in featureStatusSearch (DG_vp_[MSO]_socu already exists on the box).
        Precondition = initial feature state, it should be inverted value of 'enable' variable.
        'enable' variable represents feature state we are going to check.

        Xray:
            https://jira.tivo.com/browse/FRUM-1300
            https://jira.tivo.com/browse/FRUM-1341

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/20959896
            https://testrail.tivo.com/index.php?/cases/view/20959897
        """
        # Preparation
        self.iptv_prov_api.check_group_with_service_group_fetch(
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.iptv_prov_api.get_group_with_correct_mso("DG_vp_[MSO]_socu"), expected=True)
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        request.config.cache.set("is_relaunch_needed", False)
        # Preconditions
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, not enable)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, not enable)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.FEATURE_STATUS)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell", expected=not enable)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True, socu_on=not enable)
        if not enable:
            self.guide_page.select_and_watch_program(self, socu=True, open_rec_overlay=False)
            self.watchvideo_assertions.verify_socu_playback_started()
        # Steps
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, enable)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, enable)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.FEATURE_STATUS)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell", expected=enable)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True, socu_on=enable)
        if enable:
            self.guide_page.select_and_watch_program(self, socu=True, open_rec_overlay=False)
            self.watchvideo_assertions.verify_socu_playback_started()

    @pytest.mark.xray('FRUM-26872')
    @pytest.mark.msofocused
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.SOCU)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.SOCU)])
    @pytest.mark.parametrize("req_type,enable", [(NotificationSendReqTypes.NSR, True)])
    @pytest.mark.usefixtures("cleanup_enabling_internet")
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.notapplicable(Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_frum_26872_socu_nsr_retry_policy_fast_feature_status_update(self, request, feature_status_feature,
                                                                         device_info_store_feature, req_type, enable):
        """
        [Unmanaged -> Retry Policy] Fast featureStatus Update: Feature Enabling: Set SOCU  = TRUE in featureStatusSearch
        (DG_vp_[mso]_socu already exists on the box)

        Xray:
            https://jira.xperi.com/browse/FRUM-26872
        """
        # Preparation
        self.iptv_prov_api.check_group_with_service_group_fetch(
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.iptv_prov_api.get_group_with_correct_mso("DG_vp_[MSO]_socu"), expected=True)
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        request.config.cache.set("is_relaunch_needed", False)
        # Preconditions
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, not enable)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, not enable)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.FEATURE_STATUS)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell", expected=not enable)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True, socu_on=not enable)
        if not enable:
            self.guide_page.select_and_watch_program(self, socu=True, open_rec_overlay=False)
            self.watchvideo_assertions.verify_socu_playback_started()
        # Steps
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, enable)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, enable)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.FEATURE_STATUS,
                                                    is_retry=True)
        init_time = datetime.now()
        self.home_assertions.verify_connected_disconnected_state_happened(error_code=self.home_labels.LBL_ERROR_CODE_C228)
        cur_time = datetime.now()
        self.home_page.pause(330 - (cur_time - init_time).seconds, "Staying in the disconnected state a bit")
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        init_time = datetime.now()
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False, is_select=False)
        cur_time = datetime.now()
        self.home_page.pause(300 - (cur_time - init_time).seconds, "Waiting NSR to be sent")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell", expected=enable)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True, socu_on=enable)
        if enable:
            self.guide_page.select_and_watch_program(self, socu=True, open_rec_overlay=False)
            self.watchvideo_assertions.verify_socu_playback_started()

    @pytestrail.case("C12790642")
    # @pytest.mark.p1_regression
    # @pytest.mark.ipppv
    @pytest.mark.bc_to_fss
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.IPPPV)])
    @pytest.mark.parametrize("body_config_feature", [(BodyConfigFeatures.IPPPV)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.IPPPV)])
    @pytest.mark.parametrize("req_type", ["NO_REQ"])
    @pytest.mark.parametrize("bc_state, fs_state", [(False, False), (False, True), (True, False), (True, True)])
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.notapplicable(Settings.is_devhost(), reason="Does not support reboot")
    @pytest.mark.notapplicable(not Settings.is_internal_mso(), reason="Not allowed for External MSOs")
    def test_10464416_ipppv_from_body_config_to_feature_status(self, request, feature_status_feature,
                                                               device_info_store_feature, body_config_feature,
                                                               req_type, bc_state, fs_state):
        """
        Moving IPPPV feature from bodyConfig to featureStatus. Only feature state in featureStatus should affect
        feature enabling/disabling.
        Verifying "PPV_RENT_OR_BUY this show (<price>)" is displayed as a separate option on the Record overlay.
        bc_state = feature state in bodyConfig, fs_state = feature state in featureStatus.

        Xray:
            https://jira.tivo.com/browse/FRUM-8097
            https://jira.tivo.com/browse/FRUM-8096
            https://jira.tivo.com/browse/FRUM-694
            https://jira.tivo.com/browse/FRUM-737

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/10464417
            https://testrail.tivo.com//index.php?/cases/view/10464416
            https://testrail.tivo.com//index.php?/cases/view/11124439
            https://testrail.tivo.com//index.php?/cases/view/11124438
        """
        channel = self.service_api.get_ppv_channel_list_current(filter_channel=True)
        if not channel:
            pytest.skip("Could not find any PPV channel")
        request.config.cache.set("is_relaunch_needed", True)
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, fs_state)
        self.service_api.update_features_in_body_config(body_config_feature, is_ppv=True, is_add=bc_state)
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.service_api.check_feature_with_body_search(body_config_feature, expected=bc_state)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, expected=fs_state)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.open_record_overlay_for_future_show(self.guide_labels.LBL_RECORD_OVERLAY)
        self.guide_assertions.verify_ipppv_feature_is_on_or_off_in_record_overlay(fs_state)

    # @pytest.mark.p1_regression
    # @pytest.mark.ipppv
    @pytest.mark.fast_fs_update
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.IPPPV)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.IPPPV)])
    @pytest.mark.parametrize("req_type,enable", [
        (NotificationSendReqTypes.FCM, True), (NotificationSendReqTypes.NSR, True),
        (NotificationSendReqTypes.FCM, False), (NotificationSendReqTypes.NSR, False)])
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(not Settings.is_internal_mso(), reason="Not allowed for External MSOs")
    @pytest.mark.notapplicable(
        Settings.is_unmanaged() and Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16),
        "NSR featureStatus is enabled starting from Hydra v1.16")
    def test_20959892_ipppv_fast_feature_status_update(self, request, feature_status_feature,
                                                       device_info_store_feature, req_type, enable):
        """
        Fast featureStatus Update. Verifying IPPPV feature (IPPPV Channles already exists on the box).
        Precondition = initial feature state, it should be inverted value of 'enable' variable.
        'enable' variable represents feature state we are going to check.

        Xray:
            https://jira.tivo.com/browse/FRUM-1100
            https://jira.tivo.com/browse/FRUM-1329

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/20959892
            https://testrail.tivo.com/index.php?/cases/view/20959893
        """
        channel = self.service_api.get_ppv_channel_list_current(channel_count=2, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any PPV channel")
        request.config.cache.set("is_relaunch_needed", False)
        # Preconditions
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, not enable)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, expected=not enable)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.FEATURE_STATUS)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.open_record_overlay()
        self.guide_assertions.verify_ipppv_feature_is_on_or_off_in_record_overlay(not enable)
        self.guide_page.get_live_program_name(self, diff=2, raise_error_if_no_text=False)
        self.guide_page.press_ok_button(refresh=False)  # entering Live TV
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_assertions.verify_ipppv_feature_is_on_or_off_in_osd_text(not enable)
        # Steps
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, enable)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, expected=enable)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.FEATURE_STATUS)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[1][0])
        self.guide_page.open_record_overlay()
        self.guide_assertions.verify_ipppv_feature_is_on_or_off_in_record_overlay(enable)
        self.guide_page.press_back_button(refresh=False)  # dismissing Record Overlay
        self.guide_page.pause(2)  # waiting untill Record Overlay dismissed
        self.guide_page.press_ok_button(refresh=False)  # entering Live TV
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        if enable:
            self.watchvideo_assertions.verify_error_overlay_not_shown()
        self.watchvideo_assertions.verify_ipppv_feature_is_on_or_off_in_osd_text(enable)

    def test_11108205_verify_ipqam_preference_when_ip_preferred(self):
        """
        :Description:
            To verify IP channel is preferred when preference of the channel is IP
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11108205
        """
        channellist = self.guide_page.return_channel_with_same_stationid_lcn()
        if channellist:
            channelbitsdict = self.guide_page.return_channel_bits_of_channels(channellist)
            ipchannellist = self.guide_page.return_ip_preferred_channels(channelbitsdict)
            if ipchannellist:
                self.guide_assertions.verify_ip_prefered_channels_after_merge_policy(ipchannellist)

    def test_11108204_verify_ipqam_preference_when_qam_preferred(self):
        """
        :Description:
            To verify QAM channel is preferred when preference of the channel is QAM
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11108204
        """
        channellist = self.guide_page.return_channel_with_same_stationid_lcn()
        if channellist:
            channelbitsdict = self.guide_page.return_channel_bits_of_channels(channellist)
            qamchannellist = self.guide_page.return_qam_preferred_channels(channelbitsdict)
            if qamchannellist:
                self.guide_assertions.verify_qam_prefered_channels_after_merge_policy(qamchannellist)

    def test_11108206_verify_ipqam_preference_when_no_preference(self):
        """
        :Description:
            To verify QAM channel is preferred when preference of the channel is None
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11108206
        """
        channellist = self.guide_page.return_channel_with_same_stationid_lcn()
        if channellist:
            channelbitsdict = self.guide_page.return_channel_bits_of_channels(channellist)
            qamchannellist = self.guide_page.return_channel_with_no_preference(channelbitsdict)
            if qamchannellist:
                self.guide_assertions.verify_qam_prefered_channels_after_merge_policy(qamchannellist)

    @pytest.mark.ui_promotions
    def test_11113322_guide_header_press_select_top_level_app(self):
        """
        11113322
         Verify pressing SELECT on Guide Header an ad with Top level app destination.
        :return:
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE
        guide_header = self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                                          feed_name='/promotions/guideHeader',
                                                                          action_type=action_type_lbl,
                                                                          streamer_only=True,
                                                                          is_filter=True,
                                                                          is_app=True,
                                                                          is_installed=True,
                                                                          is_top_lvl=True)
        self.guide_assertions.press_select_and_verify_app_running(guide_header)

    @pytest.mark.ui_promotions
    def test_11113321_guide_header_press_select_deeplink_into_app(self):
        """
        :Description:
            Verify pressing SELECT on Guide Header an ad with Deeplink into application destination.
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11113321
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE
        guide_header = self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                                          feed_name='/promotions/guideHeader',
                                                                          action_type=action_type_lbl,
                                                                          streamer_only=True,
                                                                          need_deeplink=True,
                                                                          is_filter=True,
                                                                          is_app=True,
                                                                          is_installed=True,
                                                                          is_top_lvl=False)
        self.guide_assertions.press_select_and_verify_app_running(guide_header)

    @pytest.mark.ui_promotions
    def test_11113324_guide_header_position_in_list(self):
        """
        :Description:
            Verify position of Guide Header within Guide channel list.
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11113324
        """
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_header_ads_block(self)

    @pytest.mark.ipppv
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.xray("FRUM-802")
    @pytest.mark.msofocused
    def test_C11123692_future_program_ppv_icon(self):
        """
        Verify that the ppv icon is displayed in the grid cell for a future/ upcoming show in the Guide
        """
        channel_number_list = self.service_api.get_ppv_channel_list_current(Settings.tsn)
        if not channel_number_list:
            pytest.skip("Could not find any ppv channel")
        channel_number = channel_number_list[0][0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.menu_page.menu_navigate_left_right(0, 1)
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "ppv", expected=True)

    @pytest.mark.ipppv
    @pytest.mark.xray("FRUM-765")
    @pytest.mark.skipif(not Settings.is_managed(), reason="Valid only for managed")
    @pytest.mark.timeout(Settings.timeout)
    def test_C11124414_dismiss_ppv_purchase_overlay(self):
        """
        Verify the "Confirm Purchase" overlay is dismissed when No button is pressed
        """
        ppv_rental_channel = self.guide_page.get_ppv_rental_channel(self)
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(ppv_rental_channel)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.menu_page.menu_navigate_left_right(0, 1)
        self.guide_assertions.press_select_verify_ppv_info_overlay()
        self.guide_assertions.press_select_verify_confirm_purchase_overlay()
        self.guide_assertions.verify_confirm_purchase_overlay_dismiss()

    @pytest.mark.ipppv
    @pytest.mark.cloud_core_rent_ppv
    @pytest.mark.xray("FRUM-678")
    @pytest.mark.msofocused
    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.timeout(Settings.timeout)
    def test_C10838526_future_program_ppv_purchase(self):
        """
        Verify the purchase of on upcoming show in the Guide
        """
        ppv_rental_channel = self.guide_page.get_ppv_rental_channel(self)
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(ppv_rental_channel)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.menu_page.menu_navigate_left_right(0, 3)  # min 3 steps is needed to highlight upcoming show for 15min show
        self.guide_assertions.press_select_verify_ppv_info_overlay()
        self.guide_assertions.press_select_verify_confirm_purchase_overlay()
        self.guide_assertions.press_select_verify_ppv_purchase_confirm_overlay()

    # @pytest.mark.test_stabilization
    @pytest.mark.hospitality
    @pytest.mark.usefixtures("setup_cleanup_bind_hsn")
    @pytest.mark.notapplicable(not Settings.is_technicolor() and not Settings.is_jade() and not Settings.is_jade_hotwire(),
                               "This test is applicable only for Technicolor boxes")
    @pytest.mark.notapplicable(not ExecutionContext.service_api.get_feature_status(FeaturesList.HOSPITALITY, True),
                               "This test is applicable only for accounts with Hospitality Mode = ON")
    @pytest.mark.notapplicable(Settings.is_dev_host(),
                               "There are some specific actions that are made by Technicolor box firmware")
    def test_9917033_hospitality_device_clear_guide_default_channel(self):
        """
        Verify TiVo User settings are cleared after device clearing and login into Hospitality Welcome Screen
        """
        self.home_page.goto_live_tv()
        self.watchvideo_assertions.verify_livetv_mode()
        default_channel = self.watchvideo_assertions.get_channel_number()
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, live=False, filter_channel=True)
        self.watchvideo_page.enter_channel_number(channel[0][0], confirm=True)
        self.watchvideo_assertions.verify_livetv_mode()
        # HSN binding right after device clearing due to https://jira.xperi.com/browse/CA-20547
        self.iptv_prov_api.device_clear(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn))
        self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                    self.service_api.getPartnerCustomerId(Settings.tsn))
        self.menu_page.reconnect_dut_after_reboot(180)
        self.apps_and_games_assertions.select_continue_wait_for_home_screen_to_load(self, is_hospitality_screen_omitted=True)
        self.home_page.goto_live_tv()
        self.watchvideo_assertions.verify_livetv_mode()
        tuned_channel = self.watchvideo_assertions.get_channel_number()
        self.guide_assertions.verify_default_channel(default_channel, tuned_channel)

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_12784017_promote_what_to_watch_grid_guide_banner_program_cell_press_select_top_to_wtw(self):
        """
        :Description:
            Promote What To Watch - Grid Guide Banner - Program Cell - Press SELECT - Top of WTW
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/12784017
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE
        screen_name_lbl = self.wtw_labels.LBL_WTW_NOW
        home_lbl = self.wtw_labels.LBL_WTW_BROWSE_OPTS_HOME
        self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                           feed_name='/promotions/guideBanner',
                                                           action_type=action_type_lbl,
                                                           screen_name=screen_name_lbl,
                                                           link_to_top_of_screen=True)
        self.guide_assertions.press_select_and_verify_wtw_screen()
        # After clicking on AD that leads to category, a WTW screen opens with standard title: WHAT TO WATCH
        # Then dev side is asking server about which screen should be displayed
        # (sometimes it's very fast and sometimes it's about ~1-2 seconds to see the actual title).
        # After getting an answer from the server an actual category will be added to the title.
        # To avoid fails because of too early verification need to wait few seconds
        # and refresh a screen to get an actual title
        self.wtw_page.pause(5)
        self.screen.refresh()
        self.wtw_page.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH)
        self.wtw_page.nav_to_browse_options_menu(self)
        self.my_shows_assertions.verify_focused_program(home_lbl, self.my_shows_page.menu_focus())

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_12783901_promote_what_to_watch_grid_guide_footer_program_cell_press_select_top_to_wtw(self):
        """
        :Description:
            Verify Promote What To Watch - Grid Guide Footer - Program Cell - Press SELECT - Top of WTW
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/12783901
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE
        home_lbl = self.wtw_labels.LBL_WTW_BROWSE_OPTS_HOME
        self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                           feed_name='/promotions/guideFooter',
                                                           action_type=action_type_lbl,
                                                           screen_name=self.wtw_labels.LBL_WTW_NOW,
                                                           link_to_top_of_screen=True)
        self.guide_assertions.press_select_and_verify_wtw_screen()
        # After clicking on AD that leads to category, a WTW screen opens with standard title: WHAT TO WATCH
        # Then dev side is asking server about which screen should be displayed
        # (sometimes it's very fast and sometimes it's about ~1-2 seconds to see the actual title).
        # After getting an answer from the server an actual category will be added to the title.
        # To avoid fails because of too early verification need to wait few seconds
        # and refresh a screen to get an actual title
        self.wtw_page.pause(5)
        self.screen.refresh()
        self.wtw_page.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH)
        self.wtw_page.nav_to_browse_options_menu(self)
        self.my_shows_assertions.verify_focused_program(home_lbl, self.my_shows_page.menu_focus())

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_12783902_promote_what_to_watch_grid_guide_footer_program_cell_press_select_wtw_filter(self):
        """
        :Description:
            Promote What To Watch - Grid Guide Footer - Program Cell - Press SELECT - WTW filter
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/12783902
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE
        screen_name_lbl = self.wtw_labels.LBL_WTW_NOW
        guide_ad_obj = self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                                          feed_name='/promotions/guideFooter',
                                                                          action_type=action_type_lbl,
                                                                          screen_name=screen_name_lbl,
                                                                          link_to_top_of_screen=False,
                                                                          is_carousel=False,
                                                                          is_filter=True)
        caption = self.wtw_page.get_wtw_nav_caption_according_to_ad(self, guide_ad_obj)
        self.guide_assertions.press_select_and_verify_wtw_screen()
        # After clicking on AD that leads to category, a WTW screen opens with standard title: WHAT TO WATCH
        # Then dev side is asking server about which screen should be displayed
        # (sometimes it's very fast and sometimes it's about ~1-2 seconds to see the actual title).
        # After getting an answer from the server an actual category will be added to the title.
        # To avoid fails because of too early verification need to wait few seconds
        # and refresh a screen to get an actual title
        self.wtw_page.pause(15)
        self.screen.refresh()
        self.wtw_page.verify_screen_title(caption.upper())
        self.wtw_page.nav_to_browse_options_menu(self)
        self.my_shows_assertions.verify_focused_program(caption, self.my_shows_page.menu_focus())

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_12783914_promote_what_to_watch_grid_guide_header_program_cell_press_select_top_to_wtw(self):
        """
        :Description:
            Promote What To Watch - Grid Guide Header - Program Cell - Press SELECT - Top of WTW
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/12783914
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE
        screen_name_lbl = self.wtw_labels.LBL_WTW_NOW
        home_lbl = self.wtw_labels.LBL_WTW_BROWSE_OPTS_HOME
        self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                           feed_name='/promotions/guideHeader',
                                                           action_type=action_type_lbl,
                                                           screen_name=screen_name_lbl,
                                                           link_to_top_of_screen=True)
        self.guide_assertions.press_select_and_verify_wtw_screen()
        # After clicking on AD that leads to category, a WTW screen opens with standard title: WHAT TO WATCH
        # Then dev side is asking server about which screen should be displayed
        # (sometimes it's very fast and sometimes it's about ~1-2 seconds to see the actual title).
        # After getting an answer from the server an actual category will be added to the title.
        # To avoid fails because of too early verification need to wait few seconds
        # and refresh a screen to get an actual title
        self.wtw_page.pause(5)
        self.screen.refresh()
        self.wtw_page.verify_screen_title(self.wtw_labels.LBL_WHAT_TO_WATCH)
        self.wtw_page.nav_to_browse_options_menu(self)
        self.my_shows_assertions.verify_focused_program(home_lbl, self.my_shows_page.menu_focus())

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_12783915_promote_what_to_watch_grid_guide_header_program_cell_press_select_wtw_filter(self):
        """
        :Description:
            Promote What To Watch - Grid Guide Header - Program Cell - Press SELECT - WTW filter
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/12783915
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_ACTION_UI_NAVIGATE
        screen_name_lbl = self.wtw_labels.LBL_WTW_NOW
        guide_ad_obj = self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                                          feed_name='/promotions/guideHeader',
                                                                          action_type=action_type_lbl,
                                                                          screen_name=screen_name_lbl,
                                                                          link_to_top_of_screen=False,
                                                                          is_carousel=False,
                                                                          is_filter=True)
        caption = self.wtw_page.get_wtw_nav_caption_according_to_ad(self, guide_ad_obj)
        self.guide_assertions.press_select_and_verify_wtw_screen()
        # After clicking on AD that leads to category, a WTW screen opens with standard title: WHAT TO WATCH
        # Then dev side is asking server about which screen should be displayed
        # (sometimes it's very fast and sometimes it's about ~1-2 seconds to see the actual title).
        # After getting an answer from the server an actual category will be added to the title.
        # To avoid fails because of too early verification need to wait few seconds
        # and refresh a screen to get an actual title
        self.wtw_page.pause(5)
        self.screen.refresh()
        self.wtw_page.verify_screen_title(caption.upper())
        self.wtw_page.nav_to_browse_options_menu(self)
        self.my_shows_assertions.verify_focused_program(caption, self.my_shows_page.menu_focus())

    @pytest.mark.frumos_11
    @pytest.mark.audioonly
    @pytest.mark.skipif(not Settings.is_cc3(), reason="Audio only channel is supported only on CC3")
    @pytest.mark.p1_regression
    def test_13227053_audioonly_channel_non_recordable(self):
        """
        :desription:
           To Verify audio only channel doesn't support recording
        :testrail: https://testrail.tivo.com//index.php?/cases/view/13227053
        """
        audio_only_channel = self.service_api.get_random_audioonly_channel()
        if not audio_only_channel:
            pytest.skip("No Audio only channel Available")
        nonrecordable_channel_list = self.service_api.get_nonrecordable_channels()
        self.guide_assertions.verify_audioonly_channel_is_non_recordable(audio_only_channel, nonrecordable_channel_list)

    @pytest.mark.p1_regression
    @pytest.mark.frumos_13
    @pytest.mark.parental_control
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_C13527458_verfy_always_require_pin_for_rating(self):
        """
        :desription:
           To Verify PC PIN require for all violation rating content
        :testrail: https://testrail.tivo.com//index.php?/cases/view/13527458
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
                                         unrated_tv_show=self.menu_labels.LBL_ALLOW_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_ALLOW_ALL_UNRATED)
        self.menu_page.menu_press_back()
        self.menu_page.toggle_always_require_pin()
        channel = self.guide_page.get_streamable_rating_content(self)
        if len(channel) < 2:
            pytest.skip("could not find rating channel")
        self.home_page.goto_live_tv(channel[0])
        self.menu_assertions.verify_enter_PIN_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.goto_live_tv(channel[1])
        self.menu_assertions.verify_enter_PIN_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.p1_regression
    @pytest.mark.frumos_13
    @pytest.mark.parental_control
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_C13527478_verfy_always_require_pin_for_adult_content(self):
        """
        :desription:
           To Verify PC PIN require for all adult violation content
        :testrail: https://testrail.tivo.com//index.php?/cases/view/13527478
        """
        channel = self.guide_page.get_streamable_adult_content(self)
        if len(channel) < 2:
            pytest.skip("could not find more than one adult channel")
        self.menu_page.go_to_parental_controls(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.enter_default_parental_control_password(self)  # to confirm
        self.menu_page.toggle_hide_adult_content()
        self.menu_page.toggle_always_require_pin()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0])
        self.screen.base.press_enter()
        self.wtw_page.pause(5)
        if self.guide_page.is_overlay_shown() and self.menu_page.enter_PIN_overlay_visibility(self):
            self.guide_page.press_back_button()
            self.guide_page.press_right_button()
            self.screen.base.press_enter()
            self.wtw_page.pause(5)
        self.watchvideo_assertions.verify_adult_show_locked_osd()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(180)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[1])
        self.screen.base.press_enter()
        self.wtw_page.pause(5)
        self.watchvideo_assertions.verify_adult_show_locked_osd()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(180)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.p1_regression
    @pytest.mark.frumos_13
    @pytest.mark.parental_control
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_C13527480_verify_different_adult_content_detail_with_pc_always_require_pin(self):
        """
        :desription:
           To Verify title and descriptio is hidden for all adult content when enter the PIN for one of the adult content.
        :testrail: https://testrail.tivo.com//index.php?/cases/view/13527480
        """
        channel = self.guide_page.get_streamable_adult_content(self)
        if len(channel) < 2:
            pytest.skip("could not find more than 2 adult channel")
        self.menu_page.go_to_parental_controls(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.enter_default_parental_control_password(self)  # to confirm
        self.menu_page.toggle_hide_adult_content()
        self.menu_page.toggle_always_require_pin()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0])
        self.screen.base.press_enter()
        self.wtw_page.pause(5)
        if self.guide_page.is_overlay_shown() and self.menu_page.enter_PIN_overlay_visibility(self):
            self.guide_page.press_back_button()
            self.guide_page.press_right_button()
            self.screen.base.press_enter()
            self.wtw_page.pause(5)
        self.watchvideo_assertions.verify_adult_show_locked_osd()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(180)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[1])
        self.guide_assertions.guide_adult_content_is_hidden()

    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("set_one_pass_record_option_to_new_only")
    def test_329707705_newonly_guide(self):
        """
        :desription:
           To Verify the default value for record in onepass options overlay in current guide
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True, ascii=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.menu_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.menu_page.wait_for_screen_ready()
        self.guide_page.open_record_overlay()
        self.guide_page.select_menu_by_substring(self.guide_labels.LBL_CREATE)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_option(self.guide_labels.LBL_RECORD_MENU, self.guide_labels.LBL_NEW_ONLY)

    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_329707706_newonly_pastguide(self):
        """
        :desription:
           To Verify the default value for record in onepass options overlay in past guide
        """
        # channels = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn)
        channels = self.service_api.get_recordable_non_movie_channel(filter_channel=True, ascii=True)
        if not channels:
            pytest.skip("Could not find any channel.")
        channel = (channels[0][0])
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        self.menu_page.menu_navigate_left_right(2, 0)
        self.menu_page.wait_for_screen_ready()
        self.guide_page.open_record_overlay()
        self.guide_page.select_menu_by_substring(self.guide_labels.LBL_CREATE)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_option(self.guide_labels.LBL_RECORD_MENU, self.guide_labels.LBL_NEW_ONLY)

    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.xray("FRUM-826")
    @pytest.mark.msofocused
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_13526742_grid_guide_banner_press_select_live_tv_station_subscribed_station_id(self):
        """
        :Description:
            Grid Guide - Guide Banner - Press SELECT - LiveTV Station - Subscribed stationId
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/13526742
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_LIVE_TV_UI_ACTION
        guide_ad = self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                                      feed_name='/promotions/guideBanner',
                                                                      action_type=action_type_lbl,
                                                                      is_filter=True,
                                                                      is_subscribed=True,
                                                                      is_tivo_plus=False)
        self.guide_assertions.press_select_verify_playback()
        self.watchvideo_assertions.verify_channel_number(guide_ad['channelNumber'])

    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_13526742_grid_guide_banner_press_select_live_tv_station_subscribed_tivo_plus_station_id(self):
        """
        :Description:
            Grid Guide - Guide Banner - Press SELECT - LiveTV Station - TiVo+ stationId
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/13526745
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_LIVE_TV_UI_ACTION
        guide_ad = self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                                      feed_name='/promotions/guideBanner',
                                                                      action_type=action_type_lbl,
                                                                      is_filter=True,
                                                                      is_subscribed=True,
                                                                      is_tivo_plus=True)
        self.guide_page.tune_to_tivo_plus_channel(self)
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_channel_number(guide_ad['channelNumber'])

    @pytest.mark.ui_promotions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions", "remove_channel_package_sports")
    def test_13526742_grid_guide_banner_press_select_live_tv_station_unsubscribed_station_id(self):
        """
        :Description:
            Grid Guide - Guide Banner - Press SELECT - LiveTV Station - Unsubscribed stationId
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/13526743
        """
        self.home_page.go_to_guide(self)
        action_type_lbl = self.guide_labels.LBL_GUIDE_BANNER_LIVE_TV_UI_ACTION
        self.guide_page.find_and_nav_to_guide_ad_using_gui(self,
                                                           feed_name='/promotions/guideBanner',
                                                           action_type=action_type_lbl,
                                                           is_filter=True,
                                                           is_subscribed=False,
                                                           is_tivo_plus=False)
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_13):
            self.screen.base.press_enter()
            self.watchvideo_assertions.verify_livetv_mode()
            self.watchvideo_assertions.verify_rating_limits_osd_in_live_tv(error_code="V56")
        else:
            self.guide_assertions.press_select_verify_channel_not_subscribed_overlay()

    @pytest.mark.p1_regression
    @pytest.mark.frumos_13
    @pytest.mark.timeout(Settings.timeout)
    @pytestrail.case("C11687969")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_C11687969_verify_pc_violation_and_title_hidden_for_adult_content_grid_guide(self):
        """
        :description:
           To Verify user can't Tune to the channel when program with AC is in progress
           from Grid Guide.
           Verify that if PC and HAC are on, Title in the guide cell is obscured.
        :testrail: https://testrail.tivo.com/index.php?/cases/view/11687969
        """
        channel = self.guide_page.get_streamable_adult_content(self)
        if len(channel) < 1:
            pytest.skip("could not find adult channel")
        self.menu_page.go_to_parental_controls(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.enter_default_parental_control_password(self)  # to confirm
        self.menu_page.toggle_hide_adult_content()
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.get_live_program_name(self)
        self.guide_page.enter_channel_number(random.choice(channel))
        self.guide_assertions.guide_adult_content_is_hidden()
        self.screen.base.press_enter()
        self.wtw_page.pause(5)
        self.watchvideo_assertions.verify_adult_show_locked_osd()
        self.screen.base.press_enter()
        self.menu_assertions.verify_enter_PIN_overlay()
        self.vod_page.enter_pin_in_overlay(self)
        self.watchvideo_assertions.verify_playback_play()

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-1062")
    @pytest.mark.platform_cert_smoke_test
    def test_14386448_verify_jump_channel_launch_from_guide_and_appsandgames(self):
        """
        Verify if jump channel app is launched from Guide and Apps and Games

        https://testrail.tivo.com/index.php?/cases/view/14386448
        """
        channels = self.service_api.get_jump_channels_list()
        channel_num = random.choice(self.guide_page.check_channel_availability(self, channels))
        channel_name = channels[channel_num]
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(channel_num)
        self.guide_page.wait_for_screen_ready()
        channel_name_guide = self.guide_page.get_channel_call_sign()
        self.screen.base.press_enter()
        self.guide_page.wait_for_screen_ready(timeout=10000)
        screentitle = self.guide_page.get_screen_title(refresh=True)
        self.guide_assertions.verify_jump_channel_launch()
        if screentitle == self.guide_labels.LBL_ON_DEMAND_SCREEN_TITLE:
            self.vod_page.go_to_vod(self)
            self.vod_assertions.verify_screen_title(self.vod_labels.LBL_ON_DEMAND)
        elif screentitle != self.guide_labels.LBL_ON_DEMAND_SCREEN_TITLE and Settings.is_unmanaged():
            self.home_page.launch_app_from_GA_from_any_screen(self, channel_name_guide)
            self.guide_page.wait_for_screen_ready(timeout=200000)
            self.program_options_assertions.verify_ott_app_is_foreground(self, channel_name_guide.lower())
        else:
            self.apps_and_games_page.go_to_apps_and_games(self)
            self.apps_and_games_assertions.start_ott_application_and_verify_screen(self, channel_name.lower())

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_14378826_dismiss_dimming_and_go_to_guide(self):
        """
        Dismiss Dimming screen - Buttons - Guide

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/14378826
        """
        self.home_page.update_test_conf_and_reboot(TIMEOUT_TO_DIMMING_SCREEN=60000)
        self.home_page.back_to_home_short()
        self.home_page.pause(60, "Waiting for the Dimming screen to appear")
        self.home_assertions.verify_view_mode(self.home_labels.LBL_DIMMING_SCREEN_VIEW_MODE)
        self.home_page.press_guide_button()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_view_mode(self.guide_labels.LBL_VIEW_MODE)

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_14379357_verify_no_dimming_screen_when_returning_from_ott_with_back_btn(self):
        """
        Dismiss Dimming screen - Buttons - OTT: Netflix/YouTube - Back

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/14379357
        """
        self.home_page.update_test_conf_and_reboot(TIMEOUT_TO_DIMMING_SCREEN=60000)
        self.home_page.go_to_guide(self)
        self.guide_page.pause(60, "Waiting for the Dimming screen to appear")
        self.guide_assertions.verify_view_mode(self.home_labels.LBL_DIMMING_SCREEN_VIEW_MODE)
        self.guide_assertions.press_youtube_and_verify_screen(self)
        self.apps_and_games_page.exit_ott_app_with_back_button()
        self.guide_assertions.verify_view_mode(self.guide_labels.LBL_VIEW_MODE)

    @pytest.mark.subscription_management
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.SOCU)])
    @pytest.mark.parametrize("req_type", [NotificationSendReqTypes.NSR])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.SOCU)])
    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-20461")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13))
    @pytest.mark.notapplicable(not Settings.is_internal_mso())
    def test_t519533377_socu_feature_status_false(self, request, req_type, feature_status_feature, device_info_store_feature):
        """
        SOCU feature is expected to be OFF when it is OFF in featureStatusSearch.Catchup icon not displayed
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, False)
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, expected=False)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell", expected=False)

    @pytest.mark.subscription_management
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.SOCU)])
    @pytest.mark.parametrize("req_type", [NotificationSendReqTypes.NSR])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.SOCU)])
    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-20441")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13))
    @pytest.mark.notapplicable(not Settings.is_internal_mso())
    def test_t519533376_socu_feature_status_true(self, request, req_type, feature_status_feature, device_info_store_feature):
        """
        SOCU feature is expected to be ON. The feature is ON in BodyConfig and ON in featureStatusSearch.
        Verify catchup icon in Guide program cell"""
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, True)
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, "socu_guide_cell")

    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.SOCU, FeAlacartePackageTypeList.NATIVE)])
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.usefixtures("cleanup_package_names_native")
    def test_C12784854_drm_type_socu_native_socu_startover_playback(self, request, feature, package_type):
        """
        DRM type Native SOCU StartOver playback - verify socu startover playback on drm type native

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/12784854
        """
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn, filter_channel=True, filter_socu=True)
        if not channel:
            pytest.skip("Could not find any SOCU channel")
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        focused_item = self.guide_page.get_live_program_name(self)
        self.guide_assertions.press_select_verify_record_overlay(self, long_press=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_372870771_guide_logo_recovery_in_hydra(self, get_overrides):
        """
        Verify that AppGlobalDataModel do retry operation after foreground event

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870771
        """
        self.home_page.update_test_conf_and_reboot(
            "device", fast=True, clear_data=True, DEBUGENV="ModelUpdater", **get_overrides
        )
        self.home_page.back_to_home_short()
        if self.guide_page.get_channel_logo_status(self):
            raise ValueError("Logo is present with overrides applied!")
        self.guide_page.wait_for_condition_satisfied(
            self.guide_page.get_channel_logo_status, fun_args=[self], timeout=360
        )
        assert_that(self.guide_page.get_channel_logo_status(self), "Logo is not displayed!")

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_372870789_guide_logo_recovery_by_foreground_event(self, get_overrides):
        """
        Verify that AppGlobalDataModel do retry operation after foreground event

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870789
        """
        self.home_page.update_test_conf_and_reboot(
            "device", fast=True, clear_data=True, DEBUGENV="ModelUpdater", **get_overrides
        )
        self.home_page.back_to_home()
        if self.guide_page.get_channel_logo_status(self):
            raise ValueError("Logo is present with overrides applied!")
        self.screen.base.press_netflix()
        self.apps_and_games_assertions.verify_netflix_screen_with_package(self)
        self.screen.base.stop_app(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME)
        self.guide_page.wait_for_condition_satisfied(self.guide_page.get_channel_logo_status, fun_args=[self])
        assert_that(self.guide_page.get_channel_logo_status(self), "Logo is not displayed!")

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_372870772_greyed_channel_recovery_in_hydra_pt1(self, get_overrides):
        """
        Verify that SettingsModel do retry operation by timer inside of Hydra

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870789
        """
        channels = self.service_api.get_unentitled_channels()
        if not channels:
            pytest.skip("Couldn't find any greyed channel")
        self.home_page.update_test_conf_and_reboot("device", fast=True, **get_overrides)
        self.home_page.back_to_home()
        self.home_page.get_live_tv_error_status(self, "V56", channels[0])
        self.guide_page.wait_for_condition_satisfied(self.home_page.get_live_tv_error_status,
                                                     fun_args=(self, "V56", channels[0]),
                                                     timeout=400, expected_result=False)

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_372870774_greyed_channel_recovery_in_hydra_pt2(self, get_overrides):
        """
        Verify that SettingsModel do retry operation by timer inside of Hydra

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870774
        """
        channels = self.service_api.get_unentitled_channels()
        if not channels:
            pytest.skip("Couldn't find any greyed channel")
        self.home_page.update_test_conf_and_reboot("device", fast=True, **get_overrides)
        self.home_page.back_to_home()
        self.home_page.get_live_tv_error_status(self, "V56", channels[0])
        self.guide_page.wait_for_condition_satisfied(self.home_page.get_live_tv_error_status,
                                                     fun_args=(self, "V56", channels[0]),
                                                     timeout=400, expected_result=False)

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_372870792_greyed_channel_recovery_by_foreground_pt1(self, get_overrides):
        """
        Verify that SettingsModel recovers by foreground signal

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870792
        """
        channels = self.service_api.get_unentitled_channels()
        if not channels:
            pytest.skip("Couldn't find any greyed channel")
        self.home_page.update_test_conf_and_reboot("device", fast=True, **get_overrides)
        self.home_page.back_to_home()
        self.home_page.get_live_tv_error_status(self, "V56", channels[0])
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.screen.base.stop_app(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME)
        self.guide_page.wait_for_condition_satisfied(self.home_page.get_live_tv_error_status,
                                                     fun_args=(self, "V56", channels[0]),
                                                     timeout=60, expected_result=False)

    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_372870791_greyed_channel_recovery_by_foreground_pt2(self, get_overrides):
        """
        Verify that SettingsModel recovers by foreground signal

        Testrail:
            https://testrail.tivo.com/index.php?/tests/view/372870791
        """
        channels = self.service_api.get_unentitled_channels()
        if not channels:
            pytest.skip("Couldn't find any greyed channel")
        self.home_page.update_test_conf_and_reboot("device", fast=True, **get_overrides)
        self.home_page.back_to_home()
        self.home_page.get_live_tv_error_status(self, "V56", channels[0])
        self.apps_and_games_page.press_netflix_and_verify_screen(self)
        self.screen.base.stop_app(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME)
        self.guide_page.wait_for_condition_satisfied(self.home_page.get_live_tv_error_status,
                                                     fun_args=(self, "V56", channels[0]),
                                                     timeout=60, expected_result=False)

    @pytest.mark.p1_regression
    def test_20933920_verify_home_screen_is_stacked_on_guide(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20933920
        """
        self.home_page.back_to_home_short()
        for i in range(30):
            self.screen.base.press_guide()
            self.guide_page.wait_for_screen_ready()
            self.guide_assertions.verify_guide_title()
            self.screen.base.press_back()
            self.guide_page.wait_for_screen_ready()
            self.home_assertions.verify_home_title()
        if Settings.is_managed():
            for i in range(30):
                self.screen.base.press_guide()
                self.guide_page.wait_for_screen_ready()
                self.guide_assertions.verify_guide_title()
                self.screen.base.press_home()
                self.guide_page.wait_for_screen_ready()
                self.home_assertions.verify_home_title()

    @pytest.mark.p1_regression
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures("setup_delete_book_marks")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif(not Settings.is_managed(),
                        reason="Info is present on managed streamers only")
    def test_4863205_explicit_feedback_info_cards_bookmark_non_episodic(self):
        """
        Explicit Feedback - Info Cards - Bookmark show

        Testrail link : https://testrail.tivo.com//index.php?/cases/view/4863205
        """
        non_episodic_channels = self.api_parser.get_non_episodic_shows_channel_list()
        if not non_episodic_channels:
            pytest.skip("No non episodic channel found")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(non_episodic_channels[0])
        self.guide_page.wait_for_guide_next_page()
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_get_more_info(self)
        self.wtw_page.nav_to_info_card_action_mode(self)
        self.guide_page.select_menu_by_substring(self.menu_labels.LBL_BOOKMARK)
        self.wtw_page.verify_whisper(self.menu_labels.LBL_BOOKMARK_COMMON_WHISPER)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_content_in_any_category(self, program)

    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_parental_control")
    def test_C20949465_verify_adult_category_option_in_OnDemand_to_check_adult_channnels(self):
        channels = self.guide_page.get_streamable_adult_content(self)
        if len(channels) < 1:
            pytest.skip("could not find adult channel")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0])
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.toggle_hide_adult_content()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0])
        self.wtw_page.pause(5)
        self.home_page.wait_for_screen_ready("GuideListModel")
        lbl = self.liveTv_labels
        self.guide_assertions.verify_show_title(lbl.LBL_TITLE_HIDDEN_ADULT_CONTENT, mode="guide_header")

    @pytest.mark.stop_streaming
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    def test_20932949_verify_stop_streaming_while_catchup_videowindow_off(self):
        """
        Stop Streaming - Video Window OFF - CatchUP- TV OFF/ON

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/20932949
        """
        self.menu_page.disable_full_screen_video_on_home(self)
        channel = self.service_api.get_random_catch_up_channel_current_air(Settings.tsn,
                                                                           filter_channel=True,
                                                                           filter_socu=True,
                                                                           restrict=False)
        if channel is None:
            pytest.skip("No channel found")
        channel_number = (channel[0][0])
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.menu_page.menu_navigate_left_right(3, 0)
        self.guide_page.wait_for_screen_ready()
        focused_item = self.guide_page.get_focussed_grid_item(self)
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_assertions.press_select_verify_watch_screen(self, focused_item)
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

    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_4866146_verify_thuuz_rating_when_thuuz_rating_is_OFF(self):
        self.api.cancel_all_recordings()
        thuuz_channel = self.service_api.get_sports_with_thuuz_rating()
        if not thuuz_channel:
            pytest.skip("Did not find any channels with Thuuz Rating. Hence Skipping")
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.select_menu(self.menu_labels.LBL_THUUZ_SPORTS_RATING)
        self.menu_page.select_menu(self.menu_labels.LBL_NO)  # Thuuz rating OFF
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(thuuz_channel[0]['channelNumber'])
        self.guide_assertions.verify_thuuz_ratings(visible=False)
        self.guide_page.open_record_overlay()
        self.guide_page.select_menu_by_substring(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_critic_ratings(visible=False)

    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_4866147_verify_thuuz_rating_on_guide_when_thuuz_rating_is_ON(self):
        self.api.cancel_all_recordings()
        thuuz_channel = self.service_api.get_sports_with_thuuz_rating()
        if not thuuz_channel:
            pytest.skip("Did not find any channels with Thuuz Rating. Hence Skipping")
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.select_menu(self.menu_labels.LBL_THUUZ_SPORTS_RATING)
        self.menu_page.select_menu(self.menu_labels.LBL_YES)  # Thuuz rating ON
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(thuuz_channel[0]['channelNumber'])
        self.guide_assertions.verify_thuuz_ratings()
        self.guide_page.open_record_overlay()
        self.guide_page.select_menu_by_substring(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_critic_ratings()

    # @pytiest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.guide
    def test_20954167_verify_guide_data(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20954167
        """
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.home_page.go_to_guide(self)
        channel_number = self.service_api.get_random_live_channel_rich_info(channel_count=5, episodic=True,
                                                                            filter_channel=True, transport_type="stream")
        if not channel_number:
            pytest.skip("Could not find any channel. hence skipping")
        count = len(channel_number)
        for i in range(count):
            self.watchvideo_page.enter_channel_number(channel_number[i][0], confirm=True)
            self.home_page.wait_for_screen_ready()
            if self.guide_page.view_mode() == self.guide_labels.LBL_VIEW_MODE:
                self.guide_page.press_ok_button()
            self.watchvideo_assertions.verify_playback_play()
            self.watchvideo_assertions.verify_livetv_mode()
        self.home_page.press_guide_button()
        self.guide_assertions.verify_guide_screen(self)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.guide
    @pytest.mark.skipif(not Settings.is_managed(), reason="Valid only for managed")
    def test_20954503_verify_guide_data_load_after_launching_OTT(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20954503
        """
        self.home_page.go_to_guide(self)
        self.home_page.launch_app_from_GA_from_any_screen(self, "Youtube")
        self.guide_page.wait_for_screen_ready(timeout=200000)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.guide_page.wait_for_screen_ready()
        self.screen.base.press_guide()  # Press Guide button
        self.guide_page.wait_for_screen_ready(timeout=500000)
        self.guide_assertions.verify_guide_screen(self)
        self.home_page.back_to_home_short()
        self.guide_page.wait_for_screen_ready()
        self.home_assertions.verify_home_title()
        self.home_page.go_to_guide(self)
        self.home_page.launch_app_from_GA_from_any_screen(self, "Youtube")
        self.guide_page.wait_for_screen_ready(timeout=200000)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.watchvideo_page.press_exit_button()  # Press Exit button
        self.guide_page.wait_for_screen_ready(timeout=500000)
        self.guide_assertions.verify_guide_screen(self)
        self.home_page.back_to_home_short()
        self.guide_page.wait_for_screen_ready()
        self.home_assertions.verify_home_title()
        self.home_page.go_to_guide(self)
        self.home_page.launch_app_from_GA_from_any_screen(self, "Youtube")
        self.guide_page.wait_for_screen_ready(timeout=200000)
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.home_page.press_home_button()  # Press Home button
        self.screen.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=200000)
        self.home_assertions.verify_home_title()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.home_page.launch_app_from_GA_from_any_screen(self, "Youtube")
        self.guide_page.wait_for_screen_ready()
        self.program_options_assertions.verify_ott_app_is_foreground(self, "youtube")
        self.apps_and_games_page.play_youtube_content()
        self.home_page.press_guide_button()
        self.guide_page.wait_for_screen_ready(timeout=500000)
        self.guide_assertions.verify_guide_screen(self)
        self.home_page.back_to_home_short()
        self.guide_page.wait_for_screen_ready()
        self.home_assertions.verify_home_title()

    @pytest.mark.iponly_dvr_smartbox
    @pytest.mark.notapplicable(
        not Settings.is_smartbox() and not Settings.is_topaz and not Settings.is_taos(),
        "Device mode supported for Topaz and smartboxes only")
    def test_channelist_based_on_device_mode(self):
        """
        To verify channel list based on device mode.
        This test is applicable only for topaz or smartbox
        testrail :
        https://testrail.tivo.com//index.php?/cases/view/20951852
        https://testrail.tivo.com//index.php?/cases/view/20951853
        https://testrail.tivo.com//index.php?/cases/view/20955137
        https://testrail.tivo.com//index.php?/cases/view/20955139
        """
        device_mode = self.menu_page.get_stb_mode(self)
        self.guide_assertions.verify_channellist_based_on_device_mode(device_mode)

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.longrun_2
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_21259775_create_onepass_and_verify_next_episodes_are_recording(self):
        """
        Create OnePass series from the guide and verify next episodes of the series are recording.
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if not channel:
            pytest.skip("Recordable channels are not found. Hence skipping")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.get_live_program_name(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_only=True, new_only=True)
        self.home_page.log.info(f"created onepass for the program {program}")
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_screen(self)
        self.menu_page.go_to_one_pass_manager(self)
        self.home_assertions.verify_show_in_one_pass_manager(self, program)
        next_episode = self.guide_page.get_upcoming_episode(self)
        self.guide_page.wait_for_upcoming_episode_to_air(self, program, next_episode[0], next_episode[1], next_episode[3])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.nav_to_menu_by_substring(program)
        self.my_shows_assertions.verify_recording_icon()

    @pytest.mark.p1_regression
    @pytest.mark.cloud_core_guide_preview
    def test_21557980_verify_metacritic_rating_on_guide(self):
        """
        Verify Metacritic rating on action screen
        """
        self.api.cancel_all_recordings()
        metacritic_channel = self.service_api.get_movies_with_metacritic_ratings(collection_type='movie')
        if not metacritic_channel:
            pytest.skip("Did not find any channels with Metacritic Rating. Hence Skipping")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(metacritic_channel[0]['channelNumber'])
        self.guide_assertions.verify_thuuz_ratings()
        self.guide_page.open_record_overlay()
        self.guide_page.select_menu_by_substring(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_critic_ratings()

    @pytest.mark.guide_holes
    def test_21557978_detect_holes_in_guide_for_past_one_day(self):
        """
        Test case detects holes in guide by checking past 1 day data.
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if channel is None:
            pytest.skip("Could not find any channel. hence skipping")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        holes1 = self.guide_page.press_up_down_and_verify_guide_data(self, up=True)
        self.guide_page.enter_channel_number(channel[0][0])
        holes2 = self.guide_page.verify_past_future_guide_data(self, past=True, days=1)
        holes3 = self.guide_page.press_up_down_and_verify_guide_data(self, down=True)
        self.guide_assertions.verify_guide_holes(holes1, holes2, holes3)

    @pytest.mark.guide_holes
    def test_21557978_detect_holes_in_guide_for_past_three_day(self):
        """
        Test case detects holes in guide by checking past 3 days data.
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if channel is None:
            pytest.skip("Could not find any channel. hence skipping")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        holes1 = self.guide_page.press_up_down_and_verify_guide_data(self, up=True)
        self.guide_page.enter_channel_number(channel[0][0])
        holes2 = self.guide_page.verify_past_future_guide_data(self, past=True, days=3)
        holes3 = self.guide_page.press_up_down_and_verify_guide_data(self, down=True)
        self.guide_assertions.verify_guide_holes(holes1, holes2, holes3)

    @pytest.mark.guide_holes
    def test_21557978_detect_holes_in_guide_for_future_one_day(self):
        """
        Test case detects holes in guide by checking future 1 day data.
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if channel is None:
            pytest.skip("Could not find any channel. hence skipping")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        holes1 = self.guide_page.press_up_down_and_verify_guide_data(self, up=True)
        self.guide_page.enter_channel_number(channel[0][0])
        holes2 = self.guide_page.verify_past_future_guide_data(self, future=True, days=1)
        holes3 = self.guide_page.press_up_down_and_verify_guide_data(self, down=True)
        self.guide_assertions.verify_guide_holes(holes1, holes2, holes3)

    @pytest.mark.guide_holes
    def test_21557978_detect_holes_in_guide_for_future_three_day(self):
        """
        Test case detects holes in guide by checking past 3 days data.
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if channel is None:
            pytest.skip("Could not find any channel. hence skipping")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        holes1 = self.guide_page.press_up_down_and_verify_guide_data(self, up=True)
        self.guide_page.enter_channel_number(channel[0][0])
        holes2 = self.guide_page.verify_past_future_guide_data(self, future=True, days=3)
        holes3 = self.guide_page.press_up_down_and_verify_guide_data(self, down=True)
        self.guide_assertions.verify_guide_holes(holes1, holes2, holes3)

    @pytest.mark.guide_holes
    def test_21557978_detect_holes_in_guide_for_future_seven_day(self):
        """
        Test case detects holes in guide by checking past 7 days data.
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if channel is None:
            pytest.skip("Could not find any channel. hence skipping")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        holes1 = self.guide_page.press_up_down_and_verify_guide_data(self, up=True)
        self.guide_page.enter_channel_number(channel[0][0])
        holes2 = self.guide_page.verify_past_future_guide_data(self, future=True, days=7)
        holes3 = self.guide_page.press_up_down_and_verify_guide_data(self, down=True)
        self.guide_assertions.verify_guide_holes(holes1, holes2, holes3)

    @pytest.mark.nDVR_showing_restriction
    @pytest.mark.p1_regression
    @pytest.mark.frumos_15
    def test_20932925_no_record_button_on_guide_info_banner_for_nDVR_restricted_offer(self):
        """
        To verify no record options on guide info banner for nDVR restricted offer
        https://testrail.tivo.com//index.php?/cases/view/20932925
        """
        channels = self.service_api.get_recording_channel_with_live_offer_restricted()
        if not channels:
            pytest.skip("Failed to call station_search")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number((random.sample(channels, 1))[0], confirm=True)
        self.home_page.wait_for_screen_ready()
        self.screen.base.long_press_enter()
        self.guide_page.wait_for_screen_ready(self.liveTv_labels.LBL_RECORD_OVERLAY)
        self.guide_assertions.verify_no_record_button_on_guide_info_banner_for_nDVR_restricted_offer()

    @pytest.mark.nDVR_showing_restriction
    @pytest.mark.p1_regression
    @pytest.mark.frumos_15
    def test_20932924_status_message_in_guide_info_banner_for_nDVR_restricted_offer(self):
        """
        To Verify status message in guide info banner for nDVR restricted offer
        https://testrail.tivo.com//index.php?/cases/view/20932924
        """
        channels = self.service_api.get_recording_channel_with_live_offer_restricted()
        if not channels:
            pytest.skip("Failed to call station_search")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number((random.sample(channels, 1))[0], confirm=True)
        self.home_page.wait_for_screen_ready()
        self.screen.base.press_info()
        self.home_page.wait_for_screen_ready()
        self.guide_assertions.verify_status_message_in_guide_info_banner_for_nDVR_restricted_offer()

    @pytest.mark.service_reliability
    def test_21558036_press_guide_button_and_verify_guide_screen(self):
        """
        Test Case on Guide
        """
        self.home_page.back_to_home_short()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=50000)
        self.guide_page.timestamp_test_start()
        self.guide_page.screen.base.press_guide()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN, timeout=60000)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.timestamp_test_end()

    # @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures(
        "toggle_guide_rows_service_availability"
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18) else "switch_tivo_service_rasp")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Enter to Disconnected State. NoNetworkScreen is shown")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH")
    def test_21558281_verify_guide_and_livetv_when_service_down(self, request):
        """
        Verify Guide functionality when service is down
        """
        channel_number = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                                    transportType="stream")[0][0]
        if not channel_number:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_assertions.verify_disconnected_program_name(self.guide_labels.LBL_DS_PROGRAM_CELL)
        self.guide_assertions.press_select_verify_playback(stay_tick_play_bar=False, stay_ipppv_osd=False,
                                                           stay_playback=False)
        is_1_18_or_higher = True if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18) else False
        # There is ability to scroll left/right to Past/Futue Guide since Hydra v1.18
        self.guide_assertions.verify_future_guide_blocked(expected=not is_1_18_or_higher)
        if is_1_18_or_higher:
            self.home_page.go_to_guide(self)  # to return to In-Progress Guide
        self.guide_assertions.verify_past_guide_blocked(expected=not is_1_18_or_higher)

    # @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures(
        "toggle_guide_rows_service_availability"
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18) else "switch_tivo_service_rasp")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Enter to Disconnected State. NoNetworkScreen is shown")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH")
    def test_21558282_verify_channel_options_watch_now_when_service_down(self, request):
        """
        Verify Guide functionality when service is down
        """
        channel_number = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                                    transportType="stream")[0][0]
        if not channel_number:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_assertions.verify_disconnected_program_name(self.guide_labels.LBL_DS_PROGRAM_CELL)
        self.guide_page.screen.base.press_left()
        self.guide_page.screen.base.press_info()
        self.guide_assertions.press_select_verify_playback()

    @pytest.mark.tivo_plus
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.timeout(Settings.timeout)
    def test_389366323_guide_backward_stickiness_from_tivo_plus_channel(self):
        """
            Verify the TiVo+ channels - Guide - Backward stickiness
            Testrail:
                https://testrail.tivo.com//index.php?/tests/view/389366323
        """
        channel = self.service_api.get_tivo_plus_channels()[0]
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.press_down_button(refresh=True)
        highlighted_channel_number = self.guide_page.get_grid_focus_details()['channel_number']
        self.guide_assertions.verify_channel_of_highlighted_program_cell(highlighted_channel_number)
        self.screen.base.press_exit_button(5)
        self.watchvideo_page.tune_to_tivo_plus_channel(channel)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(180)
        self.watchvideo_assertions.verify_playback_play(tivo_plus_channel=True)
        self.watchvideo_assertions.verify_channel_number(channel)
        self.screen.base.press_back()
        self.guide_assertions.verify_channel_of_highlighted_program_cell(highlighted_channel_number)

    @pytest.mark.nDVR_showing_restriction
    @pytest.mark.p1_regression
    @pytest.mark.frumos_15
    def test_20932922_status_message_in_guide_info_banner_for_nDVR_restricted_channel(self):
        """
        To Verify status message in guide info banner for nDVR restricted channel offer
        https://testrail.tivo.com//index.php?/cases/view/20932922
        """
        channels = self.service_api.get_nonrecordable_channels()
        if not channels:
            pytest.skip("No non-recordable channels found.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number((random.sample(channels, 1))[0], confirm=True)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.screen.base.press_info()
        self.home_page.wait_for_screen_ready()
        self.guide_assertions.verify_status_message_in_guide_info_banner_for_nDVR_restricted_channel()

    @pytest.mark.socu
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout_mid)
    def test_21568518_playback_socu_and_verify_error_overlay_should_not_display(self):
        """
        Playback SoCu and wait for program to end and it should start next program in LiveTV without any error.
        https://jira.tivo.com/browse/CA-9730
        """
        channel = self.guide_page.get_encrypted_socu_channel(self, filter_socu=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        channel_number = (channel[0][0])
        self.home_page.goto_live_tv(channel_number)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_page.press_left_multiple_times(no_of_times=3)
        self.watchvideo_assertions.is_startover_focused(refresh=True)
        self.screen.base.press_enter(10)  # Press 'Start Over' button and wait for 10 sec
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_startover_of_the_video(value)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.wait_for_current_show_to_finish()
        self.watchvideo_page.watch_video_for(60 * 15)  # To watch next program
        self.watchvideo_assertions.verify_playback_play()

    @pytestrail.case("C21570284")
    @pytest.mark.frumos_15
    @pytest.mark.platform_cert_smoke_test
    def test_C21570284_verify_previous_guide_data_days_onelineguide(self):
        """
        Verify that the epg past content shows for number of days published from brandingbundle on
        OneLineGuide. If Bundle fetch fails or nothing is published, fallback to 3 days happens.
        Publishing of epglookbackhours (further converted to number of days) is done from service console because
        repetitive publishing through automation cases is not recommended on all environments.
        :return:
        """
        Epg_Past_Number_of_Days = self.guide_page.get_epgLookBackHours(self)
        epglookbackhours = Epg_Past_Number_of_Days * 24
        channel_number = self.service_api.get_random_channel(Settings.tsn, "entitled", mso=Settings.mso,
                                                             filter_channel=True)
        if not channel_number:
            pytest.skip("Could not find any channel.")
        self.home_page.goto_live_tv(channel_number)
        self.guide_page.goto_one_line_guide_from_live(self)
        self.menu_page.menu_navigate_left_right(epglookbackhours, 0)

    @pytest.mark.audioonly
    def test_t389366339_audioonly_channel_create_onepass(self):
        """
        :desription:
           To Verify creation of onepass in audio only channel
        :https://testrail.tivo.com//index.php?/tests/view/389366339
        """
        audio_only_channel = self.service_api.get_random_audioonly_channel()
        if not audio_only_channel:
            pytest.skip("No audio only channel found")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(audio_only_channel[0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_one_pass_on_record_overlay(self)
        self.menu_page.go_to_one_pass_manager(self)
        self.menu_assertions.verify_onepass_manager_screen_title(self)
        self.home_assertions.verify_show_in_one_pass_manager(self, program)

    @pytest.mark.xray("FRUM-91285")
    @pytest.mark.p1_regression
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_91285_launch_netflix_from_jump_channel(self):
        jump_channels = self.api.get_jump_channels_list()
        channel_num = self.guide_page.get_jump_channel_number(channels=jump_channels, app=self.menu_labels.LBL_NETFLIX)
        if channel_num is None:
            pytest.skip("Device does not have netflix app")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_num)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.screen.base.press_enter()
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_17)

    @pytest.mark.xray("FRUM-91293")
    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_91293_launch_netflix_from_action_screen(self):
        group_names = self.service_api.get_service_group_search()
        webkit_name = self.guide_page.get_webkit_group_name('Netflix', group_names)
        res = self.api.partner_info_search(partner_type="videoProvider", service_group=webkit_name)
        if res.get('partnerInfo') is not None:
            name = res.get('partnerInfo')[0].get('name')
        else:
            pytest.fail("failed to make partner info search")
        program = self.service_api.get_live_channels_with_OTT_available(count=None, verbose=True, collectionType="series",
                                                                        name=name)
        if not program:
            pytest.skip("Test requires OTT program")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(program[0][0])
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.open_record_overlay()
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_RECORD_OVERLAY)
        self.guide_page.select_menu_by_substring(self.menu_page.get_more_info_name(self))
        self.screen.refresh()
        self.my_shows_page.select_strip(self.menu_labels.LBL_NETFLIX, matcher_type='in')
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_11)

    @pytest.mark.xray("FRUM-91303")
    @pytest.mark.p1_regression
    @pytest.mark.skipif(Settings.is_unmanaged(), reason="Jump Channels are available only on managed devices")
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_91303_launch_netflix_from_guide(self):
        app_installed = self.screen.base.is_app_installed(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME)
        if not app_installed:
            pytest.skip("Netflix app is not installed.")
        group_names = self.service_api.get_service_group_search()
        webkit_name = self.guide_page.get_webkit_group_name('Netflix', group_names)
        res = self.api.partner_info_search(partner_type="videoProvider", service_group=webkit_name)
        if res.get('partnerInfo') is not None:
            name = res.get('partnerInfo')[0].get('name')
        else:
            pytest.fail("failed to make partner info search")
        program, cn_num = self.service_api.get_offer_with_parameters(is_live=False, collection_type='series', OTT=name)
        if not program:
            pytest.skip("Test requires OTT program")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(cn_num)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.choose_show_by_name(program)
        self.guide_page.press_ok_button(refresh=False)
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_17)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    def test_frum_3_verify_uhd_icon_for_4k_channels_in_guide(self):
        """
            https://jira.tivo.com/browse/FRUM-3
            """
        channel_number_list = self.service_api.get_4k_channel(recordable=True)
        if channel_number_list is None:
            pytest.skip("Could not find any 4K channel")
        channel_number = channel_number_list[0]
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.enter_channel_number(channel_number)
        self.guide_assertions.verify_uhd_icon_in_guide_cell()

    @pytest.mark.xray("FRUM-21977")
    @pytest.mark.usefixtures(
        "toggle_guide_rows_service_availability"
        if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_18) else "switch_tivo_service_rasp")
    @pytest.mark.notapplicable(Settings.transport != "SSH",
                               reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Enter to Disconnected State. NoNetworkScreen is shown")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    def test_frum_21977_verify_guide_and_livetv_when_service_is_down_after_reboot(self):
        """
        Resiliency Mode - Guide - Entry Guide and tune to channel
            Verify Guide functionality when service is down and then device rebooted
        Xray:
            https://jira.tivo.com/browse/FRUM-21977
        """
        channel_number = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                                    transportType="stream")[0][0]
        if not channel_number:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_assertions.verify_disconnected_program_name(self.guide_labels.LBL_DS_PROGRAM_CELL)
        self.guide_assertions.press_select_verify_playback(stay_tick_play_bar=False, stay_ipppv_osd=False,
                                                           stay_playback=False)

    @pytest.mark.msofocused
    @pytest.mark.lite_branding
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("unsubscribed_channel_check")
    def test_frum_43806_cable_provider_branding_unsusbcribed_channel(self):
        unsubscribed_channels = self.service_api.get_unentitled_channels(exclude_jump_channels=True)
        if not unsubscribed_channels:
            pytest.skip("Failed to find any unentitled channels")
        value = self.service_api.branding_ui(field="your_cable_provider")
        if not value:
            pytest.skip("Failed to get {} value from Ui branding bundle response".format("your_cable_provider"))
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(unsubscribed_channels[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.screen.base.press_enter()
        if self.guide_page.osd_shown():
            body_text = self.screen.get_screen_dump_item('osdtext')
        elif self.guide_page.is_overlay_shown():
            body_text = self.screen.get_screen_dump_item('bodytext')
            self.guide_page.screen.base.press_enter()
        self.menu_assertions.validate_branding_bundle_field_value(value, body_text)

    @pytest.mark.xray("FRUM-45430")
    @pytest.mark.iplinear
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device does not have Jump Channels")
    @pytest.mark.msofocused
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_45430_jump_channels_listed_by_mso(self):
        """
        verify all the jump channels listed by MSO in guide can be launched
        """
        channel_nums = list(self.api.get_jump_channels_list().keys())
        if not channel_nums:
            pytest.skip("Could not find jump channel.")
        for channel_num in channel_nums:
            self.home_page.go_to_guide(self)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(channel_num)
            self.screen.base.press_enter()
            self.home_page.wait_for_screen_ready()
            self.guide_assertions.verify_jump_channel_launch(Settings.app_package)
            if Settings.is_apple_tv():
                self.home_page.launch_hydra_when_script_is_on_ott()

    @pytest.mark.xray("FRUM-91317")
    @pytest.mark.service_reliability
    def test_frum_91317_channel_up_down_to_get_service_calls(self):
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.timestamp_test_start()
        self.screen.base.press_channel_up()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.screen.base.press_channel_down()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_view_mode(self.liveTv_labels.LBL_LIVETV_VIEWMODE)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.timestamp_test_end()

    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("back_to_home")
    def test_frum_59926_verify_user_can_switch_channels_on_oneline_guide_by_up_and_down_key_press(self):
        """
        FRUM-59926
        Verify user can switch channels on OneLine Guide by up and down key press.
        :return:
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream",
                                                                     exclude_jump_channels=True)
        if not channel:
            pytest.skip("Live Channel Not Found")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.goto_one_line_guide_from_live(self)
        self.watchvideo_assertions.verify_channel_change_from_olg()

    @pytest.mark.channel_zap
    @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_frum_68514_verify_channel_change_across_all_channels_including_error_channel(self):
        """
        FRUM-68514
        Verify channel change across all channels including error channel by channel up and down keys
        :return:
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        if not channel:
            pytest.skip("Live Channel Not Found")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.channel_change_including_error_channel(self, channel="channel up")
        self.watchvideo_page.channel_change_including_error_channel(self, channel="channel down")

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "This test case is not applicable for unmananged")
    def test_FRUM_433_voice_search_4k_asset(self):
        channel = self.service_api.get_4k_channel()
        if channel is None:
            pytest.fail("Could not find any 4k channel")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_title()
        self.guide_page.enter_channel_number(channel[0])
        program = self.guide_page.get_live_program_name(self)
        self.home_page.launch_series_voice_strip_tile(program)
        self.voicesearch_page.wait_ga_compact_overlay(self)
        expected_text = self.voicesearch_page.get_available_text(self)
        self.home_page.launch_series_voice_strip_tile(program)
        self.voicesearch_assertions.verify_availability_of_text(expected_text)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_frum_91636_verify_favorite_channels_on_channel_cell(self):
        """
        FRUM-91636
        To verify favorite channels and empty fav channels in device
        :return:
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.home_page.go_to_guide(self)
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        self.guide_assertions.verify_empty_favorite_channels_list_in_guide()
        self.guide_page.press_ok_button(refresh=False)
        self.guide_page.add_random_channel_to_favorite(self)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.switch_channel_option(self.guide_labels.LBL_FAVORITES_OPTION)
        self.guide_assertions.verify_favorite_show_in_guide()

    @pytest.mark.test_stabilization
    @pytest.mark.socu
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_94115_verify_socu_possible_trickplay(self):
        """
        FRUM-94115
        To verify possible trickplay modes when trickplay is allowed
        https://testrail.tivo.com/index.php?/cases/view/4835695
        :return:
        """
        channels = self.guide_page.get_trickplay_non_restricted_socu_channel(self, filter_channel=True)
        if not channels:
            pytest.skip("There are no SOCU channels without trickplay restriction")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channels[0])
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.screen.base.press_enter()
        self.watchvideo_assertions.verify_playback_play()
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.watch_video_for(120)
        # rewind function begins
        self.guide_page.rewind_show(self, speed=1)
        self.guide_page.rewind_show(self, speed=2)
        self.guide_page.rewind_show(self, speed=3)
        self.watchvideo_assertions.verify_playback_play()
        self.screen.base.press_playpause()
        self.guide_assertions.verify_play_normal()
        # fast forward begins
        self.guide_page.fast_forward_show(self, speed=1)
        self.guide_page.fast_forward_show(self, speed=2)
        self.guide_page.fast_forward_show(self, speed=3)
        self.screen.base.press_playpause()
        self.guide_assertions.verify_play_normal()
        # pause
        self.screen.base.press_playpause()
        self.guide_assertions.verify_pause()

    @pytest.mark.frumos_18
    @pytest.mark.parametrize("is_olg", [(False)])
    @pytest.mark.parametrize("icon, expected",
                             [("new", True), ("new", False), ("ppv", True), ("ppv", False), ("socu", True), ("socu", False),
                              ("non_rec_pg", True), ("non_rec_pg", False), ("non_req_crr", True), ("non_req_crr", False)])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows is supported since Hydra v1.18")
    @pytest.mark.usefixtures("setup_prepare_params_for_guide_cells_test")
    def test_frum_20481_checking_guide_cell_icons_guide_rows_req(self, request, icon, expected, is_olg):
        """
        Verifying NEW, PPV, SOCU, non-recordable icons on Guide Cells basing on /v1/guideRows (OpenAPI request)

        Xray:
            https://jira.xperi.com/browse/FRUM-20481 (NEW icon)
            https://jira.xperi.com/browse/FRUM-20468 (PPV icon)
            https://jira.xperi.com/browse/FRUM-20441 (SOCU icon in In-Progress Guide)
            https://jira.xperi.com/browse/FRUM-20498 (non-recordable icon in Past Guide)
            https://jira.xperi.com/browse/FRUM-25238 (non-recordable icon in
                In-Progress and Futrue Guide (copyright restriction))
            https://jira.xperi.com/browse/FRUM-26492 (comparting Guide Cell to Guide Header preview)
        """
        params_for_test = request.config.cache.get("params_for_test", None)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(params_for_test["channel_number"], confirm=False)
        self.guide_page.get_to_channel_tab()
        self.guide_page.move_highlight_to_a_cell(params_for_test["steps"])
        icon_tmp = "socu_guide_cell" if icon == "socu" else params_for_test["icon"]
        self.guide_assertions.verify_guide_cell_icons_on_highlighted_row(self, icon_tmp, expected)
        self.guide_assertions.verify_show_title(params_for_test["show_title"], "guide_cell")
        # Comparing Guide Cell title to Guide Header title
        self.guide_assertions.verify_show_title(params_for_test["show_title"], "guide_header")
        # SOCU icon is shown in the available sources area in Guide Header and may not be shown even when it's shown
        # Guide Cell if show is not available from SOCU at the moment
        if icon != "socu":
            # Non-recordable icon is shown in Guide Header for non-recordable channel while Guide Cell does not have one
            if icon == "non_rec_pg" and expected is False:
                expected = True
            # Comparing Guide Cell icons to Guide Header icons
            self.guide_assertions.verify_guide_header_title_icons(self, params_for_test["icon"], expected)

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_title(self, request, content_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "find_appropriate": True,
                  "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_assertions.verify_show_title(offer.title, "record_overlay")

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_subtitle(self, request, content_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        is_subtitle = True if content_type != "movie" else False
        params = {"content_type": content_type, "is_subtitle": is_subtitle,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_assertions.verify_program_subtitle(offer.episode_title, "record_overlay")

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_description(self, request, content_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "with_description": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_assertions.verify_program_description(offer.description, "record_overlay")

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_genre(self, request, content_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "with_category": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_assertions.verify_program_category(offer.category_label, "record_overlay")

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_1st_aired_date(self, request, content_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests).
        Notes: Movie does not have First Aired Date.

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "find_appropriate": True,
                  "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        first_aired = DateTimeUtils.convert_date(
            offer.first_aired_date, DateTimeFormats.ISO_DATE_TIME_WITH_Z, DateTimeFormats.DATE)
        self.guide_assertions.verify_program_first_aired(first_aired, "record_overlay")

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["movie"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_star_rating(self, request, content_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests).
        Note: only Movie has star rating.

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        # Test disabled for Hydra 1.18 according to comments to https://jira.xperi.com/browse/BZSTREAM-10210
        with_star_rating = True if content_type == "movie" else False
        params = {"content_type": content_type, "is_received": None, "is_ppv": False,
                  "with_star_rating": with_star_rating, "find_appropriate": True, "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_assertions.verify_program_star_rating(offer.star_rating)

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_start_end_date(self, request, content_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "find_appropriate": True,
                  "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        start_end_time = DateTimeUtils.get_combined_start_end_show_date(
            offer.start_time, offer.end_time, self.guide_page.get_current_time(), DateTimeFormats.ISO_DATE_TIME_WITH_Z,
            self.service_api.get_body_config_search().get("secondsFromGmt"))
        self.guide_assertions.verify_program_start_end_date(start_end_time, "record_overlay")

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_tv_rating(self, request, content_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "with_rating": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_assertions.verify_program_tv_rating(
            self.service_api.extract_tv_rating_name_from_preview_offer(offer), "record_overlay")

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_show_attributes(self, request, content_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "has_cc": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_assertions.verify_program_attributes(self.guide_labels.LBL_CC_SHOW_ATTRIBUTE, "record_overlay")

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("message_type", ["copyright_restriction", "no_watch_or_record", "not_allowed", None])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_non_recordable(self, request, message_type):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        expected = False if message_type is None else True
        start_time = datetime.now() - timedelta(hours=2) if message_type == "no_watch_or_record" else \
            datetime.now()
        end_time = start_time + timedelta(hours=2)
        is_recordable_chan = True if message_type in ("copyright_restriction", "no_watch_or_record", None) else False
        is_copyright_restricted = True if message_type == "copyright_restriction" else None
        is_recordable_show = True if message_type is None else None
        is_recordable_in_the_past = False if message_type == "no_watch_or_record" else None
        params = {"find_appropriate": True, "is_recordable_in_the_past": is_recordable_in_the_past,
                  "is_recordable_chan": is_recordable_chan, "start_time": start_time.timestamp(),
                  "end_time": end_time.timestamp(), "is_copyright_restricted": is_copyright_restricted,
                  "is_recordable_show": is_recordable_show, "stop_seek_at_first_match": True}
        self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_assertions.verify_non_recordable_label_in_record_overlay(message_type, expected)

    @pytest.mark.xray("FRUM-26902")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.IPPPV)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.IPPPV)])
    @pytest.mark.parametrize("is_ppv, req_type", [
        (True, NotificationSendReqTypes.NSR), (False, NotificationSendReqTypes.NSR)])
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.notapplicable(Settings.is_external_mso(), "Used IptvProvisioningApi method cannot be run on prod")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26902_checking_record_overlay_preview_info_button_ppv_message(self, request, is_ppv, req_type,
                                                                                feature_status_feature,
                                                                                device_info_store_feature):
        """
        Verifying Record Overlay preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests).
        Check either PPV warning message about problems with PPV offer or PPV option to rent offer,
        one of these two is shown on UI.

        Xray:
            https://jira.xperi.com/browse/FRUM-26902 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26913 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26526 (Guide -> Non-episodic)
        """
        channel_info = self.service_api.get_random_channel_from_guide_rows(is_ppv=True, is_live=True)
        if not channel_info:
            pytest.skip("Could not find any channel.")
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, is_ppv)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.FEATURE_STATUS)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_info[0][0])
        self.guide_page.open_record_overlay(using_info_button=True)
        # Checking if PPV option or PPV warning message (when PPV option failed to be shown) is displayed
        self.guide_assertions.verify_ipppv_feature_is_on_or_off_in_record_overlay(is_ppv)

    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/preview is supported since Hydra v1.18")
    @pytest.mark.devhost
    @pytest.mark.frumos_18
    @pytest.mark.p1_regression
    def test_frum_101238_verify_grid_guide_header_title(self):
        """
        FRUM-101238
        Verify that header is displayed according the rules when highlight a program cell with content.
        https://jira.xperi.com/browse/FRUM-101238
        :return:
        """
        grid_rows = self.service_api.get_random_channel_from_guide_rows(content_type='series')
        if not grid_rows:
            pytest.skip("Could not find any channel.")
        title = self.service_api.get_preview_offer(grid_rows[0][1].offer_id).title
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(grid_rows[0][0])
        self.guide_assertions.verify_show_title(title, "guide_header")

    @pytest.mark.service_reliability
    def test_bring_up_olg_and_press_down_button(self):
        """
        Bring up OLG
        Go down 1 cell via arrow down
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.goto_live_tv(channel, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.guide_page.timestamp_test_start()
        self.guide_page.goto_one_line_guide_from_live(self)
        self.screen.base.press_down()
        self.guide_page.exit_one_line_guide()
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    def test_bring_up_olg_and_rapid_down_button_presses(self):
        """
        Bring up OLG
        10 rapid down arrows
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.goto_live_tv(channel, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.guide_page.timestamp_test_start()
        self.guide_page.goto_one_line_guide_from_live(self)
        self.watchvideo_page.press_down_multiple_times(10)
        self.guide_page.exit_one_line_guide()
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    def test_bring_up_olg_and_go_down_with_ch_down_button(self):
        """
        Go down 1 via page down/Chan Down
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.goto_live_tv(channel, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.timestamp_test_start()
        self.guide_page.goto_one_line_guide_from_live(self)
        self.screen.base.press_channel_down()
        self.guide_page.exit_one_line_guide()
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    def test_bring_up_olg_and_rapid_ch_down_button_press(self):
        """
        10 rapid presses of page down/Chan Down
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.goto_live_tv(channel, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.guide_page.timestamp_test_start()
        self.guide_page.goto_one_line_guide_from_live(self)
        self.guide_page.press_channel_up_or_down_multiple_times('down', 10)
        self.guide_page.exit_one_line_guide()
        self.guide_page.timestamp_test_end()

    @pytest.mark.xray("FRUM-26550")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26550_verify_program_screen_preview_title(self, request, content_type):
        """
        Verifying Program Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26550 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26547 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26535 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "find_appropriate": True,
                  "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_show_title(offer.title, "program_screen")

    @pytest.mark.xray("FRUM-26550")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26550_verify_program_screen_preview_subtitle(self, request, content_type):
        """
        Verifying Program Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26550 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26547 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26535 (Guide -> Non-episodic)
        """
        is_subtitle = True if content_type != "movie" else False
        params = {"content_type": content_type, "is_subtitle": is_subtitle,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_program_subtitle(offer.episode_title, "program_screen")

    @pytest.mark.xray("FRUM-26550")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26550_verify_program_screen_preview_description(self, request, content_type):
        """
        Verifying Program Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26550 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26547 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26535 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "with_description": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_program_description(offer.description, "program_screen")

    @pytest.mark.xray("FRUM-26550")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26550_verify_program_screen_preview_genre(self, request, content_type):
        """
        Verifying Program Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26550 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26547 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26535 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "with_category": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_program_category(offer.category_label, "program_screen")

    @pytest.mark.xray("FRUM-26550")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26550_verify_program_screen_preview_1st_aired_date(self, request, content_type):
        """
        Verifying Program Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests).
        Notes: Movie does not have First Aired Date.

        Xray:
            https://jira.xperi.com/browse/FRUM-26550 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26547 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26535 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "find_appropriate": True,
                  "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        first_aired = DateTimeUtils.convert_date(
            offer.first_aired_date, DateTimeFormats.ISO_DATE_TIME_WITH_Z, DateTimeFormats.DATE)
        self.guide_assertions.verify_program_first_aired(first_aired, "program_screen")

    @pytest.mark.xray("FRUM-26550")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["movie"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26550_verify_program_screen_preview_star_rating(self, request, content_type):
        """
        Verifying Program Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests).
        Note: only Movie has star rating.

        Xray:
            https://jira.xperi.com/browse/FRUM-26550 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26547 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26535 (Guide -> Non-episodic)
        """
        with_star_rating = True if content_type == "movie" else False
        params = {"content_type": content_type, "with_star_rating": with_star_rating,
                  "find_appropriate": True, "stop_seek_at_first_match": True, "max_symbols_in_description": 100}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_program_star_rating(offer.star_rating)

    @pytest.mark.xray("FRUM-26550")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26550_verify_program_screen_preview_start_end_date(self, request, content_type):
        """
        Verifying Program Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26550 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26547 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26535 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "find_appropriate": True,
                  "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        start_end_time = DateTimeUtils.get_combined_start_end_show_date(
            offer.start_time, offer.end_time, self.guide_page.get_current_time(), DateTimeFormats.ISO_DATE_TIME_WITH_Z,
            self.service_api.get_body_config_search().get("secondsFromGmt"))
        self.guide_assertions.verify_program_start_end_date(start_end_time, "program_screen")

    @pytest.mark.xray("FRUM-26550")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26550_verify_program_screen_preview_tv_rating(self, request, content_type):
        """
        Verifying Program Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26550 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26547 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26535 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "with_rating": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_program_tv_rating(
            self.service_api.extract_tv_rating_name_from_preview_offer(offer), "program_screen")

    @pytest.mark.xray("FRUM-26550")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    def test_frum_26550_verify_program_screen_preview_show_attributes(self, request, content_type):
        """
        Verifying Program Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-26550 (Guide -> Episodic)
            https://jira.xperi.com/browse/FRUM-26547 (Guide -> Movie)
            https://jira.xperi.com/browse/FRUM-26535 (Guide -> Non-episodic)
        """
        params = {"content_type": content_type, "has_cc": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True}
        self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        self.guide_assertions.verify_program_attributes(self.guide_labels.LBL_CC_SHOW_ATTRIBUTE, "program_screen")

    @pytest.mark.xray("FRUM-109306")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("screen", ["ftux", "quick_tour"])
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.usefixtures("cleanup_sign_in_and_skip_ftux")
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/excluded-partners are supported since Hydra v1.18")
    def test_frum_109306_verify_excluded_partners_not_shown_in_guide_header_preview_ftux(self, request, screen):
        """
        Verifying Exluded Partners not shown in Guide Header preview when unchecking tiles
        in FTUX -> Streaming Apps screen and Help -> Quick Tour -> Streaming Apps screen
        basing on /v1/guideRows and /v1/excluded-partners (OpenAPI requests).

        Xray:
            https://jira.xperi.com/browse/FRUM-109306 (excluding partners in FTUX -> Streaming Apps [1st time])
            https://jira.xperi.com/browse/FRUM-109589 (excluding partners in Help -> Quick Tour -> Streaming Apps)
        """
        # SOCU cannot be disabled from Video Providers screen, so let's avoid assets available from SOCU
        params = {"count": None, "with_video_provider": True, "find_appropriate": True, "stop_seek_at_first_match": True,
                  "is_startover": False, "is_catchup": False}
        channel_show = self.service_api.get_random_channel_from_guide_rows(**params)
        params["count"] = 1
        channel_show_offer = self.service_api.get_random_filtered_channels_by_preview_offer(channel_show, **params)
        is_ftux = True if screen == "ftux" else False
        self.home_page.update_test_conf_and_reboot(skip_apps=not is_ftux, clear_data=is_ftux, SKIP_FTUX="false")
        if screen == "quick_tour":
            self.home_page.skip_ftux()
            self.menu_page.launch_quick_tour_from_help(self)
            self.home_page.skip_ftux(skip_animation=True, skip_onepass=True, skip_apps=False)
        self.home_page.check_uncheck_ftux_streaming_apps_providers(is_check=False)
        self.home_assertions.verify_streaming_apps_checked_unchecked(is_check=False)
        if self.home_page.is_ftux_streaming_apps_view_mode():
            self.home_page.select_done(times=1)
        if self.home_page.is_ftux_pc_settings_screen_view_mode():
            self.home_page.select_skip_this_step_ftux_pcsetting_screen()
        self.guide_page.find_channel_and_highlight_program_in_guide(
            self, is_olg=False, channel_show_offer=channel_show_offer, **params)
        # Currently, there's a product issue: https://jira.xperi.com/browse/CLOUD-4238
        self.guide_assertions.verify_available_sources(expected=False)

    @pytest.mark.xray("FRUM-32677")
    @pytest.mark.frumos_18
    @pytest.mark.usefixtures("cleanup_sign_in_and_skip_ftux")
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/excluded-partners are supported since Hydra v1.18")
    def test_frum_32677_verify_excluded_partners_not_shown_in_guide_header_preview_settings_video_providers(self, request):
        """
        Verifying Exluded Partners not shown in Guide Header preview when unchecking tiles
        in Settings -> User Preferences -> My Video Providers screen basing on /v1/guideRows and
        /v1/excluded-partners (OpenAPI requests).

        Xray:
            https://jira.xperi.com/browse/FRUM-32677 (excluding partners Settings -> User Preferences -> My Video Providers)
        """
        # SOCU cannot be disabled from Video Providers screen, so let's avoid assets available from SOCU
        params = {"count": None, "with_video_provider": True, "find_appropriate": True, "stop_seek_at_first_match": True,
                  "is_startover": False, "is_catchup": False}
        channel_show = self.service_api.get_random_channel_from_guide_rows(**params)
        params["count"] = 1
        channel_show_offer = self.service_api.get_random_filtered_channels_by_preview_offer(channel_show, **params)
        request.getfixturevalue("disable_video_providers")
        self.guide_page.find_channel_and_highlight_program_in_guide(
            self, is_olg=False, channel_show_offer=channel_show_offer, **params)
        # Currently, there's a product issue: https://jira.xperi.com/browse/CLOUD-4238
        self.guide_assertions.verify_available_sources(expected=False)

    @pytest.mark.xray("FRUM-115151")
    @pytest.mark.p1_regression
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.18")
    @pytest.mark.frumos_18
    @pytest.mark.parametrize("content_type", ["episode"])
    def test_frum_115151_verify_one_line_guide_preview_description(self, request, content_type):
        """
          Verify that description in preview comes from /v1/preview/offer
        """
        params = {"stop_seek_at_first_match": True, "content_type": content_type,
                  "with_description": True, "find_appropriate": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=True, **params)[0][4]
        # One Line Guide Preview description verification
        self.guide_assertions.verify_program_description(offer.description, "olg_preview")

    @pytest.mark.frumos_19
    @pytest.mark.cloud_core_watch_Recording
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_frum_119781_play_recording_from_guide_record_overlay(self):
        """
        Verify "Watch now " option on Record overlay for program with available from My shows in Grid Guide
        https://jira.xperi.com/browse/FRUM-119781
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.create_live_recording()
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu_by_substring(self.menu_labels.LBL_WATCH_NOW_RECORDING)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytest.mark.xray("FRUM-126733")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    @pytest.mark.parental_control
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Can't purchase ppv in unmanaged devices")
    @pytest.mark.msofocused
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_126733_set_purchase_pin_on_purchase_currently_airing_show(self):
        """
                       https://jira.xperi.com/browse/FRUM-126733
                       Description:  PC setting turned On from User Settings
                       Turn On Purchase Control
                       Get a currently airing ppv content from Guide
                       Play that ppv content
                       ppv ovrlay displays > Select ok
                       Series screen with "Rent & Buy" option
                       Select "rent and watch now" option
                       Enter purchase pin overlay
                       Enter Pin and verify purchase confirmed overlay
                       """
        if not self.service_api.check_groups_enabled(self.menu_labels.LBL_PURCHASE_GROUP):
            pytest.skip("PPV is not enabled in the Device")
        self.menu_page.turnonpcsettings(self, "on", "on")
        ppv_rental_channel = self.home_page.try_find_ppv_rented_ppv_channel(self)
        self.home_page.log.info(f"Channel selected for tuning: {ppv_rental_channel}")
        if not ppv_rental_channel:
            pytest.skip("PPV rental channel unavailable")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number((ppv_rental_channel[0]))
        self.guide_page.select_and_watch_program(self)
        self.guide_assertions.ppv_overlay_confirm()
        self.guide_page.select_and_watch_program(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_RENT_AND_WATCH_NOW_IPPPV)
        self.menu_page.select_menu_items(self.guide_labels.LBL_RENT_OPTIONS)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.guide_assertions.verify_ppv_purchase_confirmed_overlay_purchase_pin()
        self.screen.base.press_enter()

    @pytest.mark.longevity
    def test_multiple_vod_assets_playbacks_and_switching_to_live_tv_and_watching_for_multiple_hours(self):
        """
            Verify multiple VOD_assets continue to play till end and further continue wacthing liev tv for multiple hours
            Xray:
            https://jira.xperi.com/browse/FRUM-131016
        """
        channel = self.api.get_random_encrypted_unencrypted_channels(transportType="stream", filter_channel=True)
        if not channel:
            pytest.skip("No appropriate channels found.")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.verify_long_hours_playback(self, no_of_hrs=3)
        self.home_page.back_to_home_short()
        counter = 0
        while counter < LongevityConstants.LOW_COUNTER:
            status, result = self.vod_api.get_offer_playable()
            if result is None:
                pytest.skip("The content is not available on VOD catlog.")
            self.home_page.back_to_home_short()
            self.vod_page.goto_vodoffer_program_screen(self, result)
            self.vod_page.play_any_playable_vod_content(self, result)
            self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
            self.vod_assertions.verify_vod_playback(self)
            self.guide_page.wait_and_watch_until_end_of_program(self)
            self.vod_assertions.verify_vod_series_or_action_screen_view_mode()
            counter += 1
        self.home_page.back_to_home_short()

    @pytest.mark.xray("FRUM-118630")
    @pytest.mark.frumos_19
    @pytest.mark.cloud_core_guide_preview
    @pytest.mark.parametrize("content_type", ["episode", "movie", "special"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/guideRows and /v1/preview/offer are supported since Hydra v1.19")
    def test_frum_118630_verify_info_card_preview_description(self, content_type):
        """
        Verifying Info Card Screen preview basing on /v1/guideRows and /v1/preview/offer (OpenAPI requests)

        Xray:
            https://jira.xperi.com/browse/FRUM-118630
        """
        params = {"content_type": content_type, "with_description": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True,
                  "screen_type": "infoCard"}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        self.guide_page.navigate_by_menu_vertical_substring(self.guide_labels.LBL_UPCOMING_AIRINGS)
        self.guide_page.press_long_ok(self)
        self.guide_assertions.verify_program_description(offer.description, "info_card")

    @pytest.mark.xray('FRUM-121635')
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/preview/content is supported since Hydra 1.19")
    @pytest.mark.frumos_19
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.cloud_core_guide_preview
    @pytest.mark.parametrize("content_type", ["episode", "movie", "special"])
    def test_frum_121635_gude_already_recording_overlay_preview_title(self, content_type):
        """
        Verifying Already recording overlay preview title based on /v1/preview/content (OpenAPI requests)
        Xray:
            https://jira.xperi.com/browse/FRUM-121635
        """
        params = {"content_type": content_type, "with_title": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True,
                  "screen_type": "alreadyRecordingOverlay", "is_recordable_show": True, "preview_mode": "content"}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.create_live_recording()
        self.screen.base.press_record()
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_ALREADY_RECORDING_OVERLAY)
        self.guide_assertions.verify_show_title(offer.title, "already_recording_overlay")

    def test_136559_4k_socu_playback(self):
        """
        Verify "4k socu playback" on UHD channels as they should play on 4k resolution when playing SOCU.
        https://jira.xperi.com/browse/FRUM-136559
        """
        channel = self.service_api.get_4k_channel(socu=True)
        if not channel:
            pytest.skip("Skipping as,UHD channel not available.")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channel[0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=True)
        self.watchvideo_assertions.verify_view_mode(self.watchvideo_labels.LBL_VOD_VIEWMODE)
        self.home_assertions.verify_socu_playback(self)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.watchvideo_assertions.verify_screen_resolution(self)

    @pytest.mark.xray("FRUM-121663")
    @pytest.mark.frumos_19
    @pytest.mark.parametrize("content_type", ["episode"])
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/vodOttActionDetails/content/ is supported since Hydra v1.19")
    def test_frum_121663_verify_ott_starts_from_streaming_options_overlay(self, request, content_type):
        """
        Verifying that OTT is started from Streaming Options Overlay
        /v1/vodOttActionDetails/content/ (OpenAPI requests).

        Xray:
            https://jira.xperi.com/browse/FRUM-121916 (Streaming Options overlay view - OTT)
            https://jira.xperi.com/browse/FRUM-121663 (Guide - Record Overlay - All Streaming Options overlay - OTT)
        """
        params = {"content_type": content_type, "find_appropriate": True, "is_startover": True,
                  "vp_partner_id": "tivo:pt.4576", "screen_type": "guideHeader",
                  "with_video_provider": True}
        channel_show_offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)
        self.guide_page.open_record_overlay(using_info_button=True)
        self.guide_page.select_menu(self.menu_page.get_more_info_name(self))
        self.menu_page.select_strip(self.menu_labels.LBL_STREAMING_OPTIONS)
        self.menu_assertions.verify_all_streaming_options_overlay()
        self.menu_assertions.verify_all_streaming_options_overlay_items_view_compare_with_api(
            channel_show_offer[0][1].content_id, _screen="guide")
        self.menu_page.select_provider_on_all_streaming_options_overlay(
            channel_show_offer[0][1].content_id, tivo_partner_stations_backup["VUDU"], None,
            self.menu_labels.LBL_STREAMING_OPTIONS_RENT_ON)
        self.guide_assertions.verify_ott_app_is_foreground(self, "Vudu")

    @pytest.mark.service_reliability
    @pytest.mark.xray("FRUM-142384")
    def test_bring_up_guide_and_go_down_with_ch_down_button(self):
        """
        Go down 1 via page down/Chan Down from Guide screen
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.goto_live_tv(channel, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.home_page.go_to_guide(self)
        self.guide_page.timestamp_test_start()
        self.screen.base.press_channel_down()
        self.guide_page.timestamp_test_end()

    @pytest.mark.service_reliability
    @pytest.mark.xray("FRUM-142385")
    def test_bring_up_guide_and_press_down_button(self):
        """
        Bring up Guide
        Go down 1 cell via arrow down
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.goto_live_tv(channel, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.home_page.go_to_guide(self)
        self.guide_page.timestamp_test_start()
        self.screen.base.press_down()
        self.guide_page.timestamp_test_end()

    @pytest.mark.xray("FRUM-135714")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/actions/content is supported since Hydra 1.19")
    @pytest.mark.frumos_19
    @pytest.mark.cloud_core_guide_preview
    def test_past_guide_press_play_button(self):
        """
        Past Guide - Press - Play button - CatchUp
        """
        end_time = datetime.strptime(self.service_api.get_middle_mind_time(Settings.tsn)["currentTime"],
                                     self.service_api.MIND_DATE_TIME_FORMAT)
        start_time = end_time - timedelta(hours=2, minutes=0)
        past_socu_offer = self.service_api.get_random_channel_from_guide_rows(is_catchup=True,
                                                                              take_not_ended_shows=False,
                                                                              find_appropriate=True,
                                                                              get_playable_socu=True,
                                                                              start_time=start_time.timestamp(),
                                                                              end_time=end_time.timestamp())
        if not past_socu_offer:
            pytest.skip("Could not find past socu offer.")
        offer_id = past_socu_offer[0][1].offer_id
        self.guide_assertions.verify_action_kernel_type(offer_id=offer_id,
                                                        expected_action_kernel_type='watchFromSocuActionKernel')
        self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False,
                                                                    channel_show_offer=past_socu_offer)
        self.screen.base.press_playpause()
        self.watchvideo_assertions.verify_socu_playback_started()

    @pytest.mark.xray("FRUM-136065")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_19),
                               "/v1/actions/content is supported since Hydra 1.19")
    def test_past_one_line_guide_play_button_catchup(self):
        """
        It will go to Past One Line Guide assest without recording
        Press Play button Catch-Up will start play.
        https://jira.xperi.com/browse/FRUM-136065
        """
        end_time = datetime.strptime(self.service_api.get_middle_mind_time(Settings.tsn)["currentTime"],
                                     self.service_api.MIND_DATE_TIME_FORMAT)
        start_time = end_time - timedelta(hours=2, minutes=0)
        past_socu_offer = self.service_api.get_random_channel_from_guide_rows(is_catchup=True,
                                                                              take_not_ended_shows=False,
                                                                              find_appropriate=True,
                                                                              get_playable_socu=True,
                                                                              start_time=start_time.timestamp(),
                                                                              end_time=end_time.timestamp())
        if not past_socu_offer:
            pytest.skip("Could not find any channel with CatchUp")
        offer_id = past_socu_offer[0][1].offer_id
        self.guide_assertions.verify_action_kernel_type(offer_id=offer_id,
                                                        expected_action_kernel_type='watchFromSocuActionKernel')
        self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=True,
                                                                    channel_show_offer=past_socu_offer)
        self.home_page.goto_live_tv(past_socu_offer, confirm=False)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.goto_one_line_guide_from_live(self)
        self.menu_page.menu_navigate_left_right(3, 0)
        self.guide_page.wait_for_screen_ready()
        self.screen.base.press_playpause()
        self.guide_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_socu_playback_started()
