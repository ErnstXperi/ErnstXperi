import pytest

from set_top_box.client_api.splunk.conftest import setup_splunk, get_attributes_from_yml, setup_livetv


@pytest.mark.usefixtures('setup_splunk')
class TestQoe:
    livetv_splunk_result = {}

    @pytest.mark.usefixtures('setup_livetv')
    @pytest.mark.parametrize("event", get_attributes_from_yml(actual_event_name='playbackQoeEvents'))
    def test_frum_143715_splunk_qoe_live_tv(self, event):
        self.home_page.log.info(f"checking event: {event}")
        self.splunk_assertions.verify_splunk_response_not_empty(TestQoe.livetv_splunk_result)
        attributes = get_attributes_from_yml(actual_event_name=event)
        self.splunk_assertions.verify_attributes_for_the_event_in_splunk_responses(event, attributes,
                                                                                   TestQoe.livetv_splunk_result)
