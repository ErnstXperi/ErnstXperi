import sys

import pytest

from set_top_box.client_api.vision_tester.conftest import setup_vision_tester, vt_precondition, \
    device_wakeup
from set_top_box.client_api.guide.conftest import setup_guide
from set_top_box.client_api.my_shows.conftest import setup_myshows_delete_recordings
from set_top_box.test_settings import Settings
from set_top_box.client_api.Menu.conftest import disable_parental_controls
from set_top_box.client_api.home.conftest import ndvr_health_store
from set_top_box.conftest import health_check
from tools.logger.logger import Logger
from set_top_box.shared_context import ExecutionContext


@pytest.mark.ndvr_health_check_vt
@pytest.mark.usefixtures('device_wakeup')
@pytest.mark.usefixtures('vt_precondition')
@pytest.mark.usefixtures('setup_vision_tester')
@pytest.mark.notapplicable(not health_check)
class TestNdvrHealthCheckVT(object):
    """
    TS: To verify ndvr health check
    param: -
    status: -
    """

    ndvr_channels = []
    cl = {}
    if health_check:
        log = Logger(__name__)
        api = ExecutionContext.service_api
        try:
            cl = api.channel_details
            ndvr_channels = api.get_ndvr_channels_for_health_check()
        except Exception as err:
            log.error("Failed to generate channel list: {}".format(err))
            ndvr_channels.append(err)

    @pytest.mark.parametrize('cn', ndvr_channels)
    @pytest.mark.usefixtures("setup_myshows_delete_recordings")
    @pytest.mark.usefixtures("ndvr_health_store")
    def test_ndvr_health_check(self, cn, mso=Settings.mso, clist=cl):
        record_status = True
        show_detail = clist.get(cn)
        show_details = self.api.record_currently_airing_shows(1, includeChannelNumbers=cn)
        if len(show_details) <= 0:
            record_status = False
            result = "failed to schedule recording"
            device_time = self.my_shows_page.get_current_time()
            self.service_api.cached_channel_info(
                [cn, show_detail[0], record_status, result, None, device_time, record_status])
            pytest.fail("{}: {}".format(result, record_status))
        self.my_shows_page.select_and_start_recording_playback(self, show_details[0][0])
        status, result = self.guide_page.get_playback_status_and_result(self, cn)
        self.service_api.cached_channel_info(
            [cn, show_detail[0], status, result, show_details[0][0], show_details[0][2], record_status], mode="ndvr")
        self.guide_assertions.verify_channel_playback_status(status, result)
        self.vision_page.verify_av_playback(status=status, result=result)
