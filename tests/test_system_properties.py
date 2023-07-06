import pytest  # noqa: F401

from set_top_box.client_api.Menu.conftest import *
from set_top_box.client_api.service_properties.conftest import *
from set_top_box.client_api.service_properties.assertions import *
from set_top_box.client_api.apps_and_games.conftest import setup_cleanup_bind_hsn  # noqa: F401
from set_top_box.client_api.VOD.conftest import setup_clear_subscriptions  # noqa: F401
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings  # noqa: F401
from set_top_box.client_api.guide.conftest import setup_cleanup_list_favorite_channels_in_guide  # noqa: F401
from set_top_box.client_api.my_shows.conftest import setup_delete_book_marks  # noqa: F401
from set_top_box.client_api.account_locked.conftest import cleanup_enabling_internet
from pytest_testrail.plugin import pytestrail
from set_top_box.conf_constants import HydraBranches


@pytest.mark.usefixtures("setup_service_properties")
class TestServiceProperties(object):

    @pytest.mark.test_stabilization
    @pytest.mark.xray("FRUM-72222")
    def test_frum72222_verify_mywanipaddress_fetched_on_device_reboot(self):
        """
        This test case verifies that the wanipaddress returned in adb logs for a device is same as in Open/Trio api
        response.The test case is a part of Open API automation scope.
        https://jira.xperi.com/browse/FRUM-72222
        """
        ipaddress = self.api.get_mywanipaddress_from_api()
        self.menu_page.relaunch_hydra_app(self.home_labels.LBL_HOME_SCREEN_NAME)
        self.service_properties_assertions.verify_wanipaddress_is_found_in_logs(ipaddress)
