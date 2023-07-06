import time
import random
import re

import pytest

from core_api.stb.base import UINavigationException
from set_top_box.test_settings import Settings
from set_top_box.client_api.my_shows.conftest import *  # noqa: F401
# TODO
# Import only used fixtures from other conftest files, variables re-writing may cause errors
# !!! One of tests here fail with undefined error because of it:
# AttributeError: 'FixtureLookupErrorRepr' object has no attribute 'reprtraceback'
from set_top_box.client_api.guide.conftest import *  # noqa: F401
from set_top_box.client_api.Menu.conftest import *  # noqa: F401
from set_top_box.client_api.wtw.conftest import *  # noqa: F401
from pytest_testrail.plugin import pytestrail
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions
from set_top_box.client_api.watchvideo.conftest import setup_cleanup_turn_on_device_power, \
    increase_timeout_of_widgets_in_watch_video_screen
from set_top_box.client_api.home.conftest import set_bridge_status_up, enable_disable_stay_awake
from set_top_box.client_api.home.conftest import decrease_screen_saver, setup_disable_stay_awake, \
    launch_hydra_app_when_script_is_on_ott
from set_top_box.client_api.provisioning.conftest import activate_ndvr_simple, cancel_ndvr_simple, \
    cleanup_activate_ndvr_simple
from set_top_box.conf_constants import FeAlacarteFeatureList, FeAlacartePackageTypeList, HydraBranches, FeaturesList


@pytest.mark.usefixtures("setup_my_shows")
@pytest.mark.usefixtures("is_service_myshows_alive")
@pytest.mark.myshows
@pytest.mark.timeout(Settings.timeout)
class TestMyShows(object):

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_323415_select_movies_tab(self):
        # TODO
        # Fix test labels, take them labels.py
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, "ALL SHOWS")
        self.my_shows_page.select_my_shows_category(self, "MOVIES")

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_323416_select_sports_tab(self):
        # TODO
        # Fix test labels, take them labels.py
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, "SPORTS")

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_323410_select_tv_series_tab(self):
        # TODO
        # Fix test labels, take them labels.py
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, "TV SERIES")

    @pytestrail.case('C11123877')
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("enable_video_providers")
    def test_333196_create_bookmark_from_my_show_for_movie(self, setup_my_shows_sort_to_date,
                                                           setup_delete_book_marks,
                                                           setup_myshows_delete_recordings, setup_cleanup_myshows):
        """
        333196
        Search for movie and bookmark it, then go to My Shows and verify movie is actually bookmarked

        Also applies for:
        393520
        :return:
        """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, feedName="Movies", update_tivo_pt=True)
        if type(program) is tuple:
            program = program[0]
        if not program:
            status, result = self.vod_api.get_entitled_mapped_SVOD_movie()
            if result is None:
                pytest.skip("The content is not available on VOD catlog.")
            program = self.vod_page.extract_title(result)
            movieYear = None
            if result['offer'].movie_year:
                movieYear = result['offer'].movie_year
            if movieYear:
                self.text_search_page.search_and_select(program, program, year=movieYear)
            else:
                self.text_search_page.search_and_select(program, program)
        self.vod_assertions.verify_view_mode(self.my_shows_labels.LBL_ACTION_SCREEN_VIEW)
        self.text_search_page.bookmark_content()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.home_labels.LBL_MOVIES)
        self.my_shows_assertions.verify_category_has_content()
        self.my_shows_assertions.verify_content_in_category(program)

    @pytestrail.case("C12792781")
    @pytest.mark.p1_regression
    # @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_329344_change_sort_options_in_my_shows(self):
        """
        329344
        Changing Sort list options in My Shows Options
        :return:
        """
        sort_option = ["by Date", "by Name"]
        for option in sort_option:
            self.menu_page.go_to_user_preferences(self)
            self.menu_page.select_menu_items("My Shows Options")
            self.screen.refresh()
            m = self.menu_page.menu_item_option_focus()
            if option not in m:
                self.menu_page.menu_navigate_left_right(0, 1)
            self.home_page.go_to_my_shows(self)
            self.my_shows_assertions.verify_my_show_option(option)

    @pytest.mark.bvt
    @pytest.mark.duplicate
    @pytest.mark.iplinear
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    def test_adhoc_OTT_provider_and_functionality(self, setup_adhoc_OTT_provider_and_functionality):
        """
        305664
        Ad-doc style testing to verify that the OTT providers are displayed correctly
        for the apps which are applicable to the platform tested.
        :return:
        """
        self.text_search_page.go_to_search(self)
        # TODO
        # Find a show which is available from some OTT(s) e.g. Netflix and get provider ids with mind API
        # Note: hard coded value is not ok, since asset with same name may be available from different OTTs on different MSOs
        self.text_search_page.search_and_select("BOYHOOD", "Boyhood (2014)")
        # TODO
        # check_icons() - pass icons in input param to check
        self.my_shows_page.check_icons(self)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_NETFLIX_ICON)
        self.my_shows_page.watch_netflix(self)
        self.home_page.back_to_home_short()

    @pytestrail.case('C11123879')
    @pytest.mark.bat
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.notapplicable(Settings.is_fire_tv())
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.timeout(Settings.timeout)
    def test_365012_exit_playback_from_apps_and_my_shows(self, setup_delete_book_marks,
                                                         setup_cleanup_exit_playback):
        """
        365012
        To verify smooth exit of apps when launched from My shows and apps.
        :return:
        """
        status = False
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, feedName="Movies", update_tivo_pt=False)
        if not program:
            status, program = self.my_shows_page.get_and_search_vod_OTT_program(self, mapped=True)
            if not program:
                pytest.skip("Test requires OTT or VOD offer program.")
        self.vod_assertions.verify_view_mode(self.my_shows_labels.LBL_ACTION_SCREEN_VIEW)
        self.text_search_page.bookmark_content()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.home_labels.LBL_MOVIES)
        self.my_shows_assertions.verify_category_has_content()
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        if status:
            if Settings.mso.lower() == 'bluestream':
                self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_BLUESTREAM, matcher_type='in',
                                                     max_scrolls=1)
            else:
                self.my_shows_page.navigate_by_strip(Settings.mso.lower(), matcher_type='in',
                                                     max_scrolls=1)
            self.vod_page.play_free_vod_content(subtitle=program)
            self.vod_assertions.verify_vod_playback(self)
        else:
            state = self.screen.base.verify_foreground_app(Settings.app_package)
            if not state:
                self.home_page.verify_OTT_screen(Settings.app_package)
            else:
                OTT = self.my_shows_page.OTT_from_ca_screen(self)
                self.my_shows_page.select_strip(OTT, refresh=False)
                self.my_shows_page.pause(20)
                hydra_pkg = Settings.app_package
                if Settings.is_apple_tv():
                    self.home_page.check_for_non_hydra_screen_and_select(self)
                fg_pkg = self.screen.base.get_foreground_package()
                self.home_page.log.info(f"current app package: {fg_pkg}")
                if fg_pkg == hydra_pkg:
                    pytest.fail("OTT App did not launch.")

    @pytestrail.case("C10840400")
    @pytest.mark.sanity
    # TODO
    # Replace xyz in Settings.platform.lower() with condition like Settings.is_fire_tv()
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device does not have Apps")
    @pytest.mark.skipif("toshiba" in Settings.platform.lower(), reason="Device does not have Apps")
    @pytest.mark.skipif("appletv" in Settings.platform.lower(), reason="Device does not have Apps")
    @pytest.mark.skipif("devhost" in Settings.driver_type.lower(), reason="Device does not have Apps")
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.xray('FRUM-41')
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    @pytest.mark.usefixtures("enable_video_providers")
    @pytest.mark.timeout(Settings.timeout)
    def test_playback_from_apps(self):
        """
        365012
        To verify launch of App.
        :return:
        """
        status = False
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, feedName="Movies", update_tivo_pt=False)
        if not program:
            status, program = self.my_shows_page.get_and_search_vod_OTT_program(self)
            if not program:
                pytest.skip("Test requires OTT or VOD offer program.")
        self.vod_assertions.verify_view_mode(self.my_shows_labels.LBL_ACTION_SCREEN_VIEW)
        if status:
            if Settings.mso.lower() == 'bluestream':
                self.my_shows_page.navigate_by_strip(self.my_shows_labels.LBL_BLUESTREAM, matcher_type='in',
                                                     max_scrolls=1)
            elif Settings.mso.lower() == 'astound':
                self.my_shows_page.navigate_by_strip(self.watchvideo_labels.LBL_ON_DEMAND, matcher_type='in',
                                                     max_scrolls=1)
            else:
                self.my_shows_page.navigate_by_strip(Settings.mso.lower(), matcher_type='in',
                                                     max_scrolls=1)
            self.vod_page.play_free_vod_content(subtitle=program)
            self.vod_assertions.verify_vod_playback(self)
        else:
            OTT = self.my_shows_page.OTT_from_ca_screen(self)
            self.my_shows_page.select_strip(OTT)
            self.home_page.verify_OTT_screen(Settings.app_package)

    @pytestrail.case("C12792782")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    def test_172039_myshows_layout(self, setup_delete_book_marks, setup_cleanup_myshows):
        """
        172039
        To verify the screen layout of My Shows
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_PRIMARY_SCREEN, 30000)
        self.menu_page.menu_navigate_left_right(1, 0)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_SIDE_PANEL, 30000)
        self.menu_page.select_menu_items(self.my_shows_labels.LBL_MOVIES)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, 30000)
        self.wtw_assertions.verify_highlight_not_in_netflix_strip()
        content = self.my_shows_page.bookmark_from_wtw(self)
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_assertions.verify_my_shows_content_filters(self)
        self.my_shows_assertions.validate_bookmarked_content_in_myshows(self, content)

    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_393520_create_bookmark_from_guide(self, setup_my_shows_sort_to_date):
        """
        393520
        Verify the ability to create and delete bookmarks from Guide
        test case is covered under test_74099549_verify_all_one_pass_bookmarks_created_are_placed_under_my_shows3
        :return:
        """
        self.home_page.go_to_guide(self)
        self.guide_page.select_and_watch_program(self)
        content = self.guide_page.bookmark_content(self)
        self.home_page.go_to_my_shows(self)
        content_name, folder = self.my_shows_assertions.verify_content_in_any_category(self, content)
        self.my_shows_page.delete_content_bookmark(self, content_name)
        self.my_shows_assertions.verify_content_not_in_category(self, content_name, folder_name=folder)

    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.p1_regression
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.cloud_core_liveTV
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_delete_book_marks")
    def test_393520_create_bookmark_from_live_tv(self):
        """
        393520
        Verify the ability to create and delete bookmarks from Live TV
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        content = self.guide_page.bookmark_content(self)
        self.home_page.go_to_my_shows(self)
        content_name, folder = self.my_shows_assertions.verify_content_in_any_category(self, content)
        self.my_shows_page.delete_content_bookmark(self, content_name)
        self.my_shows_assertions.verify_content_not_in_category(self, content_name, folder_name=folder)

    @pytest.mark.bvt
    @pytest.mark.iplinear
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures("setup_delete_book_marks")
    @pytest.mark.timeout(Settings.timeout)
    def test_393520_create_bookmark_from_prediction(self):
        """
        393520
        Verify the ability to create and delete bookmarks from Home Predictions
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_prediction()
        self.home_page.wait_for_screen_ready()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        content, found = self.home_page.bookmark_from_prediction(self)
        content = self.home_page.convert_special_chars(content)
        if found:
            self.home_page.go_to_my_shows(self)
            content_name, folder = self.my_shows_assertions.verify_content_in_any_category(self, content)
            self.my_shows_page.delete_content_bookmark(self, content_name)
            self.my_shows_assertions.verify_content_not_in_category(self, content_name, folder_name=folder)
        else:
            pytest.skip("Bookmark option not found.")

    @pytestrail.case('C11123880')
    @pytest.mark.bat
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_393520_create_bookmark_from_wtw(self, setup_delete_book_marks, setup_myshows_delete_recordings,
                                             setup_cleanup_myshows):
        """
        393520
        Verify the ability to create and delete bookmarks from What to Watch
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_PRIMARY_SCREEN, 30000)
        self.menu_page.menu_navigate_left_right(1, 0)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_SIDE_PANEL, 30000)
        self.menu_page.select_menu_items(self.wtw_labels.LBL_MOVIES)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, 30000)
        self.wtw_assertions.verify_highlight_not_in_netflix_strip()
        content = self.my_shows_page.bookmark_from_wtw(self)
        self.home_page.go_to_my_shows(self)
        content_name, folder = self.my_shows_assertions.verify_content_in_any_category(self, content)
        self.my_shows_page.delete_content_bookmark(self, content_name)
        self.my_shows_assertions.verify_content_not_in_category(self, content_name, folder_name=folder)

    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.duplicate
    def test_365012_exit_playback_from_my_shows(self):
        """
        365012 - covered under - BAT - test_365012_exit_playback_from_apps_and_my_shows
        To verify smooth exit of apps with all bail buttons when launched from My shows.

        :return:
        """
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select("ARROW", "Arrow")
        self.text_search_page.create_one_pass_for_show()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, "TV Series")
        self.my_shows_page.select_show("Arrow")
        self.my_shows_page.watch_netflix(self)

    @pytestrail.case("C10838514")
    @pytest.mark.xray('FRUM-48')
    @pytest.mark.sanity
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.ndvr
    @pytest.mark.msofocused
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.cloud_core_watch_Recording
    @pytest.mark.timeout(Settings.timeout)
    def test_354461_playback_recording(self, setup_my_shows_sort_to_date, setup_myshows_delete_recordings,
                                       setup_cleanup_myshows):
        """
        354461
        To verify ability to playback an inprogress/completed recording
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytestrail.case('C11123874')
    @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.parental_control
    @pytest.mark.cloud_core_watch_Recording
    @pytest.mark.usefixtures("setup_my_shows_sort_to_date")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_309045_pc_on_recording(self):
        """
        309045
        Parental Controls - PC Challenged on playback recordings
        :return:
        """
        self.api.delete_all_subscriptions()
        self.api.delete_recordings_from_myshows()
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                            unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_menu_by_substring(program)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN)
        self.my_shows_page.select_and_wait_pin_overlay(self)
        self.my_shows_assertions.verify_overlay()

    # @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.longrun
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_393717_play_same_recording(self):
        recording = self.service_api.schedule_single_recording()[0][0]
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_menu_by_substring(recording)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.live_tv_assertions.verify_playback_play()
        self.my_shows_page.pause(60 * 4)  # watching playback
        self.home_page.back_to_home_short()
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        self.live_tv_page.wait_for_screen_ready(self.my_shows_labels.LBL_WATCH_SCREEN)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_menu_by_substring(recording)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.live_tv_assertions.verify_playback_play()
        self.live_tv_assertions.verify_currentPos_not_initial()

    @pytestrail.case('C11123873')
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-306")
    @pytest.mark.ndvr
    @pytest.mark.devhost
    @pytest.mark.msofocused
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_277186_program_actions_recover_this_show(self):
        """
        277186
        Program Actions - Recover This Show - from Recover strip - Movie - Press OK - bookmark exists
        :return:
        """
        channels = self.service_api.get_random_recordable_channel(filter_channel=True)
        if not channels:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0][0])
        content = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.delete_recording_in_my_show(content)
        self.my_shows_page.go_to_recently_deleted_folder(self)
        self.my_shows_page.undelete_recording_in_my_show(self, content)
        self.guide_page.verify_whisper_shown(self.my_shows_labels.LBL_RECOVER_WHISPER)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(content)
        self.my_shows_page.go_to_recently_deleted_folder(self)
        with pytest.raises(Exception):
            self.my_shows_assertions.verify_program_in_recently_deleted_folder(self, content)

    # @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.longrun
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_270340_program_actions_keep_from_watch_now_strip(self):
        """
        270340
        Program Actions - Keep - from Watch Now strip - Press OK
        :return:
        """
        recording = self.service_api.schedule_single_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(recording[0][0])
        self.my_shows_page.go_to_cached_action_screen(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.home_page.select_strip(self.my_shows_labels.LBL_KEEP)
        self.my_shows_assertions.select_keep_and_verify()

    @pytestrail.case('C11123958')
    @pytest.mark.bat
    @pytest.mark.devhost
    @pytest.mark.socu
    @pytest.mark.devhost
    @pytest.mark.cloud_core_vod_socu
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.cloud_core_guide_preview
    def test_363174_playback_socu_from_series_screen(self):
        """
        363174
        SOCU - E2E - Encrypted playback
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(channel_count=1, encrypted=True, socu=True,
                                                                             bookmark=True, genre='series',
                                                                             filter_channel=True,
                                                                             filter_socu=True)
        self.service_api.bookmark_show(*channel[0][2])
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(channel[0][1])
        self.my_shows_assertions.verify_series_screen(self)
        self.my_shows_page.select_socu_playback(self, label=self.guide_labels.LBL_RECORD_OVERLAY_CATCHUP_ICON)
        self.live_tv_page.watch_video_for(60 * 5)
        self.live_tv_assertions.verify_playback_play()

    @pytestrail.case("C12792776")
    @pytest.mark.p1_regression
    @pytest.mark.actionscreen
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_271293_series_screen(self):
        """
        271293
        Screens - SeriesScreen
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(
            channel_count=1, encrypted=True, OTT_count=1, subtitle=True)
        self.service_api.bookmark_show(*channel[0][3])
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(channel[0][1], truncate=30)
        self.my_shows_assertions.verify_series_screen(self)
        self.my_shows_assertions.verify_series_screen_items()

    @pytestrail.case("C12792777")
    @pytest.mark.ndvr
    @pytest.mark.p1_regression
    @pytest.mark.actionscreen
    @pytest.mark.may_also_like_ccu
    @pytest.mark.usefixtures("setup_myshows_delete_recordings", "setup_delete_all_one_pass")
    @pytest.mark.timeout(Settings.timeout)
    def test_267263_series_screen_strip_order(self):
        """
        2672263
        Screens - SeriesScreen - Strips Order
        :return:
        """
        show_list = self.service_api.bookmark_now_streaming_tv_shows()
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        show = self.my_shows_page.get_available_shows_in_all_shows(show_list)
        if not show:
            pytest.fail("None of the bookmarked shows are listed under myshows: {} - {}".format(show_list, show))
        self.my_shows_page.select_show(show[0])
        self.my_shows_assertions.verify_series_screen(self)
        self.my_shows_page.navigate_to_series_screen_menu_list()
        self.my_shows_assertions.verify_series_screen_strip_order("bookmark")

    # @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.longrun
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_309135_delete_recording_overlay(self):
        """
        309135
        TC - 309135 - Playing back a completed recording to the end goes to Delete Recording Overlay
        :return:
        """
        recording = self.service_api.schedule_single_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_menu_by_substring(recording[0][0])
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN)
        self.my_shows_page.select_and_wait_for_playback_play()
        self.live_tv_assertions.verify_playback_play()
        self.my_shows_assertions.wait_and_verify_delete_recording_overlay()

    @pytestrail.case('C11123875')
    @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.devhost
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_310879_cancel_in_progress_recording(self):
        """
        310879
        Verify behavior when cancelling an in-progress recording from Guide.
        :return:
        """
        channels = self.service_api.get_random_recordable_channel(filter_channel=True)
        if not channels:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0][0])
        program = self.guide_page.get_foucsed_content()['text']
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.select_and_cancel_program_recording(self, long_press=True)
        if Settings.is_llapr():
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
            self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MYSHOWS_SCREEN)
            self.my_shows_assertions.verify_content_not_in_category(self, program)
        else:
            self.home_page.back_to_home_short()
            self.my_shows_page.go_to_recently_deleted_folder(self)
            self.my_shows_page.undelete_recording_in_my_show(self, program)
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
            self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MYSHOWS_SCREEN)
            self.my_shows_assertions.verify_content_in_category(program)

    @pytestrail.case('C11123876')
    @pytest.mark.bat
    @pytest.mark.devhost
    @pytest.mark.ndvr
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_310891_delete_program_from_my_shows(self, setup_my_shows_sort_to_date, setup_myshows_delete_recordings,
                                                 setup_cleanup_myshows):
        """
        310891
        It is possible delete recordings from my shows
        :return:
        """
        if not Settings.is_apple_tv():
            recording = self.api.record_currently_airing_shows(number_of_shows=1, genre="series", is_preview_offer_needed=True)
            if not recording:
                pytest.skip("Failed to schedule recording")
            show = self.home_page.convert_special_chars(recording[0][0])
        else:
            channels = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
            if not channels:
                pytest.skip("Test requires recordable channels")
            show = self.guide_page.create_recording_using_ui(self, channels[0][0])
            if not show:
                pytest.skip(f"live program of {channels[0][0]} is not recordable")
        self.my_shows_page.delete_episodic_program(self, show)
        if not Settings.is_llapr():
            self.my_shows_page.go_to_recently_deleted_folder(self)
            self.my_shows_assertions.verify_program_in_recently_deleted_folder(self, show)

    @pytestrail.case("C12792783")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.wtw_openAPI_impacted
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_172114_verify_content_all_shows(self, setup_my_shows_sort_to_date, setup_myshows_delete_recordings,
                                             setup_cleanup_myshows, setup_cleanup_exit_playback,
                                             setup_delete_book_marks):
        """
        172114
        To verify the contents of  "All" /"All Shows" in My Shows
        :return:
        """
        # TODO
        # Use label from labels.py instead of hard coded value, labels may differ depending on MSO
        feed_name = self.wtw_page.get_feed_name(feedtype="On TV Today")[0]
        bookmarked_programs = self.api.bookmark_now_streaming_tv_shows_infuture(noOfShows=5, feedName=feed_name)
        no_partner_prog = self.api.bookmark_now_streaming_tv_shows_infuture_without_partnerid(noOfShows=2, feedName=feed_name)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_my_shows_title()
        if not bookmarked_programs and not no_partner_prog:
            self.my_shows_assertions.verify_content_in_category(self.my_shows_labels.LBL_RECENTLY_DELETED)
        elif bookmarked_programs and not no_partner_prog:
            self.my_shows_assertions.verify_content_in_category(self.my_shows_labels.LBL_RECENTLY_DELETED)
        else:
            self.my_shows_assertions.verify_content_in_category(self.my_shows_labels.LBL_RECENTLY_DELETED)
            self.my_shows_assertions.verify_content_in_category(
                self.my_shows_labels.LBL_MY_SHOWS_NOT_CURRENTLY_AVAILABLE_FOLDER)

    @pytestrail.case("C12792775")
    @pytest.mark.p1_regression
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    def test_267229_verify_my_shows_recordings_filter(self, setup_my_shows_sort_to_date,
                                                      setup_myshows_delete_recordings, setup_cleanup_myshows):
        """
        267229
        To verify the Recordings Filter in My Shows
        """
        channel = self.guide_page.guide_streaming_channel_number(self)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        program = self.guide_page.get_focussed_grid_item(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.my_shows_page.navigate_to_recordings_filter(self)
        self.my_shows_assertions.verify_content_under_recordings_filter(program)

    @pytestrail.case('C11123881')
    @pytest.mark.xray("FRUM-314")
    @pytest.mark.bat
    @pytest.mark.devhost
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_393716_trickplay_recording(self):
        """
        393716
        To  Verify Trickplay actions on Playback of Recordings from My shows
        :return:
        """
        # TODO
        # Add skip condition to record_currently_airing_shows() when no channels returned
        if not Settings.is_apple_tv():
            recording = self.api.record_currently_airing_shows(number_of_shows=1, genre="series", is_preview_offer_needed=True)
            if not recording:
                pytest.skip("Failed to schedule recording")
            program = self.my_shows_page.convert_special_chars(recording[0][0])
        else:
            channels = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
            if not channels:
                pytest.skip("Test requires recordable channels")
            program = self.guide_page.create_recording_using_ui(self, channels[0][0])
            if not program:
                pytest.skip(f"live program of {channels[0][0]} is not recordable")
        platform = Settings.platform
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.my_shows_page.validate_trickplay_actions(self, platform)

    @pytestrail.case("C12792774")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_97999_onepass_options_overlay(self, setup_myshows_delete_recordings, setup_cleanup_myshows):
        """
        97999
        To verify the Select and Right behavior when the highlight is on
        the Modify Recording options for a single ONE_PASS_NAME
        :return:
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_one_pass_on_record_overlay(self)
        self.guide_assertions.verify_whisper_shown(self.guide_labels.LBL_ONEPASS_WHISPER_TEXT)
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program)
        self.my_shows_page.wait_for_screen_ready(program.upper())
        self.my_shows_assertions.verify_onepass_options_overlay(self)

    @pytestrail.case("C12792773")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_98123_recording_options_with_modify_recording(self):
        """
        98123
        Content - Movie/Non-episodic/Episode - Modify recording - Recording options - Press SELECT/RIGHT
        :return:
        """
        # TODO
        # Add skip condition to record_currently_airing_shows() when no channels returned
        recording = self.api.record_currently_airing_shows(number_of_shows=1, genre="series")
        if not recording:
            pytest.skip("Failed to schedule recording")
        program = self.my_shows_page.convert_special_chars(recording[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.go_to_cached_action_screen(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(self.my_shows_labels.LBL_RECORDING_OPTIONS)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_RECORDING_OPTIONS_OVERLAY)
        self.my_shows_assertions.verify_overlay()

    @pytestrail.case("C12792787")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-124")
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.msofocused
    @pytest.mark.timeout(Settings.timeout)
    def test_393719_verify_cancelling_upcoming_recording(self, setup_myshows_delete_recordings, setup_cleanup_myshows):
        """
        393719
        Verify Cancelling the upcoming Recording
        """
        channel = self.guide_page.guide_streaming_channel_number(self)
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        self.guide_page.get_live_program_name(self)
        self.guide_page.wait_for_screen_ready()
        self.menu_page.menu_navigate_left_right(0, 2)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        program = self.guide_page.get_focussed_grid_item(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.guide_page.tab_refresh_explicit_recording_icon(icon_validation=False)
        self.my_shows_page.cancel_upcoming_recording_from_guide(self, program)
        self.menu_page.go_to_to_do_list(self)
        self.my_shows_assertions.verify_empty_to_do_list(self)

    @pytestrail.case("C12792779")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.cloud_core_watch_Recording
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_88524_inprogress_recording_playback(self, setup_my_shows_sort_to_date, setup_myshows_delete_recordings,
                                                 setup_cleanup_myshows):
        """
        88524
        To verify playback of in-progress recording
        :return:
        """
        channel = self.guide_page.guide_streaming_channel_number(self)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.nav_to_menu_by_substring(program)
        self.my_shows_assertions.verify_recording_icon()
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.live_tv_assertions.verify_view_mode(self.my_shows_page.get_watch_or_video_recording_view_mode(self))
        self.my_shows_assertions.verify_recording_playback(self)

    @pytestrail.case("C12792772")
    # @pytest.mark.test_stabilization
    # @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.cloud_core_watch_Recording
    @pytest.mark.infobanner
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_80987_my_shows_recording_playback(self):
        """
        80987
        Trickplay - Myshows recording - Enter PLAY mode
        :return:
        """
        recording = self.api.record_currently_airing_shows(number_of_shows=1, genre="series", filter_channel=True,
                                                           filter_ndvr=True, is_preview_offer_needed=True)
        if not recording:
            pytest.skip("Failed to schedule recording")
        program = self.my_shows_page.convert_special_chars(recording[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_infobanner_and_trickplay_shown()
        self.guide_assertions.verify_play_normal()

    @pytestrail.case("C12792778")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_80988_FFWDx1_mode(self):
        """
        80988
        Trickplay - My Shows recording - FFWDx1 mode
        :return:
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(
            recordable=True, filter_channel=True, filter_ndvr=True, is_preview_offer_needed=True)
        recording = self.api.record_currently_airing_shows(number_of_shows=1, includeChannelNumbers=channels,
                                                           genre="series", use_cached_grid_row=True)
        if not recording:
            pytest.skip("Failed to schedule recording")
        program = self.my_shows_page.convert_special_chars(recording[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_recording_playback(self)
        self.guide_assertions.verify_play_normal()
        self.guide_assertions.verify_fast_forward_1(self)

    @pytestrail.case("C12792788")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-125")
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_393720_delete_recording_from_todo_list(self):
        """
        393720
        Delete recordings from To Do List.
        """
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.menu_page.menu_navigate_left_right(0, 4)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.guide_page.tab_refresh_explicit_recording_icon(icon_validation=False)
        self.menu_page.go_to_to_do_list(self)
        self.guide_assertions.verify_show_name_present(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.go_to_cached_action_screen(self, Recording=True)
        self.my_shows_page.cancel_upcoming_recording_in_todo_list(self)

    @pytestrail.case("C12792790")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_393513_schedule_multiple_recordings_from_livetv(self, setup_myshows_delete_recordings,
                                                             setup_cleanup_myshows):
        """
        393513
        Verify the ability to record 4-5 explicit Episodic & Non Episodic programs from LiveTV with nDVR.
        """
        channels = self.service_api.get_recordable_non_movie_channel(channel_count=2, filter_channel=True)
        if not channels:
            pytest.skip("Test requires recordable channels")
        programs = []
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_page.enter_channel_number(channels[0][0])
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()
        for channel in channels:
            show_name = self.my_shows_page.create_recording_from_live_tv(self, channel[0])
            if not show_name:
                pytest.fail("Test failed to get the name of the recorded program")
            programs.append(show_name)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_recorded_programs(programs)

    @pytestrail.case("C12792786")
    @pytest.mark.xray("FRUM-123")
    @pytest.mark.p1_regression
    @pytest.mark.bvt
    @pytest.mark.ndvr
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.timeout(Settings.timeout)
    def test_393715_w2w_recording(self, setup_myshows_delete_recordings, setup_cleanup_myshows):
        """
        393715
        Verify Recording from W2W Screen
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_PRIMARY_SCREEN, 10000)
        self.wtw_page.nav_to_browse_options_menu(self)
        self.menu_page.select_menu_items(self.my_shows_labels.LBL_TV)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_PRIMARY_SCREEN, 10000)
        self.wtw_assertions.verify_highlight_not_in_netflix_strip()
        program = self.my_shows_page.record_tvseries_from_wtw()
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_recorded_content(self, program)

    @pytestrail.case("C12792789")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_231784_my_shows_delete_group_overlay(self):
        channels = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if not channels:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_series_from_myshows(program)
        self.my_shows_assertions.verify_delete_group_overlay(self, program)

    @pytestrail.case("C12792162")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_359552_pause_recording_validation(self):
        """
        359552
        To play recorded program from predictions and deleting the program when it is being played
        should gracefully exit and starts playing Live TV.
        :return:
        """
        recording = self.api.record_currently_airing_shows(number_of_shows=1, genre="series", filter_channel=True,
                                                           filter_ndvr=True, is_preview_offer_needed=True)
        if not recording:
            pytest.skip("Failed to schedule recording")
        program = self.my_shows_page.convert_special_chars(recording[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_assertions.verify_playback_play()
        self.guide_page.pause_show(self)
        self.my_shows_page.pause(30)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_PAUSED)
        self.my_shows_page.select_show(program)
        try:
            self.my_shows_page.select_strip(self.my_shows_labels.LBL_STOP_REC)
        except (KeyError, LookupError):
            self.my_shows_page.select_strip(self.my_shows_labels.LBL_DELETE)
        self.my_shows_page.select_delete_pause_overlay(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_assertions.verify_content_in_category(self.my_shows_labels.LBL_RECENTLY_DELETED)
        self.my_shows_page.select_show(self.my_shows_labels.LBL_RECENTLY_DELETED)
        self.my_shows_assertions.verify_program_in_recently_deleted_folder(self, program)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_LIVETV_SHORTCUT)
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_WATCHVIDEO_SHORTCUT)

    @pytestrail.case("C12792163")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_333981_verify_enter_pin_overlay_for_movie_screen(self):
        channel = self.service_api.get_random_recordable_movie_channel()
        if not channel:
            pytest.skip("Test requires recordable channels")
        channel_number = channel[0][0]
        movie = channel[0][2]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_MOVIES)
        self.my_shows_page.select_show(movie)
        self.my_shows_page.select_strip(self.my_shows_labels.LBL_PLAY)
        self.menu_assertions.verify_enter_PIN_overlay()

    @pytestrail.case("C12792795")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.notapplicable(Settings.is_dev_host())
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_9916709_verify_resume_playing_overlay_timeout_in_ndvr_recording(self):
        """
        To verify Resume Playing Overlay timeout watching recording
        Testcase:  https://testrail.tivo.com//index.php?/cases/view/9916709
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True, filter_ndvr=True)
        recording = self.api.record_currently_airing_shows(1, includeChannelNumbers=channels, filter_channel=True,
                                                           filter_ndvr=True)
        if not recording:
            pytest.skip("Failed to schedule recording")
        show = self.home_page.convert_special_chars(recording[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_screen_title(self.my_shows_labels.LBL_MY_SHOWS)
        last_screen = self.my_shows_page.play_recording(show)
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_watch_recording_mode(self)
        self.watchvideo_page.skip_hdmi_connection_error()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_play_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.live_tv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.watchvideo_page.wait_for_resume_playing_overlay()
        self.watchvideo_assertions.verify_resume_playing_overlay_shown(True)
        self.watchvideo_page.wait_for_resume_playing_overlay_timeout()
        self.watchvideo_assertions.verify_resume_playing_overlay_shown(False)
        self.watchvideo_assertions.verify_view_mode(last_screen)

    @pytestrail.case("C12792792")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.notapplicable(Settings.is_dev_host())
    @pytest.mark.timeout(Settings.timeout)
    def test_9916706_verify_stop_option_in_resume_playing_overlay_in_ndvr_recording(self):
        """
        To verify Resume Playing Overlay 'Stop' option watching recording
        Testcase:  https://testrail.tivo.com//index.php?/cases/view/9916706
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True, filter_ndvr=True)
        recording = self.api.record_currently_airing_shows(1, includeChannelNumbers=channels, filter_channel=True,
                                                           filter_ndvr=True)
        if not recording:
            pytest.skip("Failed to schedule recording")
        show = self.my_shows_page.convert_special_chars(recording[0][0])
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
        self.watchvideo_assertions.verify_video_playback_mode(self.live_tv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.watchvideo_page.wait_for_resume_playing_overlay()
        self.watchvideo_assertions.verify_resume_playing_overlay_shown(True)
        self.watchvideo_page.select_menu(self.live_tv_labels.LBL_STOP_PLAYING_OPTION)
        self.watchvideo_assertions.verify_resume_playing_overlay_shown(False)
        self.watchvideo_assertions.verify_view_mode(last_screen)

    @pytestrail.case("C12792793")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.notapplicable(Settings.is_dev_host())
    @pytest.mark.timeout(Settings.timeout)
    def test_9916707_verify_play_option_in_resume_playing_overlay_in_ndvr_recording(self, setup_my_shows_sort_to_date,
                                                                                    setup_myshows_delete_recordings):
        """
        To verify Resume Playing Overlay 'Play' option watching recording
        Testcase:  https://testrail.tivo.com//index.php?/cases/view/9916707
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True, filter_channel=True)
        recording = self.api.record_currently_airing_shows(1, includeChannelNumbers=channels)
        if not recording:
            pytest.skip("Failed to schedule recording")
        show = self.my_shows_page.convert_special_chars(recording[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(show)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_screen_ready()
        self.watchvideo_assertions.verify_watch_recording_mode(self)
        self.watchvideo_page.skip_hdmi_connection_error()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_play_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.live_tv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        self.watchvideo_page.wait_for_resume_playing_overlay()
        self.watchvideo_assertions.verify_resume_playing_overlay_shown(True)
        self.watchvideo_page.select_menu(self.live_tv_labels.LBL_PLAY_OPTION)
        self.watchvideo_assertions.verify_resume_playing_overlay_shown(False)
        self.watchvideo_assertions.verify_watch_recording_mode(self)
        self.watchvideo_assertions.verify_video_playback_mode(self.live_tv_labels.LBL_PLAYBACK_IN_PLAY_MODE)

    @pytestrail.case("C12792785")
    @pytest.mark.xray("FRUM-122")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_parental_control")
    def test_393711_explicit_recording_prediction_bar(self):
        """
        393711 - Explicit recording from prediction bar
        :return:
        """
        self.home_page.back_to_home_short()
        show = self.home_page.get_recordable_prediction_content(self)
        if not show:
            pytest.skip("No live recordable show found on prediction bar")
        self.home_page.goto_prediction()
        self.home_assertions.verify_highlighter_on_prediction_strip()
        self.home_page.navigate_by_strip(show[0])
        self.watchvideo_assertions.press_select_and_verify_streaming(self)
        channel = self.watchvideo_page.get_channel_number()
        title = self.my_shows_page.create_recording_from_live_tv(self, channel)
        if title is None:
            pytest.fail("Unable to schedule a recording for a live program available on prediction bar")
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_under_recordings_filter(title)

    @pytestrail.case("C12792791")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.onepass
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_393705_modify_recording_options_todo_list(self):
        """
        TC 393705 - modify recording options from To Do List.
        """
        self.home_page.go_to_guide(self)
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if channel is None:
            pytest.fail("Recordable channel is not available")
        self.guide_page.enter_channel_number(channel, confirm=False)
        self.guide_page.get_live_program_name(self)
        self.menu_page.menu_navigate_left_right(0, 2)
        self.guide_page.wait_for_screen_ready()
        self.guide_page.select_and_record_program(self)
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.guide_page.wait_for_screen_ready()
        program = self.guide_page.get_focussed_grid_item(self)
        self.menu_page.go_to_to_do_list(self)
        self.guide_assertions.verify_show_name_present(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.go_to_cached_action_screen(self, Recording=True)
        preview = self.my_shows_page.modify_recording_options(self, Recording=True)
        self.my_shows_assertions.verify_modified_recording_or_onepass_options(preview, Recording=True)

    @pytestrail.case("C12792166")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_393705_modify_onepass_options_todo_list(self):
        """
        TC 393705 - modify one pass options from To Do List.
        """
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, live=True, filter_channel=True)
        if channel is None:
            raise AssertionError("could not any channel airing episodic program")
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.get_live_program_name(self)
        self.menu_page.menu_navigate_left_right(0, 2)
        program = self.guide_page.create_one_pass_on_record_overlay(self)
        self.my_shows_page.wait_for_screen_ready()
        self.menu_page.go_to_to_do_list(self)
        self.guide_assertions.verify_show_name_present(program)
        self.my_shows_page.select_show(program)
        try:
            self.my_shows_page.go_to_cached_action_screen(self, self.my_shows_labels.LBL_UPCOMING)
        except Exception:
            self.my_shows_page.go_to_cached_action_screen(self, self.guide_labels.LBL_LIVE_AND_UPCOMING)
        preview = self.my_shows_page.modify_recording_options(self)
        self.my_shows_assertions.verify_modified_recording_or_onepass_options(preview)

    @pytestrail.case("C12792164")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_334107_verify_enter_pin_overlay_unknown_rating(self):
        '''
        TC 334107 - Verify enter pin overlay is displayed on playback of recording of a non episodic program
        :return:
        '''
        params = {"with_rating": False, "find_appropriate": True, "stop_seek_at_first_match": True,
                  "is_recordable_chan": True, "is_recordable_show": True, "is_live": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        if offer is None:
            pytest.skip("Could not find any recordable program airing live with no rating")
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_record_program(self)
        self.menu_page.lock_pc_with_ratings(self, unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                            unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.menu_assertions.verify_enter_PIN_overlay()

    @pytestrail.case("C12792161")
    # @pytest.mark.test_stabilization
    # @pytest.mark.p1_regression -- Deprecating as case C13230091 under test_home.py is covering the same behaviour
    # @pytest.mark.predictionbar
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device does not have Video Providers")
    def test_358157_launch_app_using_prediction_ad(self):
        """
        TC 358157 - Verifying App launch using prediction ads.
        :param
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_page.goto_prediction()
        self.service_api.get_feed_item_find_results("/predictions")
        if not self.my_shows_page.select_prediction_ad(self):
            pytest.skip("Ads are not available in prediction bar")
        self.my_shows_assertions.verify_prediction_ad_launch(self, Settings.app_package)
        self.home_page.back_to_home_short()

    @pytestrail.case("C12792165")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.parental_control
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_334108_verify_enter_pin_overlay(self):
        '''
        TC 334108 - Verify enter pin overlay on playback of recording from my shows
        :param setup_cleanup_parental_and_purchase_controls:
        :return:
        '''

        self.home_page.go_to_guide(self)
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.guide_page.enter_channel_number(channel, confirm=False)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_record_program(self)
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                            unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.menu_assertions.verify_enter_PIN_overlay()

    # @pytest.mark.test_stabilization
    # @pytest.mark.p1_regression
    @pytest.mark.longrun
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_393722_inprogress_and_completed_recording_option_modification(self):
        """
        TC 393722 - modify recording options for in progress and completed recording
        """
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        if channel is None:
            pytest.fail("Recordable channel is not available")
        self.guide_page.enter_channel_number(channel, confirm=False)
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.go_to_cached_action_screen(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        preview = self.my_shows_page.modify_inprogress_recording_options(self)
        self.my_shows_assertions.verify_modified_recording_options(preview)
        self.my_shows_page.wait_for_record_completion(self, showtime)
        preview = self.my_shows_page.select_keep_from_watch_now_strip(self)
        self.my_shows_assertions.verify_preview_message(self, preview)

    # @pytest.mark.e2e
    @pytest.mark.longrun
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_8880444_record_playback_delete_program(self):
        """
        8880444
        Verify watching an airing available & entitled nDVR show,navigating to My Shows,playing & watching show until the end
        Then deleting the show is removed from My Shows and displays in the Recently Deleted folder
        """
        recording = self.service_api.schedule_single_recording()
        if not recording:
            pytest.skip("Unable to create recording")
        program = recording[0][0]
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_under_recordings_filter(program)
        self.my_shows_page.select_menu_by_substring(program)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN)
        self.my_shows_page.select_and_wait_for_playback_play()
        self.live_tv_assertions.verify_playback_play()
        self.my_shows_assertions.wait_and_verify_delete_recording_overlay()
        self.my_shows_page.select_keep_option(self)
        self.my_shows_page.wait_for_screen_ready(program.upper())
        self.my_shows_assertions.verify_cached_action_screen(program.upper())
        self.my_shows_page.delete_episodic_program(self, program)
        self.my_shows_page.go_to_recently_deleted_folder(self)
        self.my_shows_assertions.verify_program_in_recently_deleted_folder(self, program)

    # @pytest.mark.p1_regression
    @pytest.mark.skipif(not Settings.is_stb(),
                        reason="This test is applicable only for stb boxes")
    def test_112048054_max_pre_roll_launching_my_shows_folder(self):
        """
        112048054
        Verify MAX Pre-roll launching before watching a recording from My Shows Folder.
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, movie=False, live=True)
        if not channel:
            pytest.skip("Test requires recordable channels")
        self.home_page.log.step("channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.create_live_recording()
        program = self.guide_page.get_grid_focus_details()["program_name_in_cell"]
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.nav_to_show(program)
        self.screen.base.press_play()
        self.my_shows_page.verify_view_mode(self.liveTv_labels.LBL_PRE_ROLL_VIEW_MODE)

    # @pytest.mark.p1_regression
    @pytest.mark.skipif(not Settings.is_stb(),
                        reason="This test is applicable only for stb boxes")
    def test_112048063_max_pre_roll_launching_series_screen_recordings(self):
        """
        112048063
        Verify MAX Pre-roll launching before watching a recording from Series screen.
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, movie=False, live=True)
        if not channel:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        program = self.guide_page.create_one_pass_on_record_overlay(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.verify_view_mode(self.liveTv_labels.LBL_PRE_ROLL_VIEW_MODE)

    # @pytest.mark.p1_regression
    @pytest.mark.skipif(not Settings.is_stb(),
                        reason="This test is applicable only for stb boxes")
    def test_112048085_max_pre_roll_launching_series_screen_watchlist(self):
        """
        112048085
        MAX Pre-roll - Launching - Series screen - WatchList
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, movie=False, live=True)
        if not channel:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        program = self.guide_page.create_one_pass_on_record_overlay(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_WATCH_LIST)
        self.my_shows_page.verify_view_mode(self.liveTv_labels.LBL_PRE_ROLL_VIEW_MODE)

    # @pytest.mark.p1_regression
    @pytest.mark.skipif(not Settings.is_stb(),
                        reason="This test is applicable only for stb boxes")
    def test_112048005_max_pre_roll_ad_not_fully_watched(self):
        """
        112048005
        Verify MAX Pre-roll - Ad not fully watched.
        """
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, movie=False, live=True)
        if not channel:
            pytest.skip("Test requires recordable channels")
        self.home_page.log.step("channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.create_live_recording()
        program = self.guide_page.get_grid_focus_details()["program_name_in_cell"]
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.nav_to_show(program)
        self.screen.base.press_play()
        self.my_shows_page.verify_view_mode(self.liveTv_labels.LBL_PRE_ROLL_VIEW_MODE)
        self.home_assertions.press_home_and_verify_screen(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.nav_to_show(program)
        self.screen.base.press_play()
        self.my_shows_page.verify_view_mode(self.liveTv_labels.LBL_PRE_ROLL_VIEW_MODE)

    @pytestrail.case("C12792167")
    @pytest.mark.favorite_channels
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_my_shows_sort_to_date")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    @pytest.mark.timeout(Settings.timeout)
    def test_10195352_verify_favorite_channels_panel_watch_recording(self):
        """
        :Description:
            To verify Favorite Channels panel watching recording
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/10195352
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.go_to_favorite_channels()
        channel = self.guide_page.guide_streaming_channel_number(self)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()

    # @pytest.mark.e2e
    @pytest.mark.longrun
    @pytest.mark.ndvr
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_74395711_record_and_watch_till_end(self):
        """
        TC 74395711 - record and watch till end
        """
        self.home_page.go_to_guide(self)
        channel = self.service_api.map_channel_number_to_currently_airing_offers(
            self.service_api.get_random_recordable_channel(
                channel_count=-1, filter_channel=True, is_preview_offer_needed=True),
            self.service_api.channels_with_current_show_start_time(use_cached_grid_row=True),
            genre="series", linear_only=True, count=1)

        if channel is None:
            pytest.skip("Recordable channel is not available")
        self.guide_page.enter_channel_number(channel[0][1])
        self.guide_page.wait_for_screen_ready()
        program = self.guide_page.get_live_program_name(self)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.text_search_page.go_to_search(self)
        self.text_search_page.search_and_select(program, program)
        self.vod_page.check_onepass_SVOD(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_WATCH_LIST)
        self.watchvideo_assertions.verify_playback_play()
        self.my_shows_assertions.wait_and_verify_delete_recording_overlay()
        self.my_shows_page.select_keep_option(self)

    @pytest.mark.disconnected_state
    @pytest.mark.usefixtures("set_bridge_status_up")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.notapplicable(Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH")
    def test_74494107_start_recording_from_live_and_disconnect_reconnect(self):
        '''
        TC 74494107 - start recording from live - disconnect and reconnect
        :return:
        '''
        channel_list = self.api.get_ndvr_channels_for_health_check()
        if channel_list is None:
            pytest.fail("Could not find any recordable channel for non episodic program airing live")
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_list[0], confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()
        self.my_shows_page.create_recording_from_live_tv(self, channel_list[0])
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.validate_disconnected_state(self)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.guide_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_list[0], confirm=False)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_assertions.verify_playback_play()

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.watch_stickiness
    @pytest.mark.timeout(21600)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_11678348_verify_watch_stickiness_in_my_shows_after_recording(self):
        """
        :Description:
            Verify Watch Stickiness (highlighted next ep) in My Shows after a recording have been watched to the end.
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11678348
        """
        title = self.my_shows_page.create_one_pass_and_wait_second_offer(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_WATCH_LIST)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        focused_episode, next_episode = self.my_shows_page.get_cur_and_next_episodes_info()
        self.my_shows_page.select_and_wait_for_playback_play()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_currently_playing_episode(focused_episode['num'])
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete()
        self.my_shows_page.wait_for_screen_ready()
        self.screen.base.press_back()
        self.my_shows_page.select_keep_option(self)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        self.my_shows_assertions.verify_focused_episode(focused_episode['name'])
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(title)
        self.my_shows_assertions.verify_focused_episode(next_episode['name'])

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.watch_stickiness
    @pytest.mark.timeout(21600)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_11400975_watch_stickiness_forward_stickiness_watched_half_of_the_recording(self):
        """
        :Description:
            Verify Watch Stickiness in My Shows -> Recordings -> Watch list after a half of recording was watched
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11400975
        :Note:
            Sometimes need to re-run test few times because if 2 episodes won't be found for recording test will fail
        """
        title = self.my_shows_page.create_one_pass_and_wait_second_offer(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_WATCH_LIST)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        focused_episode, next_episode = self.my_shows_page.get_cur_and_next_episodes_info()
        self.my_shows_page.press_down_button()
        self.my_shows_page.select_and_wait_for_playback_play()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_currently_playing_episode(next_episode['num'])
        duration = self.watchvideo_page.get_trickplay_duration_in_sec()
        cur_position = self.base.convert_time_to_sec(self.watchvideo_page.get_trickplay_current_position())
        self.watchvideo_page.watch_video_for((duration - cur_position) / 2)
        self.screen.base.press_back()
        self.my_shows_page.select_keep_option(self)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        self.my_shows_assertions.verify_focused_episode(next_episode['name'])
        self.screen.base.press_up()
        self.my_shows_assertions.verify_focused_episode(focused_episode['name'])
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        self.my_shows_assertions.verify_focused_episode(next_episode['name'])

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.watch_stickiness
    @pytest.mark.timeout(21600)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_11400976_watch_stickiness_forward_stickiness_watched_the_beginning_of_recording(self):
        """
        :Description:
            Verify Watch Stickiness in My Shows -> Recordings -> Watch list after a recording was started and interrupted
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11400976
        :Note:
            Sometimes need to re-run test few times because if 2 episodes won't be found for recording test will fail
        """
        title = self.my_shows_page.create_one_pass_and_wait_second_offer(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_WATCH_LIST)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        focused_episode, next_episode = self.my_shows_page.get_cur_and_next_episodes_info()
        self.my_shows_page.press_down_button()
        self.my_shows_page.select_and_wait_for_playback_play()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_currently_playing_episode(next_episode['num'])
        self.watchvideo_page.watch_video_for(20)
        self.screen.base.press_back()
        self.my_shows_page.select_keep_option(self)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        self.my_shows_assertions.verify_focused_episode(next_episode['name'])
        self.screen.base.press_up()
        self.my_shows_assertions.verify_focused_episode(focused_episode['name'])
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        self.my_shows_assertions.verify_focused_episode(next_episode['name'])

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.watch_stickiness
    @pytest.mark.timeout(21600)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_11400977_watch_stickiness_forward_stickiness_watched_recording_to_the_end(self):
        """
        :Description:
            Verify Watch Stickiness in My Shows -> Recordings -> Watch list after a recording was watched to the end
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11400977
        :Note:
            Sometimes need to re-run test few times because if 2 episodes won't be found for recording test will fail
        """
        title = self.my_shows_page.create_one_pass_and_wait_second_offer(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_WATCH_LIST)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        focused_episode, next_episode = self.my_shows_page.get_cur_and_next_episodes_info()
        self.my_shows_page.select_and_wait_for_playback_play()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_currently_playing_episode(focused_episode['num'])
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete(False)
        self.watchvideo_page.press_ok_button()
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        self.my_shows_assertions.verify_focused_episode(next_episode['name'])

    # @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.watch_stickiness
    @pytest.mark.timeout(21600)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_11400978_watch_stickiness_forward_stickiness_watched_recording_and_started_watch_next(self):
        """
        :Description:
            Verify Watch Stickiness in My Shows -> Recordings -> Watch list after a recording
            was watched to the end and next episode was started.
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/cases/view/11400978
        :Note:
            Sometimes need to re-run test few times because if 2 episodes won't be found for recording test will fail
        """
        title = self.my_shows_page.create_one_pass_and_wait_second_offer(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_WATCH_LIST)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        focused_episode, next_episode = self.my_shows_page.get_cur_and_next_episodes_info()
        self.my_shows_page.select_and_wait_for_playback_play()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_currently_playing_episode(focused_episode['num'])
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete(False)
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_currently_playing_episode(next_episode['num'])
        self.watchvideo_page.watch_video_for(20)
        self.screen.base.press_back()
        self.my_shows_page.select_keep_option(self)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        self.my_shows_assertions.verify_focused_episode(focused_episode['name'])
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        self.my_shows_assertions.verify_focused_episode(next_episode['name'])

    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_14379900_verify_ndvrscreen_after_press_back_from_asset_playing(self):
        """
        Verify if ndvrscreen is displayed when back button is pressed immediately after playing an asset

        https://testrail.tivo.com//index.php?/cases/view/14379900
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_recording_playback(self)
        self.screen.base.press_back()
        self.vod_assertions.verify_vod_series_or_action_screen_view_mode()

    @pytest.mark.longrun
    def test_14386478_verify_if_recordings_are_not_deleted_after_hours_from_myshows(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/14386478
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.nav_to_menu_by_substring(program)
        self.my_shows_assertions.verify_recording_icon()
        self.my_shows_page.pause(60 * 60)
        self.my_shows_assertions.verify_content_in_category(program)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_19779803_verify_start_over_option_for_recording_having_pause_point(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/19779803
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_recording_playback(self)
        self.watchvideo_page.watch_video_for(20)
        self.guide_page.pause_show(self)
        self.home_page.back_to_home_short()
        self.home_page.goto_livetv_short(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.wait_for_screen_ready()
        if self.my_shows_page.view_mode() == self.my_shows_labels.LBL_SERIES_SCREEN_VIEW:
            self.my_shows_page.menu_navigate_left_right(1, 0)
            self.my_shows_assertions.verify_content_in_category(self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.nav_to_menu(self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.pause(2)
            self.my_shows_page.select_item()
            self.my_shows_page.pause(10)
            self.screen.base.press_right()
            self.my_shows_page.pause(5)
            self.screen.base.press_enter()
            self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_start_over(self, refresh=True)

    @pytest.mark.stop_streaming
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_disable_stay_awake")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "The test is applicable only for Hydra v1.13 and higher")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_cleanup_turn_on_device_power")
    def test_14391789_verify_stop_streaming_tv_on_off_while_playing_recording(self):
        """
        Stop Streaming - Stream a recording - TV(HDMI Adapter) Power OFF/ON

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/14391789
        """
        channels = self.service_api.get_random_recordable_channel(channel_count=2, filter_channel=True)
        if not channels:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.guide_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0][0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.guide_page.wait_for_screen_ready("GridGuide")
        self.guide_page.enter_channel_number(channels[1][0])
        self.guide_page.wait_for_screen_ready("GridGuide")
        self.watchvideo_page.press_ok_button()
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        last_tuned_channel = self.watchvideo_page.get_channel_number()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.wait_for_screen_ready()
        if self.watchvideo_page.is_overlay_shown():
            if self.watchvideo_page.is_delete_recording_overlay():
                self.my_shows_page.select_keep_recording(self)
                self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
                self.my_shows_page.wait_for_screen_ready()
        self.my_shows_page.verify_recording_playback_and_curl_url(self)
        self.watchvideo_page.turn_off_device_power(Settings.equipment_id)
        self.home_page.wait_for_screen_saver(time=self.guide_labels.LBL_SCREEN_SAVER_WAIT_TIME)
        self.watchvideo_assertions.verify_video_playback_stopped()
        self.watchvideo_assertions.verify_foreground_package_name(self.liveTv_labels.LBL_SCREEN_SAVER_PACK)
        self.watchvideo_page.turn_on_device_power(Settings.equipment_id)
        self.screen.base.press_right()
        if not Settings.is_managed():
            self.home_page.unamanged_sign_in(self, Settings.app_package, Settings.username, Settings.password)
        time.sleep(self.guide_labels.LBL_TEN_SECONDS)
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=900000)
        self.home_assertions.verify_home_title()
        self.watchvideo_assertions.verify_video_playback_started()
        self.screen.refresh()
        self.watchvideo_page.press_exit_button()
        self.watchvideo_assertions.verify_channel_number(last_tuned_channel)

    @pytest.mark.ndvr
    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_20934311_verify_highlight_on_recordings(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20934311
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)[0][0]
        if not channel:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(program)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_series_screen(self)
        self.screen.base.press_left()
        self.my_shows_assertions.verify_menu_has_focus()  # focus is on RECORDINGS category
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_menu_has_focus()  # focus is on Recordings

    @pytestrail.case("T389366344")
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("exit_overlay")
    def test_389366344_verify_long_key_press_info_card(self):
        """
        https://testrail.tivo.com//index.php?/tests/view/389366344
        """
        channel = self.service_api.get_recordable_non_movie_channel(episodic=True, filter_ndvr=False)
        if not channel:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        program = self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(program)
        self.my_shows_assertions.verify_series_screen(self)
        self.screen.base.press_right()
        self.screen.base.press_enter()
        self.wtw_page.verify_screen_title(f"{program.upper()}")
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_ALL_EPISODES,
                                                                        select_view_all=True)
        self.wtw_page.verify_screen_title(f"ALL EPISODES: {program.upper()}")
        for _ in range(2):
            self.screen.base.press_down()
        self.screen.base.long_press_enter()
        self.my_shows_assertions.verify_overlay_title(program)
        self.screen.base.press_back()
        if Settings.is_managed():
            self.screen.base.press_info()
            self.my_shows_assertions.verify_overlay_title(program)
            self.screen.base.press_back()

    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_21568509_playback_ndvr_and_watch_recording_for_some_time(self):
        """
        https://jira.tivo.com/browse/CA-7785

        verify Paused Time out(Resume Playing) overlay did not display on playing nDVR assets
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True,
                                                                        filter_channel=True,
                                                                        filter_ndvr=True,
                                                                        is_preview_offer_needed=False)
        recording = self.api.record_currently_airing_shows(number_of_shows=1,
                                                           includeChannelNumbers=channels,
                                                           genre="series",
                                                           use_cached_grid_row=True)
        if not recording:
            pytest.skip("Failed to schedule recording")
        program = self.my_shows_page.convert_special_chars(recording[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_recording_playback(self)
        self.guide_assertions.verify_play_normal()
        self.watchvideo_page.watch_video_for(60 * 15)
        self.screen.refresh()
        self.my_shows_assertions.verify_resume_playing_overlay_not_shown()

    @pytest.mark.xray("FRUM-91312")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_frum_91312_verify_recording_folder_is_visible(self):
        """
        https://jira.tivo.com/browse/CA-9434
        Verify Recording tab under the My Shows folder
        """
        channels = self.api.get_channels_with_no_trickplay_restrictions(recordable=True,
                                                                        filter_channel=True,
                                                                        filter_ndvr=True,
                                                                        is_preview_offer_needed=False
                                                                        )
        recording = self.api.record_currently_airing_shows(number_of_shows=1,
                                                           includeChannelNumbers=channels,
                                                           genre="series",
                                                           use_cached_grid_row=True,
                                                           )
        if not recording:
            pytest.skip("Failed to schedule recording")
        program = self.my_shows_page.convert_special_chars(recording[0][0])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.delete_recording_in_my_show(program)
        self.my_shows_page.go_to_recently_deleted_folder(self)
        self.my_shows_page.undelete_recording_in_my_show(self, program)
        self.guide_page.verify_whisper_shown(self.my_shows_labels.LBL_RECOVER_WHISPER)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_assertions.verify_recording_folder_is_visible(self)

    @pytest.mark.xray("FRUM-91308")
    @pytest.mark.ndvr
    @pytest.mark.ndvr_fill_storage
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.longrun
    def test_frum_91308_verify_error_msg_displayed_after_recovering_item_when_storage_is_full(self):
        """
        https://jira.tivo.com/browse/CA-9667
        Error message is displayed recovering a deleted item when the storage quota is 100%
        """
        # TODO
        # Perhaps, need to enlarge shows number to record, currently this test fails due to storage limit overlay is not shown
        channels = self.api.get_channels_with_no_trickplay_restrictions(
            recordable=True, filter_channel=True, filter_ndvr=True, is_preview_offer_needed=True)
        recording = self.api.record_currently_airing_shows(number_of_shows=10, includeChannelNumbers=channels,
                                                           genre="series", keepBehavior="forever", use_cached_grid_row=True)
        if not recording:
            pytest.skip("Skipping because recodrings are not created.")
        program = self.my_shows_page.convert_special_chars(recording[0][0])
        self.menu_page.go_to_user_preferences(self)
        option_name = self.menu_page.get_onepass_option_name(self)
        self.menu_page.select_menu_items(option_name)
        self.menu_assertions.validate_one_pass_and_recording_option(self, option_name)
        self.menu_page.modify_onepass_recording_options_from_user_preference_option(self, self.guide_labels.LBL_EVERYTHING,
                                                                                    self.guide_labels.LBL_ALL_SHOWS,
                                                                                    self.guide_labels.LBL_KEEP_UNTIL[1])
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.delete_recording_in_my_show(program)
        self.my_shows_page.search_and_select_recently_deleted_folder(self)
        self.my_shows_page.recover_and_verify_storage_limit_overlay(self)

    @pytest.mark.p1_regression
    @pytest.mark.frumos_15
    @pytest.mark.ndvr
    @pytest.mark.cc_my_shows_acceptance
    def test_21558674_21558675_21558676_21558677_21558679_verify_ndvr_space_display_in_UI(self):
        """
        Verify client disk configuration from branding UI (Service console) matches with UI display in My shows
        https://testrail.tivo.com//index.php?/cases/view/21558674
        https://testrail.tivo.com//index.php?/cases/view/21558675
        https://testrail.tivo.com//index.php?/cases/view/21558676
        https://testrail.tivo.com//index.php?/cases/view/21558677
        https://testrail.tivo.com//index.php?/cases/view/21558679
        """
        self.home_page.relaunch_hydra_app()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_home_title()
        clientdiskconfig = self.my_shows_page.get_ndvr_space_display(self)
        diskmeter = self.my_shows_page.get_diskmeter_from_UI(self)
        if diskmeter:
            self.my_shows_assertions.verify_diskconfig_against_ui(clientdiskconfig, diskmeter)
        else:
            pytest.fail("Diskmeter is unavailable on Myshows UI")

    @pytest.mark.test_stabilization
    @pytest.mark.frumos_15
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.timeout(Settings.timeout_mid)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_21558682_verify_change_in_space_display_in_myshows_after_scheduling_recordings(self):
        """
        To verify adding recording in nDVR decreases the disk meter space
        https://testrail.tivo.com//index.php?/cases/view/21558682
        """
        clientdiskconfig = self.my_shows_page.get_ndvr_space_display(self)
        self.home_page.relaunch_hydra_app()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_home_title()
        diskmeter_before = self.my_shows_page.get_diskmeter_from_UI(self)
        recording = self.api.record_currently_airing_shows(number_of_shows=5, is_preview_offer_needed=True)
        if not recording:
            pytest.skip("Failed to create recording.")
        recording_list = len(recording)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(recording[recording_list - 1][1])
        showtime = self.guide_page.get_program_start_and_end_time()
        self.my_shows_page.wait_for_record_completion(self, showtime)
        diskmeter_after = self.my_shows_page.get_diskmeter_from_UI(self)
        if diskmeter_before and diskmeter_after:
            self.my_shows_assertions.verify_disk_meter_change(
                diskmeter_before, diskmeter_after, clientdiskconfig, add_recording=True)
        else:
            pytest.fail("Diskmeter is unavailable on Myshows UI")

    @pytest.mark.test_stabilization
    @pytest.mark.frumos_15
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.timeout(Settings.timeout_mid)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_21558683_verify_change_in_space_display_in_myshows_after_deleting_recordings(self):
        """
        To verify deleting recording in nDVR increases the disk meter space
        https://testrail.tivo.com//index.php?/cases/view/21558683
        """
        recordings = self.api.get_recordings_in_my_shows()
        disk_meter_ui = self.my_shows_page.get_diskmeter_from_UI(self)
        if disk_meter_ui is None:
            pytest.fail("Could be an Infra issue, please check whether NDVR is activated or not")
        disk_meter = int(''.join(re.findall(r'\d', disk_meter_ui)))
        if len(str(disk_meter)) == 2:
            disk_meter = int(str(disk_meter) + "00")
        clientdiskconfig = self.my_shows_page.get_ndvr_space_display(self)
        if not recordings or disk_meter == Settings.ndvr_disk_max_limit_time or \
                disk_meter == Settings.ndvr_disk_max_limit_percent:
            recording = self.api.record_currently_airing_shows(number_of_shows=5, is_preview_offer_needed=True)
            if not recording:
                pytest.skip("Failed to create recording.")
            recording_list = len(recording)
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(recording[recording_list - 1][1])
            showtime = self.guide_page.get_program_start_and_end_time()
            self.my_shows_page.wait_for_record_completion(self, showtime)
        self.home_page.relaunch_hydra_app()
        self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, timeout=600000)
        self.home_assertions.verify_home_title()
        diskmeter_before = self.my_shows_page.get_diskmeter_from_UI(self)
        self.api.delete_recordings_from_myshows()
        diskmeter_after = self.my_shows_page.get_diskmeter_from_UI(self)
        if diskmeter_before and diskmeter_after:
            self.my_shows_assertions.verify_disk_meter_change(
                diskmeter_before, diskmeter_after, clientdiskconfig, delete_recording=True)
        else:
            pytest.fail("Diskmeter is unavailable on Myshows UI")
        disk_bef = self.my_shows_page.get_diskmeter_from_UI(self)
        self.my_shows_page.search_and_select_recently_deleted_folder(self)
        self.my_shows_page.recover_and_verify_storage_limit_overlay(self, verify_overlay=False)
        disk_aft = self.my_shows_page.get_diskmeter_from_UI(self)
        if disk_bef and disk_aft:
            self.my_shows_assertions.verify_disk_meter_change(
                diskmeter_before, diskmeter_after, clientdiskconfig, delete_recording=True)
        else:
            pytest.fail("Diskmeter is unavailable on Myshows UI. new one")

    @pytestrail.case("C12934358")
    @pytest.mark.ndvr
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("exit_overlay")
    def test_12934358_verify_long_key_press_info_season(self):
        """
        https://testrail.tivo.com//index.php?/cases/view/12934358
        """
        channel = self.service_api.get_recordable_non_movie_channel(episodic=True, filter_ndvr=False)
        if not channel:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        program = self.guide_page.create_one_pass_on_record_overlay(self)
        if program is None:
            pytest.skip("Program not found in My Shows skipping")
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_screen_title(self.my_shows_labels.LBL_MY_SHOWS)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.select_show(program)
        self.my_shows_assertions.verify_series_screen(self)
        self.screen.base.press_right()
        self.screen.base.press_enter()
        self.wtw_page.verify_screen_title(f"{program.upper()}")
        self.guide_page.move_or_select_view_all_in_biaxial_screen_strip(self, self.my_shows_labels.LBL_ALL_EPISODES,
                                                                        select_view_all=False)
        self.screen.base.press_right()
        self.screen.base.long_press_enter()
        self.wtw_page.verify_screen_title(f"ALL EPISODES: {program.upper()}")

    @pytest.mark.xray("FRUM-91278")
    @pytest.mark.test_stabilization
    def test_frum_91278_create_onepass_of_netflix_shows_and_launch_netflix_from_series_screen(self):
        self.api.create_multiple_onepass_ott(tsn=Settings.tsn)
        self.menu_page.go_to_one_pass_manager(self)
        self.watchvideo_page.press_ok_button()
        self.home_page.nav_to_all_episodes_listview()
        self.watchvideo_page.press_ok_button()
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)
        self.apps_and_games_assertions.verify_source_type_netflix_app(self.home_labels.LBL_NETFLIX_SOURCE_11)

    @pytest.mark.frumos_17
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.timeout)
    def test_FRUM34_record_4k_upcoming_shows(self):
        """
        https://jira.tivo.com/browse/FRUM-34
        """
        channel = self.service_api.get_4k_channel(recordable=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0])
        self.screen.base.press_right()
        self.guide_page.wait_for_screen_ready()
        self.guide_page.select_and_record_program(self)
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.guide_page.wait_for_screen_ready()
        program = self.guide_page.get_focussed_grid_item(self)
        self.home_page.back_to_home_short()
        self.menu_page.go_to_to_do_list(self)
        self.guide_assertions.verify_show_name_present(program)

    @pytest.mark.notapplicable(Settings.is_external_mso())
    @pytest.mark.notapplicable(Settings.is_dev_host(), "Devhost does not support restart")
    @pytest.mark.xray("FRUM-17940")
    @pytest.mark.usefixtures("cleanup_activate_ndvr_simple")
    def test_frum_17940_check_1st_filter_my_shows_ndvr_on_off(self, request):
        """
        No nDVR - Check All Shows filter is 1st in My Shows - enable nDVR - check Recordings filter is 1st.

        Xray:
            https://jira.tivo.com/browse/FRUM-17940
        """
        cancel_ndvr_simple(request)
        self.home_page.go_to_my_shows(self)
        self.menu_assertions.verify_menu_item_available(
            self.my_shows_page.get_expected_ordered_filter_list_in_my_shows(is_rec_enabled=False),
            expected=True, mode="equal")
        activate_ndvr_simple(request)
        self.home_page.go_to_my_shows(self)
        self.menu_assertions.verify_menu_item_available(
            self.my_shows_page.get_expected_ordered_filter_list_in_my_shows(is_rec_enabled=True),
            expected=True, mode="equal")

    @pytest.mark.notapplicable(Settings.is_external_mso())
    @pytest.mark.xray("FRUM-18001")
    @pytest.mark.may_also_like_ccu
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_frum_18001_check_if_recordings_1st_filter_series_screen(self, request):
        """
        Schedule recording - enter Series screen - check Recordings filter is 1st.

        Xray:
            https://jira.tivo.com/browse/FRUM-18001
        """
        channel_number = self.service_api.get_recordable_non_movie_channel()[0][0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_one_pass_on_record_overlay(self, record_everything=True)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)
        self.my_shows_page.select_show(program)
        self.my_shows_assertions.verify_series_screen_strip_order(mode="onepass", is_recording_required=True)

    @pytest.mark.watch_stickiness
    @pytest.mark.timeout(21600)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_11),
                               "The test is applicable only for Hydra v1.11 and higher")
    def test_389366315_verify_watch_stickiness_entry_point_my_shows(self):
        """
        :Description:
            Verify Watch Stickiness from following entry point.
        :testrail:
            Test case: https://testrail.tivo.com//index.php?/tests/view/389366315
        """
        title = self.my_shows_page.create_one_pass_and_wait_second_offer(self)
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_WATCH_LIST)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        focused_episode, next_episode = self.my_shows_page.get_cur_and_next_episodes_info()
        self.my_shows_page.select_and_wait_for_playback_play()
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_assertions.verify_currently_playing_episode(focused_episode['num'])
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete()
        self.my_shows_page.wait_for_screen_ready()
        self.screen.base.press_back()
        self.my_shows_page.select_keep_option(self)
        self.watchvideo_page.press_home_button()
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_show(title)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_SERIES_SCREEN, timeout=20000)
        self.my_shows_assertions.verify_focused_episode(next_episode['name'])

    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.wtw_openAPI_impacted
    def test_389366317_watch_stickiness_entry_ott(self):
        """
        389366317
        Verify Watch Stickiness in My Shows after an OTT offer.
        :return:
        """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self,
                                                                    feedName="/content/tvShowsOnNow")
        if not program:
            pytest.skip("No show in prediction without OTT")
        self.text_search_page.create_one_pass_for_show()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.home_labels.LBL_TV_SERIES)
        self.my_shows_page.select_show(program)
        self.home_page.nav_to_all_episodes_listview()
        self.home_page.press_right_button()
        for i in range(2):
            self.my_shows_page.screen.base.press_down()
        self.watchvideo_page.press_ok_button()
        self.home_page.back_to_home_short()
        self.my_shows.assertion.verify_my_shows_title()
        self.press_down_button()
        self.home_page.back_to_home_short()
        self.my_shows.assertion.verify_my_shows_title()

    @pytest.mark.test_stabilization
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_51350_verify_recordings_sort_by_name(self):
        """
        To verify recordings in myshows are sorted by name
        FRUM-51350
        :return:
        """
        recording = self.api.record_currently_airing_shows(number_of_shows=3)
        name_of_recordings = []
        for i in range(3):
            name_of_recordings.append(recording[i][0])
        if len(name_of_recordings) < 3:
            pytest.skip("Minimum 3 recordings are required")
        name_of_recordings = self.my_shows_page.sort_by_name(name_of_recordings)
        self.home_page.back_to_home_short()
        self.my_shows_page.my_shows_sort_by_name_or_date(self, "name")
        self.my_shows_assertions.verify_sorted_shows_by_name(self, name_of_recordings)

    @pytest.mark.test_stabilization
    @pytest.mark.cc_my_shows_acceptance
    def test_frum_73629_all_shows_filter_displayed(self):
        """
        Verify "All Shows" filter is displayed in My Shows screen.
        """
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_assertions.verify_filter_available_in_myshows_screen(self.my_shows_labels.LBL_ALL_SHOWS)

    @pytest.mark.test_stabilization
    @pytest.mark.cc_my_shows_acceptance
    def test_frum_73632_paused_filter_displayed(self):
        """
        Verify "Paused" filter is displayed in My Shows screen.
        """
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_assertions.verify_filter_available_in_myshows_screen(self.my_shows_labels.LBL_PAUSED)

    @pytest.mark.test_stabilization
    @pytest.mark.cc_my_shows_acceptance
    def test_frum_73633_tv_series_filter_displayed(self):
        """
        Verify "TV Series" filter is displayed in My Shows screen.
        """
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_assertions.verify_filter_available_in_myshows_screen(self.my_shows_labels.LBL_TV_SERIES)

    @pytest.mark.test_stabilization
    @pytest.mark.cc_my_shows_acceptance
    def test_73634_movies_filter_displayed(self):
        """
        Verify "Movies" filter is displayed in My Shows screen.
        """
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_assertions.verify_filter_available_in_myshows_screen(self.my_shows_labels.LBL_MOVIES)

    @pytest.mark.test_stabilization
    @pytest.mark.cc_my_shows_acceptance
    def test_frum_73635_sports_filter_displayed(self):
        """
        Verify "Sports" filter is displayed in My Shows screen.
        """
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_assertions.verify_filter_available_in_myshows_screen(self.my_shows_labels.LBL_SPORTS)

    @pytest.mark.test_stabilization
    @pytest.mark.cc_my_shows_acceptance
    def test_frum_73639_kids_filter_displayed(self):
        """
        Verify "Kids" filter is displayed in My Shows screen.
        """
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_assertions.verify_filter_available_in_myshows_screen(self.my_shows_labels.LBL_KIDS)

    @pytest.mark.test_stabilization
    @pytest.mark.cc_my_shows_acceptance
    def test_frum_73642_recordings_filter_displayed(self):
        """
        Verify "Recordings" filter is displayed in My Shows screen.
        """
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_assertions.verify_filter_available_in_myshows_screen(self.my_shows_labels.LBL_RECORDINGS)

    @pytest.mark.xray('FRUM-91568')
    @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_frum_91568_verify_recording_with_NO_padding(self):
        icm_channel, ccm_channel = self.service_api.get_CCM_or_ICM_channel(filter_channel=True, filter_ndvr=True)
        self.home_page.log.info(f"icm_channel: {icm_channel}, ccm_channel:{ccm_channel}")
        if len(icm_channel) == 0 and len(ccm_channel) == 0:
            pytest.skip("device does not have both ICM and CCM channels.")
        if icm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(icm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording()
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)
        if ccm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(ccm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording()
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)

    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.longrun
    @pytest.mark.cc_my_shows_acceptance
    @pytest.mark.usefixtures("enable_disable_stay_awake")
    @pytest.mark.usefixtures("decrease_screen_saver")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_frum_81938_verify_recordings_sort_by_date(self):
        """
        FRUM-81938
        To verify recordings in myshows are sorted by date
        :return:
        """
        recording = self.api.record_currently_airing_shows(number_of_shows=1)
        if len(recording) < 1:
            pytest.skip("Suitable recordings are not available")
        date = []
        date.append(recording[0][2])
        self.home_page.back_to_home_short()
        self.my_shows_page.play_recording_continously(self, recording[0][0], wait_time=24)
        channel = self.service_api.get_recordable_non_movie_channel(channel_count=4)
        if channel:
            self.home_page.go_to_guide(self)
            self.guide_assertions.verify_guide_screen(self)
            check = self.my_shows_page.compare_different_channel_for_recording(self, channel, recording)
            if check:
                self.guide_page.select_and_record_program(self)
        self.home_page.back_to_home_short()
        self.my_shows_page.my_shows_sort_by_name_or_date(self, "date")
        self.my_shows_assertions.verify_sorted_shows_by_date(self, date)

    @pytest.mark.usefixtures("setup_delete_book_marks")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.test_stabilization
    def test_frum_75168_my_shows_filter_stickiness_movies(self):
        """
        FRUM-78158
        To verify stickiness for myshows filters - MOVIES  used.
        :return:
        """
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.home_labels.LBL_MOVIES)
        self.screen.refresh()
        self.my_shows_assertions.verify_filter_has_focus(self.home_labels.LBL_MOVIES)
        self.home_page.back_to_home_short()
        self.home_page.go_to_my_shows(self)
        self.screen.refresh()
        self.my_shows_assertions.verify_filter_has_focus(self.home_labels.LBL_MOVIES)

    @pytest.mark.usefixtures("setup_delete_book_marks")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.test_stabilization
    def test_frum_75168_my_shows_filter_stickiness_kids(self):
        """
        FRUM-78158
        To verify stickiness for myshows filters - KIDS used.
        :return:
        """
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.home_labels.LBL_KIDS)
        self.screen.refresh()
        self.my_shows_assertions.verify_filter_has_focus(self.home_labels.LBL_KIDS)
        self.home_page.back_to_home_short()
        self.home_page.go_to_my_shows(self)
        self.screen.refresh()
        self.my_shows_assertions.verify_filter_has_focus(self.home_labels.LBL_KIDS)

    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.test_stabilization
    def test_frum_75171_special_group_stickiness(self):
        """
        FRUM-78158
        To verify stickiness for myshows special groups - Recently Deleted group used.
        :return:
        """
        self.text_search_page.go_to_search(self)
        program = self.my_shows_page.search_select_program_from_OTT(self, feedName="Movies", update_tivo_pt=True)
        if not program:
            status, result = self.vod_api.get_entitled_mapped_SVOD_movie()
            if result is None:
                pytest.skip("The content is not available on VOD catlog.")
            program = self.vod_page.extract_title(result)
            movieYear = result['offer'].movie_year
            self.text_search_page.search_and_select(program, program, year=movieYear)
        try:
            self.vod_assertions.verify_view_mode(self.my_shows_labels.LBL_ACTION_SCREEN_VIEW)
            self.text_search_page.bookmark_content()
        except Exception:
            pytest.skip("Unable to bookmark content")
        self.my_shows_page.go_to_recently_deleted_folder(self)
        self.home_page.back_to_home_short()
        self.home_page.go_to_my_shows(self)
        self.screen.refresh()
        self.my_shows_assertions.verify_filter_has_focus(self.my_shows_labels.LBL_RECENTLY_DELETED)

    @pytest.mark.test_stabilization
    def test_frum_75195_my_shows_filter_with_predetermined_sort_order(self):
        """
        Paused filter is not ordered by name or date, like other filters.
        Validation will be done by checking the info on sort order is not displayed when the filter is selected
        """
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_PAUSED)
        self.screen.refresh()
        item_sort_tiptext = self.screen.get_screen_dump_item("tiptext")
        self.my_shows_assertions.verify_substring_string_not_in_string("sorted by", str(item_sort_tiptext))

    @pytest.mark.xray('FRUM-91568')
    @pytest.mark.full_regression_tests
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_frum_91572_verify_recording_with_stop_recording_padding(self):
        myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
        self.home_page.log.info(f"myShowsItemSearch START: {myShowsItemSearch}")
        icm_channel, ccm_channel = self.service_api.get_CCM_or_ICM_channel(filter_channel=True, filter_ndvr=True)
        self.home_page.log.info(f"icm_channel: {icm_channel}, ccm_channel:{ccm_channel}")
        if len(icm_channel) == 0 and len(ccm_channel) == 0:
            pytest.skip("device does not have both ICM and CCM channels.")
        if icm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(icm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording(stop_rec=self.guide_labels.LBL_STOP_RECORDING_PADDING)
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)
        if ccm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(ccm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording(stop_rec=self.guide_labels.LBL_STOP_RECORDING_PADDING)
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)

    @pytest.mark.xray('FRUM-93222')
    @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_frum_93222_verify_recording_with_start_and_stop_recording_padding(self):
        icm_channel, ccm_channel = self.service_api.get_CCM_or_ICM_channel(filter_channel=True, filter_ndvr=True)
        self.home_page.log.info(f"icm_channel: {icm_channel}, ccm_channel:{ccm_channel}")
        if len(icm_channel) == 0 and len(ccm_channel) == 0:
            pytest.skip("device does not have both ICM and CCM channels.")
        start_rec = self.guide_labels.LBL_START_RECORDING_PADDING
        stop_rec = self.guide_labels.LBL_STOP_RECORDING_PADDING
        if icm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(icm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording(start_rec, stop_rec)
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)
        if ccm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(ccm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording(start_rec, stop_rec)
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)

    @pytest.mark.xray('FRUM-115689')
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_frum_115689_verify_recording_with_NO_padding_from_long_term_storage(self):
        icm_channel, ccm_channel = self.service_api.get_CCM_or_ICM_channel(filter_channel=True, filter_ndvr=True)
        self.home_page.log.info(f"icm_channel: {icm_channel}, ccm_channel:{ccm_channel}")
        if len(icm_channel) == 0 and len(ccm_channel) == 0:
            pytest.skip("device does not have both ICM and CCM channels.")
        if icm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(icm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording()
            self.guide_page.wait_for_24_hours()
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)
        if ccm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(ccm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording()
            self.guide_page.wait_for_24_hours()
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)

    @pytest.mark.xray('FRUM-115915')
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_frum_115915_verify_recording_with_start_and_stop_recording_padding_long_term_storage(self):
        icm_channel, ccm_channel = self.service_api.get_CCM_or_ICM_channel(filter_channel=True, filter_ndvr=True)
        self.home_page.log.info(f"icm_channel: {icm_channel}, ccm_channel:{ccm_channel}")
        if len(icm_channel) == 0 and len(ccm_channel) == 0:
            pytest.skip("device does not have both ICM and CCM channels.")
        start_rec = self.guide_labels.LBL_START_RECORDING_PADDING
        stop_rec = self.guide_labels.LBL_STOP_RECORDING_PADDING
        if icm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(icm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording(start_rec, stop_rec)
            self.guide_page.wait_for_24_hours()
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)
        if ccm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(ccm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording(start_rec, stop_rec)
            self.guide_page.wait_for_24_hours()
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)

    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-918")
    @pytest.mark.timeout(Settings.longrun_timeout)
    def test_frum918_record_playback_delete_movie(self):
        channel = self.service_api.get_random_recordable_movie_channel()
        if not channel:
            pytest.skip("Test requires recordable channels")
        channel_number = channel[0][0]
        movie = channel[0][2]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number, confirm=False)
        showtime = self.guide_page.get_program_start_and_end_time()
        self.guide_page.create_live_recording()
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self, self.my_shows_labels.LBL_MOVIES)
        self.my_shows_page.wait_for_record_completion(self, showtime)
        self.my_shows_page.select_show(movie)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_page.select_strip(self.watchvideo_labels.LBL_PLAY_OPTION)
        self.my_shows_page.wait_for_screen_ready()
        self.live_tv_assertions.verify_playback_play()
        self.my_shows_assertions.wait_and_verify_delete_recording_overlay()
        self.my_shows_page.select_delete_option(self)
        self.watchvideo_page.press_home_button()
        self.my_shows_page.navigate_from_home_screen_to_myshows_categories(self,
                                                                           self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_page.go_to_recently_deleted_folder(self)
        self.my_shows_assertions.verify_program_in_recently_deleted_folder(self, movie)

    @pytest.mark.xray('FRUM-128280')
    @pytest.mark.full_regression_tests
    @pytest.mark.usefixtures("setup_cleanup_myshows")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_128280_verify_recording_with_start_recording_padding(self):
        icm_channel, ccm_channel = self.service_api.get_CCM_or_ICM_channel(filter_channel=True, filter_ndvr=True)
        self.home_page.log.info(f"icm_channel: {icm_channel}, ccm_channel:{ccm_channel}")
        if len(icm_channel) == 0 and len(ccm_channel) == 0:
            pytest.skip("device does not have both ICM and CCM channels.")
        if icm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(icm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording(start_rec=self.guide_labels.LBL_START_RECORDING_PADDING)
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)
        if ccm_channel:
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(random.choice(ccm_channel))
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording(start_rec=self.guide_labels.LBL_START_RECORDING_PADDING)
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_assertions.verify_content_in_category(program)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)
            myShowsItemSearch = self.service_api.get_my_shows_item_search(Settings.tsn)
            self.my_shows_assertions.verify_padding_from_myShowItemSearch(self, program, myShowsItemSearch)

    @pytest.mark.xray("FRUM-113775")
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.parametrize("content_type", ["episode"])
    def test_113775_title_series_screen_upcoming_preview(self, content_type):
        """"
        Go to my shows and select TV SERIES and select the series that currently airing
        or has upcoming episode then go to upcoming and verify header title <series title>

        Xray:
             https://jira.xperi.com/browse/FRUM-113775
                """
        params = {"content_type": content_type, "with_title": True,
                  "find_appropriate": True, "stop_seek_at_first_match": True,
                  "screen_type": "seriesScreenUpcoming", "is_live": True}
        offer = self.guide_page.find_channel_and_highlight_program_in_guide(self, is_olg=False, **params)[0][4]
        self.guide_page.select_and_record_program(self)
        program = self.guide_page.get_live_program_name(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_series_screen_menu_list_upcoming(program)
        self.my_shows_page.select_show(program)
        self.my_shows_assertions.verify_my_show_upcoming_title(offer.title, "seriesScreenUpcoming")

    @pytest.mark.frumos_19
    @pytest.mark.acceptance_4k
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    def test_FRUM_5_record_4k_content_from_Guide(self):
        channel = self.service_api.get_4k_channel(recordable=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0])
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_assertions.verify_content_in_category(program)

    @pytest.mark.frumos_19
    @pytest.mark.cloud_core_watch_Recording
    @pytest.mark.infobanner
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guide_rows is supported since Hydra v1.18")
    def test_frum_120263_stop_recording_from_info_banner(self,
                                                         get_and_restore_tcdui_test_conf,  # noqa: F811
                                                         increase_timeout_of_widgets_in_watch_video_screen,  # noqa: F811
                                                         ):
        """
        Verify Stop recording action during recording playback from Full Info Banner action strip
        """
        # schedule recording
        channels = self.service_api.get_random_recordable_channel(filter_channel=True)
        if not channels:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0][0])
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        # start playing recording playback
        self.guide_page.start_recording_playback_from_record_overlay(self)
        # Select 'Stop Recording' action in Full Info Banner
        self.watchvideo_page.stop_recording_from_info_banner_action_list(self)
        # Verify full video screen is closed and user is in previous screen
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        # Verify liveTV is playing in Watch TV
        self.home_page.go_to_watch_tv(self)
        self.watchvideo_assertions.verify_livetv_mode()

    @pytest.mark.frumos_19
    @pytest.mark.cloud_core_watch_Recording
    @pytest.mark.infobanner
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18),
                               "/v1/guide_rows is supported since Hydra v1.18")
    def test_frum_120264_create_one_pass_from_info_banner(self,
                                                          get_and_restore_tcdui_test_conf,  # noqa: F811
                                                          increase_timeout_of_widgets_in_watch_video_screen,  # noqa: F811
                                                          ):
        """
        Verify Create One Pass Action during recording playback from Full Info Banner action strip
        """
        channels = self.service_api.get_random_recordable_channel(filter_channel=True)
        if not channels:
            pytest.skip("Test requires recordable channels")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0][0])
        self.guide_page.create_live_recording()
        self.guide_page.verify_whisper_shown(self.guide_labels.LBL_RECORD_SCHEDULED)
        # Start playing recording playback
        self.guide_page.start_recording_playback_from_record_overlay(self)
        # Select "Create One Pass" action in Full Info Banner
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.press_down_button()
        self.screen.get_json()
        show = self.home_page.create_one_pass(self)
        show_name = self.my_shows_page.cleanup_text_char(show)
        # Verify OnePass is added in MY SHOWS
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.home_assertions.verify_show_in_my_shows(self, show_name)
        self.menu_page.go_to_one_pass_manager(self)
        self.home_assertions.verify_show_in_one_pass_manager(self, show_name)
