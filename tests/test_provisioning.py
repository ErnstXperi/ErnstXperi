import time

import pytest

from set_top_box.client_api.provisioning.conftest import setup_provisioning
from set_top_box.client_api.provisioning.conftest import activate_ndvr
from set_top_box.client_api.home.conftest import cleanup_ftux
from set_top_box.client_api.account_locked.conftest import cleanup_re_activate_and_sign_in
from set_top_box.test_settings import Settings
from tools.logger.logger import Logger


@pytest.mark.usefixtures("setup_provisioning")
class TestProvisioning(object):
    log = Logger(__name__)

    @pytest.mark.usefixtures("activate_ndvr")
    def test_c11962189_ndvr_activate_cancel_reset(self):
        """
        #TC link
        :return:
        """
        pr1_prov_account_get = self.iptv_prov_api.pr1_prov_account_get(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn))
        dictionary = pr1_prov_account_get.get("provDevice")
        if dictionary is not None:
            value = "platformName"
            resource = [sub[value] for sub in dictionary]
            if "npvrPlatform" in resource:
                self.iptv_prov_api.pr1_prov_device_cancel(
                    self.service_api.getPartnerCustomerId(Settings.tsn),
                    self.service_api.get_mso_partner_id(Settings.tsn))
            self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, 5)
            if self.provisioning_page.is_ndvr_disabled_overlay():
                self.home_page.press_enter()
            self.home_page.wait_for_screen_ready(timeout=40000)
            self.iptv_prov_api.pr1_prov_device_reset(
                self.service_api.getPartnerCustomerId(Settings.tsn),
                self.service_api.get_mso_partner_id(Settings.tsn))
            self.home_page.wait_for_screen_ready(timeout=40000)
            self.iptv_prov_api.pr1_prov_device_activate(
                'NpvrSmallPackage',
                self.service_api.getPartnerCustomerId(Settings.tsn),
                self.service_api.get_mso_partner_id(Settings.tsn),
                self.service_api.fe_device_mso_service_id_get()["msoServiceId"])
            self.home_page.wait_for_screen_ready(self.home_labels.LBL_HOME_SCREEN_NAME, 5)
            if self.provisioning_page.is_ndvr_enabled_overlay():
                self.home_page.press_enter()
            self.home_page.wait_for_screen_ready(timeout=40000)
            channel = self.guide_page.guide_streaming_channel_number(self)
            self.home_page.go_to_guide(self)
            self.home_page.wait_for_screen_ready(self.guide_labels.LBL_GUIDE_SCREEN)
            self.guide_assertions.verify_guide_screen(self)
            self.guide_page.enter_channel_number(channel)
            program = self.guide_page.get_live_program_name(self)
            self.guide_page.create_live_recording()
            self.home_page.go_to_my_shows(self)
            self.my_shows_page.select_my_shows_category(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.select_show(program)
            self.my_shows_page.playback_recording(self, self.my_shows_labels.LBL_SERIES_RECORDINGS)
            self.my_shows_page.verify_recording_playback_and_curl_url(self)

    @pytest.mark.xray('FRUM-1035')
    def test_389366330_brandingui_after_signin_successful(self):
        """
        TC Link: https://testrail.tivo.com//index.php?/tests/view/389366330
        """
        branding_value = self.api.branding_ui()
        if not branding_value:
            pytest.fail("Could not find Banding ui value")
        branding_dict = branding_value.__dict__['_BaseEntity__dict_item']
        self.provisioning_assertions.verify_branding_labels(branding_dict)

    @pytest.mark.xray('FRUM-54012')
    def test_389366286_Customer_support_number(self):
        """
        verify phone customer account no
        TC Link: https://testrail.tivo.com//index.php?/tests/view/389366286
        """
        # TODO
        # This test will fail for unmanaged devices and for managed if Android Settings or OTT were opened before
        # e.g. by other test, so it's better to use handlers from set_top_box.client_api.account_locked.page and assertion
        # since pointed cases are implemented there
        branding_value = self.api.branding_ui()
        phn = branding_value.phone_customer_support_number.get('value')
        dump = self.provisioning_page.get_customer_support_screen_dump()
        if not dump:
            pytest.fail("Failed to get dump")
        if phn in dump["text"]:
            self.log.info("CustomerSupportNumber found in ")
            self.acc_locked_page.cancel_device()
            self.home_page.wait_for_screen_ready(timeout=40000)
            self.home_assertions.verify_view_mode(self.provisioning_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE)
            dump1 = self.screen.get_screen_dump_item()
            if not dump1:
                pytest.fail("Could not find dumps in Account Locked screen")
            phone_number = dump1["accountLockout"]["textOnTop"]["left-block1"]
            if phn in phone_number["text"]:
                self.log.info("CustomerSupportNumber found in Account Locked screen")
                self.acc_locked_page.re_activate_device()
                self.guide_page.relaunch_hydra_app()
                self.home_page.skip_ftux()
                self.home_assertions.verify_view_mode(self.home_labels.LBL_HOME_VIEW_MODE)
            else:
                pytest.fail("Could not find CustomerSupportNumber in Account Locked screen")
                self.acc_locked_page.re_activate_device()
                self.guide_page.relaunch_hydra_app()
                self.home_page.skip_ftux()
                self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        else:
            pytest.fail("Could not find phone number")

    @pytest.mark.xray('FRUM-54013')
    def test_389366287_url_account_management(self):
        """
        verify url_account_management
        TC Link:https://testrail.tivo.com//index.php?/tests/view/389366287
        """
        # TODO
        # This test will fail for unmanaged devices and for managed if Android Settings or OTT were opened before
        # e.g. by other test, so it's better to use handlers from set_top_box.client_api.account_locked.page* and assertion
        # since pointed cases are implemented there
        branding_value = self.api.branding_ui()
        value = branding_value.url_account_management.get('value')
        dump = self.provisioning_page.get_customer_support_screen_dump()
        if not dump:
            pytest.fail("Failed to get dump")
        if value["value"] in dump["text"]:
            self.log.info("Account Management Url is found")
            self.acc_locked_page.cancel_device()
            self.home_page.wait_for_screen_ready(timeout=40000)
            self.home_assertions.verify_view_mode(self.provisioning_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE)
            for i in range(21):
                self.iptv_prov_api.tve_service_activate(
                    self.service_api.getPartnerCustomerId(Settings.tsn),
                    Settings.hsn,
                    self.service_api.get_mso_partner_id(Settings.tsn),
                    self.service_api.fe_device_mso_service_id_get()["msoServiceId"],
                    self.service_api.get_device_type(), Settings.ca_device_id)
            self.acc_locked_page.re_activate_device()
            self.guide_page.relaunch_hydra_app()
            self.home_page.skip_ftux()
            self.home_assertions.verify_view_mode(self.home_labels.LBL_HOME_VIEW_MODE)
            dump1 = self.provisioning_page.get_customer_support_screen_dump()
            if not dump1:
                pytest.fail("Failed to get dump")
            if value["value"] in dump1["text"]:
                self.log.info("Account Management Url is found")
            else:
                pytest.fail("Couldn't find url in customer support screen")
        else:
            pytest.fail("Couldn't find url in customer support screen")

    @pytest.mark.usefixtures("cleanup_ftux")
    @pytest.mark.notapplicable(Settings.is_unmanaged())
    @pytest.mark.xray("FRUM57695")
    def test_xtq_53278_bind_hsn(self):
        """
        Method to bind HSN
        """
        if self.provisioning_page.get_authentication_lp_url():
            pytest.skip("Do not follow HSN binding flow")
        self.home_page.back_to_home_short()
        self.home_assertions.verify_home_title()
        if self.home_page.is_overlay_shown():
            self.screen.base.press_enter()
        if Settings.is_internal_mso():
            self.pps_api_helper.remove_device_provisioning(Settings.ca_device_id)
        self.iptv_prov_api.tve_service_cancel(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn))
        self.iptv_prov_api.tve_service_reset(
            self.service_api.getPartnerCustomerId(Settings.tsn),
            self.service_api.get_mso_partner_id(Settings.tsn))
        self.screen.base.launch_application(Settings.app_package)
        self.home_page.wait_loading_indicator_disappear()
        if not Settings.specified_pcid:
            self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                        Settings.pcid)
        else:
            self.iptv_prov_api.bind_hsn(Settings.hsn, self.service_api.get_mso_partner_id(Settings.tsn),
                                        Settings.specified_pcid)
        self.home_page.skip_ftux()
        self.home_assertions.verify_view_mode(self.home_labels.LBL_HOME_VIEW_MODE)

    def test_CA_10827_add_svod_remove_svod_deactivate_vod(self):
        mso = Settings.mso.lower()
        pcid = Settings.pcid.lower()
        site_id = None
        if mso == 'cableco11':
            site_id = self.provisioning_page.find_vod_site_id_cc11()
        if mso == 'cableco' or mso == 'cableco2' or (site_id == 'cableco11_510' or site_id == 'cableco11_511'):
            response = self.provisioning_page.seachange_account_check()
            if response == f"For account {pcid} Subscriptions are Both":
                self.provisioning_page.sechange_remove_svod()
                status, result = self.vod_api.getOffer_svod_notEntitledSubscribable()
                if result is None:
                    pytest.skip("The content is not available on VOD catalog.")
                self.home_page.back_to_home_short()
                self.vod_page.goto_vodoffer_program_screen(self, result)
                self.vod_assertions.verify_svod_upsell_overlay(self, result)
            else:
                status, result = self.vod_api.getOffer_svod_entitledSubscribed(600, 7200, count=1000)
                if result is None:
                    pytest.skip("The content is not available on VOD catlog.")
                self.home_page.back_to_home_short()
                self.vod_page.goto_vodoffer_program_screen(self, result)
                self.vod_page.play_vod_entitled_content(self, result)
        else:
            response = self.provisioning_page.cubiware_svod_account_info()
            if response == pcid:
                self.provisioning_page.cubiware_svod_package_removal()
                status, result = self.vod_api.getOffer_svod_notEntitledSubscribable()
                if result is None:
                    pytest.skip("The content is not available on VOD catlog.")
                self.home_page.back_to_home_short()
                self.vod_page.goto_vodoffer_program_screen(self, result)
                self.vod_assertions.verify_svod_upsell_overlay(self, result)
            else:
                status, result = self.vod_api.getOffer_svod_entitledSubscribed(600, 7200, count=1000)
                if result is None:
                    pytest.skip("The content is not available on VOD catlog.")
                self.home_page.back_to_home_short()
                self.vod_page.goto_vodoffer_program_screen(self, result)
                self.vod_page.play_vod_entitled_content(self, result)
                self.vod_assertions.verify_vod_playback(self)

    @pytest.mark.usefixtures("cleanup_re_activate_and_sign_in")
    @pytest.mark.usefixtures("cleanup_ftux")
    @pytest.mark.xray('FRUM-62329')
    @pytest.mark.sol_provisioning
    def test_frum_62329_attributes_values_after_suspend_the_account(self):
        """
        FRUM-62329
        verify branding UI attributes values after the account suspend
        """
        branding_value = self.api.branding_ui()
        if not branding_value:
            pytest.fail("Failed to get Branding UI Value")
        actual_list = self.provisioning_page.get_branding_ui_labels_values(branding_value)
        self.acc_locked_page.cancel_device()
        self.home_page.wait_for_screen_ready(timeout=80000)
        self.home_assertions.verify_view_mode(self.provisioning_labels.LBL_ACC_LOCKED_SCREEN_VIEW_MODE)
        branding_value_cancel = self.api.branding_ui()
        if not branding_value_cancel:
            pytest.fail("Failed to get Branding UI Value")
        expected_list = self.provisioning_page.get_branding_ui_labels_values(branding_value_cancel)
        self.provisioning_assertions.verify_branding_ui_values(actual_list, expected_list)
