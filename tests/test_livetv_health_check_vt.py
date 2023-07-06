import pytest

from set_top_box.client_api.vision_tester.conftest import setup_vision_tester, vt_precondition  # noqa:F401
from set_top_box.client_api.guide.conftest import setup_guide, channel_status_store  # noqa:F401
from set_top_box.client_api.Menu.conftest import disable_parental_controls  # noqa:F401
from set_top_box.test_settings import Settings
from tools.logger.logger import Logger
from set_top_box.shared_context import ExecutionContext


@pytest.mark.livetv_health_check_vt
@pytest.mark.usefixtures('vt_precondition')
@pytest.mark.usefixtures('setup_vision_tester')
class TestLiveTvHealthCheckVT(object):
    """
    TC: To verify channel and playback URL health check
    param: -
    status: -
    """

    def pytest_generate_tests(self, metafunc):
        """
        Hook to generate TC ids for every channel. Uses in TestLiveTvHealthCheck
        """
        if "channel_ids" in metafunc.fixturenames:
            channels_ids = []
            if not metafunc.config.getoption("skip_health_check"):
                channels_ids = ExecutionContext.service_api.channels_ids
            metafunc.parametrize("channel_ids", channels_ids)

    @pytest.fixture(autouse=True)
    def setup(self, request):
        self.log = Logger(__name__)

    @pytest.mark.usefixtures("channel_status_store")
    # @pytest.mark.test_stabilization
    def test_livetv_health_check_vt(self, channel_ids):
        channel_detail = self.service_api.channel_details[channel_ids]
        channel = (channel_ids, channel_detail[1], channel_detail[2], channel_detail[3], channel_detail[0])
        status, result, url_status, url = self.guide_page.playback_status_check_on_device(self, channel)
        self.service_api.cached_channel_info(
            [channel_ids, channel_detail[0], status, result, url_status, url, channel_detail[5]])
        self.vision_page.verify_av_playback(status=status, result=result, url=url)
