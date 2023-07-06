"""
    @author: iurii.nartov@tivo.com
    @created: Oct-31-2019
"""

import re

from hamcrest import assert_that, contains_string, is_not, is_, equal_to

from set_top_box.client_api.apps_and_games.page import AppsAndGamesPage
from set_top_box.client_api.home.page import HomePage
from set_top_box.test_settings import Settings
from set_top_box.conf_constants import *
from tools.logger.logger import Logger


class AppsAndGamesAssertions(AppsAndGamesPage):
    __log = Logger(__name__)

    def verify_sections(self, first_section, second_section):
        """
        Verify section names and their order
        """
        self.__log.info("Verifying Apps & Games: section names and order")
        section_names = self.get_section_names()
        is_first_matched = True if first_section == section_names[0] else False
        is_second_matched = True if second_section == section_names[1] else False
        assert_that(is_first_matched and is_second_matched, "Either section names or section order is inappropriate")

    def verify_screen_title(self, tester):
        super().verify_screen_title(tester.home_labels.LBL_APPSANDGAME_SHORTCUT)

    def verify_featured_apps_first_item(self, tester, expected_featured_apps_first_item):
        """
        Verify if the 1st item in Featured Apps tab is the expected one
        """
        self.__log.info("Verifying if Netflix is the 1st app in the Featured Apps section")
        assert_that(self.get_first_item(tester.apps_and_games_labels.LBL_APPS_AND_GAMES_FEATURED_APPS_SECTION_TITLE).lower(),
                    contains_string(expected_featured_apps_first_item.lower()),
                    "Featured Apps section has unexpected first app")

    def verify_featured_apps_second_item(self, tester, expected_featured_apps_second_item):
        """
        Verify if the 2nd item in Featured Apps tab is the expected one
        """
        self.__log.info("Verifying if opened app is the 2nd app in the Featured Apps section")
        assert_that(self.get_second_item(
            tester.apps_and_games_labels.LBL_APPS_AND_GAMES_FEATURED_APPS_SECTION_TITLE).lower(),
            contains_string(expected_featured_apps_second_item.lower()),
            "Featured Apps section has unexpected second app")

    def start_google_play_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME, limit=15)
        self.pause(5)

    def start_netflix_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.NETFLIX_PACKAGE_NAME)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.NETFLIX_PACKAGE_NAME, limit=15)

    def start_hbo_max_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.HBO_MAX_PACKAGE_NAME)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.HBO_MAX_PACKAGE_NAME, limit=15)

    def start_disney_plus_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.DISNEY_PLUS_PACKAGE_NAME)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.DISNEY_PLUS_PACKAGE_NAME, limit=15)

    def start_youtube_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.YOUTUBE_PACKAGE_NAME, ott_screen=True)
        focus = self.get_focussed_app()
        packages = [tester.apps_and_games_labels.YOUTUBE_MUSIC_PACKAGE_NAME,
                    tester.apps_and_games_labels.YOUTUBE_KIDS_PACKAGE_NAME,
                    tester.apps_and_games_labels.YOUTUBE_PACKAGE_NAME]
        for i in range(len(packages)):
            if packages[i] in focus:
                self.screen.base.press_enter(5000)
                self.wait_fo_app_launch(packages[i], limit=15)
                break

    def start_tubitv_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.TUBITV_PACKAGE_NAME)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.TUBITV_PACKAGE_NAME, limit=15)

    def start_google_play_movies_and_tv_app(self, tester):
        self.__log.info("Lauching Google movies and TV app from apps and games gallery")
        self.nav_to_item(tester.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME2)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME2, limit=15)

    def start_pandora_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.PANDORA_PACKAGE_NAME)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.PANDORA_PACKAGE_NAME, limit=15)

    def start_pbs_kids_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.PBS_KIDS_PACKAGE_NAME)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.PBS_KIDS_PACKAGE_NAME, limit=15)

    def start_youtube_kids_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.YOUTUBE_KIDS_PACKAGE_NAME)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.YOUTUBE_KIDS_PACKAGE_NAME, limit=15)

    def start_ott_application_and_verify_screen(self, tester, app, launch_apps=True):
        """
        Start OTT app from APPS & GAMES screen
        :param app: list of OTT apps
        :return:
        """
        if launch_apps:
            self.press_apps_and_verify_screen(tester)
        focus = self.get_focussed_app()
        self.log.info(f"Current focused app: {focus}")
        if app == "netflix":
            self.start_netflix_and_verify_screen(tester)
        if app == "youtube":
            self.start_youtube_and_verify_screen(tester)
        if app == "google play":
            self.start_google_play_and_verify_screen(tester)
        if app == "HBO MAX":
            self.start_hbo_max_and_verify_screen(tester)
        if app == "disney plus":
            self.start_disney_plus_and_verify_screen(tester)
        if app == "pandora":
            self.start_pandora_and_verify_screen(tester)
        if app == "pbs kids":
            self.start_pbs_kids_and_verify_screen(tester)
        if app == "pluto":
            self.start_pandora_and_verify_screen(tester)
        if app == "YOUTUBE KIDS":
            self.start_youtube_kids_and_verify_screen(tester)
        if app == "HBO MAX":
            self.start_hbo_max_and_verify_screen(tester)

    def verify_if_app_is_not_present_in_system(self, test_app_package_name):
        """
        Verify if a test app is not present in the Android system

        Args:
            test_app_package_name (str): package name of an apk file
        """
        self.__log.info("Verifying if a test app is not present in the Android system")
        assert_that(self.is_app_installed(test_app_package_name), is_not(True), "The sideloaded app is present in the system")

    def select_continue_wait_for_home_screen_to_load(self, tester, is_hospitality_screen_omitted=False):
        """
        Selects Continue and then waits for Home screen
        Hospitality screen should be displayed and HSN should be bound to the account before running the method.

        Args:
            is_hospitality_screen_omitted (bool): True - waiting for the Home screen without selecting Continue option,
                                                  False - selecting Continue option on the Hospitality screen and then
                                                          waiting for the Home screen
        """
        self.__log.info("Selecting Continue on the Hospitality screen and waiting for the Home screen")
        if not is_hospitality_screen_omitted:
            self.select_menu(tester.apps_and_games_labels.LBL_CONTINUE)
        self.wait_for_screen_ready(tester.home_labels.LBL_HOME_SCREEN_NAME, 120000)
        self.verify_view_mode(tester.home_labels.LBL_HOME_SCREEN_MODE)

    def verify_if_app_is_not_present_on_ui_apps_and_games(self, test_app_name_from_screen_dump):
        """
        Verify if a test app is not present on the Apps & Games screen.
        Apps & Games screen should be displayed before calling the method

        Args:
            test_app_name_from_screen_dump (str): the app name from the screen dump
        """
        self.__log.info("Verifying if a test app is not present on the Apps & Games screen")
        sections = self.get_section_names()
        is_not_contained = True
        for section in sections:
            items = self.get_items_by_section_name(section)
            for item in items:
                if test_app_name_from_screen_dump in item:
                    is_not_contained = False
        assert_that(is_not_contained, "The sideloaded app is present on UI in the Apps & Games screen")

    def wait_and_verify_hospitality_screen_is_shown(self, tester):
        self.__log.info("Waiting for the Hospitality screen")
        hospitality_view_mode = tester.apps_and_games_labels.LBL_HOSPITALITY_SCREEN_VIEW_MODE
        self.wait_for_screen_ready(tester.apps_and_games_labels.EXM_HOSPITALITY_SCREEN, 100000)
        # Sometimes, taking the screen dump may occur when HospitalityLoadingScreen is displayed,
        # this screen usually shown for about 3-8 secs and then Hospitality screen is back
        # (if HSN is not bound), so need to try to take the screen dump once again
        error_message = ""
        for i in range(0, 2):
            try:
                self.verify_view_mode(hospitality_view_mode)
                break
            except Exception as ex:
                error_message = ex
                self.__log.warning(f"{error_message}")
        else:
            raise Exception(f"{error_message}")

    def verify_hospitality_screen_elements(self, tester):
        """
        Verifies next elements:
            - Continue and Network Settings options presence
            - Background image
            - Hydra logo
            - Description text
            - Greeting text
        """
        self.wait_and_verify_hospitality_screen_is_shown(tester)
        self.__log.info("Verifying Hospitality screen's elements")
        self.verify_menu_list(
            [self.apps_and_games_labels.LBL_CONTINUE, self.apps_and_games_labels.LBL_NETWORK_SETTINGS], True, "equal")
        background_image = self.screen.get_screen_dump_item("hospitality", "background-image", "imagename")
        description = self.screen.get_screen_dump_item("hospitality", "description", "text")
        greeting = self.screen.get_screen_dump_item("hospitality", "greeting", "text")
        hydra_logo = self.screen.get_screen_dump_item("hospitality", "hydra-logo", "imagename")
        assert_that(background_image, equal_to(self.apps_and_games_labels.LBL_BACKGROUND_IMAGE))
        assert_that(description, equal_to(self.apps_and_games_labels.LBL_DESCRIPTION_TXT))
        assert_that(greeting, equal_to(self.apps_and_games_labels.LBL_GREETING_TXT))
        assert_that(hydra_logo, equal_to(self.apps_and_games_labels.LBL_HYDRA_LOGO))

    def verify_clear_button_in_ott_apps(self, tester, apps):
        """
        To verify that CLEAR button doesn't exit from OTT apps
        :param apps:
        :return:
        """
        for app in apps:
            self.press_apps_and_verify_screen(tester)
            if app == "netflix":
                self.start_netflix_and_verify_screen(tester)
            elif app == "youtube":
                self.start_youtube_and_verify_screen(tester)
            elif app == "google play":
                self.start_google_play_and_verify_screen(tester)
            elif app == "tubitv":
                self.start_tubitv_and_verify_screen(tester)
            self.screen.base.press_clear_button()
            assert_that(self.verify_ott_app_is_foreground(tester, app), "Clear button exits " + app + ".")

    def verify_bail_buttons_in_ott_app(self, tester, apps, bail_buttons):
        """
        To verify exit from OTT app by bail buttons
        :param apps: list
        :param bail_buttons: list
        :return:
        """
        for app in apps:
            for button in bail_buttons:
                self.log.info(f"Verifying {app} exit with {button} press")
                self.start_ott_application_and_verify_screen(tester, app)
                if button == "home":
                    self.press_home_and_verify_screen(tester)
                elif button == "guide":
                    self.press_guide_and_verify_screen(tester, key_press='inputkeyevent')
                elif button == "exit":
                    self.screen.base.press_exit_button()
                    self.wait_for_screen_ready(self.apps_and_games_labels.LBL_APPS_AND_GAMES_SCREENTITLE, 10000)
                elif button == "back":
                    count = 3
                    while self.verify_ott_app_is_foreground(tester, app) and count != 0:
                        self.screen.base.press_back_button()
                        self.wait_for_screen_ready(self.apps_and_games_labels.LBL_APPS_AND_GAMES_SCREENTITLE, 10000)
                        count -= 1
                elif button == "vod":
                    self.press_vod_and_verify_screen(tester)
                elif button == "apps":
                    self.press_apps_and_verify_screen(tester)
                assert_that(not self.verify_ott_app_is_foreground(tester, app),
                            "Button " + button + " doesn't exit " + app + ".")

    def verify_back_button_exits_ott_app(self, app):
        count = 3
        while self.screen.base.verify_foreground_app(app) and count != 0:
            self.press_back_button()
            count -= 1
            continue
        self.verify_app_is_foreground(app, state=False)

    def verify_netflix_screen_with_package(self, tester):
        self.pause(20)
        self.log.info("Verifying Netflix program screen shown.")
        assert_that(self.screen.base.verify_foreground_app(tester.apps_and_games_labels.NETFLIX_PACKAGE_NAME),
                    "NETFLIX app didn't start.")

    def verify_app_content_playing(self):
        status = self.wait_for_app_content_playback()
        if status:
            return True
        else:
            raise AssertionError("Failed to playback the app content")

    def wait_fo_app_launch(self, package, limit=5):
        self.log.info("Launching APP and verifying the screen.")
        # loop to get a app package name.
        c = 0
        while c < limit:
            self.pause(1)
            value = self.screen.base.verify_foreground_app(package)
            if value:
                break
            else:
                c += 1
        if not value:
            raise AssertionError("App screen not launched.")

    def verify_content_provider_app_is_foreground(self):
        self.log.info("Verifying that content provider app is foreground.")
        self.screen.base.verify_foreground_app(Settings.CONTENT_PROVIDER_APP_PACKAGE)

    def verify_content_provider_info(self):
        self.log.info("Verifying content provider info.")
        self.log.info("Verifying MSO name.")
        mso_name = Settings.mso
        if Settings.mso == "astound":
            mso_name = "rcn"
        elif Settings.mso == "breezeline":
            mso_name = "abb"
        assert_that(self.get_content_provider_mso_name(), is_(mso_name))
        self.log.info("Verifying device type.")
        assert_that(self.get_content_provider_device_type(), is_(self.service_api.get_device_type()))

    def check_jump_channel_is_available(self, all_jump_channels, jump_channel_label):
        self.log.info("Checking {} in {}".format(jump_channel_label, all_jump_channels))
        jump_channel_list = list(all_jump_channels.values())
        for value in jump_channel_list:
            if value.lower() == jump_channel_label.lower():
                return list(all_jump_channels.keys())[list(all_jump_channels.values()).index(value)]
            else:
                continue

    def press_channel_button_and_verify_channel_change_in_pluto_tv(self, button):
        """
        To verify that channel up and channel down buttons could change channels in Pluto TV app
        Application should be started and playing to use this assertion
        :param button: str, correct values are 'channel up' and 'channel down'
        """
        self.log.info(f"Verifying channel change by '{button}' button in Pluto TV app.")
        self.screen.base.native_key_press('center')  # To bring up infobanner in Pluto TV and get title
        start_channel = self.get_plutotv_channel_title()
        if button == 'channel up':
            self.press_channel_up_button()
        elif button == 'channel down':
            self.press_channel_down_button()
        else:
            raise Exception("Button option is invalid, please input correct value.")
        current_channel = self.get_plutotv_channel_title()
        assert_that(start_channel, not is_not(current_channel), "Channel wasn't changed.")

    def verify_source_type_netflix_app(self, source_type=None):
        self.log.info("verifying source type of netflix")
        raw_log = self.wait_for_netflix_app_to_launch()
        logs = raw_log.split()
        str1 = ""
        for log in logs:
            r = log.replace('\\', "")  # To remove Escape char
            str1 = str1 + ' ' + r
        self.log.info("raw log after split: {}".format(str1))
        match = re.search(source_type, str1)
        if match is None:
            raise AssertionError("Netflix source type is not matched")

    def verify_netflix_app_iid(self, iid=None):
        self.log.info("verifying netflix iid")
        raw_log = self.screen.base.find_str_in_log(string="Netflix: extras")
        if not raw_log:
            raise AssertionError("UTAF unable to find any log with string: 'Netflix: extras'")
        assert_that(raw_log, contains_string(iid), "Netflix LST is not matched")

    def start_pluto_and_verify_screen(self, tester):
        self.nav_to_item(tester.apps_and_games_labels.PLUTO_PACKAGE_NAME)
        self.screen.base.press_enter(5000)
        self.wait_fo_app_launch(tester.apps_and_games_labels.PLUTO_PACKAGE_NAME, limit=15)

    def verify_uri(self, uri=None):
        self.log.info("verifying uri")
        raw_log = self.wait_for_netflix_app_to_launch()
        logs = raw_log.split()
        str1 = ""
        for log in logs:
            r = log.replace('\\', "")  # To remove Escape char
            str1 = str1 + '' + r
        self.log.info("raw log after split: {}".format(str1))
        if uri in str1:
            self.log.info("{} url is opened and played in youtube".format(uri))
        else:
            raise AssertionError("uri is not matched")

    def verify_ott_or_google_play_shown(self, package, limit=15):
        """
        Verify whether app is installed ,launch correctly the requested app
        if app is not installed, launch google play
        """
        self.log.info("Verification of ott screen")
        result = self.screen.base.is_app_installed(package)
        if result:
            foreground_app = self.screen.base.get_foreground_package()
            self.log.info("foreground_app ={}".format(foreground_app))
            if foreground_app in self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME:
                raise AssertionError("App is installed in the device , Please check whether it needs google sign in")
            else:
                self.wait_fo_app_launch(package, limit=limit)
        else:
            self.wait_fo_app_launch(self.apps_and_games_labels.GOOGLE_PLAY_PACKAGE_NAME, limit)

    def verify_playback_options_order(self, play_options=None, priority_dict=None):
        self.log.step("Verify playoptions priority order: {}".format(play_options))
        priority = []
        if play_options and isinstance(play_options['imagename'], list):
            for option in play_options['imagename']:
                for k, v in priority_dict.items():
                    if option in v:
                        priority.append(k)
                        break
                else:
                    self.log.info("{} image not found in priority dict".format(option))
        elif play_options and isinstance(play_options['imagename'], str):
            for k, v in priority_dict.items():
                if play_options['imagename'] in v:
                    self.log.info("{} found".format(play_options['imagename']))
                    priority.append(k)
                    break
        self.log.info("priority: {}".format(priority))
        assert_that((priority == sorted(priority)), "incorrect playback order: \
                                                     Expected: {}, Actual: {}".format(play_options,
                                                                                      priority_dict))
