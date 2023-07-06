import time

import pytest  # noqa: F401

from set_top_box.client_api.Menu.conftest import *
from set_top_box.conf_constants import FeaturesList, BodyConfigFeatures, DeviceInfoStoreFeatures
from pytest_testrail.plugin import pytestrail


@pytest.mark.usefixtures("setup_menu")
@pytest.mark.menu
class TestMenuStb(object):

    def test_navigate_from_home_to_menu_help(self):
        """
        Navigate from Home to Help in STB
        """
        self.menu_page.go_to_help_stb(self)
        self.menu_assertions.verify_item_option_focus(self.menu_labels.LBL_HELP_SCREENTITLE)

    @pytest.mark.iponly_dvr_smartbox
    def test_select_menu_help_account_system_info(self):
        """
        Navigate from help to account & system info in STB
        """
        self.menu_page.go_to_account_system_info_stb(self)
        self.menu_assertions.verify_account_system_info_screen_title_stb(self)

    @pytest.mark.iponly_dvr_smartbox
    def test_navigate_to_system_information(self):
        """
        Navigate from help to account & system info in STB
        """
        self.menu_page.go_to_system_information_stb(self)
        self.menu_assertions.verify_system_information_screen_title_stb(self)

    @pytest.mark.iponly_dvr_smartbox
    def test_availability_of_channel_signal_strength_in_stb(self):
        """
        Verify channel signal strength option availability based on mode type
        testrail:
        https://testrail.tivo.com//index.php?/cases/view/20959941
        https://testrail.tivo.com//index.php?/cases/view/20959942
        https://testrail.tivo.com//index.php?/cases/view/20955302
        https://testrail.tivo.com//index.php?/cases/view/20955303
        https://testrail.tivo.com//index.php?/cases/view/20951881
        https://testrail.tivo.com//index.php?/cases/view/20951882
        """
        self.menu_page.go_to_channel_settings_stb(self)
        self.menu_assertions.verify_channel_signal_strength_option(self)

    @pytest.mark.iponly_dvr_smartbox
    @pytest.mark.notapplicable(not Settings.is_smartbox())
    def test_availability_of_conditional_access_option_in_stb(self):

        """
        Verify conditional access option in smartbox stb
        testrail:
        https://testrail.tivo.com//index.php?/cases/view/20959940
        https://testrail.tivo.com//index.php?/cases/view/20959870
        """
        device_mode = self.menu_page.get_stb_mode(self)
        self.menu_page.go_to_remote_devices_conditionalaccess_cableCARD(self, device_mode)
        self.menu_assertions.verify_conditional_access_option(self)

    @pytest.mark.iponly_dvr_smartbox
    def test_remote_device_option_based_on_mode(self):
        """
        Verify Remote device and cablecard option on box according to device type
        testrail :
        https://testrail.tivo.com//index.php?/cases/view/20959867
        https://testrail.tivo.com//index.php?/cases/view/20959868
        https://testrail.tivo.com//index.php?/cases/view/20959869
        https://testrail.tivo.com//index.php?/cases/view/20959464
        https://testrail.tivo.com//index.php?/cases/view/20959465
        """
        device_mode = None
        if Settings.is_smartbox() or Settings.is_topaz() or Settings.is_taos():
            device_mode = self.menu_page.get_stb_mode(self)
        self.menu_page.go_to_remote_devices_conditionalaccess_cableCARD(self, device_mode)
        self.menu_assertions.verify_remote_device_screen_title_stb(device_mode)

    @pytest.mark.iponly_dvr_smartbox
    def test_navigate_to_diagnostic_screen(self):
        """
        Verify navigation to diagnostic screen
        """
        self.menu_page.go_to_system_diagnostics_screen_stb(self)
        self.menu_assertions.verify_system_diagnostics_screen_title_stb()

    @pytest.mark.iponly_dvr_smartbox
    @pytest.mark.notapplicable(not (Settings.is_topaz() or Settings.is_taos()))
    def test_cablecard_decoder_option_on_stb_based_on_mode(self):
        """
        Verify cablecard decoder option based on mode
        testrail:
        https://testrail.tivo.com//index.php?/cases/view/20961316
        https://testrail.tivo.com//index.php?/cases/view/20961319
        """
        device_mode = self.menu_page.get_stb_mode(self)
        self.menu_page.go_to_remote_devices_conditionalaccess_cableCARD(self, device_mode)
        self.menu_assertions.verify_cablecard_decoder_option(device_mode)
