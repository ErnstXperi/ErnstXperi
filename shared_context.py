

class ExecutionContext:
    """
    The object is test execution context and serve for sharing object across framework independently
    The object is singleton

    Examples:
        ExecutionContext.service_api = MindInterface(Settings).service
    """
    def __init__(self):
        raise AssertionError("ExecutionContext is static and cannot be instantiated")

    service_api = None  # mind_api.middle_mind.service_api.ServiceAPI
    vod_api = None  # mind_api.middle_mind.vod_api_helper.VODApiHelper
    pps_api_helper = None  # mind_api.middle_mind.device_provisioning_api_helper.DeviceProvisioningApiHelper
    iptv_prov_api = None  # mind_api.iptv_provisioning_mind.iptv_prov_api.IptvProvisioningApi
    health_api = None  # mind_api.middle_mind.health_api_helper.HealthApiHelper
    api_parser = None  # mind_api.middle_mind.api_parser.ApiParser
    loki_labels = None  # mind_api.middle_mind.loki_api_helper.LokiApiHelper
    eula_api = None  # mind_api.eula.eulahandler.EULAHandler
    mind_if = None  # mind_api.mind_interface.MindInterface
    user = {}
