"""
    @author: iurii.nartov@tivo.com
    @created: Oct-31-2019
"""
import re

import pytest

from core_api.stb.assertions import CoreAssertions
from tools.logger.logger import Logger
from set_top_box.client_api.apps_and_games.en_us.labels import AppsAndGamesLabels


class AppsAndGamesPage(CoreAssertions):
    __log = Logger(__name__)
    apps_and_games_labels = AppsAndGamesLabels()

    def get_prepared_screen_elements(self):
        """
        Returns:
            dict, cosists of next elements:
                  hasLineSeparator (bool): depending on line separator presence
                  sections (list): dict containing section names and section items
                  lineSeparatorAfterElement (int): element index before the line separator
        """
        all_elements = {}
        all_elements["hasLineSeparator"] = True if "hasLineSeparator" in self.screen.screen_dump["xml"] else False
        all_elements["sections"] = []
        all_elements["lineSeparatorAfterElement"] = 0
        apps_and_games_screen = self.screen.screen_dump["xml"]["appsAndGamesScreen"]
        items = []
        section_name_old = ""
        for i in range(0, len(apps_and_games_screen)):
            item = apps_and_games_screen[i]
            section_name_new = item["sectionName"]
            section_name_old = item["sectionName"] if section_name_old == "" else section_name_old
            if section_name_new != section_name_old or i == len(apps_and_games_screen) - 1:
                all_elements["sections"].append({"sectionName": section_name_old,
                                                 "items": items})
                all_elements["lineSeparatorAfterElement"] = i  # the previous element when counting from 1
                items = []
                section_name_old = section_name_new
            items.append(item["item"])
        return all_elements

    def get_section_names(self):
        """
        Returns:
            list of section names
        """
        section_names = []
        for item in self.get_prepared_screen_elements()["sections"]:
            section_names.append(item["sectionName"])
        return section_names

    def get_items_by_section_name(self, section_name):
        """
        Returns:
            list of items the given section contains
        """
        items = []
        for item in self.get_prepared_screen_elements()["sections"]:
            if section_name == item["sectionName"]:
                items = item["items"]
                break
        return items

    def get_element_index_before_line_separator(self):
        """
        Returns:
            int, element index before the line separator counting begins from 1;
                 0 means that there's no any element before the line separator
        """
        return self.get_prepared_screen_elements()["lineSeparatorAfterElement"]

    def get_first_item(self, section_name):
        """
        Returns:
            str, name of the 1st item.
                 None if there's no any item in the section
        """
        section_items = self.get_items_by_section_name(section_name)
        first_item = section_items[0] if len(section_items) > 0 else None
        return first_item

    def get_second_item(self, section_name):
        """
        Returns:
            str, name of the 2nd item.
                 None if there's no any item in the section
        """
        section_items = self.get_items_by_section_name(section_name)
        second_item = section_items[1] if len(section_items) > 1 else None
        return second_item

    def nav_to_item(self, item_name, ott_screen=False):
        self.log.step("Navigate to '{}' on Aps&Games and select it".format(item_name[-50:]))
        all_shown_menu_items = []
        scroll_numbers = 3  # number of reties (i.e. pages) to inspect current page for 'item_name'.
        for step in range(scroll_numbers):
            self.screen.refresh()
            menu_items = self.menu_list_images()
            if item_name in " ".join(menu_items):
                item = self.get_element_by_substring(menu_items, item_name, ott_screen=ott_screen)
                self.nav_to_menu_horizontal(item)
                return
            else:
                all_shown_menu_items.extend(menu_items)
                # if target item is not displayed then press down 3 times to go to the nexet apps page
                for i in range(3):
                    self.screen.base.press_down()
        raise AssertionError("After {} scrolls menu still doesnt contain {}."
                             "All detected menus: {}".format(scroll_numbers,
                                                             item_name,
                                                             all_shown_menu_items))

    def press_back_button(self):
        super().press_back_button()
        self.screen.refresh()

    def get_app_name_by_icon(self, tester, icon):
        self.log.step("Get app name by icon Icon name: {}".format(icon))
        partners = tester.api.partner_info_search()
        for partner in partners['partnerInfo']:
            for image in partner['image']:
                if image['imageUrl'] == icon:
                    return partner['vodAppNameShort']
        return False

    def play_youtube_content(self):
        self.log.step("playback any app content")
        self.pause(20)  # wait time to launch the youtube app page completely
        self.screen.base.press_right()
        self.screen.base.press_down()
        self.screen.base.press_enter()
        self.pause(30)
        self.screen.base.press_playpause()
        self.pause(2)
        self.screen.base.press_fast_forward()
        self.pause(2)
        self.screen.base.press_rewind()
        self.pause(2)
        self.screen.base.press_playpause()

    def go_to_apps_and_games(self, tester):
        tester.home_page.back_to_home_short()
        tester.home_page.select_menu_shortcut_num(tester, tester.home_labels.LBL_APPSANDGAME_SHORTCUT)
        tester.apps_and_games_assertions.wait_for_screen_ready(self.apps_and_games_labels.EXM_APPS_AND_GAMES_SCREEN)
        tester.apps_and_games_assertions.verify_screen_title(tester)

    def launch_content_provider_app(self):
        self.log.step("Launching content provider app.")
        return self.screen.base.launch_content_provider_app()

    def get_content_provider_mso_name(self):
        self.log.info("Getting MSO name value from content provider app.")
        try:
            mso = self.screen.base.get_text_by_locator(self.apps_and_games_labels.CONTENT_PROVIDER_MSO_NAME)
        except LookupError as err:
            raise Exception("MSO name value is not shown in content provider app with error: {}.".format(err))
        return mso

    def get_content_provider_device_type(self):
        self.log.info("Getting Device type value from content provider app.")
        try:
            device_type = self.screen.base.get_text_by_locator(self.apps_and_games_labels.CONTENT_PROVIDER_DEVICE_TYPE)
        except LookupError as err:
            raise Exception("Device type value is not shown in content provider app with error: {}.".format(err))
        return device_type

    def get_focussed_app(self):
        self.screen.refresh()
        menuitem = self.screen.get_screen_dump_item('menuitem')
        for i in range(len(menuitem)):
            item = self.menu_item_image_focus()
            if item is None:
                self.screen.base.press_down()
            self.log.step("Focus is on {}".format(item))
        item_spilt = item.split(";")
        component = item_spilt[3]
        self.log.step("Component is {}".format(component))
        return component

    def wait_for_pluto_tv_start_playing(self):
        self.log.info("Waiting for Pluto TV starts playing.")
        self.screen.base.wait_ui_element_gone(self.apps_and_games_labels. LOC_PLUTO_TV_APP_LOADING, timeout=15000)
        self.screen.base.wait_ui_element_gone(self.apps_and_games_labels. LOC_PLUTO_TV_CHANNEL_LOADING, timeout=15000)
        self.screen.base.wait_ui_element_gone(self.apps_and_games_labels.LOC_PLUTO_SUBTITLE, timeout=15000)

    def get_plutotv_channel_title(self):
        self.log.info("Getting PlutoTV channel title.")
        try:
            channel_title = self.screen.base.get_text_by_locator(self.apps_and_games_labels.LOC_PLUTO_TITLE)
            return channel_title
        except LookupError:
            self.log.error("Unable to get PlutoTV channel title.")

    def launch_all_apps_present_in_apps_and_games_screen(self, tester):
        apps = self.screen.get_screen_dump_item('menuitem')
        for app in apps:
            pkg_name = re.findall(r'android-app://(.*?)#', app.get('imagename'))[0]
            self.nav_to_item(pkg_name)
            self.log.info(f"Navigated to {pkg_name} and pressing enter")
            self.screen.base.press_enter(5000)
            # tester.apps_and_games_assertions.wait_fo_app_launch(pkg_name, limit=15)
            self.pause(10)
            forground_pkg = self.screen.base.get_foreground_package()
            self.log.info(f"forground_pkg: {forground_pkg} and pressing exit")
            if forground_pkg not in pkg_name:
                raise AssertionError("App screen not launched.")
            self.screen.base.press_exit_button()
            tester.apps_and_games_assertions.wait_for_screen_ready(self.apps_and_games_labels.EXM_APPS_AND_GAMES_SCREEN)
            tester.apps_and_games_assertions.verify_screen_title(tester)

    def get_watch_now_option_images(self):
        '''
        Api to get imagenames from watchnow option of Info Card Overlay
        '''
        images = list(filter(None, self.menu_list_images()))
        if images and len(images) > 0:
            return {'imagename': images[0]}
        return None

    def play_youtube_content_for_3hours(self):
        self.log.step("playback any app content")
        self.pause(10)  # wait time to launch the youtube app page completely
        self.log.step("Open google assistant and play from youtube")
        self.screen.base.tell_google_assistant("Play 3 hour video from Youtube")
        self.pause(10)
        self.screen.base.press_up()
        self.log.step("***Pressed UP***")
        self.screen.base.press_enter()
        self.log.step("***Pressed enter***")
