from set_top_box.client_api.Menu.conftest import *
from set_top_box.conftest import *
from set_top_box.test_settings import Settings


@pytest.mark.notapplicable(Settings.is_external_mso())
@pytest.mark.usefixtures("setup_menu")
@pytest.mark.parental_control
class TestPCsettingfromPSS:
    """
    As per new functionality PC setting will be pushed when user does not have any pin.
    default pin is 9999 along with following PC setting can be pushed from PPS.

     This class will cover following test cases.
        1. 9916459 - Verify PC setting are pushed from PPS or not.
        2. 9916460 - Verify when PC settings update from user setting first and then PPS.
        3. 9916461 - Verify when PC settings update from PPS first and then User setting.
        4. 9916470 - Verify PC setting update from PPS multiple times.
        5. C12792838
        6. C12792840

     docs:
        http://refpps-provision-integ-01.tpa3.tivo.com:40203/swagger-ui.html#!/device/

    """
    @pytest.mark.frumos_11
    @pytest.mark.pps_pc_settings
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused_solutions
    @pytest.mark.xray("FRUM-1359")
    @pytest.mark.usefixtures("push_parental_controls__from_pps_with_adult_content_true")
    def test_9916459_verify_pc_setting_push_from_PPS(self, remove_parental_controls__from_pps):
        """
               Description:  PPS PC setting update is reflecting on streamer device.

                Following PC setting pushed from PPS and verify those are reflecting in streamer device or not
                Default pin 9999
                hide Adult = True

        """
        self.home_page.clear_cache_launch_hydra_app()
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)
        self.menu_assertions.verify_hide_adult_content_on()

    @pytest.mark.frumos_11
    @pytest.mark.pps_pc_settings
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused_solutions
    @pytest.mark.xray("FRUM-1348")
    @pytest.mark.usefixtures("push_parental_controls__from_pps_with_adult_content_true",
                             "push_parental_controls__from_pps_with_movie_rating_block_all_tv_rating_block_all")
    def test_9916470_verify_pc_setting_update_from_pps_multiple_times(self, remove_parental_controls__from_pps):
        """
               Description:  PC setting(movie_rating: Block all, tv_rating: Block All)pushed from PPS multiple tinms.

                Following PC setting pushed in 1st iterations,
                Default pin 9999
                hide Adult = True

                Following PC setting pushed in 2nd iteration, all changes will be verified in streamer device.
                Highest Allowed movie rating Block all
                Highest Allowed TV rating = Block all

        """
        self.home_page.clear_cache_launch_hydra_app()
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)
        self.menu_assertions.verify_hide_adult_content_on()
        self.menu_page.go_to_set_rating_limit_screen()
        self.menu_assertions.verify_movie_rating_block_all()
        self.menu_assertions.verify_is_tv_rating_block_all()

    # @pytest.mark.test_stabilization
    @pytest.mark.pps_pc_settings
    @pytest.mark.xray("FRUM-1453")
    @pytest.mark.frumos_11
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused
    @pytest.mark.parental_control
    def test_9916460_verify_pc_setting_push_from_userSettings_then_from_PPS(self, request,
                                                                            setup_cleanup_parental_and_purchase_controls
                                                                            ):
        """
              Description:  PC setting(movie_rating,hide Adult content) changed from user settings
              then, PC setting(movie rating) changed from PPS.

              Following PC setting done from streamer device,all changes will be verified in streamer device.
              Default pin 9999
              hide Adult= True
              Highest Allowed movie rating = Allow all
              Highest Allowed TV rating = Allow all

              Following PC setting pushed from PPS, all changes will be verified in streamer device.
              Highest Allowed movie rating = Block all
              Highest Allowed TV rating = Block all

        """
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.menu_page.turnonpcsettings(self, "on", "off")
        request.cls.menu_page.toggle_hide_adult_content()
        movie_rating = self.menu_page.get_highest_movie_rating()
        tv_rating = self.menu_page.get_highest_tv_rating()
        self.menu_page.select_menu_items(self.menu_labels.LBL_SET_RATING_LIMITS)
        self.menu_page.set_rating_limits(rated_movie=movie_rating,
                                         rated_tv_show=tv_rating,
                                         unrated_tv_show=self.menu_labels.LBL_ALLOW_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_ALLOW_ALL_UNRATED)

        # making changes from PPS and verifying on device again
        request.getfixturevalue('push_parental_controls__from_pps_with_movie_rating_block_all_tv_rating_block_all')
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.wait_for_screen_ready(parental_control)
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)
        self.menu_assertions.verify_hide_adult_content_on()
        self.menu_page.go_to_set_rating_limit_screen()
        self.menu_assertions.verify_is_movie_rating_allow_all_except_adult()
        self.menu_assertions.verify_is_tv_rating_allow_all_except_adult()

    # @pytest.mark.test_stabilization
    @pytest.mark.pps_pc_settings
    @pytest.mark.xray("FRUM-1363")
    @pytest.mark.frumos_11
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("push_parental_controls__from_pps_with_adult_content_true",
                             "push_parental_controls__from_pps_with_movie_rating_block_all_tv_rating_block_all")
    def test_9916461_verify_pc_setting_push_from_PPS_then_from_userSettings(self, remove_parental_controls__from_pps):
        """
              Description:  PC setting(hide Adult content) changed from PPS
              then, PC setting(hide Adult, movie_rating) changed from device.

              Following PC setting done from PPS,all changes will be verified in streamer device.
              Default pin 9999 or from brandingbundle
              hide Adult= True

              Following PC setting done from streamer device, all changes will be verified in streamer device.
              hide Adult= True
              Highest Allowed movie rating = Allow all except adult.
              Highest Allowed TV rating = Allow all except adult.
        """
        self.home_page.clear_cache_launch_hydra_app()
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.wait_for_screen_ready(parental_control)
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)
        self.menu_assertions.verify_hide_adult_content_on()
        self.menu_page.go_to_set_rating_limit_screen()
        self.menu_assertions.verify_movie_rating_block_all()
        self.menu_assertions.verify_is_tv_rating_block_all()

        # making PC changes from device and checking on device again
        self.menu_page.set_rating_limits(rated_movie=self.menu_labels.LBL_ALLOW_ALL_HIGHEST_ALLOWED_MOVIE_RATING_EXCEPT_ADULT,
                                         rated_tv_show=self.menu_labels.LBL_ALLOW_ALL_HIGHEST_ALLOWED_TV_RATING_EXCEPT_ADULT,
                                         unrated_tv_show=self.menu_labels.LBL_ALLOW_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_ALLOW_ALL_UNRATED)
        self.menu_page.menu_press_back()
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.wait_for_screen_ready(parental_control)
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)
        self.menu_page.go_to_set_rating_limit_screen()
        self.menu_assertions.verify_is_movie_rating_allow_all_except_adult()
        self.menu_assertions.verify_is_tv_rating_allow_all_except_adult()

    # @pytest.mark.test_stabilization
    @pytest.mark.pps_pc_settings
    @pytest.mark.xray("FRUM-1362")
    @pytest.mark.frumos_11
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused
    @pytest.mark.usefixtures("push_parental_controls__from_pps_with_adult_content_true")
    def test_C12792838_defaultPCpin_update_from_brandingUiBundleGet(self, remove_parental_controls__from_pps):
        """
        Description: This test case has pre requisite of publishing default PC PIN from branding bundle if we want to
        verify that default pin can be set from service side now.
        If PIN has been published from bundle, it will be used to access PC settings successfully.
        If no PIN has been published from bundle, by default 9999 from PPS is valid.
        """
        self.home_page.clear_cache_launch_hydra_app()
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.wait_for_screen_ready(parental_control)
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)

    # @pytest.mark.test_stabilization
    @pytest.mark.pps_pc_settings
    @pytest.mark.frumos_11
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.msofocused_solutions
    @pytest.mark.xray("FRUM-1387")
    @pytest.mark.usefixtures("push_parental_controls__from_pps_with_adult_content_true")
    def test_C12792840_publishedDefaultPCpin_changed_from_userSettings(self,
                                                                       setup_cleanup_parental_and_purchase_controls):
        """
        Description: This test case has pre requisite of publishing default PC PIN from branding bundle if we want to
        verify that default pin can be set from service side now.
        1. Publish PIN from bundle, verify that can be used to enter PC settings on device.
        2. Change the PIN from user settings.
        3. Reboot device.
        4. Verify that user settings are always preferred, so the new pin changed from user settings will now work.
        """
        self.home_page.clear_cache_launch_hydra_app()
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_page.wait_for_screen_ready(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.wait_for_screen_ready(parental_control)
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)

        # Change PIN from user settings.
        self.menu_page.change_pin_from_usersettings(self)

        # Reboot the device & navigate to PC settings to verify that pin set from user settings always gets preference.
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_parental_control_password()
        self.menu_page.wait_for_screen_ready(parental_control)
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)

    @pytest.mark.pps_pc_settings
    @pytest.mark.xray("FRUM-106822")
    @pytest.mark.frumos_11
    @pytest.mark.msofocused_solutions
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.notapplicable(Settings.is_external_mso())
    @pytest.mark.parental_control
    @pytest.mark.usefixtures("push_parental_controls__from_pps_with_adult_content_true")
    def test_106822_verify_PC_config_updated_clear_data(self, setup_cleanup_parental_and_purchase_controls,
                                                        remove_parental_controls__from_pps):
        """
        https://jira.xperi.com/browse/FRUM-106822
        Description:  PC setting turned On from PPS
        without setting any Rating
        then, PC setting changed from device.
        Following PC setting done from PPS,all changes will be verified in streamer device.
        Default pin 9999 from brandingbundle
        hide Adult= True
        Following PC setting done from streamer device, all changes will be verified in streamer device.
        hide Adult=False
        Highest Allowed movie rating = Block all.
        Highest Allowed TV rating = Block all.
        """
        self.home_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.menu_page.turnonpcsettings(self, "on", "off")
        self.menu_page.go_to_set_rating_limit_screen()
        # making PC changes from device and checking on device again
        self.menu_page.set_rating_limits(rated_movie=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         rated_tv_show=self.menu_labels.LBL_BLOCK_ALL_RATED,
                                         unrated_tv_show=self.menu_labels.LBL_BLOCK_ALL_UNRATED,
                                         unrated_movie=self.menu_labels.LBL_BLOCK_ALL_UNRATED)
        self.menu_page.menu_press_back()
        self.home_page.clear_cache_launch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.menu_page.go_to_settings(self)
        parental_control = self.menu_page.get_parental_controls_menu_item_label()
        self.menu_page.select_menu(parental_control)
        self.menu_assertions.verify_enter_PIN_overlay()
        self.menu_page.enter_default_parental_control_password(self)
        self.menu_page.wait_for_screen_ready(parental_control)
        parental_control_title = parental_control.upper()
        self.menu_page.verify_screen_title(parental_control_title)
        self.menu_assertions.verify_pc_value_is_on_unlocked()
        self.menu_assertions.verify_hide_adult_content_on()
        self.menu_page.go_to_set_rating_limit_screen()
        self.menu_assertions.verify_is_movie_rating_allow_all_except_adult()
        self.menu_assertions.verify_is_tv_rating_allow_all_except_adult()
