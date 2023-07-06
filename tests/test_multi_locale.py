import pytest

from set_top_box.test_settings import Settings
from set_top_box.conf_constants import HydraBranches
from set_top_box.client_api.home.conftest import setup_home, language_changed_supported_locale_spanish, \
    reset_language_code_to_en_us
from set_top_box.client_api.Menu.conftest import disable_parental_controls, \
    setup_cleanup_parental_and_purchase_controls, setup_parental_controls_and_always_require_pin


@pytest.mark.usefixtures("setup_home")
class TestMultiLocale:
    """
    As per new functionality hydra app support multi-locales, On Phase -1 implementation support Spanish.
      following two approach for Language change
        1. Navigate Device Setting --> Device Preference --> Language --> Change Language.
        2. Passing APP_LANGUAGE_CODE flag in tcdui_test.config

    following test cases will be covered.
        1. App launches with Unsupported Language : Verify Unsupported pop-up shows or not and fallback to en_US locale
        2. App launches with Supported Language: Verify content is localed with selected language or not.

        Use case -1 Test cases:
        https://testrail.tivo.com//index.php?/cases/view/5314733
        https://testrail.tivo.com//index.php?/cases/view/5314734

        Use Case -2 Test cases:
        https://testrail.tivo.com//index.php?/cases/view/5314732

      DRD document :
      https://confluence.tivo.com/display/IPTVAcc/Multi+Language+support+for+Streamers

    """

    @pytest.mark.multi_locale
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("language_changed_supported_locale_spanish")
    @pytest.mark.usefixtures("reset_language_code_to_en_us")
    def test_5314732_verify_app_launches_with_supported_language(self):
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.multi_locale
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("language_changed_unsupported_locale_filipino")
    @pytest.mark.usefixtures("reset_language_code_to_en_us")
    def test_5314733_5314734_verify_app_launches_with_unsupported_language(self):
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.screen.refresh()
        self.home_assertions.verify_language_not_supported()
        self.screen.refresh()
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)

    @pytest.mark.multi_locale
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("language_changed_supported_locale_spanish")
    @pytest.mark.usefixtures("reset_language_code_to_en_us")
    def test_verify_homescreen_translated_string(self):
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.home_assertions.verify_screen_title(self.home_labels.LBL_HOME_SCREENTITLE)
        for i in self.home_labels.LBL_HOME_MENU_ITEMS:
            self.home_assertions.verify_menu_item_available(i)
        self.home_page.goto_prediction()
        self.home_assertions.verify_predictions()
        self.home_assertions.verify_highlighter_on_prediction_strip()

    @pytest.mark.multi_locale
    @pytest.mark.xray("FRUM-121244")
    @pytest.mark.e2e1_18
    @pytest.mark.notapplicable(Settings.is_telus())
    @pytest.mark.notapplicable(Settings.hydra_branch() < Settings.hydra_branch(HydraBranches.STREAMER_1_18))
    @pytest.mark.timeout(Settings.timeout)
    @pytest.mark.usefixtures("setup_parental_controls_and_always_require_pin")
    @pytest.mark.usefixtures("reset_language_code_to_en_us")
    @pytest.mark.usefixtures("setup_cleanup_parental_and_purchase_controls")
    def test_121244_verify_pc_lock_icon_after_language_change(self):
        """
        FRUM - 121244 Verify PC rating after language change
        """
        pass
        self.system_page.change_language(user_language_code="es-US")
        self.screen.refresh()
        self.home_page.handling_hydra_app_after_exit(Settings.app_package, is_wait_home=True)
        self.home_assertions.verify_home_mode()
        self.home_assertions.verify_pc_lock_icon()
