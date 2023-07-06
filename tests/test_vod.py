"""
Created on Aug 1, 2017

@author: sghosh
"""

import os
import random
import time
from datetime import datetime

import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.VOD.conftest import *
from set_top_box.client_api.Menu.conftest import setup_cleanup_parental_and_purchase_controls,\
    setup_enable_video_window, disable_parental_controls, setup_cleanup_remove_playback_source, \
    setup_disable_closed_captioning, setup_enable_closed_captioning
from set_top_box.client_api.my_shows.conftest import setup_delete_book_marks
from set_top_box.client_api.guide.conftest import setup_cleanup_list_favorite_channels_in_guide  # noqa: F401
from set_top_box.conf_constants import FeAlacarteFeatureList, FeAlacartePackageTypeList, HydraBranches, \
    BailButtonList, LongevityConstants, NotificationSendReqTypes, RemoteCommands
from set_top_box.client_api.home.conftest import cleanup_package_names_native, preserve_initial_package_state, \
    remove_packages_if_present_before_test
from set_top_box.client_api.account_locked.conftest import cleanup_enabling_internet, cleanup_re_activate_and_sign_in
from pytest_testrail.plugin import pytestrail
from tools.logger.logger import Logger


@pytest.mark.vod
@pytest.mark.usefixtures("setup_vod")
# Removing the check due to service timeout CA-10523
# @pytest.mark.usefixtures("is_service_vod_alive")
class TestVOD(object):
    __log = Logger(__name__)

    @pytest.mark.notapplicable(True)
    @pytest.mark.demo
    @pytest.mark.timeout(Settings.timeout)
    def test_free_offer(self):
        """
        TC number is required
        """
        requests = {'request1': {"offer": {"entitlement": "free"}}}

        status, result = self.vod_api._searchVODMixes(requests)
        ep = self.vod_page.extract_entryPoint(result)
        self.vod_page.go_to_vod(self)
        self.vod_page.navigate_to_entryPoint(self, ep)

    # or SANITY?
    @pytestrail.case('C11123935')
    @pytest.mark.bat
    @pytest.mark.devhost
    # @pytest.mark.test_stabilization
    @pytest.mark.bvt
    @pytest.mark.cloud_core_vod_socu
    @pytest.mark.timeout(Settings.timeout)
    def test_310110_watch_vod(self):
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytestrail.case('C11123926')
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-250")
    # @pytest.mark.test_stabilization
    @pytest.mark.bvt
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_disable_closed_captioning")
    def test_309964_closed_captioning_on(self):
        """
        309964
        Verify closed captioning is working while asset is playing.
        :return:
        """
        status, result = self.vod_api.getOffer_free_with_cc_available()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.vod_page.set_closed_captioning_on(self.vod_labels.LBL_CLOSED_CAPTIONING_ON)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        if Settings.is_unmanaged():
            self.screen.base.press_down()
        else:
            self.screen.base.press_info()
        self.screen.refresh()
        self.vod_assertions.verify_closed_captioning(self.vod_labels.LBL_CLOSED_CAPTIONING_OFF)

    @pytestrail.case('C11123925')
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-249")
    @pytest.mark.msofocused
    # @pytest.mark.test_stabilization
    @pytest.mark.bvt
    @pytest.mark.cloud_core_vod_socu
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.skipif(Settings.is_cc5(), reason="Purchase control is not applicable for cableco5 mso")
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("mibox" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("appletv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("rcn" in Settings.mso.lower(), reason="Case is skipped as there are no TVOD assets.")
    @pytest.mark.skipif("midco" in Settings.mso.lower(), reason="Midco is not going to provide purchase credit")
    @pytest.mark.skipif(not Settings.is_purchase_controls_enabled(),
                        reason="Purchase Controls is not available/enabled on the device")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_309958_rentandwatch_tvod(self):
        self.menu_page.turnonpcsettings(self, parentalon="on", purchaseon="on")
        status, result = self.vod_api.getOffer_tvod_notEntitledRentable()
        if result is None:
            pytest.skip("TVOD - unentitled assets are not available")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_rented_content(self, result, Settings.platform, purchaseon="on")
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.guide_assertions.verify_live_playback()

    @pytestrail.case('C11123936')
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("mibox" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("appletv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    def test_310111_rented_tvod(self):
        status, result = self.vod_api.getOffer_tvod_entitledRented()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytestrail.case('C11123937')
    @pytest.mark.bat
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("mibox" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("appletv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_310112_confirmrentandwatch_tvod(self):
        status, result = self.vod_api.getOffer_tvod_notEntitledRentable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_confirmrented_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytestrail.case('C11123930')
    @pytest.mark.bat
    @pytest.mark.msofocused
    @pytest.mark.search_ccu
    @pytest.mark.xray("FRUM-255")
    @pytest.mark.timeout(Settings.timeout)
    def test_310004_search_VOD_program(self):
        """
        310004
        VOD - Search - Program Screen for program available from VOD
        :return:
        """
        status, result = self.vod_api.getOffer_playable_rating_movie()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        ep = self.vod_page.extract_title(result)
        movieYear = None
        if result['offer'].movie_year:
            movieYear = result['offer'].movie_year
        self.text_search_page.go_to_search(self)
        self.text_search_page.wait_for_screen_ready()
        self.text_search_assertions.verify_search_screen_title()
        if movieYear:
            self.text_search_page.search_and_select(ep, ep, year=movieYear)
        else:
            self.text_search_page.search_and_select(ep, ep)
        result = self.vod_labels.LBL_ON_DEMAND not in self.vod_page.menu_list() or \
            self.vod_labels.LBL_ON_DEMAND not in self.vod_page.strip_list()
        if not result:
            raise AssertionError("{} not found in menus or strips:{}, {}".format(self.vod_labels.LBL_ON_DEMAND,
                                                                                 self.vod_page.menu_list(),
                                                                                 self.vod_page.strip_list()))

    @pytestrail.case('C11123932')
    @pytest.mark.bat
    @pytest.mark.timeout(Settings.timeout)
    def test_310023_vod_upsell_overlay(self):
        '''
        310023
        Watch now - Unsubscribed SVOD
        :return:
        '''
        status, result = self.vod_api.getOffer_svod_notEntitledSubscribable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_assertions.verify_svod_upsell_overlay(self, result)

    # @pytestrail.case('C11123933')
    @pytest.mark.xray("FRUM-258")
    @pytest.mark.msofocused
    @pytest.mark.bat
    @pytest.mark.cloud_core_vod_socu
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_310024_svod_playback(self):
        '''
        310024
        Watch now - Subscribed SVOD
        :return:
        '''
        status, result = self.vod_api.getOffer_svod_entitledSubscribed(600, 7200, count=1000)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)

    @pytestrail.case('C11123931')
    @pytest.mark.bat
    @pytest.mark.platform_cert_smoke_test
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_310011_svod_screen(self):
        '''
        310011
        VOD Program Screens - Screen Display for Entitled SVOD Episode
        :return:
        '''
        status, result = self.vod_api.getOffer_svod_entitledSubscribed(count=1000)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        title = self.vod_page.extract_title(result)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result, through_clientui=False)
        self.vod_page.wait_for_screen_ready()
        self.vod_page.navigate_to_action_screen_from_series_screen()
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_ACTIONS_SCREEN)
        self.vod_assertions.verify_episode_screen(self, title)

    @pytestrail.case('C11123939')
    @pytest.mark.bat
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.skipif("devhost" in Settings.driver_type.lower(), reason="Device do not have VOD button on the remote")
    @pytest.mark.skipif("nvidia" in Settings.driver_type.lower(), reason="Device do not have VOD button on the remote")
    def test_310675_vod_from_live(self):
        """
        310675
        Verify VOD access holds good whilst being in the LIVE TV screen
            - Takes only self as argument
            - Test Case holds good only for managed devices with VOD button on the remote
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                             transportType="stream")[0][0]
        self.home_page.goto_live_tv(channel)
        self.watchvideo_assertions.verify_playback_play()
        self.vod_page.get_vod_press()
        self.home_assertions.verify_screen_title(self.guide_labels.LBL_ON_DEMAND_SCREEN_TITLE)

    @pytestrail.case('C11123929')
    @pytest.mark.bat
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    def test_310003_onepass_from_svod(self):
        """
        310003
        Verify the onepass activation from a subscribed SVOD screen
            - Takes only self as argument
        :return:
        """
        status, results = self.vod_api.getOffer_mapped_svod_entitledSubscribed_series()
        if results is None:
            pytest.skip("Test requires mapped offer to validate onepass")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.check_onepass_SVOD(self)

    @pytestrail.case('C11123928')
    @pytest.mark.bat
    # @pytest.mark.test_stabilization
    @pytest.mark.bvt
    @pytest.mark.timeout(Settings.timeout)
    def test_309997_resume_playing(self):
        """
        309997
        Verify to check video is playing after clicking Resume Playing.
        :return:
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration(600, 7200)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_page.wait(30)
        self.screen.base.press_back()
        self.vod_page.validate_resume_playing(self, result)
        self.vod_assertions.verify_vod_playback(self)

    @pytestrail.case('C11123927')
    @pytest.mark.xray("FRUM-251")
    @pytest.mark.msofocused
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.cloud_core_vod_socu
    @pytest.mark.parental_control
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_309977_parental_controls(self):
        """
        Verify that Parental Controls prompts a PIN challenge when watching an asset that exceeds the Rating Limit
        and that entering the correct Parental Controls PIN begins offer playback while Purchase Controls OFF.

        Testrail:
            https://testrail.corporate.local/index.php?/tests/view/72255181

        Testopia:
            https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=309977
        """
        asset_availability = "tvod"
        is_pc_pin = True
        if Settings.is_dev_host():
            # Check to validate highest allowed rating with allow all value till we get correct values from service API
            self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_G_HIGHEST_ALLOWED_MOVIE_RATING,
                                                rated_tv_show=self.menu_labels.LBL_ALLOW_ALL_HIGHEST_ALLOWED_RATING)
        else:
            self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_G_HIGHEST_ALLOWED_MOVIE_RATING)
        self.home_page.back_to_home_short()
        status, result = self.vod_api.getoffer_rented_movie_rating_exceed_G()
        if result is None:
            status, result = self.vod_api.getoffer_rentable_movie_rating_exceed_G()
            if result is None:
                pytest.skip("The content is not available on VOD catlog.")
            self.vod_page.goto_vodoffer_program_screen(self, result)
            # Playing not rented asset
            self.vod_page.play_asset_from_watch_now_strip_any_vod_status(self, availability_type=asset_availability,
                                                                         is_rent_over_available=True,
                                                                         is_pc_pin=is_pc_pin, is_purchase_pin=False)
            is_pc_pin = False  # since the pin was entered once at this point
            self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_page.goto_vodoffer_program_screen(self, result)
        # Playing already rented asset
        self.vod_page.play_asset_from_watch_now_strip_any_vod_status(self, availability_type=asset_availability,
                                                                     is_rent_over_available=False,
                                                                     is_pc_pin=is_pc_pin, is_purchase_pin=False)
        self.vod_page.select_start_over_or_resume(self.vod_labels.LBL_START_OVER_FROM_BEGINNING)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytestrail.case('C11123941')
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.notapplicable(Settings.is_dev_host())
    @pytest.mark.timeout(Settings.timeout)
    def test_314075_trick_play_enabled(self):
        """
        314075
        To verify the possible TrickPlay modes in watching a VOD program when TrickPlay is allowed.
        :return:
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(3600, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.watchvideo_page.skip_hdmi_connection_error()
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_page.pause(2)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_forward(value, value1, 3)
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX1)
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_page.press_ok()  # FF2 mode
        self.vod_page.pause(2)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_forward(value, value1, 18)
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX2)
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_page.press_ok()  # FF2 mode
        self.vod_page.press_ok()  # FF3 mode
        self.vod_page.pause(2)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_forward(value, value1, 60)
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX3)
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_page.wait(900)  # wait is needed to build cache for REW modes verification
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_reverse()
        self.vod_page.press_ok()  # REW1 mode
        self.vod_page.press_ok()  # REW2 mode
        self.vod_page.press_ok()  # REW3 mode
        self.vod_page.pause(2)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_backward(value, value1, 60)
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX3)
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_page.press_ok()  # FF2 mode
        self.vod_page.press_ok()  # FF3 mode
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_reverse()
        self.vod_page.press_ok()  # REW1 mode
        self.vod_page.press_ok()  # REW2 mode
        self.vod_page.pause(2)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_backward(value, value1, 18)
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX2)
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_page.press_ok()  # FF2 mode
        self.vod_page.press_ok()  # FF3 mode
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_reverse()
        self.vod_page.press_ok()  # REW1 mode
        self.vod_page.pause(4)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_backward(value, value1, 3)
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX1)
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_page.press_play_pause_button()
        self.vod_assertions.verify_pause_mode(self.vod_labels.LBL_PAUSE_ICON)

    @pytestrail.case('C11123934')
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-259")
    @pytest.mark.msofocused
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_310058_my_rentals_on_demand_content(self):
        '''
        310058
        My Rentals - My On Demand Content
        '''
        status, results = self.vod_api.get_offer_playable()
        if results is None:
            pytest.skip("The content is not available on VOD catlog.")
        title = self.vod_page.extract_title(results)
        # collectionId = self.vod_page.extract_collectionId(results)
        # content_id = self.vod_page.extract_contentId(results)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results, through_clientui=False)
        self.vod_page.play_any_playable_vod_content(self, results)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_page.wait(30)
        self.vod_page.go_to_vod(self)
        self.core_api_base.nav_to_menu(self.vod_labels.LBL_MY_RENTALS)
        self.vod_page.wait_for_screen_ready()
        self.vod_page.wait(2)
        self.vod_assertions.verify_my_rentals(self, title, self.vod_labels.LBL_MY_RENTALS)

    # @pytestrail.case('C11123944')
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-270")
    @pytest.mark.bat
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures('disable_parental_controls')
    def test_326769_my_adult_rentals(self):
        '''
        326769
        My Rentals - My Adult On Demand List - Entry
        '''
        status, results = self.vod_api.get_adult_offer_playable()
        if results is None:
            pytest.skip("The adult content is not available on VOD catlog.")
        mixID = self.vod_page.extract_mixID(results)
        title = self.vod_page.extract_title(results)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.play_any_playable_vod_content(self, results)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_page.wait(100)  # Play content for sometime to list in my adult rentals
        self.vod_page.go_to_vod(self)
        self.vod_page.wait_for_screen_ready()
        self.vod_page.navigate_to_entryPoint(self, f'1/{self.vod_labels.LBL_MY_ADULT_RENTALS}', mixID)
        self.vod_page.wait_for_screen_ready()
        self.vod_page.wait(2)
        self.vod_assertions.verify_my_rentals(self, title, self.vod_labels.LBL_MY_ADULT_RENTALS)

    @pytestrail.case("C12792173")
    @pytest.mark.msofocused
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-383")
    @pytest.mark.textsearch
    @pytest.mark.timeout(Settings.timeout)
    def test_330453_search_adult_vod_content(self):
        '''
        330453
        Text Search - Adult Content is not shown
        '''
        status, results = self.vod_api.getOffer_adult_notEntitledRentable()
        if results is None:
            pytest.skip("The adult content is not available on VOD catlog.")
        self.vod_page.extract_entryPoint(results)
        title = self.vod_page.extract_title(results)
        self.text_search_page.go_to_search(self)
        try:
            self.text_search_page.search_and_select(title, title)
            self.program_options_page.run_from_on_demand()
        except Exception:
            pass
        else:
            raise AssertionError("Adult show was in search")

    @pytestrail.case('C11123943')
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-269")
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_ruby() or Settings.is_jade(), reason="Netflix is not supported")
    def test_323203_select_vod_jump_channel(self):
        """
        323203 Jump Channel - Grid Guide - Select Jump Channel - Launch VOD app

        TODO: As get_jump_channels api is not implemented VOD filter. Need to modify this api to filter vod.

        Test case is trying to launch Netflix on ruby and jade which does not supports Netflix app. Hence
        notapplicable marker is introduced.
        """
        jmp_ch = self.api.get_jump_channels(filter="VOD")
        channel_number = self.guide_page.check_channel_availability(self, jmp_ch, self.vod_labels.LBL_ALL_VOD_NAMES_FOR_MSO)
        if not channel_number:
            pytest.skip("No jump channel number found")
        channel_num = channel_number[0]
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel_num, confirm=False)
        self.guide_page.wait_for_screen_ready()
        self.guide_assertions.verify_show_title_available()
        if not Settings.is_apple_tv():
            self.screen.base.press_enter()
            self.vod_page.wait_for_screen_ready()
        self.guide_assertions.verify_jump_channel_launch()

    @pytestrail.case('C11123938')
    @pytest.mark.bat
    @pytest.mark.xray("FRUM-263")
    @pytest.mark.msofocused
    @pytest.mark.cloud_core_vod_socu
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("mibox" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("appletv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    def test_310115_tvod_preview(self):
        status, result = self.vod_api.getOffer_tvod_withPreview()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_tvod_preview_content(self)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytestrail.case('C11123940')
    @pytest.mark.bat
    # @pytest.mark.test_stabilization
    @pytest.mark.bvt
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_delete_book_marks")
    def test_312397_bookmark_subscribed_svod_movie(self):
        """
            312397 OnePass - Bookmark Subscribed SVOD Movie
        """
        status, result = self.vod_api.get_entitled_mapped_SVOD_movie()
        if result is None:
            pytest.skip("Test requires mapped offer to validate bookmark")
        title = self.vod_page.extract_title(result)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN)
        self.core_api_base.select_menu_by_substring(self.my_shows_labels.LBL_BOOKMARK)
        self.screen.refresh()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_MOVIES)
        self.my_shows_assertions.verify_content_in_category(title)
        self.my_shows_page.select_show(title)
        self.vod_page.play_asset_from_watch_now_strip_any_vod_status(self,
                                                                     availability_type="svod",
                                                                     is_rent_over_available=False,
                                                                     is_pc_pin=False,
                                                                     is_purchase_pin=False)
        self.vod_page.select_start_over_or_resume(self.vod_labels.LBL_START_OVER_FROM_BEGINNING)
        self.vod_assertions.verify_video_streaming()

    @pytestrail.case('C11123945')
    @pytest.mark.bat
    @pytest.mark.timeout(Settings.timeout)
    def test_342906_vod_playback_encrypted_offer(self):
        status, result = self.vod_api.getOffer_playable_rating_movie()
        if not status:
            pytest.skip("Test requires vod offer")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_vod_playback(self)

    @pytestrail.case('C11123942')
    # @pytest.mark.bat
    @pytest.mark.xray("FRUM-268")
    @pytest.mark.infobanner
    @pytest.mark.notapplicable(Settings.is_dev_host())
    @pytest.mark.timeout(Settings.timeout)
    def test_318398_vod_trickplay_ff_restricted(self):
        """
        318398
        Verify VOD TrickPlay restrictions during playback function correctly for assets that have only
        Fast Forwarding disabled (i.e. only FF is restricted, then Pause and REW function normally).
        :return:
        """
        status, result = self.vod_api.getOffer_vod_ff_disabled()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_page.press_forward()
        self.watchvideo_assertions.verify_trickplay_button_status(self.liveTv_labels.LBL_FORWARD_BUTTON, disabled=True)
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_page.wait(450)  # wait is needed to build cache for REW modes verification
        self.vod_page.press_play_pause_button()
        self.vod_assertions.verify_pause_mode(self.vod_labels.LBL_PAUSE_ICON)
        self.vod_page.press_play()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_page.press_reverse()
        self.vod_page.press_ok()
        self.vod_page.press_ok()
        self.vod_page.press_ok()
        # next verification should be modified with the examiner
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX3)

    @pytestrail.case("C12792175")
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_309966_watch_streaming_video_GUIDE_button(self):
        """
        318398
         Verify a VOD offer continues to play in the video window when pressing GUIDE while watching the VOD offer.
        :return:
        """
        status, result = self.vod_api.get_entitled_HD_asset()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_page.screen.base.press_guide()
        self.vod_page.wait_for_screen_ready()
        self.vod_assertions.verify_view_mode(self.guide_labels.LBL_VIEW_MODE)

    @pytestrail.case("C12792188")
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_339544_vod_browse_program_screen_info_strip(self):
        """
        339544
          To verify that  'INFO Strip' is displayed in VOD Program screen
        :return:
        """
        status, result = self.vod_api.get_hd_vod_asset()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.navigate_to_action_screen_from_series_screen()
        self.vod_assertions.select_more_info_and_verify(self)

    @pytestrail.case("C12792177")
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_delete_book_marks")
    def test_310008_vod_screen_validation(self):
        """
            310008 Vod action screen validation
        """
        status, result = self.vod_api.getOffer_playable_rating_movie()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        title = self.vod_page.extract_title(result)
        movieYear = self.vod_page.extract_movie_year(result)
        self.vod_page.verify_vod_movie_screen(self, title, movieYear)

    @pytestrail.case("C12792180")
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_330327_vod_collapsed_offers_display(self):
        """
        Verify the display of SD/HD collapsed offers when presented on VOD Browse Gallery Screen.
        """
        status, result = self.vod_api.get_collapsible_asset()
        ep = self.vod_page.extract_entryPoint(result)
        mixID = self.vod_page.extract_mixID(result)
        contentID = self.vod_page.extract_contentId(result)
        collectionID = self.vod_page.extract_collectionId(result)
        title = self.vod_page.extract_title(result)
        self.vod_page.go_to_vod(self)
        self.vod_page.navigate_to_entryPoint(self, ep, mixID)
        self.vod_page.select_vod(self, collectionID, contentID, title)
        self.vod_page.wait_for_screen_ready()
        self.vod_assertions.verify_collapsed_offers(title)

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685248")
    @pytest.mark.e2e
    @pytest.mark.vod
    @pytest.mark.notapplicable(Settings.is_devhost())
    # @pytest.mark.bvt
    @pytest.mark.timeout(Settings.timeout)
    def test_69584590_vod_playback_continue_to_play_after_pressing_watch_video_button(self):
        """
            Verify that after pressing "Watch Video" button VOD playback continue to play

            Testrail case ID: https://testrail.corporate.local/index.php?/tests/view/69584590
        """
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_page.watch_video_for(20)
        self.vod_assertions.verify_vod_playback(self)
        self.home_page.back_to_home_short()
        self.home_assertions.verify_menu_item_available(self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        self.home_page.select_strip(self.home_labels.LBL_WATCHVIDEO_SHORTCUT)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytestrail.case("C12792182")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.bvt
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif("rcn" in Settings.mso.lower(), reason="Case is skipped as there are no TVOD assets.")
    @pytest.mark.notapplicable(Settings.is_managed())
    def test_330563_tvod_rental_now_allowed(self):
        status, result = self.vod_api.getOffer_tvod_notEntitledRentable()
        if result is None:
            pytest.skip("TVOD - unentitled assets are not available")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_rented_content(self, result, Settings.platform, purchaseon="off")

    @pytestrail.case("C12792171")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.bvt
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_333988_playbutton_pinchallenge(self):
        status, result = self.vod_api.getOffer_playable_adult_rating_movie()
        ep = self.vod_page.extract_entryPoint(result)
        mixID = self.vod_page.extract_mixID(result)
        contentID = self.vod_page.extract_contentId(result)
        collectionID = self.vod_page.extract_collectionId(result)
        title = self.vod_page.extract_title(result)
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.vod_page.go_to_vod(self)
        self.vod_page.navigate_to_entryPoint(self, ep, mixID)
        self.vod_page.select_vod(self, collectionID, contentID, title)
        self.screen.base.press_back(time=5000)
        self.screen.base.press_playpause()
        self.vod_page.validate_enterpin_overlay_streamvod(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytestrail.case("C12792172")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.bvt
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_333987_incorrect_pinentry_and_test_333986_rating_limit_exceeded(self):
        status, result = self.vod_api.getOffer_playable_rating_movie()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                            unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.validate_incorrectpin_overlay(self, result)
        self.vod_page.validate_enterpin_overlay_streamvod(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytestrail.case("C12792170")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.bvt
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_333992_okbutton_adultcontent_pinchallenge(self):
        status, result = self.vod_api.getOffer_playable_adult_rating_movie()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.wait_for_screen_ready()
        self.vod_page.press_ok()
        self.vod_page.validate_enterpin_overlay_streamvod(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytestrail.case("C12792179")
    @pytest.mark.p1_regression
    @pytest.mark.bvt
    @pytest.mark.timeout(Settings.timeout)
    def test_325550_vod_episode_list_view(self):
        status, result = self.vod_api.getOffer_svod_entitledSubscribed_series()
        ep = self.vod_page.extract_entryPoint(result)
        mixID = self.vod_page.extract_mixID(result)
        contentID = self.vod_page.extract_contentId(result)
        collectionID = self.vod_page.extract_collectionId(result)
        title = self.vod_page.extract_title(result)
        self.vod_page.go_to_vod(self)
        self.vod_page.navigate_to_entryPoint(self, ep, mixID)
        self.vod_page.select_vod(self, collectionID, contentID, title)
        if self.vod_page.launch_episode_list_view(self, self.vod_labels.LBL_ON_DEMAND_EPISODES):
            pytest.skip("Selected vod series does not have multiple episodes")
        self.vod_assertions.verify_episode_list_view(self)

    @pytestrail.case("C12792178")
    @pytest.mark.p1_regression
    @pytest.mark.bvt
    def test_313490_ipvod_fastforwarding1(self):
        status, result = self.vod_api.getOffer_free_with_cc_available()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.guide_page.build_cache(600)
        self.screen.base.press_fast_forward()
        self.guide_assertions.verify_fast_forward(1)

    @pytestrail.case("C12792184")
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_309961_vod_browse_gallery_screen_validation(self):
        """
        TC 309961 - Verify that the VOD Browse Gallery screen displays when selecting a View All tile on VOD Browse Main Screen
        :return:
        """
        requests = {'request1': {"offer": {"packageType": "zvod"}}, 'request2': {"offer": {"packageType": "fvod"}}}
        status, result = self.vod_api._searchVODMixes(requests)
        ep = self.vod_page.extract_entryPoint(result)
        mixID = self.vod_page.extract_mixID(result)
        contentID = self.vod_page.extract_contentId(result)
        collectionID = self.vod_page.extract_collectionId(result)
        title = self.vod_page.extract_title(result)
        self.vod_page.go_to_vod(self)
        self.vod_page.navigate_to_entryPoint(self, ep, mixID)
        self.vod_page.select_vod(self, collectionID, contentID, title)
        self.screen.base.press_back()
        self.vod_assertions.verify_vod_browse_gallery_screen()

    @pytestrail.case("C12792176")
    @pytest.mark.msofocused
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-385")
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_310006_vod_browse_biaxial_screen(self):
        self.vod_page.go_to_vod(self)
        self.vod_assertions.verify_vod_main_screen(self)

    # @pytestrail.case("C12792183")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-62300")
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.branding_check
    # @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_330538_vod_browse_program_screen_primary_branding_logo(self):
        """
               Navigate to program screen and verify the branding logo.
        """
        status, result = self.vod_api.getOffer_svod_entitledSubscribed()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.wait_for_screen_ready()
        self.vod_page.navigate_to_action_screen_from_series_screen()
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_ACTIONS_SCREEN)
        self.vod_assertions.verify_primary_branding_icon()

    # @pytest.mark.test_stabilization
    # @pytest.mark.p1_regression
    @pytest.mark.longrun
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("mibox" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.skipif("appletv" in Settings.platform.lower(), reason="Device do not support Transactional VOD")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_340275_graceful_end_overlay(self):
        '''
        TC: 340275: verifing Graceful End overlay
        :return:
        '''
        status, result = self.vod_api.get_asset_with_rental_duration(3590, 3610)
        if result is None:
            pytest.skip("VOD asset with shorter duration time is not found")
        # ep = self.vod_page.extract_entryPoint(result)
        # mixID = self.vod_page.extract_mixID(result)
        contentID = self.vod_page.extract_contentId(result)
        collectionID = self.vod_page.extract_collectionId(result)
        title = self.vod_page.extract_title(result)
        playbackDuration = self.vod_page.extract_playback_duration(result)
        rentalDuration = self.vod_page.extract_rental_duration(result)
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.select_vod(self, collectionID, contentID, title)
        self.vod_page.play_confirmrented_content(self, result)
        self.guide_assertions.verify_live_playback()
        self.home_page.go_to_guide(self)
        self.guide_page.get_live_program_name(self)
        self.guide_page.select_and_watch_program(self, socu=False)
        self.guide_assertions.verify_live_playback()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.select_vod(self, collectionID, contentID, title)
        self.vod_page.wait_to_launch_graceful_overlay(self, playbackDuration, rentalDuration, result)
        self.vod_assertions.assert_graceful_end_overlay(self)

    # @pytest.mark.test_stabilization
    # @pytest.mark.p1_regression
    @pytest.mark.GA
    @pytest.mark.timeout(Settings.timeout)
    def test_354562_jump_forward_by_GA(self):
        """
        354562
        To verify when watching a VOD offer a user can jump to a specific timestamp via voice
        :return:
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(900, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.home_page.jump_forward_by_minutes_using_GA(5)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.validate_jump_forward(value, value1, 300)

    @pytestrail.case("C12792187")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.skipif(Settings.hydra_branch() <= Settings.hydra_branch(HydraBranches.STREAMER_1_7), reason="NA for < 1.7")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_10195352_verify_favorite_channels_panel_watch_vod(self):
        """
        :Description:
            To verify Favorite Cahnnels panel watching VOD
        :testrail:
                Test case: https://testrail.tivo.com//index.php?/cases/view/10195352
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        status, result = self.vod_api.getOffer_fvod()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.vod_page.open_favorite_panel()
        self.vod_assertions.verify_favorite_channels_panel_shown()

    # @pytest.mark.test_stabilization
    @pytestrail.case("C11685251")
    @pytest.mark.e2e
    @pytest.mark.vod
    @pytest.mark.notapplicable(Settings.is_devhost())
    @pytest.mark.timeout(Settings.timeout)
    def test_74131992_advance_blocked_when_ff_restricted(self):
        """
        Verify Advance is blocked when Fast Forward is restricted
        """
        status, result = self.vod_api.getOffer_vod_ff_disabled()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.watchvideo_page.pause(4)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.press_advance_button()
        self.vod_assertions.verify_advance_blocked_when_ff_restricted()

    @pytestrail.case("C12792185")
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-134")
    @pytest.mark.timeout(Settings.timeout)
    def test_10465825_verify_scroll_back_watch_vod(self):
        """
        To verify scroll back functionality watching VOD

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/10465825
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(600, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        #  precondition steps
        self.vod_page.press_right_button()
        self.vod_page.press_ok()
        self.vod_page.press_right_button()
        self.vod_page.press_ok()
        self.vod_page.press_left_button()
        self.vod_page.press_left_button()
        self.vod_page.press_ok()
        #  end of precondition
        self.vod_page.press_left_button()
        self.vod_page.press_ok()  # Press 'Rewind' button
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX1)
        self.watchvideo_page.press_right_button()
        self.vod_page.press_ok()  # Press 'Play' button
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_left_button()
        self.vod_page.press_left_button()
        self.vod_page.press_ok()
        self.vod_page.press_ok()  # Press '-8s' button
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_8seconds_backward(value, value1)
        self.vod_page.pause(5)  # wait for trickplay menu dismiss
        self.vod_page.press_ok()
        self.vod_page.press_left_button()
        self.vod_page.press_left_button()
        self.vod_page.press_left_button()
        self.vod_page.press_ok()  # Press 'Start Over' button
        value2 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_startover_of_the_video(value2)

    @pytestrail.case("C12792186")
    @pytest.mark.xray("FRUM-135")
    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    def test_10465826_verify_scroll_forward_watch_vod(self):
        """
        To verify scroll forward functionality watching VOD

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/10465826
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(600, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_page.press_right_button()
        self.vod_page.press_ok()
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX1)
        self.watchvideo_page.press_left_button()
        self.vod_page.press_ok()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_page.press_right_button()
        self.vod_page.press_right_button()
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_ok()  # Press '+30s' button
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_30seconds_forward(value, value1)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_right_multiple_times(no_of_times=3)
        self.screen.refresh()
        self.vod_page.press_ok()  # Press 'Go to End' button
        self.screen.refresh()
        if self.vod_page.view_mode() == self.vod_labels.LBL_WATCHVOD:
            value2 = self.guide_page.get_trickplay_current_position_in_sec(refresh=False)
            self.vod_assertions.verify_30seconds_to_end_of_video(value2)
        else:
            self.vod_assertions.verify_view_mode(self.vod_labels.LBL_ACTIONS_SCREEN)

    @pytestrail.case("C12792181")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.cloud_core_vod_socu
    @pytest.mark.xray("FRUM-391")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_enable_video_window")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_336040_lock_vod_asset_during_playback(self):
        """
        336040
        PC lock the show during playback of VOD asset
        """
        status, results = self.vod_api.get_offer_playable()
        if results is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.play_any_playable_vod_content(self, results)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.menu_page.lock_pc_with_ratings(self, rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                            unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                            unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.vod_assertions.verify_video_blanking_status(state="true")
        self.home_page.back_to_home_short()
        self.home_page.press_back_from_home_to_livetv(self, view=self.vod_labels.LBL_WATCHVOD)
        self.menu_assertions.verify_enter_PIN_overlay()

    @pytest.mark.p1_regression
    @pytest.mark.vod
    @pytest.mark.cloud_core_vod_socu
    def test_11112180_continue_watching_vod(self):
        """
        To verify continue playing VOD asset from Continue Watching panel
        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/11112180
        """
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        title = self.vod_page.extract_title(result)
        movieYear = self.vod_page.extract_movie_year(result)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_assertions.verify_error_overlay_not_shown()
        self.vod_page.wait(60)  # wait for pause point availability
        last_played_position = self.my_shows_page.get_trickplay_position(self)
        self.home_page.goto_livetv_short(self)
        self.watchvideo_assertions.verify_error_overlay_not_shown()
        self.watchvideo_page.open_continue_watching_panel()
        self.watchvideo_assertions.verify_continue_watching_panel_shown()
        self.watchvideo_assertions.verify_continue_watching_program_title(title)
        self.watchvideo_page.press_ok_button()
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_assertions.verify_error_overlay_not_shown()
        resume_position = self.my_shows_page.get_trickplay_position(self)
        self.watchvideo_assertions.verify_video_resumed(last_played_position, resume_position)
        if movieYear:
            title = f"{title} ({movieYear})"
        self.watchvideo_assertions.verify_program_title(title)

    # pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.p1_reg_stability
    @pytest.mark.ndvr
    @pytest.mark.cloud_core_watch_Recording
    @pytest.mark.timeout(Settings.timeout)
    def test_8880245_verify_resume_playing_the_paused_nDVR_program_and_vod_program(self):
        """
        Verify playing a nDVR recording, pressing Pause, playing a VOD program,
        pausing the VOD program, resume playing the paused nDVR recording,
        and then resume playing the VOD program.
        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/8880245
        """
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        recording = self.api.record_currently_airing_shows(number_of_shows=1, genre="series", is_preview_offer_needed=True)
        if not recording:
            pytest.skip("Failed to create recording.")
        program_name = self.home_page.convert_special_chars(recording[0][0])
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.vod_page.press_play_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        vod_pause_position = self.my_shows_page.get_trickplay_position(self)
        self.home_page.go_to_my_shows(self)
        self.my_shows_assertions.verify_my_shows_title()
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.select_menu_by_substring(program_name)
        self.home_page.wait_for_screen_ready()
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.watchvideo_page.wait_for_LiveTVPlayback(status="PLAYING")
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.watch_video_for(60)
        self.vod_page.press_play_pause_button()
        self.watchvideo_assertions.verify_video_playback_mode(self.liveTv_labels.LBL_PLAYBACK_IN_PAUSE_MODE)
        pause_position = self.my_shows_page.get_trickplay_position(self)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result, resume=True)
        self.vod_assertions.verify_vod_playback(self)
        vod_current_position = self.my_shows_page.get_trickplay_position(self)
        time_diff = self.my_shows_page.check_time_diff_min(vod_current_position, vod_pause_position)
        self.my_shows_assertions.check_time_different(time_diff, 0, greater=True)
        self.vod_assertions.verify_vod_playback(self)
        self.my_shows_assertions.verify_and_playback_the_paused_program(self, recording)
        current_position = self.my_shows_page.get_trickplay_position(self)
        time_diff = self.my_shows_page.check_time_diff_min(current_position, pause_position)
        self.my_shows_assertions.check_time_different(time_diff, 0, greater=True)
        self.watchvideo_assertions.verify_playback_play()

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    def test_C10197319_verify_vodcontent_trickplay_menu_pressing_left_multiple_times(self):
        """
        :description:
            Verify vod content trickplay menu by pressing left multiple times.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197319
        :return:
        """
        status, result = self.vod_api.getOffer_vod_without_trickplay_restrictions()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.screen.base.press_left()
        self.watchvideo_assertions.is_rewind_focused(refresh=True)
        self.watchvideo_page.press_left_multiple_times(no_of_times=10)
        self.watchvideo_assertions.is_startover_focused(refresh=True)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    def test_C10197318_verify_vodcontent_trickplay_menu_pressing_ok_button(self):
        """
        :description:
            Verify trickplay menu by pressing ok button.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197318
        :return:
        """
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.guide_page.pause_show(self)
        self.guide_assertions.verify_pause()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout_in_pause_mode)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.is_playpause_focused(refresh=True)
        self.guide_assertions.verify_pause()

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    def test_C10197320_verify_vodcontent_trickplay_menu_pressing_right_multiple_times(self):
        """
        :description:
            Verify vod content trickplay menu by pressing right multiple times.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197320
        :return:
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(1200, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.screen.base.press_right()
        self.watchvideo_assertions.is_forward_focused(refresh=True)
        self.watchvideo_page.press_right_multiple_times(no_of_times=10)
        self.watchvideo_assertions.is_guide_focused(refresh=True)

    @pytest.mark.p1_regression
    def test_C10197327_verify_trickplay_menu_guide_button_selection_from_vod_playback(self):
        """
        :description:
            VOD - TrickPlay Menu - select Guide.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197327
        :return:
        """
        status, result = self.vod_api.getOffer_vod_without_trickplay_restrictions()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        pause = self.watchvideo_page.index_position_of_icon(icon="Pause")
        guide = self.watchvideo_page.index_position_of_icon(icon="Guide")
        self.watchvideo_page.show_trickplay_if_not_visible(wait=True)
        self.watchvideo_page.press_right_multiple_times(no_of_times=(guide - pause), refresh=False)
        self.watchvideo_assertions.verify_guide_button_selection(self, refresh=True)

    @pytest.mark.p1_regression
    def test_C10197326_verify_trickplay_menu_info_button_selection_from_vod_playback(self):
        """
        :description:
            VOD - TrickPlay Menu - select Info.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197326
        :return:
        """
        status, result = self.vod_api.getOffer_vod_without_trickplay_restrictions()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        pause = self.watchvideo_page.index_position_of_icon(icon="Pause")
        guide = self.watchvideo_page.index_position_of_icon(icon="Info")
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_right_multiple_times(no_of_times=(guide - pause))
        self.watchvideo_assertions.verify_info_icon_selection(self)
        # to verify info banner through info button
        if Settings.is_info_available():
            self.home_page.press_info_button()
            self.watchvideo_assertions.verify_full_info_banner_is_shown()

    @pytest.mark.p1_regression
    @pytest.mark.favoritepanel
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_C10195355_favorites_panel_press_ok_selection_from_vod_playback(self):
        """
        :description:
            VOD - TrickPlay Menu - select OK in favorite panel.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10195355
        :return:
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
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_page.open_favorite_panel()
        self.watchvideo_assertions.verify_favorite_channels_panel_shown()
        self.watchvideo_page.find_channel_on_favorite_panel(channel[0][0])
        self.watchvideo_assertions.verify_playback_play()
        self.watchvideo_page.press_ok_button(refresh=False)
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.verify_standard_info_banner_shown()
        self.watchvideo_assertions.verify_favorite_channels_panel_not_shown()

    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-32971")
    @pytest.mark.favoritepanel
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_C10195355_favorites_panel_press_ok_selection_from_vod_playback_for_vod_jump_channel(self):
        """
        :description:
            VOD - TrickPlay Menu - select OK in favorite panel.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10195355
        :return:
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        channel_num = list(self.api.get_jump_channels_list().keys())[0]
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready()
        self.guide_page.remove_channel_from_favorites(self, channel_num)
        self.guide_page.add_channel_to_favorites(channel_num)
        self.home_page.back_to_home_short()
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
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
        if self.screen.get_screen_dump_item('viewMode') == self.vod_labels.LBL_BIAXIAL_SCREEN_VIEW_MODE:
            self.vod_assertions.verify_screen_title(self.home_labels.LBL_ONDEMAND_SHORTCUT)
        else:
            self.watchvideo_page.wait_for_screen_ready(self.liveTv_labels.LBL_LIVETV_SCREEN)
            self.watchvideo_assertions.verify_playback_play()

    @pytest.mark.p1_regression
    def test_299593264_verify_go_to_livetv_trickplay_menu_button_exits_vod(self):
        """
        :description:
            VOD - TrickPlay Menu - select Live TV.
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10197327
        :return:
        """
        channel = self.service_api.get_random_encrypted_unencrypted_channels(filter_channel=True,
                                                                             transportType="stream")
        if not channel:
            pytest.skip("Could not find any channel.")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.get_live_program_name(self, raise_error_if_no_text=False)
        self.guide_page.select_and_watch_program(self)  # Tune to playable live channel
        self.watchvideo_assertions.verify_playback_play()
        status, result = self.vod_api.getOffer_vod_without_trickplay_restrictions()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        pause = self.watchvideo_page.index_position_of_icon(icon="Pause")
        livetv = self.watchvideo_page.index_position_of_icon(icon="Go to Live TV")
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_page.press_right_multiple_times(no_of_times=(livetv - pause))
        self.watchvideo_page.press_ok_button()
        self.watchvideo_assertions.verify_livetv_mode()
        self.watchvideo_assertions.verify_playback_play()

    # @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    def test_10841794_vod_subtitle_trick_mode(self):
        """
        Subtitle verification cannot be done when in FFWD/RWD mode.

        Product Bug --> https://jira.tivo.com/browse/BZSTREAM-7171
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(3600, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.take_screenrecord_and_pull("cc_on.mp4", "/sdcard/cc_on.mp4", ".", 10)
        self.watchvideo_assertions.verify_cc_or_subtitle_is_rendered_when_ON_or_OFF("cc_on.mp4", "ON")
        self.screen.base.press_fast_forward()  # FWD1
        self.guide_assertions.verify_fast_forward(1)
        self.screen.base.press_fast_forward()
        self.screen.base.press_fast_forward()  # FWD3
        self.guide_assertions.verify_fast_forward(1)
        self.screen.base.press_rewind()
        self.screen.base.press_rewind()
        self.screen.base.press_rewind()  # NormalPlayback
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.take_screenrecord_and_pull("cc_on_rw1.mp4", "/sdcard/cc_on_rw1.mp4", ".", 10)
        self.watchvideo_assertions.verify_cc_or_subtitle_is_rendered_when_ON_or_OFF("cc_on_rw1.mp4", "ON")
        self.screen.base.press_rewind()
        self.screen.base.press_rewind()
        self.screen.base.press_rewind()  # RWD3
        self.guide_assertions.verify_rewind(1)

    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.xray("FRUM-933")
    @pytest.mark.msofocused
    def test_c10841803_rew_ok_fwd_advance(self):
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(1000, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.skip_hdmi_connection_error()
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_page.wait(600)  # wait is needed to build cache for REW modes verification
        self.vod_page.press_reverse()
        self.vod_page.press_ok()  # REW1 mode
        self.vod_page.press_ok()  # REW2 mode
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_RWDX2)
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.screen.base.press_advance()
        self.vod_page.wait(60)
        self.guide_assertions.verify_play_normal()

    # @pytest.mark.p1_regression
    @pytest.mark.GA
    @pytest.mark.voicesearch
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif(not Settings.is_voice_C2C(), reason="Valid for voice apk")
    def test_C13525047_searching_vod_asset_by_GA_C2C_part1(self):
        """
        Searching vod asset by google assistant by means of collectionID
        """
        status, result = self.vod_api.getOffer_fvod()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        collectionId = self.vod_page.extract_collectionId(result)
        self.guide_page.launch_action_screen_using_GA(collectionId)

    @pytest.mark.p1_regression
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.timeout(Settings.timeout)
    def test_13525046_whether_adult_assets_are_there_in_my_rentals(self):
        '''
        test_whether_adult_assets_are_there_in_my_rentals
        '''
        status, results = self.vod_api.get_adult_offer_playable()
        if results is None:
            pytest.skip("The content is not available on VOD catlog.")
        mixID = self.vod_page.extract_mixID(results)
        title = self.vod_page.extract_title(results)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.play_any_playable_vod_content(self, results)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_page.wait(30)
        self.vod_page.go_to_vod(self)
        self.vod_page.wait_for_screen_ready()
        self.vod_page.navigate_to_entryPoint(self, f'1/{self.vod_labels.LBL_MY_ADULT_RENTALS}', mixID)
        self.vod_assertions.verify_my_rentals(self, title, self.vod_labels.LBL_MY_ADULT_RENTALS)
        self.menu_page.go_to_parental_controls(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.enter_default_parental_control_password(self)  # to confirm
        self.menu_page.select_menu_items(self.menu_labels.LBL_HIDE_ADULT_CONTENT)
        self.menu_page.select_menu_items(self.menu_labels.LBL_HIDE_ADULT_NEW)
        self.vod_page.go_to_vod(self)
        self.vod_page.wait_for_screen_ready()
        self.vod_page.navigate_to_entryPoint(self, f'1/{self.vod_labels.LBL_MY_RENTALS}', mixID)
        with pytest.raises(Exception):
            self.vod_assertions.verify_my_rentals(self, title, self.vod_labels.LBL_MY_RENTALS)

    @pytest.mark.p1_regression
    # @pytest.mark.test_stabilization
    @pytest.mark.skipif(not Settings.is_android_tv(), reason="Screen recording is applicable only for android")
    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    def test_312064646_verify_cc_rendered_when_ON_part1(self):
        """
        Description:
            To verify subtitle/closed caption is rendered on VOD when it is ON
        Testrail:
            Test Case: https://testrail.tivo.com//index.php?/tests/view/312064646
        """
        status, result = self.vod_api.getOffer_free_with_cc_available()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_assertions.verify_playback_play()
        self.vod_assertions.verify_vod_playback(self)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.watchvideo_assertions.verify_trickplay_bar_not_shown()
        self.watchvideo_assertions.record_and_verify_cc(".", 20, Settings.log_path, "ON")

    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    # @pytest.mark.test_stabilization
    @pytest.mark.skipif(not Settings.is_android_tv(), reason="Screen recording is applicable only for android")
    @pytest.mark.usefixtures("setup_enable_closed_captioning")
    def test_312064646_verify_cc_rendered_when_ON_part2(self):
        """
        Description:
            To verify subtitle/closed caption is rendered for Recordings when it is ON
        Testrail:
            Test Case: https://testrail.tivo.com//index.php?/tests/view/312064646
        """
        channel = self.guide_page.guide_streaming_channel_number(self, filter_channel=True)
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel)
        program = self.guide_page.get_live_program_name(self)
        self.guide_page.create_live_recording()
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_page.select_show(program)
        self.my_shows_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_show_is_selected(self, program)
        self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
        self.my_shows_page.wait_for_screen_ready()
        self.vod_assertions.verify_view_mode(self.my_shows_page.get_watch_or_video_recording_view_mode(self))
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.watchvideo_assertions.verify_trickplay_bar_shown()
        self.watchvideo_assertions.record_and_verify_cc(".", 20, Settings.log_path, "ON")

    @pytest.mark.p1_regression
    def test_C14390253_verify_play_position_after_fastforward(self):
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(600, 7200)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_forward()
        self.vod_page.press_ok()
        self.vod_page.press_ok()
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX2)
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(value, value1, rewind=False)

    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-705")
    @pytest.mark.msofocused
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_list_favorite_channels_in_guide")
    def test_c10841799_up_down_vtp_vod_playback(self):
        """
        :description:
            VOD - up/down on VTP while playing VOD
        :testrail:
            Test Case: https://testrail.tivo.com//index.php?/cases/view/10195355
        :return:
        """
        self.guide_page.remove_all_fav_channels_in_guide(self)
        self.guide_page.add_random_channel_to_favorite(self)
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(3600, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catalog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.skip_hdmi_connection_error()
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_page.press_forward()
        self.vod_page.press_ok()  # FF1 mode
        self.vod_page.press_ok()  # FF2 mode
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX2)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.screen.base.press_up()
        self.vod_assertions.verify_one_line_guide()
        self.vod_page.wait(30)  # wait for OLG to dismiss
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_page.press_reverse()
        self.vod_page.press_ok()  # REW1 mode
        self.vod_page.press_ok()  # REW2 mode
        self.vod_page.press_ok()  # REW3 mode
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_RWDX3)
        self.screen.base.press_down()  # Pressing down twice to skip Continue Watching Panel(in case it exists)
        self.screen.base.press_down()
        self.vod_assertions.verify_favorite_channels_panel_shown()
        self.vod_page.wait(30)  # wait for favorite channel panel to dismiss
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.vod_page.press_play_pause_button()
        self.vod_assertions.verify_pause_mode(self.vod_labels.LBL_PAUSE_ICON)
        self.screen.base.press_up()
        self.vod_assertions.verify_one_line_guide()
        self.vod_page.wait(30)  # wait for OLG to dismiss
        self.vod_page.press_play_pause_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        self.guide_page.remove_all_fav_channels_in_guide(self)

    @pytestrail.case("T403889704")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize(
        "feature, package_type", [(FeAlacarteFeatureList.VOD, FeAlacartePackageTypeList.NATIVE)])
    def test_T403889704_drm_type_vod_verimatrix_to_widevine(self, request, feature, package_type):
        """
        DRM type Native VOD StartOver playback - verify VOD playback on drm type native
        Testrail:
            https://testrail.tivo.com//index.php?/tests/view/403889704
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration(600, 7200)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)
        request.getfixturevalue("preserve_initial_package_state")
        request.getfixturevalue("remove_packages_if_present_before_test")
        self.home_page.update_drm_package_names_native(feature, package_type)
        self.home_assertions.verify_drm_package_names_native(feature, package_type)
        status, result = self.vod_api.get_entitled_vod_with_within_duration(600, 7200)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-1203")
    def test_19782947_verify_program_screen_reach_on_FFWD_till_end(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/19782947
        """
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.navigate_to_the_end_of_video_and_complete()
        self.vod_page.wait_for_screen_ready()
        self.vod_assertions.verify_vod_series_or_action_screen_view_mode()

    @pytestrail.case('C11123941')
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.notapplicable(Settings.is_dev_host())
    @pytest.mark.skipif(not Settings.is_cc11(), reason="VOD VTP hardcoded asset specific to cc11 MSO")
    @pytest.mark.timeout(Settings.timeout)
    def test_314075_part1_VTP_VOD_trick_play(self):
        """
        Validate forward and rewind trickplay action and position of VTP VOD offer
        """
        ep = self.vod_labels.LBL_VTP_VOD_EP
        collectionID = self.vod_labels.LBL_VTP_VOD_COLLECTIONID
        program = self.vod_labels.LBL_VTP_VOD_PROGRAM
        mixID = contentID = title = None
        self.vod_page.go_to_vod(self)
        try:
            self.vod_page.navigate_to_entryPoint(self, ep, mixID)
        except LookupError:
            pytest.skip("No VTP content available")
        self.vod_page.select_vod(self, collectionID, contentID, title)
        self.vod_page.play_free_vod_content(subtitle=program)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_page.watch_video_for(30)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.vod_page.press_right_button()
        self.vod_page.press_ok()
        self.vod_page.pause(2)
        self.vod_assertions.verify_press_forward_trick_play(self.vod_labels.LBL_FWDX1)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(value, value1, rewind=False)
        self.vod_page.press_back_button()
        self.vod_assertions.verify_trick_play_available(self.vod_labels.LBL_PLAY_NORMAL)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.vod_page.press_left_button()
        self.vod_page.press_ok()
        self.vod_page.pause(2)
        self.vod_assertions.verify_press_reverse_trick_play(self.vod_labels.LBL_RWDX1)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_play_position(value, value1, rewind=True)
        self.vod_page.back_to_vod_main_screen(Settings.manage_id)

    @pytest.mark.p1_regression
    def test_20958257_verify_adult_folder_when_EAS_triggered(self):
        status, results = self.vod_api.get_adult_offer_playable()
        if results is None:
            pytest.skip("The content is not available on VOD catlog.")
        title = self.vod_page.extract_title(results)
        if Settings.is_managed():
            self.screen.base.launch_application(self.apps_and_games_labels.YOUTUBE_PACKAGE_NAME)
            self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.YOUTUBE_PACKAGE_NAME, limit=15)
            self.apps_and_games_page.play_youtube_content()
            self.vod_page.wait(30)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_page.play_any_playable_vod_content(self, results)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_page.wait(30)
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.home_page.wait_for_EAS_to_dismiss(timeout=90)
        self.vod_page.wait_for_screen_ready()
        self.screen.refresh()
        if self.screen.get_screen_dump_item('viewMode') == self.vod_labels.LBL_ACTIONS_SCREEN:
            self.vod_assertions.verify_program_name_under_adult_on_demand(title)
        else:
            self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)

    @pytest.mark.p1_regression
    def test_20941217_verify_RWDx1_in_pause_mode(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20941217
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(600, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.vod_page.wait(100)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.vod_page.press_ok()
        self.vod_assertions.verify_pause_mode(self.vod_labels.LBL_PAUSE_ICON)
        self.vod_page.press_left_button()
        self.vod_page.press_ok()
        self.vod_page.pause(4)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_backward(value, value1, 3)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    def test_verify_20951468_navigations_on_trickplay_when_in_ffwd3(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20951468
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(3600, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.vod_page.press_right_button()
        self.watchvideo_assertions.is_forward_button_focused(self)
        self.vod_page.press_ok()
        self.vod_page.press_ok()
        self.vod_page.press_ok()
        self.vod_page.pause(2)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_forward(value, value1, 60)
        self.vod_page.press_right_button()
        self.watchvideo_assertions.is_advance_focused(self)
        self.vod_page.press_right_button()
        self.watchvideo_assertions.is_gotoend_focused(self)
        self.vod_page.press_left_button()
        self.vod_page.press_left_button()
        self.vod_page.press_left_button()
        self.watchvideo_assertions.is_playpause_focused(refresh=True)
        self.vod_page.press_left_button()
        self.watchvideo_assertions.is_rewind_button_focused(self)
        self.vod_page.press_left_button()
        self.watchvideo_assertions.is_replay_focused(self)
        self.vod_page.press_left_button()
        self.watchvideo_assertions.is_startover_focused(refresh=True)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-1275")
    @pytest.mark.timeout(Settings.timeout)
    def test_20958660_verify_trickplay_actions_after_EAS_trigger(self):
        """
        https://testrail.tivo.com/index.php?/cases/view/20958660
        """
        status, result = self.vod_api.get_entitled_vod_with_within_duration_without_restriction(1800, 10800)
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.home_page.wait_for_EAS_to_dismiss(timeout=90)
        self.vod_page.wait_for_screen_ready()
        self.vod_assertions.verify_vod_playback(self)
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.watchvideo_page.show_trickplay_if_not_visible()
        self.vod_page.press_right_button()
        self.watchvideo_assertions.is_forward_focused()
        value = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_ok()
        self.vod_page.pause(5)
        value0 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_forward(value, value0, 3)
        value1 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_ok()
        self.vod_page.pause(5)
        value11 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_forward(value1, value11, 18)
        value2 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_ok()
        self.vod_page.pause(5)
        value22 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_forward(value2, value22, 60)
        self.vod_page.press_left_button()
        self.vod_page.press_ok()
        self.vod_page.press_left_button()
        self.watchvideo_assertions.is_rewind_focused()
        value3 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_ok()
        self.vod_page.pause(5)
        value3 = value3 + 1  # 1 sec for Rewind key press as it was in play mode before
        value33 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_backward(value3, value33, 3)
        value4 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_ok()
        self.vod_page.pause(5)
        value44 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_backward(value4, value44, 18)
        value5 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_page.press_ok()
        self.vod_page.pause(5)
        value55 = self.guide_page.get_trickplay_current_position_in_sec()
        self.vod_assertions.verify_scroll_backward(value5, value55, 60)

    @pytestrail.case("C12787152")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.VOD,
                                                        FeAlacartePackageTypeList.VERIMATRIX)])
    def test_C12787152_change_drm_type_vod_verimatrix(self, request, feature, package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/12787152
        """
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("Failed to get an VOD asset")
        drm_type = self.api.provisioning_info_type(self.home_labels.LBL_VOD_PROVISIONING_INFO_SEARCH)
        self.home_page.check_drmtype(
            self, request, drm_type, self.home_labels.KEY_DRM_ANDROID_NATIVE,
            feature, FeAlacartePackageTypeList.VERIMATRIX)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)

    @pytestrail.case("C12787151")
    @pytest.mark.mdrm_functional
    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(not (Settings.is_cc5() or Settings.is_cc11()),
                               "Mdrm implemented only for cableco5 and cableco11")
    @pytest.mark.notapplicable(not Settings.is_android_tv())
    @pytest.mark.parametrize("feature, package_type", [(FeAlacarteFeatureList.VOD,
                                                        FeAlacartePackageTypeList.NATIVE)])
    def test_C12787151_change_drm_type_vod_reboot(self, request, feature, package_type):
        """
        Test rail:
        https://testrail.tivo.com/index.php?/cases/view/12787151
        """
        status, result = self.vod_api.get_offer_playable()
        if result is None:
            pytest.skip("Failed to get an VOD asset")
        drm_type = self.api.provisioning_info_type(self.home_labels.LBL_VOD_PROVISIONING_INFO_SEARCH)
        self.home_page.check_drmtype(
            self, request, drm_type, self.home_labels.KEY_DRM_ANDROID_NATIVE,
            feature, FeAlacartePackageTypeList.VERIMATRIX)
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_vod_entitled_content(self, result)
        self.vod_assertions.verify_vod_playback(self)
        self.home_page.relaunch_hydra_app(reboot=True)

    @pytest.mark.parametrize("is_pps_lite, is_make_dis", [(False, True), (False, False)])
    @pytest.mark.usefixtures("cleanup_enabling_internet")
    @pytest.mark.usefixtures("setup_cleanup_set_tier_and_site_id")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_frum_6481_change_tier_site_id_internet_reconnect_vod_catalog_changed(self, request, is_pps_lite, is_make_dis):
        """
        Checking if VOD catalog is changed after serviceCall request and internet reconnection.
        Change serviceTier and vodSiteId - send serviceCall - select Remind me later - disconnect - connect -
        Restart now/Exit now option in overlay - start Hydra - verify if VOD catalog has been changed.

        Xray:
            https://jira.tivo.com/browse/FRUM-6481 with deviceInfoStore
            https://jira.tivo.com/browse/FRUM-6456 no deviceInfoStore
        """
        old_strip_list = request.config.cache.get("vod_strip_name_list", None)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_connected_disconnected_state_happened(error_code=self.home_labels.LBL_ERROR_CODE_C228,
                                                                          is_select=True)
        # Getting internet connection back
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        start_time = datetime.now()
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False, is_select=True, timeout=330)
        end_time = datetime.now()
        self.__log.debug("test_frum_6481: end_time - start_time = {}".format(end_time - start_time))
        self.vod_page.go_to_vod(self)
        # There should not be any error overlay while opening the VOD Browse Main screen
        self.vod_assertions.verify_overlay_shown(expected=False)
        # After getting internet connection back. Checking if current VOD strip name list differs from the old one
        self.menu_assertions.verify_menu_item_available(old_strip_list, expected=False)
        self.vod_page.press_back_button(refresh=False)
        self.vod_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
        self.home_page.select_menu(request.cls.home_labels.LBL_RESTART_NOW)
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.vod_page.go_to_vod(self)
        # There should not be any error overlay while opening the VOD Browse Main screen
        self.vod_assertions.verify_overlay_shown(expected=False)
        # After Hydra app restart. Checking if current VOD strip name list differs from the old one
        self.menu_assertions.verify_menu_item_available(old_strip_list, expected=False)

    @pytest.mark.parametrize("is_pps_lite, is_make_dis", [(True, True), (False, True)])
    @pytest.mark.usefixtures("setup_cleanup_set_tier_and_site_id")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_frum_9392_pps_lite_change_tier_site_id_restart_hydra_vod_catalog_changed(self, request, is_pps_lite,
                                                                                      is_make_dis):
        """
        Change serviceTier and vodSiteId - restart Hydra - check VOD Browse (strips and assets differ from the old ones)

        Xray:
            https://jira.tivo.com/browse/FRUM-9392 (PPS-Lite feature)
            https://jira.tivo.com/browse/FRUM-5209 (Service Login and Config Update)
        """
        old_strip_list = request.config.cache.get("vod_strip_name_list", None)
        lower_1_15 = False if Settings.hydra_branch() >= Settings.hydra_branch(HydraBranches.STREAMER_1_15) else True
        self.home_page.select_menu_shortcut_num(self, self.home_labels.LBL_MENU_SHORTCUT)
        self.vod_page.press_back_button(refresh=False)
        if not lower_1_15:
            self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)
            self.home_page.select_menu(request.cls.home_labels.LBL_RESTART_NOW)
            self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        else:
            # There should no be any Assert or overlay after re-entering the Home screen on older Hydra versions
            self.home_assertions.verify_overlay_shown(expected=False)
            self.home_page.relaunch_hydra_app()
        self.vod_page.go_to_vod(self)
        # There should not be any error overlay while opening the VOD Browse Main screen
        self.vod_assertions.verify_overlay_shown(expected=False)
        # Checking if current VOD strip name list differs from the old one
        # v1.15 and higher - VOD browse differs from the old one, v1.13 and lower - VOD browse stays the same
        self.menu_assertions.verify_menu_item_available(old_strip_list, expected=lower_1_15)

    @pytest.mark.parametrize("is_pps_lite, is_make_dis", [(False, True)])
    @pytest.mark.usefixtures("setup_cleanup_set_tier_and_site_id")
    @pytest.mark.usefixtures("cleanup_re_activate_and_sign_in")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_frum_6387_change_tier_site_id_cancel_re_activate_device_vod_catalog_changed(self, request, is_pps_lite,
                                                                                         is_make_dis):
        """
        Change serviceTier and vodSiteId - send serviceCall - select Remind me later - cancel account -
        Account Locked screen - Netflix - re-activate account - Home screen - verify if VOD catalog has been changed

        Xray:
            https://jira.tivo.com/browse/FRUM-6387
        """
        old_strip_list = request.config.cache.get("vod_strip_name_list", None)
        self.acc_locked_page.cancel_device()
        self.acc_locked_page.managing_hydra_app_after_canceling_acc()
        self.acc_locked_assertions.verify_if_account_locked_shown()
        # Netflix will not work on Jade and Ruby,Launching Youtube
        self.acc_locked_assertions.press_youtube_and_verify_screen(self)
        self.acc_locked_page.re_activate_device()
        self.acc_locked_assertions.press_bail_button_and_verify_if_account_locked_shown(BailButtonList.BACK)
        # NOTE
        # Possibly, back-off algorithm may be added in future for case when Hydra app is on foreground again,
        # so signing in will be started automatically after getting back to the Hydra app
        self.acc_locked_page.managing_sign_in_after_acc_status_change(is_re_activated=True)
        self.home_assertions.verify_view_mode(self.acc_locked_labels.LBL_HOME_SCREEN_VIEW_MODE)
        self.vod_page.go_to_vod(self)
        # There should not be any error overlay while opening the VOD Browse Main screen
        self.vod_assertions.verify_overlay_shown(expected=False)
        # Checking if current VOD strip name list differs from the old one
        self.menu_assertions.verify_menu_item_available(old_strip_list, expected=False)

    @pytest.mark.parametrize("is_pps_lite, is_make_dis", [(False, False)])
    @pytest.mark.usefixtures("setup_cleanup_set_tier_and_site_id")
    @pytest.mark.usefixtures("cleanup_enabling_internet")
    @pytest.mark.usefixtures("get_and_restore_tcdui_test_conf")
    @pytest.mark.notapplicable(Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_frum_18678_disconnect_change_tier_site_id_connect_domain_expir_vod_catalog_changed(self, request,
                                                                                                is_pps_lite,
                                                                                                is_make_dis):
        """
        Disconnect - Change serviceTier and vodSiteId - Connect - Domain token expires while staying in Home -
        Verify if VOD catalog has been changed

        Xray:
            https://jira.tivo.com/browse/FRUM-18678
        """
        req_type = NotificationSendReqTypes.FCM if Settings.is_managed() else NotificationSendReqTypes.NSR
        mso_env = Settings.mso.lower() + " " + Settings.test_environment.lower()
        self.home_page.update_test_conf_and_reboot(BUG_514565_HACK_DOMAIN_TOKEN_EXPIRATION_INTERVAL=300, clear_data=True)
        self.home_page.back_to_home_short()
        old_strip_list = request.config.cache.get("vod_strip_name_list", None)
        new_vod_id_mso_id = request.config.cache.get("new_site_id_and_service_id", None)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_connected_disconnected_state_happened(error_code=self.home_labels.LBL_ERROR_CODE_C228,
                                                                          is_select=True)
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            site_id=new_vod_id_mso_id[mso_env]["vodSiteId"],
            tier=new_vod_id_mso_id[mso_env]["serviceTier"])
        if not is_pps_lite:
            # There's no serviceCall notification if PPS-Lite feature is off, so need need to send one separately
            self.home_page.send_fcm_or_nsr_notification(req_type, RemoteCommands.SERVICE_CALL)
        self.home_page.pause(300, "Waiting a bit to miss serviceCall")
        # Getting internet connection back
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        start_time = datetime.now()
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False, is_select=True, timeout=330)
        end_time = datetime.now()
        self.__log.debug("test_frum_18678: end_time - start_time = {}".format(end_time - start_time))
        self.home_page.pause(480, "Waiting for domain token expiration")
        self.vod_page.go_to_vod(self)
        # There should not be any error overlay while opening the VOD Browse Main screen
        self.vod_assertions.verify_overlay_shown(expected=False)
        # Checking if current VOD strip name list differs from the old one
        self.menu_assertions.verify_menu_item_available(old_strip_list, expected=False)

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_vod_playback
    @pytest.mark.per_program_device_restrictions
    @pytest.mark.timeout(Settings.timeout)
    def test_489015_vod_restricted_device_type_check_with_mso_true(self):
        """
        Restricted device type check condition
         if (restrictedDeviceType True) and (checkDeviceTypeWithMso True)
                Then Playback will be decide based on MOS instructions
                    if no MSO instructions
                        then playback start without any error
                    else:
                        playback will be restricted based on MSO instructions
                        playback failed with V414 error
        Xray link: https://jira.tivo.com/browse/XTQ-489015
        """
        status, result = self.vod_api.get_device_restricted_mso_true_vod_asset()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_vod_playback
    @pytest.mark.per_program_device_restrictions
    @pytest.mark.timeout(Settings.timeout)
    def test_489016_vod_restricted_device_type_check_with_mso_false(self):
        """
         Restricted device type check condition
          if (restrictedDeviceType True) and  (checkDeviceTypeWithMso False)
                 then playback failed with V414 error
          Xray link: https://jira.tivo.com/browse/XTQ-489016
         """
        status, result = self.vod_api.get_device_restricted_mso_false_vod_asset()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_vod_playback
    @pytest.mark.per_program_device_restrictions
    @pytest.mark.timeout(Settings.timeout)
    def test_489017_vod_restricted_device_type_check_with_mso_blank(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
             and (restrictedDeviceType True) and (checkDeviceTypeWithMso False)
                 then playback failed with V414 error
          Xray link: https://jira.tivo.com/browse/XTQ-489017
         """
        status, result = self.vod_api.get_device_restricted_mso_none_vod_asset()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_can_not_watch_show_overlay_shown()

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_vod_playback
    @pytest.mark.per_program_device_restrictions
    @pytest.mark.timeout(Settings.timeout)
    def test_489018_vod_not_restricted_device_type_check_with_mso_true(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
              (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback will start
         Xray link: https://jira.tivo.com/browse/XTQ-489018
         """
        status, result = self.vod_api.get_not_device_restricted_mso_true_vod_asset()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_vod_playback
    @pytest.mark.per_program_device_restrictions
    @pytest.mark.timeout(Settings.timeout)
    def test_489019_vod_not_restricted_device_type_check_with_mso_false(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
              (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback start
          Xray link: https://jira.tivo.com/browse/XTQ-489019
         """
        status, result = self.vod_api.get_not_device_restricted_mso_false_vod_asset()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)

    @pytest.mark.frumos_16
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_16))
    @pytest.mark.per_program_device_restrictions_vod_playback
    @pytest.mark.per_program_device_restrictions
    @pytest.mark.timeout(Settings.timeout)
    def test_489020_vod_not_restricted_device_type_check_with_mso_blank(self):
        """
         Restricted device type check condition
         checkDeviceTypeWithMso blank takes as False
          if
             (restrictedDeviceType False) and (checkDeviceTypeWithMso False)
                 then playback start
          Xray link: https://jira.tivo.com/browse/XTQ-489020
         """
        status, result = self.vod_api.get_not_device_restricted_mso_none_vod_asset()
        if result is None:
            pytest.skip("The content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.vod_assertions.verify_view_mode(self.vod_labels.LBL_WATCHVOD)
        self.vod_assertions.verify_vod_playback(self)

    @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_verify_purchase_control_with_incorrect_pin(self):
        """
        Verify Purchase Control with incorrect PIN.
        :return:
        """
        # Turning on P&PC
        self.menu_page.turnonpcsettings(self, "on", "on")
        # Disabling Parental controls
        self.menu_page.select_menu_items(self.menu_labels.LBL_DISABLE_PARENTAL_CONTROLS)
        time.sleep(2)
        self.menu_page.enter_default_parental_control_password(self)
        self.home_page.back_to_home_short()
        status, result = self.vod_api.getOffer_tvod_notEntitledRentable()
        if result is None:
            pytest.skip("The content is not available on VOD Catalog")
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.select_watch_now(self)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_wrong_pc_password(self)
        self.menu_assertions.verify_wrong_PIN_overlay()

    @pytest.mark.test_stabilization
    def test_xtq_36921_verify_currency_value_is_appear_in_the_vod_content_for_rent(self):
        status, result = self.vod_api.getoffer_rented_movie_rating_exceed_G()
        if result is None:
            status, result = self.vod_api.getoffer_rentable_movie_rating_exceed_G()
            if result is None:
                pytest.skip("VOD program not avaialable.")
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_assertions.verify_currency_value_on_action_screen()
        self.vod_assertions.verify_currency_value_rental_confirm_overlay()

    @pytest.mark.longevity
    def test_multiple_vod_assets_playbacks_to_continue_till_end(self):
        """
            Verify multiple VOD_assets continue to play till end
        """
        counter = 0
        while counter < LongevityConstants.MED_COUNTER:
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

    @pytest.mark.e2e1_15
    @pytest.mark.e2e
    @pytest.mark.xray("FRUM-19240")
    @pytest.mark.timeout(Settings.timeout)
    def test_unmapped_series_poster(self):
        status, results = self.vod_api.get_offer_unmapped_svod_entitledSubscribed_series()
        if results is None:
            pytest.skip("There are no unmapped series VOD assets")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, results)
        self.vod_assertions.verify_fallback_to_default_image(self, poster_color="black", asset_type="series")
        self.screen.base.long_press_enter()
        self.vod_page.wait_for_info_card_ready()
        self.vod_assertions.verify_fallback_to_default_image(self, poster_color="notblack", asset_type="series")

    def test_136563_playback_4k_VOD(self):
        """
        Verify 4k assets play on 4k resolution.
        https://jira.xperi.com/browse/FRUM-136563
        """
        status, result = self.vod_api.get_UHD_entitled_vod_with_duration()
        if result is None:
            pytest.skip("4k vod content is not available on VOD catlog.")
        self.home_page.back_to_home_short()
        self.vod_page.goto_vodoffer_program_screen(self, result)
        self.vod_page.play_any_playable_vod_content(self, result)
        self.watchvideo_page.watch_video_for(self.watchvideo_labels.LBL_PLAYBACK_CONTENT)
        self.vod_assertions.verify_vod_playback(self)
        self.watchvideo_assertions.verify_screen_resolution(self)
