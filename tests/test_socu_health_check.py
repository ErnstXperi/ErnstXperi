import sys

import pytest

from set_top_box.client_api.guide.conftest import setup_guide, channel_status_store
from set_top_box.test_settings import Settings
from tools.logger.logger import Logger
from set_top_box.client_api.Menu.conftest import disable_parental_controls
from set_top_box.client_api.home.conftest import socu_health_store
from set_top_box.shared_context import ExecutionContext
from set_top_box.conftest import health_check


@pytest.mark.socu_health_check
@pytest.mark.notapplicable(not health_check)
class TestSocuHealthCheck(object):
    """
    TS: To verify ndvr health check
    param: -
    status: -
    """

    def pytest_generate_tests(self, metafunc):
        """
        Hook to generate TC ids for every channel. Uses in TestLiveTvHealthCheck
        """
        if "socu_channels" in metafunc.fixturenames:
            socu_channels = []
            if not metafunc.config.getoption("skip_health_check"):
                socu_channels = ExecutionContext.service_api.socu_channels
            metafunc.parametrize("socu_channels", socu_channels)

    @pytest.fixture(autouse=True)
    def setup(self, request):
        self.log = Logger(__name__)

    @pytest.mark.usefixtures("socu_health_store")
    def test_socu_health_check(self, socu_channels, mso=Settings.mso):
        cn_data = self.service_api.get_all_socu_channels_details[socu_channels]
        st_pgm, st_status, st_result, cu_pgm, cu_status, cu_result = self.guide_page.start_socu_playback(self, socu_channels,
                                                                                                         st=cn_data[2],
                                                                                                         cu=cn_data[1])
        self.service_api.cached_channel_info(
            [socu_channels, cn_data[3], cn_data[2], st_pgm, st_status, st_result, cn_data[1], cu_pgm, cu_status, cu_result],
            mode="socu")
        self.guide_assertions.verify_socu_playback_status(st_pgm, st_status, st_result, cu_pgm, cu_status, cu_result)
