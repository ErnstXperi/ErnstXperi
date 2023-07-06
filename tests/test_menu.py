from datetime import datetime

import pytest  # noqa: F401

from set_top_box.client_api.Menu.conftest import setup_menu, setup_parental_control, cleanup_favorite_channels,\
    setup_cleanup_parental_and_purchase_controls, disable_parental_controls  # noqa: F401
from set_top_box.client_api.home.conftest import relaunch_hydra_app, launch_hydra_app_when_script_is_on_ott  # noqa: F401
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_bind_hsn  # noqa: F401
from set_top_box.conf_constants import FeaturesList, BodyConfigFeatures, DeviceInfoStoreFeatures, \
    NotificationSendReqTypes, RemoteCommands
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions  # noqa: F401
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings  # noqa: F401
from set_top_box.shared_context import ExecutionContext
from set_top_box.client_api.guide.conftest import setup_cleanup_list_favorite_channels_in_guide  # noqa: F401
from set_top_box.client_api.home.conftest import setup_cleanup_return_initial_feature_state  # noqa: F401
from set_top_box.client_api.my_shows.conftest import setup_delete_book_marks  # noqa: F401
from set_top_box.client_api.account_locked.conftest import cleanup_enabling_internet  # noqa: F401
from pytest_testrail.plugin import pytestrail
from set_top_box.conf_constants import HydraBranches
from set_top_box.test_settings import Settings
from mind_api.dependency_injection.entities.branding import Branding


@pytest.mark.usefixtures("setup_menu")
@pytest.mark.menu
class TestMenu(object):

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_326129_navigate_from_home_to_menu_settings(self):
        """
        Navigate from Home to Settings
        :return:
        """
        self.menu_page.go_to_settings(self)

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_326138_select_menu_settings_user_preference(self):
        """
        Navigate from Settings to User Preference
        :return:
        """
        self.menu_page.go_to_user_preferences(self)

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_326140_select_menu_help_account_and_system(self):
        """
        Navigate from Help to Account & System Info
        :return:
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.select_menu_items("System Info")
        self.home_assertions.verify_screen_title("SYSTEM INFO")

    @pytest.mark.ibc
    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_326135_select_menu_onepass_manager(self):
        """
        Navigate from Manage to OnePass Manager
        :return:
        """
        self.menu_page.go_to_one_pass_manager(self)
        self.home_assertions.verify_screen_title("ONEPASS MANAGER")

    @pytest.mark.duplicate
    @pytest.mark.timeout(Settings.timeout)
    def test_326139_select_settings_signout(self):
        """
        This test case is covered under test_347783_ftux_second_signin
        Sign Out from the App
        :return:
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.select_menu_items("Sign Out")
        self.home_assertions.verify_screen_title("SIGN IN")

    @pytestrail.case('C11123883')
    @pytest.mark.bat
    @pytest.mark.compliance
    @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_347998_verify_settings_menu_items(self):
        """
        :description:
            Verifying menu items under Settings
        :testopia:
            Test Case: https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=347998
        :return:
        """
        self.menu_page.go_to_parental_controls(self)
        self.menu_assertions.verify_menu_items_availability(self.menu_labels.PARENTAL_CONTROLS_MENUITEMS)

    @pytestrail.case('C11123882')
    @pytest.mark.devhost
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_parental_control")
    def test_328471_verify_user_preferences_menu_item(self):
        """
        328471
        Verifying menu items under User Preferences
        :return:
        """
        self.menu_page.go_to_user_preferences(self)
        for i in self.menu_labels.USER_PREFERENCES_OPTIONS:
            self.menu_assertions.verify_menu_item_available(i)

    @pytestrail.case('C11123885')
    @pytest.mark.devhost
    @pytest.mark.bat
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_parental_control")
    @pytest.mark.xray("FRUM-302")
    @pytest.mark.msofocused
    def test_365013_ability_to_change_user_preferences(self):
        """
        365013
        Goes in user preferences and makes changes in all of the categories
        verify if changes are actually made
        :return:
        """
        if "firetv" in Settings.platform.lower():
            press_ok = [self.menu_labels.LBL_FAVOURITE_CHANNELS]
        else:
            press_ok = [self.menu_labels.LBL_MY_VIDEO_PROVIDERS, self.menu_labels.LBL_FAVOURITE_CHANNELS]
        press_right = [self.menu_labels.LBL_ONEPASS_OPTIONS, self.menu_labels.LBL_VIDEO_BACKGROUND]
        if not Settings.is_ndvr_applicable():
            move_down = [self.menu_labels.LBL_MY_SHOWS_OPTIONS]
        else:
            move_down = [self.menu_labels.LBL_MY_SHOWS_OPTIONS, self.menu_labels.LBL_AUTOPLAY_NEXTEPSD]
        self.menu_page.go_to_user_preferences(self)

        for i in self.menu_labels.USER_PREFERENCES_OPTIONS:
            self.menu_assertions.verify_menu_item_available(i)

        for item in press_ok:
            current_screen = self.menu_page.get_screen_name()
            self.menu_page.select_menu_items(item)
            self.menu_page.select_item(delay=2)
            self.menu_page.wait_for_screen_ready(current_screen, timeout=20000)
            m = self.menu_page.menu_item_image_focus()
            self.menu_page.menu_press_back()
            self.menu_page.wait_for_screen_ready(self.menu_labels.LBL_USER_PREF_SCREEN_NAME, timeout=18000)
            self.menu_page.select_item(delay=2)
            self.menu_page.wait_for_screen_ready()
            n = self.menu_page.menu_item_image_focus()
            self.menu_assertions.verify_items_are_same(m, n)
            self.menu_page.menu_press_back()

        for item in press_right:
            self.menu_page.select_menu_items(item)
            self.menu_page.menu_navigate_left_right(1, 0)
            self.screen.refresh()
            m = self.menu_page.menu_item_option_focus()
            self.menu_page.menu_press_back()
            self.menu_page.select_menu_items(item)
            self.screen.refresh()
            n = self.menu_page.menu_item_option_focus()
            self.menu_assertions.verify_items_are_same(m, n)
            self.menu_page.menu_navigate_left_right(0, 1)
            self.menu_page.menu_press_back()

        for item in move_down:
            self.menu_page.select_menu_items(item)
            if item == self.menu_labels.LBL_MY_SHOWS_OPTIONS:
                self.menu_page.check_myshows_options(self)
            else:
                self.menu_page.change_autoplay_option(self)
            m = self.menu_page.menu_focus()
            self.menu_page.select_menu_items(item)
            n = self.menu_page.menu_focus()
            self.menu_assertions.verify_items_are_same(m, n)
            self.menu_page.menu_press_back()

    @pytestrail.case("C12792608")
    @pytest.mark.favorite_channels  # noqa: F811
    # @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("cleanup_favorite_channels")
    def test_328478_add_channels_to_favorite(self):
        """
        328478
        look for first unchecked show, mark it as favorite
        go to guide, view favorites shows, and verify if newly checked show in there
        """
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.select_menu_items("Favorite Channels")
        unchecked = 'com/tivo/applib/ResAppLibImages/applib/images/hydra/hydra_icon_checkbox_unchecked.png'
        index = self.menu_page.find_first_unchecked(unchecked)
        if index >= 0:
            self.menu_page.menu_navigate_up_down(0, index)
            show = self.menu_page.menu_focus()
            show = show[1]
            self.menu_page.select_item()
        else:
            show = self.menu_page.menu_focus()
            show = show[1]

        self.home_page.go_to_guide(self)
        self.guide_page.switch_channel_option("Favorites")
        self.guide_assertions.verify_favorite_show_in_guide()

    @pytestrail.case('C10838512')
    @pytest.mark.xray('FRUM-50')
    @pytest.mark.devhost
    @pytest.mark.sanity
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    def test_94980_navigate_to_system_info_screen(self):
        """
        94980
        Verify that the TCD is able to display the system information screen
        :return:
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_SYSTEM_INFO)
        self.menu_page.select_menu_items(self.menu_labels.LBL_SYSTEM_INFORMATION)
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFORMATION_SCREENTITLE)

    @pytest.mark.mandatory_test
    @pytest.mark.timeout(Settings.timeout)
    def test_mandatory_test(self):
        """
        Used during mandatory test stage
        Launch app, check for home screen with menu items and predictions
        :return:
        """
        self.home_page.back_to_home_short()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        self.home_page.goto_prediction()
        self.home_assertions.verify_predictions()
        self.home_page.goto_home_menu_items_from_prediction()
        for i in self.home_labels.LBL_HOME_MENU_ITEMS:
            self.home_assertions.verify_menu_item_available(i)

    @pytestrail.case("C12792610")
    @pytest.mark.p1_regression
    # @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_329329_change_one_pass_options_start_from(self):
        """
        329329
        Changing onepass options for Start from to Season 1
        :return:
        """
        self.menu_page.go_to_user_preferences(self)
        option_name = self.menu_page.get_onepass_option_name(self)
        self.menu_page.select_menu_items(option_name)
        self.menu_page.select_menu_items(self.my_shows_labels.LBL_START_FROM)
        self.menu_page.nav_to_item_option(self.my_shows_labels.LBL_SEASON_1)
        self.menu_page.menu_press_back()

    @pytestrail.case("C12792609")
    @pytest.mark.p1_regression
    # @pytest.mark.devhost
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_329330_change_rent_or_buy_one_pass_options(self):
        """
        329330
        Changing onepass options for Start from to Season 1
        :return:
        """
        self.menu_page.go_to_user_preferences(self)
        option_name = self.menu_page.get_onepass_option_name(self)
        self.menu_page.select_menu_items(option_name)
        self.menu_page.select_menu_items(self.my_shows_labels.LBL_RENT_OR_BUY)
        self.menu_page.nav_to_item_option(self.my_shows_labels.LBL_INCLUDE_NO_COLON)
        self.menu_page.menu_press_back()
        self.menu_page.select_menu_items(option_name)
        self.menu_page.select_menu_items(self.my_shows_labels.LBL_RENT_OR_BUY)
        self.menu_assertions.verify_item_option_focus(self.my_shows_labels.LBL_INCLUDE_NO_COLON)
        self.menu_page.nav_to_item_option(self.my_shows_labels.LBL_DONT_INCLUDE)
        self.menu_assertions.verify_item_option_focus(self.my_shows_labels.LBL_DONT_INCLUDE)

    @pytestrail.case('C11123888')
    @pytest.mark.bat
    @pytest.mark.ndvr
    @pytest.mark.devhost
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("setup_parental_control")
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif("firetv" in Settings.platform.lower(), reason="TODO: to investigate Logger error")
    def test_ToDo_list_ordered(self):
        """
        350695
        Creating OnePass and checking that the created onepass ordered alphabetically in to_do_list.
        :return:
        """
        self.api.cancel_all_onepass(Settings.tsn)
        non_recordable_channel_list = self.service_api.get_nonrecordable_channels()
        if non_recordable_channel_list is False:
            non_recordable_channel_list = None
        channels = self.api.one_pass_currently_airing_shows(5, excludeChannelNumbers=non_recordable_channel_list,
                                                            duration=True)
        if not channels:
            pytest.skip("No one pass channel found")
        self.menu_page.go_to_to_do_list(self)
        self.menu_assertions.verify_toDo_list_items_ordered(len(channels))
        channel = channels.pop()
        self.home_page.go_to_guide(self)
        self.guide_page.enter_channel_number(channel[1])
        self.guide_page.delete_one_pass_on_record_overlay(self)
        self.menu_page.go_to_to_do_list(self)
        self.menu_assertions.verify_toDo_list_items_ordered(len(channels), removedItem=channel[0])

    @pytestrail.case('C11123884')
    @pytest.mark.bat
    @pytest.mark.devhost
    @pytest.mark.ndvr
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.usefixtures("setup_parental_control")
    @pytest.mark.timeout(Settings.timeout)
    def test_350212_ToDo_list_empty(self):
        """
        350212
        Checking empty To Do list
        :return:
        """
        self.menu_page.go_to_to_do_list(self)
        self.menu_assertions.verify_toDo_list_empty(self)

    @pytestrail.case('C11123887')
    @pytest.mark.bat
    @pytest.mark.compliance
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_parental_control")
    @pytest.mark.xray("FRUM-304")
    @pytest.mark.msofocused
    def test_393663_block_all_shows(self):
        """
        :testopia:
            Test Case: https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=393663 (Duplicate 350652)
        :description:
            Block all the shows in device level
        :testrail:
            Test Case: https://testrail.corporate.local/index.php?/cases/view/4811179
        :return:
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.go_to_set_rating_limit(self)
        self.menu_page.set_rating_limits(rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.menu_page.menu_press_back()
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        channel = self.api.get_random_encrypted_unencrypted_channels(transportType="stream", filter_channel=True)
        if not channel:
            pytest.skip("Could not find any episodic channel")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.get_live_program_name(self, raise_error_if_no_text=False)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.skip_hdmi_connection_error()
        self.home_assertions.verify_parental_lock()
        self.watchvideo_page.wait_for_trickplay_bar_dismiss(Settings.trickplay_bar_timeout)
        self.home_page.press_enter()
        self.menu_page.enter_default_parental_control_password(self)

    @pytestrail.case("C12792611")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.bvt
    @pytest.mark.compliance
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_parental_control")
    def test_4811163_allow_all_shows(self):
        """
        :description:
            Allow all shows and check if there's no Parental Controls OSD when watching Live TV
        :testrail:
            Test Case: https://testrail.corporate.local/index.php?/cases/view/4811163
        :return:
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.go_to_set_rating_limit(self)
        movie_rating = self.menu_page.get_highest_movie_rating()
        tv_rating = self.menu_page.get_highest_tv_rating()
        self.menu_page.set_rating_limits(rated_movie=movie_rating,
                                         rated_tv_show=tv_rating,
                                         unrated_tv_show=self.menu_labels.LBL_ALLOW_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_ALLOW_ALL_UNRATED)
        self.menu_page.menu_press_back()
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        channel = self.api.get_random_encrypted_unencrypted_channels(transportType="stream", filter_channel=True)
        if not channel:
            pytest.skip("Could not find any episodic channel")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.get_live_program_name(self, raise_error_if_no_text=False)
        self.guide_page.select_and_watch_program(self)
        self.watchvideo_page.skip_hdmi_connection_error()
        self.home_assertions.verify_parental_is_not_locked()

    @pytest.mark.bvt
    @pytest.mark.duplicate
    @pytest.mark.iplinear
    @pytest.mark.timeout(Settings.timeout)
    def test_325060_verify_build_and_branch(self):
        """
        Verify new build can be installed and used for testing (currently via abd)
        325060
        :return:
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_SYSTEM_INFO)
        self.menu_page.select_menu_items("System Information")
        self.menu_assertions.verify_build_and_branch(Settings.branch, Settings.build)

    @pytestrail.case('C11123886')
    @pytest.mark.bat
    @pytest.mark.compliance
    @pytest.mark.bvt
    @pytest.mark.iplinear
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_parental_control")
    def test_393657_ability_to_go_into_each_available_settings(self):
        """
        :description:
            Ability to go into each available settings
        :testopia:
            Test Case: https://w3-bugs.tivo.com/tr_show_case.cgi?case_id=393657
        :return:
        """
        self.menu_page.go_to_settings(self)
        # verify settings options
        menu = self.menu_page.get_parental_controls_menu_item_label()
        if menu == self.menu_labels.LBL_PARENTAL_CONTROLS_SHORTCUT:
            if Settings.is_managed():
                menuitem = self.menu_labels.SETTINGS_OPTIONS_MANAGED
            else:
                menuitem = self.menu_labels.SETTINGS_OPTIONS_UNMANAGED
        else:
            if Settings.is_managed():
                menuitem = self.menu_labels.SETTINGS_OPTIONS_MANAGED_WITH_PURCHASE_CONTROLS
            else:
                menuitem = self.menu_labels.SETTINGS_OPTIONS_UNMANAGED_WITH_PURCHASE_CONTROLS
        if not Settings.is_ndvr_applicable():
            menuitem.remove("To Do List")
        self.menu_assertions.verify_menu_items_availability(menuitem)
        # verify accessibility options
        self.menu_page.select_menu_items(self.menu_labels.LBL_ACCESSIBILITY)
        if "b-hydra-streamer-1-7" in Settings.branch.lower():
            self.menu_assertions.verify_accesssibility_menu_items(self.menu_labels.ACCESSIBILITY_MENU_ITEMS)
        else:
            self.menu_assertions.verify_accesssibility_menu_items(self.menu_labels.ACCESSIBILITY_MENUITEMS)
        self.menu_page.menu_press_back()
        # verify onepass manager
        self.menu_page.select_menu_items(self.menu_labels.LBL_ONEPASS_MANAGER)
        self.home_assertions.verify_screen_title(self.menu_labels.LBL_ONEPASS_MANAGER_SCREENTITLE)
        self.menu_page.menu_press_back()
        # verify todolist
        if Settings.is_ndvr_applicable():
            self.menu_page.select_menu_items(self.menu_labels.LBL_TODO_LIST)
            self.home_assertions.verify_screen_title(self.menu_labels.LBL_TODO_LIST_SCREENTITLE)
            self.menu_page.menu_press_back()
        # verify user preferences options
        self.menu_page.select_menu_items(self.menu_labels.LBL_USER_PREFERENCES)
        self.menu_assertions.verify_user_preferences_menu_items(self.menu_labels.USER_PREFERENCES_OPTIONS)
        self.menu_page.menu_press_back()
        # verify parental controls options
        menu = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu_items(menu)
        if menu == self.menu_labels.LBL_PARENTAL_CONTROLS_SHORTCUT:
            menuitem = self.menu_labels.PARENTAL_CONTROLS_MENUITEMS
        else:
            menuitem = self.menu_labels.PARENTAL_AND_PURCHASE_CONTROLS_MENUITEMS
        self.menu_assertions.verify_parental_controls_menu_items(menuitem)
        self.menu_page.menu_press_back()
        # verify audio settings options
        self.menu_page.select_menu_items(self.menu_labels.LBL_AUDIO_SETTINGS)
        self.menu_assertions.verify_audio_settings_menu_items(self.menu_labels.AUDIO_SETTINGS_MENUITEMS)
        self.menu_page.menu_press_back()
        # verify remote settings options
        if Settings.is_managed():
            self.menu_page.select_menu_items(self.menu_labels.LBL_REMOTE_SETTINGS)
            if Settings.test_environment.lower() == "usqe1":
                self.menu_assertions.verify_remote_settings_menu_items([self.menu_labels.LBL_PAIR_YOUR_REMOTE_BOX])
            else:
                device_name = self.menu_assertions.get_device_name(self)
                self.menu_assertions.verify_remote_settings_menu_items(
                    [self.menu_labels.LBL_PAIR_YOUR_REMOTE + " " + device_name])
            self.menu_page.menu_press_back()

    @pytest.mark.p1_regression
    @pytest.mark.bc_to_fss
    @pytest.mark.parametrize("feature_status_feature", [(FeaturesList.PURCHASE_PIN)])
    @pytest.mark.parametrize("body_config_feature", [(BodyConfigFeatures.PURCHASE_PIN)])
    @pytest.mark.parametrize("device_info_store_feature", [(DeviceInfoStoreFeatures.PURCHASE_PIN)])
    @pytest.mark.parametrize("req_type", ["NO_REQ"])
    @pytest.mark.parametrize("bc_state, fs_state", [(False, False), (False, True), (True, False), (True, True)])
    @pytest.mark.usefixtures("setup_cleanup_return_initial_feature_state")
    @pytest.mark.notapplicable(Settings.is_devhost(), reason="Does not support reboot")
    @pytest.mark.notapplicable(not Settings.is_internal_mso(), reason="Not allowed for External MSOs")
    @pytest.mark.timeout(Settings.timeout)
    def test_10464399_purchase_pin_from_body_config_to_feature_status(self, request, feature_status_feature,
                                                                      device_info_store_feature, body_config_feature,
                                                                      req_type, bc_state, fs_state):
        """
        Verify "Purchase Controls" option in Settings.
        Only feature state in featureStatus should affect feature enabling/disabling.
        bc_state = feature state in bodyConfig, fs_state = feature state in featureStatus.

        Xray:
            https://jira.tivo.com/browse/FRUM-663
            https://jira.tivo.com/browse/FRUM-738
            https://jira.tivo.com/browse/FRUM-823
            https://jira.tivo.com/browse/FRUM-885

        Testrail:
            https://testrail.tivo.com//index.php?/cases/view/10464411
            https://testrail.tivo.com//index.php?/cases/view/10464399
            https://testrail.tivo.com//index.php?/cases/view/11124432
            https://testrail.tivo.com//index.php?/cases/view/11124431
        """
        request.config.cache.set("is_relaunch_needed", True)
        self.iptv_prov_api.device_info_store(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn),
            self.service_api.get_device_type(),
            self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
            device_info_store_feature, fs_state)
        self.service_api.update_features_in_body_config(body_config_feature, is_add=bc_state)
        self.menu_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.service_api.check_feature_with_body_search(body_config_feature, expected=bc_state)
        self.service_api.check_feature_with_feature_status_search(feature_status_feature, expected=fs_state)
        self.menu_page.go_to_parental_controls(self)
        self.menu_assertions.verify_menu_item_available(self.menu_labels.LBL_PURCHASE_CONTROLS, expected=fs_state)

    @pytestrail.case("C12792158")
    @pytest.mark.p1_regression
    @pytest.mark.compliance
    @pytest.mark.parental_control
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_124958_parental_controls_PIN_check(self):
        """
        Description:
        To verify the PIN check while accessing parental controls from TiVo Central in Hydra menus
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
        self.menu_page.menu_press_back()
        self.menu_page.wait_for_screen_ready(self.menu_labels.LBL_MENU_SCREEN)
        self.menu_page.select_menu(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()

    # @pytest.mark.p1_regression
    @pytest.mark.hospitality
    @pytest.mark.usefixtures("setup_cleanup_bind_hsn", "setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.notapplicable(not Settings.is_technicolor() and not Settings.is_jade() and not Settings.is_jade_hotwire(),
                               "This test is applicable only for Technicolor boxes")
    @pytest.mark.notapplicable(not ExecutionContext.service_api.get_feature_status(FeaturesList.HOSPITALITY, True),
                               "This test is applicable only for accounts with Hospitality Mode = ON")
    @pytest.mark.notapplicable(Settings.is_dev_host(),
                               "There are some specific actions that are made by Technicolor box firmware")
    def test_5413280_hospitality_device_clear_parental_controls(self):
        """
        Verify if Parental Controls is cleared after making Device Clear

        Testrail:
            https://testrail.corporate.local/index.php?/cases/view/5413280
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        # HSN binding right after device clearing due to https://jira.xperi.com/browse/CA-20547
        self.iptv_prov_api.device_clear(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn))
        self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                    self.service_api.getPartnerCustomerId(Settings.tsn))
        self.menu_page.reconnect_dut_after_reboot(180)
        self.apps_and_games_assertions.select_continue_wait_for_home_screen_to_load(self, is_hospitality_screen_omitted=True)
        self.menu_assertions.verify_no_pin_chanllenge_on_parental_controls_entrance(self)

    # @pytest.mark.p1_regression
    @pytest.mark.hospitality
    @pytest.mark.usefixtures("setup_cleanup_bind_hsn")
    @pytest.mark.notapplicable(not Settings.is_technicolor() and not Settings.is_jade() and not Settings.is_jade_hotwire(),
                               "This test is applicable only for Technicolor boxes")
    @pytest.mark.notapplicable(not ExecutionContext.service_api.get_feature_status(FeaturesList.HOSPITALITY, True),
                               "This test is applicable only for accounts with Hospitality Mode = ON")
    @pytest.mark.notapplicable(Settings.is_dev_host(),
                               "There are some specific actions that are made by Technicolor box firmware")
    def test_5413622_hospitality_device_clear_onepass(self):
        """
        Verify if OnePasses are cleared after making Device Clear

        Testrail:
            https://testrail.corporate.local/index.php?/cases/view/5413622
        """
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_assertions.verify_guide_title()
        channel = self.service_api.get_random_encrypted_unencrypted_channels(encrypted=None, subtitle=True)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        self.guide_page.get_live_program_name(self, raise_error_if_no_text=False)
        self.guide_page.create_one_pass_on_record_overlay(self)
        self.menu_page.go_to_one_pass_manager(self)
        self.menu_assertions.verify_one_pass_exists()
        # HSN binding right after device clearing due to https://jira.xperi.com/browse/CA-20547
        self.iptv_prov_api.device_clear(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn))
        self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                    self.service_api.getPartnerCustomerId(Settings.tsn))
        self.menu_page.reconnect_dut_after_reboot(180)
        self.apps_and_games_assertions.select_continue_wait_for_home_screen_to_load(self, is_hospitality_screen_omitted=True)
        self.home_page.back_to_home_short()
        self.home_page.select_menu_shortcut(self.home_labels.LBL_MENU_SHORTCUT)
        self.menu_page.nav_to_top_of_list()
        self.menu_page.select_menu_category(self.menu_labels.LBL_SETTINGS_SHORTCUT)
        self.menu_page.select_menu_items(self.guide_labels.LBL_ONEPASS_MANAGER)
        self.menu_assertions.verify_onepass_manager_empty_screen()

    @pytestrail.case("C12792149")
    @pytest.mark.p1_regression
    @pytest.mark.menu
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_335908_branding_check_for_system_info_menu_screens(self):
        """
        TC: 335908
        To verify mso branding icon in System Info - Menu items screen
        :return:
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_SYSTEM_INFO)
        self.menu_assertions.verify_menu_items_availability(self.menu_labels.LBL_SYSTEM_INFO_SHORTCUTS)
        self.menu_page.select_and_verify_branding(self.menu_labels.LBL_SYSTEM_INFO_SHORTCUTS)

    @pytestrail.case("C12792612")
    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.actionscreen
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_delete_book_marks")
    def test_271460_moviescreen_watchnow_and_test_339618_streamingoptions(self):
        """
        Verify Movie Screen displays the strip WATCH_NOW strip in the Navigation List
        :return:
        """
        self.home_page.go_to_what_to_watch(self)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_PRIMARY_SCREEN, 30000)
        self.menu_page.menu_navigate_left_right(1, 0)
        self.my_shows_page.wait_for_screen_ready(self.home_labels.LBL_WTW_SIDE_PANEL, 30000)
        self.menu_page.select_menu_items(self.home_labels.LBL_MOVIES)
        self.my_shows_page.wait_for_screen_ready(self.my_shows_labels.LBL_MOVIE_SCREEN, 30000)
        self.menu_assertions.validate_watch_now_streamingoption_strip(self)

    @pytestrail.case("C12792147")
    @pytest.mark.p1_regression
    @pytest.mark.menu
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_335910_branding_check_for_userpreferences_menu_screens(self):
        """
        TC: 355910
        To verify mso branding icon in user preferences - Menu items screen
        :return:
        """
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.select_and_verify_branding(self.base.menu_list())

    # @pytestrail.case("C12792148")
    @pytest.mark.p1_regression
    @pytest.mark.menu
    @pytest.mark.xray('FRUM-62306')
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif("b-hydra-streamer-1-7" in Settings.branch.lower(), reason="Device does not support Tips & tricks")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_335906_branding_check_for_system_account_screen(self):
        """
        TC: 335906
        To verify mso branding icon in user preferences - Menu items screen
        :return:
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_assertions.verify_menu_items_availability(self.menu_labels.LBL_SYSTEM_AND_ACCOUNT_MENU_ITEMS)
        self.menu_page.select_and_verify_branding(self.menu_labels.LBL_SYSTEM_AND_ACCOUNT_MENU_ITEMS,
                                                  title_validation=True)

    @pytestrail.case("C12792150")
    @pytest.mark.p1_regression
    @pytest.mark.menu
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_335905_menu_settings(self):
        """
        TC:335905
        Ability to go into settings and check for brand logo and screen title
        :return:
        """
        self.menu_page.go_to_settings(self)
        self.menu_page.select_and_verify_branding(self.menu_page.get_settings_menu_items_list(), title_validation=True)

    @pytestrail.case("C12792154")
    @pytest.mark.p1_regression
    @pytest.mark.menu
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.timeout(Settings.timeout)
    def test_329861_onepass_manager_list_items(self):
        """
        Verify List Items details in OnePass Manager screen for Streamer.
        :return:
        """
        channel = self.service_api.get_recordable_non_movie_channel(filter_channel=True)
        if not channel:
            pytest.skip("Recordable episodic channels are not found.")
        self.home_page.go_to_guide(self)
        self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        title = self.guide_page.get_live_program_name(self)
        self.guide_page.create_one_pass_on_record_overlay(self, streaming_only=True)
        self.menu_page.go_to_one_pass_manager(self)
        self.home_assertions.verify_screen_title(self.menu_labels.LBL_ONEPASS_MANAGER_SCREENTITLE)
        self.menu_page.verify_the_streaming_only_option_item_details(self, title)

    @pytestrail.case("C12792151")
    @pytest.mark.p1_regression
    @pytest.mark.menu
    @pytest.mark.timeout(Settings.timeout)
    def test_267946_verify_menu_screen_content(self):
        """
        TC:267946
        Verify the Content of the Menu screen
        :return
        """
        self.menu_page.go_to_menu_screen(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_menu_screen_title()
        self.menu_assertions.verify_menu_strip_items(self)

    @pytestrail.case("C12792159")
    @pytest.mark.p1_regression
    @pytest.mark.menu
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_329266_change_and_check_audio_languages(self):
        """
        TC:267946 - change and verify audio setting languages
        :return
        """
        self.menu_page.go_to_audio_settings(self)
        self.menu_page.change_and_verify_audio_languages(self)

    @pytestrail.case("C12792157")
    @pytest.mark.p1_regression
    @pytest.mark.wtw
    @pytest.mark.cloudcore_wtw_predictions
    @pytest.mark.timeout(Settings.timeout)
    def test_333435_WTW_Collection_contentstrip_display(self):
        """
        TC:333435
        Verify that W2W-Nav_List_Items "Collections" Content Strip is displayed correct
        :return
        """
        self.menu_page.navigate_and_select_wtw_side_panel_category(self, self.home_labels.LBL_COLLECTIONS)
        self.wtw_page.wait_for_screen_ready()
        self.menu_assertions.verify_WTW_content_strip_title(self.home_labels.LBL_COLLECTIONS)

    @pytestrail.case("C12792153")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_350238_pc_on_user_preference(self):
        """
        TC:350238
        Verifying "Parental Control" PIN on User Preferences.
        :return:
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.go_to_user_preferences(self)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.home_assertions.verify_screen_title(self.menu_labels.LBL_USER_PREFERENCES_TITLE)

    @pytestrail.case("C12792152")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.compliance
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_350239_verify_parental_control_with_incorrect_pin(self):
        """
        Verify Parental Control with incorrect PIN.
        :return:
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.go_to_parental_controls(self)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_wrong_pc_password(self)
        self.menu_assertions.verify_wrong_PIN_overlay()

    @pytestrail.case("C12792155")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.compliance
    @pytest.mark.notapplicable(Settings.is_managed())
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_330628_pc_check_with_pin_acceptance(self):
        """
        Verify pressing SELECT button on the right-most PIN box in Enter PIN Overlay commits the input and
        navigate as per directions in the individual UI spec
        :return:
        """
        self.menu_page.go_to_parental_controls(self)
        self.menu_page.select_menu_items(self.menu_page.get_parental_controls_menu_item_label())
        self.menu_assertions.verify_create_PIN_overlay()
        self.menu_page.check_enter_pin_overlay_first_spinner_box_and_values()
        self.menu_assertions.store_the_value_and_move_the_highlight_to_next_box(self)
        self.home_assertions.verify_screen_title(self.menu_labels.LBL_PARENTAL_CONTROLS_TITLE)

    @pytestrail.case("C12792156")
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.compliance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_330623_pc_check_with_right_navigation(self):
        """
        Verify pressing LEFT/RIGHT buttons on Enter PIN Overlay does nothing on Managed devices or
        move to Next pin box on Unmanaged devices
        :return:
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.go_to_parental_controls(self)
        self.menu_assertions.verify_enter_PIN_overlay()
        if Settings.is_managed():
            self.menu_assertions.check_enter_pin_overlay_navigation()
        else:
            self.menu_page.check_enter_pin_overlay_first_spinner_box_and_values()
            self.menu_assertions.store_the_value_and_move_the_highlight_to_next_box(self)

    @pytest.mark.p1_regression
    @pytest.mark.xray("FRUM-667")
    # @pytest.mark.test_stabilization
    @pytest.mark.deeplink
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(not Settings.is_apple_tv() and not Settings.is_fire_tv(),
                               reason="This feature is only for Fire Tv and Apple Tv.")
    @pytest.mark.msofocused
    def test_11116760_tips_tricks_youtube_deeplinking_not_supported_device(self):
        """
        Verify the behavior when the Tips & Tricks option is selected on deeplinking nonsupported devices.
        :return:
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_TIPS_TRICKS)
        self.menu_assertions.verify_tips_and_tricks_screen_text(self)

    # @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.menu
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_13525044_validate_one_pass_and_recording_options_in_settings(self):
        """
        Ability to go into settings and check for one_pass and recording_options
        :return:
        """
        self.menu_page.go_to_user_preferences(self)
        option_name = self.menu_page.get_onepass_option_name(self)
        self.menu_page.select_menu_items(option_name)
        self.menu_assertions.validate_one_pass_and_recording_option(self, option_name)

#     @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.parental_control
    @pytest.mark.vod
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_13525045_hide_adult_content(self):
        """
        Hiding Adult content
        """
        self.menu_page.go_to_parental_controls(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.enter_default_parental_control_password(self)  # to confirm
        self.menu_page.select_menu_items(self.menu_labels.LBL_HIDE_ADULT_CONTENT)
        self.menu_page.select_menu_items(self.menu_labels.LBL_HIDE_ADULT_NEW)
        self.vod_page.go_to_vod(self)
        menu_array = self.vod_assertions.get_vod_menu_contents()
        self.vod_assertions.verify_item_in_array(menu_array, self.vod_labels.LBL_ADULT_MENUS)

#     @pytest.mark.test_stabilization
    @pytest.mark.p1_regression
    @pytest.mark.compliance
    @pytest.mark.subtitle_and_closed_caption
    @pytest.mark.timeout(Settings.timeout)
    def test_312064633_verify_preview_text_for_subtitles_and_closedcaption(self):
        self.menu_page.go_to_accessibility(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_page.navigate_to_subtitles_and_closed_captioning_language()
        self.menu_page.wait_for_screen_ready()
        actual_preview_text = self.menu_page.get_preview_text(refresh=True)
        self.menu_assertions.verify_preview_text(actual_preview_text)

    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.p1_regression
    @pytest.mark.ndvr
    @pytest.mark.op_rec_bm_acceptance
    @pytest.mark.timeout(Settings.timeout)
    def test_329707704_verify_default_onepass_option(self):
        """
        :desription:
        To Verify the default value for record in onepass options settings screen  """
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_page.select_menu_items(self.menu_labels.LBL_ONEPASS_OPTIONS)
        self.menu_page.wait_for_screen_ready()
        self.menu_page.select_menu_items(self.menu_labels.LBL_RECORD_MENU)
        self.menu_assertions.verify_item_option_focus(self.menu_labels.LBL_NEW_ONLY)

    @pytest.mark.compliance
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    # @pytest.mark.p1_regression
    @pytest.mark.subtitle_tests
    @pytest.mark.timeout(Settings.timeout)
    def test_312064634_verify_subtitle_language_after_clear_cache(self):
        """
        To verify after cache and data clear, "Subtitles & Closed Captioning Language" screen options
        reset to default
        """
        self.menu_page.go_to_accessibility(self)
        self.menu_page.change_subtitle_language(self.menu_labels.LBL_SPANISH, refresh=True)
        self.home_page.clear_cache_launch_hydra_app()
        self.menu_page.wait_for_screen_ready()
        self.menu_page.go_to_accessibility(self)
        if self.home_page.is_overlay_shown():
            self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_subtitle_lang_change(self.menu_labels.LBL_ENGLISH, refresh=True)

    @pytestrail.case("C11687782")
    @pytest.mark.p1_regression
    @pytest.mark.frumos_13
    @pytest.mark.platform_cert_smoke_test
    @pytest.mark.usefixtures("setup_parental_control")
    @pytest.mark.usefixtures("setup_clear_subscriptions")
    @pytest.mark.timeout(Settings.timeout)
    def test_c11687782_to_do_list_hide_adult_content_on(self, setup_cleanup_parental_and_purchase_controls):  # noqa F815
        """
        :description:
           To verify the PIN challenge on TO_DO_LIST_TITLE for an adult program when
           #PARENTAL CONTROLS STATE# is ON and PCHideAdult is
        :testrail: https://testrail.tivo.com/index.php?/cases/view/11687969
        """
        channels = self.guide_page.get_streamable_adult_content(self)
        if len(channels) < 1:
            pytest.skip("could not find adult channel")
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channels[0])
        show_name = self.guide_page.get_focussed_grid_item(self)
        self.guide_page.create_one_pass_on_record_overlay(self)
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_page.select_menu(self.menu_labels.LBL_PARENTAL_CONTROLS)
        self.menu_assertions.verify_create_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_assertions.verify_confirm_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.toggle_hide_adult_content()
        self.menu_page.go_to_to_do_list(self)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.menu_press_back()
        self.home_assertions.verify_screen_title(self.menu_labels.LBL_MENU_TITLE)
        self.screen.base.press_left()
        self.screen.base.press_enter()
        self.screen.base.press_enter()
        self.menu_page.select_menu_items(self.menu_labels.LBL_TODO_LIST)
        self.guide_assertions.verify_show_name_present(show_name)
        self.my_shows_page.select_show(show_name)
        self.menu_assertions.verify_enter_PIN_overlay()

    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.subscription_management
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-13"))
    @pytest.mark.notapplicable(not Settings.is_internal_mso())
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-1231")
    def test_T395351290_operator_features(self):
        """
        :description:
           To verify the operator feature option in settings -> User Prefrence
           https://testrail.tivo.com//index.php?/tests/view/395351290
        """
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_page.select_menu(self.menu_labels.LBL_OPERATOR_FEATURES)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_OPERATOR_FEATURES_SCREENTITLE)

    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.subscription_management
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-13"))
    @pytest.mark.notapplicable(not Settings.is_internal_mso())
    @pytest.mark.msofocused
    @pytest.mark.xray("FRUM-1347")
    def test_T395744640_ndvr_operator_features_settings(self):
        """
        :description:
           To verify the options displayed in Operator feature settings screen when ndvr is enabled and disabled.
           https://testrail.tivo.com//index.php?/tests/view/363050100
        """
        ndvr = self.api.get_feature_status(FeaturesList.NDVR)
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_page.select_menu(self.menu_labels.LBL_OPERATOR_FEATURES)
        self.menu_page.wait_for_screen_ready()
        label = self.menu_labels.LBL_OPERATOR_FEATURES_OPTIONS_REMOVE_NDVR if ndvr else\
            self.menu_labels.LBL_OPERATOR_FEATURES_OPTIONS_ADD_NDVR
        for i in label:
            self.menu_assertions.verify_menu_item_available(i)

    @pytest.mark.notapplicable(not Settings.is_managed())
    @pytest.mark.subscription_management
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch("b-hydra-streamer-1-13"))
    @pytest.mark.notapplicable(not Settings.is_internal_mso())
    def test_T363050100_socu_operator_features_settings(self):
        """
        :description:
           To verify the options displayed in Operator feature settings screen when socu is enabled and disabled.
        """
        socu = self.api.get_feature_status(FeaturesList.SOCU)
        self.menu_page.go_to_user_preferences(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_page.select_menu(self.menu_labels.LBL_OPERATOR_FEATURES)
        self.menu_page.wait_for_screen_ready()
        label = self.menu_labels.LBL_DISABLE_SOCU if socu else self.menu_labels.LBL_ENABLE_SOCU
        self.menu_assertions.verify_menu_item_available(label)

    @pytest.mark.crash_signature
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for Managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               "This test is applicable only for Hydra v1.15 and higher")
    def test_frum_69421_tombstone_and_verify_the_crash_signature(self):
        """
        :description:
            To verify tombstone the crash signature
            https://jira.tivo.com/browse/FRUM-69421
        """
        self.home_page.update_test_conf_and_reboot(fast=True, ENABLE_BACKDOOR_CRASH_SIMULATION_SCREEN="true")
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.go_to_system_info(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFO_TITLE)
        self.menu_page.go_to_simulate_crash(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)
        self.menu_page.go_to_tombstone(self)
        self.menu_assertions.verify_string_in_adb_logs(self.menu_labels.LBL_TOMBSTONE_CRASH)

    @pytest.mark.parametrize("req_type", [NotificationSendReqTypes.NSR])
    @pytest.mark.usefixtures("cleanup_enabling_internet")
    @pytest.mark.usefixtures("relaunch_hydra_app")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15))
    @pytest.mark.notapplicable(Settings.transport != "SSH", reason="Working with disconnected state requires transport = SSH")
    @pytest.mark.notapplicable(Settings.is_dev_host(), reason="Does not support reboot")
    @pytest.mark.notapplicable(Settings.is_external_mso())
    def test_21571809_service_call_disconnect_nsr_connect(self, req_type):
        """
        Retry Policy while in Disconnected State: Send Service Call Notification -
        Connect - Wait retry - Re-enter Home - Check overlay

        Testrail:
            https://testrail.tivo.com/index.php?/cases/view/21571809

        Xray:
            https://jira.xperi.com/browse/FRUM-1993
        """
        self.home_page.back_to_home_short()
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_DOWN)
        self.home_page.send_fcm_or_nsr_notification(req_type=req_type, payload_type=RemoteCommands.SERVICE_CALL, is_retry=True)
        init_time = datetime.now()
        self.home_assertions.verify_connected_disconnected_state_happened(error_code=self.home_labels.LBL_ERROR_CODE_C228)
        cur_time = datetime.now()
        self.home_page.pause(310 - (cur_time - init_time).total_seconds(),
                             "Staying in the disconnected state a bit", is_negative_time_to_0=True)
        self.home_page.change_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        self.home_assertions.verify_bridge_state(self.home_labels.LBL_SET_BRIDGE_UP)
        # Handling new behavior of reconnects (since Hydra v1.16 IPTV-22111)
        init_time = datetime.now()
        self.home_assertions.verify_connected_disconnected_state_happened(wait_disconnect=False, is_select=False)
        self.home_page.go_to_guide(self)
        cur_time = datetime.now()
        self.home_page.pause((290 + 3) - (cur_time - init_time).total_seconds(),
                             "Waiting NSR to be sent", is_negative_time_to_0=True)
        self.home_page.press_back_button(refresh=False)
        self.home_assertions.verify_overlay_title(self.home_labels.LBL_RESTART_TO_APPLY_UPDATES_OVERLAY)

    @pytest.mark.p1_regression
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.skipif(Settings.is_apple_tv() or Settings.is_fire_tv(),
                        reason="Deeplinking not supported on Fire Tv and Apple Tv.")
    def test_11116751_verify_tips_and_tricks_preview_pane(self):
        """
        Verify whether user able to navigate to tips & tricks menu and validate the preview pane
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.nav_to_menu_by_substring(self.menu_labels.LBL_TIPS_AND_TRICKS_YOUTUBE)
        device_name = self.menu_assertions.get_device_name(self)
        expected_preview_text = self.menu_labels.LBL_TIPS_AND_TRICKS_YOUTUBE_PREVIEW + device_name + "."
        self.menu_assertions.verify_preview_pane(expected_preview_text, 'previewpanel')

    @pytest.mark.crash_signature
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for Managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               "This test is applicable only for Hydra v1.15 and higher")
    def test_frum_69625_Java_crash_and_verify_the_crash_signature(self):
        """
        To verify java crash signature
        https://jira.xperi.com/browse/FRUM-69625
        """
        self.home_page.update_test_conf_and_reboot(fast=True, ENABLE_BACKDOOR_CRASH_SIMULATION_SCREEN="true")
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.go_to_system_info(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFO_TITLE)
        self.menu_page.go_to_simulate_crash(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)
        self.menu_page.go_to_java_crash(self)
        self.menu_page.pause(self.home_labels.LBL_FOOTER_ICON_ACTIVE_USER_ANIMATION_TIME)
        self.menu_assertions.verify_string_in_adb_logs(self.menu_labels.LBL_JAVA_CRASH_RESULT)

    @pytest.mark.crash_signature
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for Managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               "This test is applicable only for Hydra v1.15 and higher")
    def test_frum_69424_ANR_and_verify_the_crash_signature(self):
        """
        To verify ANR crash signature
        https://jira.xperi.com/browse/FRUM-69424
        """
        self.home_page.update_test_conf_and_reboot(fast=True, ENABLE_BACKDOOR_CRASH_SIMULATION_SCREEN="true")
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.go_to_system_info(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFO_TITLE)
        self.menu_page.go_to_simulate_crash(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)
        self.menu_page.go_to_anr_crash(self)
        self.screen.base.press_up()
        self.screen.base.press_down()
        self.menu_page.pause(self.watchvideo_labels.LBL_RESUME_PLAYING_OVERLAY_TIMEOUT)
        self.menu_assertions.verify_string_in_adb_logs(self.menu_labels.LBL_ANR_CRASH_RESULT)

    @pytest.mark.msofocused
    @pytest.mark.lite_branding
    @pytest.mark.branding_check
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_42699_distribtuion_name_validation_use_case_1(self):
        """
        To verify Distributor name resource map variable
        https://jira.xperi.com/browse/XTQ-36911
        """
        value = self.service_api.branding_ui(field="distributor_name")
        if not value:
            pytest.skip("Failed to get {} value from Ui branding bundle response".format("distributorName"))
        self.menu_page.go_to_settings(self)
        self.menu_page.nav_to_menu(self.menu_labels.LBL_AUDIO_SETTINGS)
        self.menu_page.wait_for_screen_ready()
        self.screen.refresh()
        preview_text = self.screen.get_screen_dump_item('previewpanel')['text']
        self.menu_assertions.validate_branding_bundle_field_value(value, preview_text)

    @pytest.mark.msofocused
    @pytest.mark.lite_branding
    @pytest.mark.branding_check
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_42699_distribtuion_name_validation_use_case_2(self):
        """
        To Verify Distributor name resource map variable
        https://jira.xperi.com/browse/XTQ-36911
        """
        value = self.service_api.branding_ui(field="distributor_name")
        if not value:
            pytest.skip("Failed to get {} value from Ui branding bundle response".format("distributorName"))
        items = [self.menu_labels.LBL_HELP, self.menu_labels.LBL_SYSTEM_INFO]
        for item in items:
            self.menu_page.go_to_system_info_screen(self, press_enter=False)
            if not self.menu_page.is_menu_focus() and self.menu_page.is_strip_focus and \
               self.menu_page.strip_focus() == self.menu_labels.LBL_SYSTEM_AND_ACCOUNT:
                self.menu_page.screen.base.press_enter()
            self.menu_page.nav_menu_items(item)
            self.menu_page.wait_for_screen_ready()
            self.screen.refresh()
            preview_text = self.screen.get_screen_dump_item('previewpanel')['text']
            self.menu_assertions.validate_branding_bundle_field_value(value, preview_text)

    @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("disable_parental_controls")
    def test_frum_43032_verify_pin_challenge_on_audio_settings(self):
        """
        Verify Pin Challenge when Parental Control ON with Audio Settings
        FRUM-43032
        :return:
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.screen.base.press_back()
        self.menu_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_content_in_category(self.home_labels.LBL_DEVICE_SETTINGS_TITLE)
        self.menu_page.select_menu_items(self.menu_labels.LBL_AUDIO_SETTINGS)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.screen.base.press_back()

    @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("disable_parental_controls")
    def test_frum_44656_verify_pin_challenge_on_onepass_manager(self):
        """
        Verify Pin Challenge when Parental Control ON with Onepass Manager
        FRUM-44656
        :return:
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.screen.base.press_back()
        self.menu_page.wait_for_screen_ready()
        self.my_shows_assertions.verify_content_in_category(self.home_labels.LBL_DEVICE_SETTINGS_TITLE)
        self.menu_page.select_menu_items(self.menu_labels.LBL_ONEPASS_MANAGER)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.screen.base.press_back()

    @pytest.mark.crash_signature
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for Managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               "This test is applicable only for Hydra v1.15 and higher")
    def test_frum_69423_Assert_and_verify_the_crash_signature(self):
        """
        To verify Assert crash signature
        https://jira.xperi.com/browse/FRUM-69423
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.go_to_system_info(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFO_TITLE)
        self.menu_page.go_to_simulate_crash(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)
        self.menu_page.go_to_assert_crash(self)
        self.screen.base.press_enter()
        self.menu_page.pause(self.home_labels.LBL_FOOTER_ICON_ACTIVE_USER_ANIMATION_TIME)
        self.menu_assertions.verify_string_in_adb_logs(self.menu_labels.LBL_ASSERT_RESULT)

    @pytest.mark.crash_signature
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for Managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               "This test is applicable only for Hydra v1.15 and higher")
    def test_frum_69420_Assert_Restart_and_verify_the_crash_signature(self):
        """
        To verify Assert Restart crash signature
        https://jira.xperi.com/browse/FRUM-69420
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.go_to_system_info(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFO_TITLE)
        self.menu_page.go_to_simulate_crash(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)
        self.menu_page.go_to_assert_restart(self)
        self.screen.base.press_enter()
        self.menu_page.pause(self.home_labels.LBL_FOOTER_ICON_ACTIVE_USER_ANIMATION_TIME)
        self.menu_assertions.verify_string_in_adb_logs(self.menu_labels.LBL_ASSERT_RESTART)

    @pytest.mark.crash_signature
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for Managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               "This test is applicable only for Hydra v1.15 and higher")
    def test_frum_69425_ANR_by_out_of_memory_and_verify_the_crash_signature(self):
        """
        To verify ANR by out of memory crash signature
        https://jira.xperi.com/browse/FRUM-69425
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.go_to_system_info(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFO_TITLE)
        self.menu_page.go_to_simulate_crash(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)
        self.menu_page.go_to_anr_outOfMemory(self)
        self.menu_page.pause(self.home_labels.LBL_FOOTER_ICON_ACTIVE_USER_ANIMATION_TIME)
        self.menu_assertions.verify_string_in_adb_logs(self.menu_labels.LBL_OUTOFMEMORY)

    @pytest.mark.crash_signature
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for Managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               "This test is applicable only for Hydra v1.15 and higher")
    def test_frum_69426_Haxe_app_died_and_verify_the_crash_signature(self):
        """
        To verify haxe app died crash signature
        https://jira.xperi.com/browse/FRUM-69426
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.go_to_system_info(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFO_TITLE)
        self.menu_page.go_to_simulate_crash(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)
        self.menu_page.go_to_haxeAppDied(self)
        self.menu_page.pause(self.home_labels.LBL_AUTOMATION_PAUSE_TIME)
        self.menu_assertions.verify_string_in_adb_logs(self.menu_labels.LBL_HAXE_DIED)

    @pytest.mark.crash_signature
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for Managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               "This test is applicable only for Hydra v1.15 and higher")
    def test_frum_69427_Haxe_app_crash_and_verify_the_crash_signature(self):
        """
        To verify haxe app crash signature
        https://jira.xperi.com/browse/FRUM-69427
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.go_to_system_info(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFO_TITLE)
        self.menu_page.go_to_simulate_crash(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)
        self.menu_page.go_to_haxe_app(self)
        self.screen.base.press_enter()
        self.menu_page.pause(self.home_labels.LBL_FOOTER_ICON_ACTIVE_USER_ANIMATION_TIME)
        self.menu_assertions.verify_string_in_adb_logs(self.menu_labels.LBL_HAXE_CRASH)

    @pytest.mark.crash_signature
    @pytest.mark.notapplicable(Settings.is_unmanaged(), "Applicable only for Managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_15),
                               "This test is applicable only for Hydra v1.15 and higher")
    def test_frum_61729_Assert_continue_and_verify_the_crash_signature(self):
        """
        To verify assert continue crash signature
        https://jira.xperi.com/browse/FRUM-61729
        """
        self.home_page.update_test_conf_and_reboot(fast=True, ENABLE_BACKDOOR_CRASH_SIMULATION_SCREEN="true")
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.go_to_system_info(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SYSTEM_INFO_TITLE)
        self.menu_page.go_to_simulate_crash(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)
        self.menu_page.go_to_assert_continue(self)
        self.screen.base.press_enter()
        self.menu_assertions.verify_screen_title(self.menu_labels.LBL_SIMULATE_CRASH_TITLE)

    @pytest.mark.restart_reason
    @pytest.mark.notapplicable(Settings.is_managed(), "This test case is not applicable for managed devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "This test is applicable only for Hydra v1.13 and higher")
    def test_frum_69419_signOut_and_relaunch_the_app(self):
        self.home_page.unamanged_sign_out(self)
        self.screen.base.launch_application(Settings.app_package)
        self.menu_page.wait_for_screen_ready()
        self.home_page.bind_license(self)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_string_in_adb_logs(self.home_labels.LBL_SIGNOUT_RESULT)

    @pytest.mark.restart_reason
    @pytest.mark.notapplicable(Settings.is_managed() or Settings.is_apple_tv(),
                               "This test case is not applicable for managed and appletv devices")
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_13),
                               "This test is applicable only for Hydra v1.13 and higher")
    def test_frum_69418_Exit_and_relaunch_the_app(self):
        self.home_page.exit_unmanaged_app(self)
        self.menu_page.pause(self.home_labels.LBL_FOOTER_ICON_IDLE_USER_TIMEOUT)
        self.screen.base.launch_application(Settings.app_package)
        self.menu_page.wait_for_screen_ready()
        self.home_assertions.verify_home_title(self.home_labels.LBL_MENU_SCREENTITLE)
        self.menu_assertions.verify_string_in_adb_logs(self.home_labels.LBL_EXIT_RESULT)

    @pytest.mark.channel_zap
    @pytest.mark.timeout(Settings.longrun_timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    @pytest.mark.usefixtures("setup_parental_control")
    def test_frum_69378_channel_zapping_after_enable_parental_control(self):
        """
        FRUM-69378
        Verify channel zapping across all channels  after enable parental control,turn on HAC,set rating limit to block all
        :return:
        """
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.toggle_hide_adult_content()
        self.menu_page.go_to_set_rating_limit(self)
        self.menu_page.set_rating_limits(rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.menu_page.menu_press_back()
        self.menu_page.select_menu_items(self.menu_labels.LBL_PARENTAL_CONTROLS)
        channel = self.service_api.get_random_live_channel_rich_info(episodic=True, filter_channel=True,
                                                                     transport_type="stream")
        if not channel:
            pytest.skip("Live Channel Not Found")
        self.home_page.goto_live_tv(channel[0][0])
        self.watchvideo_page.channel_change_including_error_channel(self, channel="channel up", channel_name_confirmation=True)
        self.watchvideo_page.channel_change_including_error_channel(self, channel="channel down",
                                                                    channel_name_confirmation=True)

    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("launch_hydra_app_when_script_is_on_ott")
    @pytest.mark.skipif(Settings.is_apple_tv() or Settings.is_fire_tv(),
                        reason="Deeplinking not supported on Fire Tv and Apple Tv.")
    @pytest.mark.xray('FRUM-69601')
    def test_frum_69601_verify_tips_and_tricks_on_youtube_on_supported_device(self):
        """
        FRUM-69601
        Verify the behaviour when select the Tips & Tricks oiption on deeplinking supported device.
        """
        self.menu_page.go_to_system_info_screen(self)
        self.menu_page.nav_to_menu_by_substring(self.menu_labels.LBL_TIPS_AND_TRICKS_YOUTUBE)
        branding_value = self.api.branding_ui()
        channel_url = branding_value.mso_tutorial_channel_info.get(
            'tipsAndTricksWebUrl').get('value') if branding_value.mso_tutorial_channel_info else None
        if channel_url is None:
            pytest.skip("MSO hasn't configured the tips and tricks web url value")
        self.screen.base.press_enter()
        self.apps_and_games_assertions.wait_fo_app_launch(self.apps_and_games_labels.YOUTUBE_PACKAGE_NAME)
        self.apps_and_games_assertions.verify_uri(uri=channel_url)

    @pytest.mark.test_stabilization
    @pytest.mark.timeout(Settings.timeout)
    def test_frum_98270_verify_device_name_resource_map_variable(self):
        """
        FRUM-98270
        Verify DEVICE NAME from settings and UI
        :return:
        """
        device_name = self.menu_assertions.get_device_name(self)
        voice = self.menu_labels.LBL_VOICE_PREVIEW
        access = self.menu_labels.LBL_ACCESSIBILITY_PREVIEW
        branding_value = self.api.branding_ui()
        mso_name = branding_value.distributor_name.get(
            'value') if branding_value.distributor_name else None
        # case1(Remote settings)
        self.home_page.back_to_home_short()
        self.menu_page.go_to_menu_screen(self)
        self.menu_page.select_menu_items(self.menu_labels.LBL_REMOTE_SETTINGS)
        self.menu_page.wait_for_screen_ready()
        self.menu_assertions.verify_device_name_remote_setting(device_name)
        # case2(Voice)
        self.menu_page.go_to_system_info_screen(self)
        self.menu_assertions.verify_menu_items_availability(self.menu_labels.LBL_SYSTEM_AND_ACCOUNT_MENU_ITEMS)
        self.menu_page.select_menu_items(self.menu_labels.LBL_HELP)
        self.menu_page.wait_for_screen_ready()
        self.menu_page.nav_menu_items(self.menu_labels.LBL_VOICE)
        mso = self.menu_page.format_mso_name(mso_name)
        self.menu_assertions.verify_preview_pane(voice + mso + " " + device_name + ".")
        if not Settings.is_managed():
            # case3(Unmanaged devices)
            self.menu_page.go_to_system_info_screen(self)
            self.menu_assertions.verify_menu_items_availability(self.menu_labels.LBL_SYSTEM_AND_ACCOUNT_MENU_ITEMS)
            self.menu_page.select_menu_items(self.menu_labels.LBL_HELP)
            self.menu_page.wait_for_screen_ready()
            self.menu_page.nav_menu_items(self.menu_labels.LBL_ACCESSIBILITY)
            self.menu_assertions.verify_preview_pane(access + device_name + ".")

    @pytest.mark.test_stabilization
    def test_frum_103570_verify_customer_support_name_resource_map_variable(self):
        """
        FRUM-103570
        Verify Customer support Name from settings and preview pane in UI
        """
        mso = self.menu_page.get_mso_name(self)
        if not mso:
            pytest.fail("Failed to get Branding UI Value")
        cust_preview = self.menu_labels.LBL_CUSTOMER_PREVIEW
        self.menu_page.go_to_system_info_screen(self)
        self.menu_assertions.verify_menu_items_availability(self.menu_labels.LBL_SYSTEM_AND_ACCOUNT_MENU_ITEMS)
        self.menu_page.select_menu_items(self.menu_labels.LBL_HELP)
        self.menu_page.wait_for_screen_ready()
        self.menu_page.nav_menu_items(self.menu_labels.LBL_CUSTOMER_SUPPORT)
        self.menu_assertions.verify_preview_pane(cust_preview + mso + " Customer Support.")

    @pytest.mark.hospitality
    @pytest.mark.xray("FRUM-48571")
    @pytest.mark.msofocused_solutions
    @pytest.mark.usefixtures("setup_cleanup_bind_hsn")
    @pytest.mark.notapplicable(not Settings.is_technicolor(), "This test is applicable only for Technicolor boxes")
    @pytest.mark.notapplicable(not ExecutionContext.service_api.get_feature_status(FeaturesList.HOSPITALITY, True),
                               "This test is applicable only for accounts with Hospitality Mode = ON")
    @pytest.mark.notapplicable(Settings.is_dev_host(),
                               "There are some specific actions that are made by Technicolor box firmware")
    def test_48571_hospitality_device_clear_myshows(self):
        """
        Verify TiVo Service settings are cleared after device clearing and login into Hospitality Welcome Screen
        xray:
            https://jira.xperi.com/browse/FRUM-48571
        """
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        channel = self.service_api.get_random_encrypted_unencrypted_channels(encrypted=None, filter_socu=True,
                                                                             OTT_count=1)
        if not channel:
            pytest.skip("Required channels are not found. Hence skipping")
        self.guide_page.enter_channel_number(channel[0][0], confirm=False)
        show = self.guide_page.get_live_program_name(self, raise_error_if_no_text=False)
        self.guide_page.create_one_pass_on_record_overlay(self, streaming_only=True)
        self.home_page.go_to_my_shows(self)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_in_category(show)
        # HSN binding right after device clearing due to https://jira.xperi.com/browse/CA-20547
        self.iptv_prov_api.device_clear(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn))
        self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                    self.service_api.getPartnerCustomerId(Settings.tsn))
        self.menu_page.reconnect_dut_after_reboot(180)
        self.apps_and_games_assertions.select_continue_wait_for_home_screen_to_load(self, is_hospitality_screen_omitted=True)
        self.home_page.back_to_home_short()
        self.home_page.go_to_my_shows(self)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_MYSHOWS_SHORTCUT)
        self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_ALL_SHOWS)
        self.my_shows_assertions.verify_content_not_in_category(self, show)

    @pytest.mark.xray("FRUM-140954")
    @pytest.mark.compliance
    @pytest.mark.eas
    @pytest.mark.parental_control
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_140954_eas_on_parental_controls(self):
        """
        Description:
        To verify correct behavior for EAS event while browsing Settings screens, where Parental Control is needed.
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
        self.home_page.trigger_EAS_validate_eas_response(self, Settings.tsn)
        self.home_page.wait_for_EAS_to_dismiss(timeout=90)
        self.menu_page.menu_press_back()
        self.menu_page.wait_for_screen_ready(self.menu_labels.LBL_MENU_SCREEN)
        self.menu_page.select_menu(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
