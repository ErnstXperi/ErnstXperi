"""
Created on Dec 21, 2022

@author: hadagali sani
"""

import time
import json
import random
from datetime import datetime, timedelta

import pytest

from set_top_box.test_settings import Settings
from set_top_box.client_api.provisioning.conftest import setup_provisioning
from set_top_box.client_api.provisioning.conftest import setup_add_new_channel, delete_new_channel
from tools.logger.logger import Logger
from pytest_testrail.plugin import pytestrail
from tools.utils import DateTimeUtils


@pytest.mark.usefixtures("setup_provisioning")
@pytest.mark.usefixtures("setup_add_new_channel")
@pytest.mark.solutions
@pytest.mark.notapplicable(Settings.is_external_mso())
@pytest.mark.timeout(Settings.timeout)
class TestSolutions(object):

    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.sollinear
    @pytest.mark.xray("XRAYS-13")
    def test_new_unentitled_channel(self, request):
        channel_number = self.iptv_prov_api.get_channel_num()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        if not self.guide_page.channel_number_highlight_in_guide(self, channel_number):
            self.home_page.log.step(f"Channel {channel_number} not in guide hence refreshing app")
            self.home_page.back_to_home_short()
            self.menu_page.go_to_system_info_screen(self)
            self.menu_page.select_menu_items(self.menu_labels.LBL_HELP)
            self.menu_page.select_menu_items(self.menu_labels.LBL_HELP_REFRESH_ACC_AND_USER_DATA)
            self.home_assertions.verify_overlay_title(self.menu_labels.LBL_REFRESH_OVERLAY_TITLE)
            self.home_page.select_menu(self.menu_labels.LBL_REFRESH_OK_OPTION)
            self.home_page.handling_hydra_app_after_exit(Settings.app_package)
            self.home_page.wait_for_app_hydra_events("AppHydra", 120000)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.watch_channel(self, channel_number)
        self.guide_assertions.verify_channel_not_subscribed_osdtext(self)
        request.getfixturevalue("delete_new_channel")
        self.home_page.back_to_home_short()
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        if self.guide_page.channel_number_highlight_in_guide(self, channel_number):
            self.home_page.log.step(f"Channel {channel_number} still in guide hence refreshing app")
            self.home_page.back_to_home_short()
            self.menu_page.go_to_system_info_screen(self)
            self.menu_page.select_menu_items(self.menu_labels.LBL_HELP)
            self.menu_page.select_menu_items(self.menu_labels.LBL_HELP_REFRESH_ACC_AND_USER_DATA)
            self.home_assertions.verify_overlay_title(self.menu_labels.LBL_REFRESH_OVERLAY_TITLE)
            self.home_page.select_menu(self.menu_labels.LBL_REFRESH_OK_OPTION)
            self.home_page.handling_hydra_app_after_exit(Settings.app_package)
            self.home_page.wait_for_app_hydra_events("AppHydra", 120000)
        self.home_page.go_to_guide(self)
        self.guide_assertions.verify_guide_screen(self)
        self.guide_page.enter_channel_number(channel_number)
        self.guide_assertions.verify_channel_not_present(channel_number)
