import json
import requests
import time
import re
import random
from datetime import datetime, timedelta, timezone
from dateutil import tz
from http import HTTPStatus
import os
import pytz

import pytest

from mind_api.dependency_injection.containers.wanipaddress_container import WanIpAddressContainer
from tools.logger.logger import Logger
from tools.utils import DateTimeUtils
from shared_components.caching import Cacher
from tools.tcdui_config_parser import SpecializationExtractor
from mind_api.middle_mind.service_api import ServiceAPI
from mind_api.dependency_injection.containers.channel_container import ChannelIocContainer
from mind_api.dependency_injection.containers.station_policies_container import StationPoliciesIocContainer
from mind_api.dependency_injection.containers.station_container import StationIocContainer
from mind_api.dependency_injection.containers.grid_row_container import GridRowIocContainer
from mind_api.dependency_injection.containers.guide_cell_container import GuideCellIocContainer
from mind_api.dependency_injection.containers.one_line_guide_tile_container import OlgTileIocContainer
from mind_api.dependency_injection.containers.preview_offer_container import PreviewOfferIocContainer
from mind_api.dependency_injection.containers.actions_offer_container import ActionsOfferIocContainer
from mind_api.dependency_injection.containers.wtw_container import WtwContainer
from mind_api.dependency_injection.containers.airing_container import AiringIocContainer
from mind_api.dependency_injection.containers.excluded_partners_container import ExcludedPartnersContainer
from mind_api.dependency_injection.containers.branding_container import BrandingContainer
from mind_api.dependency_injection.containers.offer_container import OfferIocContainer
from mind_api.dependency_injection.containers.myshows_container import MyShowsIocContainer
from mind_api.dependency_injection.containers.search_container import SearchContainer
from mind_api.dependency_injection.containers.ipppv_details_container import IpppvDetailsContainer
from mind_api.dependency_injection.containers.session_create_container import SessionCreateContainer
from mind_api.dependency_injection.containers.vod_ott_action_details_container import VodOttActionDetailsContainer
from mind_api.dependency_injection.containers.may_also_like_container import MayAlsoLikeContainer
from mind_api.dependency_injection.containers.on_demand_availability import OnDemandAvailabilityIocContainer
from mind_api.dependency_injection.containers.rating_instructions_container import RatingInstructionsContainer


class ServiceOpenAPI(ServiceAPI):
    """
    Notes:
        1. Add the method with the same name that method from Mind API has if you add a replacing method in OpenAPI.
    """

    def __init__(self, settings, *args, **kwargs):
        super(ServiceAPI, self).__init__(settings, *args, **kwargs)
        self.log = Logger(__name__)
        self.settings = settings

    def get_headers(self, tsn=None):
        """
        Args:
            tsn (str): TiVo Serial Number e.g. A8F0F0000218A21

        Notes:
            Settings.api_additional_headers: it's used in mind_api.open_api.open_api.SeriviceOpenAPI, contained keys:
             - assigned_marker_names: str, comma-separated markers assigned to currently running test
             - test_case_name: currently running test name e.g. test_one or test_one[True-False-param1] (if parametrized test)
        """
        tsn = tsn or self.settings.tsn
        mso_partner_id = self.get_mso_partner_id(tsn)
        api_addit_headers = self.settings.api_additional_headers if "api_additional_headers" in vars(self.settings) else dict()
        markers_assigned_to_test = api_addit_headers.get("assigned_marker_names")
        running_test_name = api_addit_headers.get("test_case_name")
        language = self.settings.language[0:self.settings.language.find("_")] + "-" + \
            self.settings.language[self.settings.language.find("_") + 1:].upper()
        app_version = "UTAF_{}".format(self.settings.branch) if "branch" in self.settings.__dict__ else "UTAF_Hydra"
        body_config = self.get_body_config_search(use_cached_response=True)
        # Sometimes, bodyConfig may not return secondsFromGmt, so let's set GMT offset to PST when it happens
        sec_gmt = body_config.get("secondsFromGmt", -28800)
        utc_offset = timedelta(seconds=sec_gmt)
        now = datetime.now(pytz.utc)
        time_zone_name_list = [
            _t_z.zone for _t_z in map(pytz.timezone, pytz.all_timezones_set) if now.astimezone(_t_z).utcoffset() == utc_offset]
        time_zone_name = time_zone_name_list[0] if time_zone_name_list else "America/Denver"
        headers_to_add = {"Authorization": self.get_authorization_token(tsn, use_cached_response=True),
                          "ApplicationVersion": app_version,
                          "ApplicationName": app_version,
                          "ProductName": app_version,
                          "ApplicationFeatureArea": "UTAF_OpenAPI",
                          "BodyId": f"tsn:{tsn}",
                          "TimeZoneName": time_zone_name,
                          "DeviceType": self.get_device_type(),
                          "Accept-Language": language,
                          "Accept-Encoding": "identity",
                          "User-Agent": "UTAF",
                          "MsoPartnerId": mso_partner_id,
                          # "Whiny": "true",  # set it temporarily only if you need to debug a service issue
                          "TestCaseName": running_test_name,
                          "TestSuiteName": markers_assigned_to_test,
                          "JenkinsJobName": os.environ.get("JOB_NAME") or os.environ.get("HOSTNAME"),
                          "Content-Type": "application/json"}
        return headers_to_add

    @Cacher.process
    def get_channel_search(self, tsn=None, is_received=True, channel_count=0, omit=True, entitled=None,
                           use_cached_response=True, **kwargs):
        """
        /v1/channels
        Method to return all channels, to modify payload please use **kwargs
        Method supported since Hydra v1.15.

        Args:
            tsn (str): TiVo serial number
            is_received (bool): is received
            channel_count (int): number of channels to be returned, 0 means no limit on number of channels
            omit (bool): True - omitting channels without station
            entitled (bool): True - return only entitled channels
            is_favorite (bool): True - returns only favorite channels,
                                False - returns only non-favorite channels,
                                None - returns all channels no matter if it's favorite or not
            use_cached_response (bool): True - getting cached value, False - making request

        Returns:
            list, [Channel]
        """
        tsn = tsn or self.settings.tsn
        device_type = self.get_device_type()
        payload = {}
        include_unavailable_channels = kwargs.get("includeUnavailableChannels", False)
        is_favorite = kwargs.get("is_favorite", None)
        if channel_count:
            payload["count"] = channel_count
        if is_received is not None:
            payload["isReceived"] = is_received
        if 'Phone' not in device_type:  # Additional key added for Streamers
            payload['applicableDeviceType'] = device_type
        if include_unavailable_channels is not None:
            payload["includeUnavailableChannels"] = include_unavailable_channels
        if omit is not None:
            payload["omitChannelsWithNoStation"] = omit
        if is_favorite is not None:
            payload["isFavorite"] = is_favorite
        if kwargs:
            payload.update(kwargs)
        if is_received is None and "isReceived" in payload:
            del payload["isReceived"]
        if "applicableDeviceType" in payload and 'Phone' not in device_type:
            del payload["applicableDeviceType"]
        station_policies = self.get_station_policies(use_cached_response=True)
        url = self.url_resolver.get_endpoints("channels-iptv")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        channel_list = ChannelIocContainer.get_list(
            self.settings, url_base, port, payload, http_protocol=http_protocol, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name="open_api_channels",
            use_query_params=False, tsn=tsn, station_policy_list=station_policies,
            partner_id=self.get_mso_partner_id(self.settings.tsn), pcid=self.getPartnerCustomerId())
        if channel_count > 0 and len(channel_list) > channel_count:
            del channel_list[channel_count:]
        updated_list = []
        if entitled is not None:
            for channel in channel_list:
                if entitled and channel.is_entitled or \
                   not entitled and not channel.is_entitled:
                    updated_list.append(channel)
            channel_list = updated_list
        return channel_list

    def update_channel(self, chan_number_list, field_dict_to_update, omit=True):
        """
        Args:
            chan_number_list (list): list of channel numbers; update only channels being present in chan_number_list
                                     or all channels if chan_number_list is not set
            field_dict_to_update (dict): in format {fieldName: [fieldValue, mode]}, mode one of (update, delete)
        """
        # TODO
        # Activate method https://jira.xperi.com/browse/CA-21221 after channelSettings feature activation
        ch_list_json_updated = []
        tsn = self.settings.tsn
        ch_needed_fields = ["channelNumber", "isFavorite"]
        channel_list = self.get_channel_search(omit=omit)
        for channel in channel_list:
            # Let's leave only needed paramas for request
            cur_ch_upd_dict = {key: value for key, value in channel.dict_item.items() if key in ch_needed_fields}
            if channel.channel_number in chan_number_list or not chan_number_list:
                for k_field in field_dict_to_update:
                    if field_dict_to_update[k_field][1] == "update":
                        cur_ch_upd_dict[k_field] = field_dict_to_update[k_field][0]
                    elif field_dict_to_update[k_field][1] == "delete":
                        # If a param needs to be removed then it should not be conained in ch_needed_fields
                        continue
            if cur_ch_upd_dict.get("isFavorite") is None:
                # Handling the case when isFavorite is not set (False is the default value)
                cur_ch_upd_dict["isFavorite"] = False
            ch_list_json_updated.append(cur_ch_upd_dict)
        url = self.url_resolver.get_endpoints("cloudcore-channel-settings")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        self.url_resolver.make_request(
            url_base, port, ch_list_json_updated, http_protocol=http_protocol, http_method="post",
            function_name="open_api_channel_settings", use_query_params=False, headers=self.get_headers(tsn),
            update_headers=True)
        # Updating cached channel list, setting new value for isFavorite param
        self.get_channel_search(omit=omit, use_cached_response=False)

    @Cacher.process
    def get_station_policies(self, policy_name=None, use_cached_response=True):
        """
        /v1/stationPolicies
        This request returns all rules that can be applicable to channels.
        Info returned by this request conatains data related to streamingAndRecordingRules param from old Mind request.
        This is a brand new request, no analogue in Trio API.
        Supported since Hydra v1.15.

        Args:
            policy_name (str): station policy name e.g. ln:sol-lp-concurrency
            use_cached_response (bool): True - getting cached value, False - making request

        Returns:
            list, [StationPolicy] if policy_name is None
            StationPolicy, if policy_name is not None
        """
        tsn = self.settings.tsn
        station_policy_result = []
        url = self.url_resolver.get_endpoints("channels-iptv")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        if policy_name:
            station_policy_result = StationPoliciesIocContainer.get_item(
                self.settings, url_base, port, {}, policy_name, http_protocol=http_protocol, http_method="get",
                headers=self.get_headers(tsn), update_headers=True,
                function_name="open_api_station_policies", use_query_params=False, tsn=tsn)
        else:
            station_policy_result = StationPoliciesIocContainer.get_list(
                self.settings, url_base, port, {}, http_protocol=http_protocol, http_method="get",
                headers=self.get_headers(tsn), update_headers=True,
                function_name="open_api_station_policies", use_query_params=False, tsn=tsn)
        return station_policy_result

    @Cacher.process
    def get_station_search(self, tsn=None, count=2000, request_mdrm_fields=None, use_cached_response=True):
        """
        Note:
            There's no such thing as stationSearch since Hydra 1.15. This method was added just to support existing methods
            that call get_station_search(), do not use this method if preparing API for Hydra in this file.

        Args:
            tsn (str): TiVo serial number
            count (int): stations number to return
            request_mdrm_fields (dict): request mdrm fields; e.g. {"supportedDrmType": [drm_server_type["trioSodiDirect"]],
                                        "supportedTransportEncodingType": ["hlsFmp4TransportStream", "hlsTransportStream"]}
            use_cached_response (bool): True - using cached value for stationSearch without making request,
                                        False - making staionSearch request

        Returns:
            list, [Station]
        """
        kwargs = request_mdrm_fields if request_mdrm_fields else {}
        channel_list = self.get_channel_search(tsn=tsn, is_received=None, omit=True, entitled=None, count=count,
                                               includeUnavailableChannels=True,
                                               use_cached_response=use_cached_response, **kwargs)
        station_list = []
        tsn = tsn if tsn else self.settings.tsn
        url = self.url_resolver.get_endpoints("channels-iptv")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        station_list = StationIocContainer.get_list(
            self.settings, url_base, port, {}, http_protocol=http_protocol, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name="open_api_channels",
            use_query_params=False, tsn=tsn, channel_list=channel_list)
        if count > 0 and len(station_list) > count:
            del station_list[count:]
        return station_list

    @Cacher.process
    def get_onDemandAvailabilityList(self, collectionId, contentId=None, use_cached_response=False, **kwargs):
        """
        Note:
            There's no such thing as stationSearch since Hydra 1.15. This method was added just to support existing methods
            that call get_station_search(), do not use this method if preparing API for Hydra in this file.

        Args:
            collectionId (str): Collection Id
            contentId (str): Content ID
            # tsn (str): TiVo serial number
            # count (int): providers number to return
            # request_mdrm_fields (dict): request mdrm fields; e.g. {"supportedDrmType": [drm_server_type["trioSodiDirect"]],
            #                             "supportedTransportEncodingType": ["hlsFmp4TransportStream", "hlsTransportStream"]}
            use_cached_response (bool): True - using cached value for stationSearch without making request,
                                        False - making staionSearch request

        Returns:
            list, [Providers]
        """
        self.log.info("Checking onDemandAvailability with open api")
        tsn = self.settings.tsn
        screen_type = kwargs.get("screen_type", "wtwnScreen")
        enable_critic_rating = kwargs.get("enable_critic_rating", True)
        if contentId is not None:
            function_name = "open_api_preview_content"
            param = contentId
        else:
            function_name = "open_api_preview_series"
            param = collectionId
        preview_offer_payload = {"screenType": screen_type, "enableCriticRating": "true" if enable_critic_rating else "false"}
        preview_offer_url = self.url_resolver.get_endpoints("cloudcore-previews")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(preview_offer_url)[0:3]
        providers_list = OnDemandAvailabilityIocContainer.get_item(
            self.settings, url_base, port, preview_offer_payload, http_protocol=http_protocol, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name=function_name, use_query_params=False,
            tsn=tsn, part_uri="/{}".format(param))
        return providers_list

    @Cacher.process
    def get_mywanipaddress_from_api(self, tsn=None, use_cached_response=False, **kwargs):
        """
        /v1/myWanIpAddress
        This api will fetch mywanipaddress using open/new api.
        Method supported since Hydra v1.16.
        """
        self.log.info("Calling myWanIpAddress from OpenAPI")
        tsn = tsn or self.settings.tsn
        url = self.url_resolver.get_endpoints("httpsinsecurexff")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        response = WanIpAddressContainer.get_item(
            self.settings, url_base, port, {}, http_protocol=http_protocol, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name="wanip_open_api",
            use_query_params=False, tsn=tsn)
        return response.ip_address

    @Cacher.process
    def get_guide_rows(self, channel_list, window_start_time=None, window_end_time=None,
                       dict_key="channel_number", dup_programs_on_edge=False, use_cached_response=False):
        """
        /v1/guideRows
        Client application calls this request to get programs for Grid Guide.
        Supported since Hydra v1.18.
        Getting Guide Cells.

        Args:
            channel_list (list): [Channel]
            window_start_time (int): UTC time in seconds e.g. datetime.now().timestamp(), if None - current time is taken
            window_end_time (int): UTC time in seconds e.g. datetime.now().timestamp(), if None - +2 hours is chosen
            dict_key (str): one of (channel_id, channel_number, station_id)
            dup_programs_on_edge (bool): True - duplicating programs that starts in current 2 hour time frame and
                                                end in the next one (may come in handy when you need to get
                                                number of steps Left/Right to get to the needed program in Grid Guide)
                                                Note: it makes number of programs bigger than it actually is
                                         False - leaving only one program on the list if it starts in current
                                                 2 hour time frame and end in the next one
                                                 (it only affects the steps on UI, may come in handy if you need
                                                 to get the real number of programs for a channel);
            use_cached_response (bool): True - getting cached value of channelSearch, False - making channelSearch request

        Returns:
            dict, {channelNumber: [GuideCell]}
        """
        tsn = self.settings.tsn
        cur_mind_time = datetime.strptime(
            self.get_middle_mind_time(tsn, use_cached_response=use_cached_response)["currentTime"], self.MIND_DATE_TIME_FORMAT)
        w_start_time = window_start_time if window_start_time else cur_mind_time.timestamp()
        max_window_size = timedelta(hours=GuideCellIocContainer.MAX_TIME_FRAME_SIZE_IN_HOURS)
        end_time = datetime.fromtimestamp(int(w_start_time)) + max_window_size
        w_end_time = window_end_time if window_end_time else end_time.timestamp()
        guide_row_payload = {
            "msoPartnerId": self.get_mso_partner_id(tsn),
            "stationId": [],  # needs to be set in GuideCellIocContainer
            "windowStartTime": int(w_start_time),
            "windowEndTime": int(w_end_time)}
        guide_cell_url = self.url_resolver.get_endpoints("cloudcore-guide")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(guide_cell_url)[0:3]
        guide_cell_dict = GuideCellIocContainer.get_dict(
            self.settings, url_base, port, guide_row_payload, channel_list=channel_list, cur_mind_time=cur_mind_time,
            http_protocol=http_protocol, http_method="get", headers=self.get_headers(tsn), update_headers=True,
            dict_key=dict_key, function_name="open_api_guide_cell", use_query_params=False,
            dup_programs_on_edge=dup_programs_on_edge)
        return guide_cell_dict

    @Cacher.process
    def get_one_line_guide_cells(self, channel_item, count=50, offset=0, past_mode=False, use_cached_response=False):
        """
        /v1/oneLineGuideCells
        Client application calls this request to get programs for One Line Guide.
        Getting One Line Guide Cells. Can make request for the only one station at a time.

        Args:
            channel_item (Channel): channel
            count (int): number of Guide Cells to return, 50 max
            offset (int): change to get next portion of Guide Cells
            past_mode (bool): True - getting items from past OLG, False - gettings items from current and future OLG
            use_cached_response (bool): True - getting cached value, False - making request

        Returns:
            list, [GuideCell]
        """
        tsn = self.settings.tsn
        cur_mind_time = datetime.strptime(
            self.get_middle_mind_time(tsn, use_cached_response=use_cached_response)["currentTime"], self.MIND_DATE_TIME_FORMAT)
        anchor_time = OlgTileIocContainer.get_timestamp_multiple_of(cur_mind_time.timestamp(), 1800, False)
        olg_payload = {
            "msoPartnerId": self.get_mso_partner_id(tsn, use_cached_response=True),
            "anchorTime": anchor_time,
            "stationId": channel_item.station_id,
            "count": count,
            "offset": offset,
            "pastMode": "true" if past_mode else "false"}
        olg_url = self.url_resolver.get_endpoints("cloudcore-guide")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(olg_url)[0:3]
        olg_cell_list = OlgTileIocContainer.get_list(
            self.settings, url_base, port, olg_payload, channel_item=channel_item, cur_mind_time=cur_mind_time,
            http_protocol=http_protocol, http_method="get", headers=self.get_headers(tsn), update_headers=True,
            function_name="open_api_olg_tile", use_query_params=False)
        return olg_cell_list

    def get_recordable_non_recordable_channel_items(self, channel_list=None):
        """
        Method supported since Hydra v1.15.

        Args:
            channel_list (list): [Channel]

        Returns:
            dict, {channelNumber: bool}, True - channel is recordable, False - otherwise
        """
        tsn = self.settings.tsn
        channel_list = self.get_channel_search(tsn=tsn, is_received=None, include_unavailable_channels=True, omit=False) \
            if not channel_list else channel_list
        restrictions_details = {}
        for channel in channel_list:
            restrictions_details[channel.channel_number] = False  # channel is not allowed to record
            restr_capability = channel.policy_rules("recordingRules", "restrictedCapability")
            if restr_capability and "allowRecording" in restr_capability:
                restrictions_details[channel.channel_number] = True  # channel is allowed to record
        self.log.debug(f"restrictions_details = {restrictions_details}")
        return restrictions_details

    def get_recordable_channels_list(self):
        """
        Method supported since Hydra v1.15.


        Returns:
            list [Channels]
        """
        tsn = self.settings.tsn
        channel_list = self.get_channel_search(tsn=tsn, is_received=None, include_unavailable_channels=True, omit=False,
                                               entitled=True)
        recordable_channels = []
        for channel in channel_list:
            restr_capability = channel.policy_rules("recordingRules", "restrictedCapability")
            if restr_capability and "allowRecording" in restr_capability:
                recordable_channels.append(channel)     # channel is allowed to record
        self.log.debug(f"restrictions_details = {recordable_channels}")
        return recordable_channels

    def get_filtered_channels_by_guide_cell_attributes(self, chan_show_list, is_catchup=None, is_startover=None,
                                                       is_adult=None, is_ppv=None, is_new=None, content_type=None):
        """
        Method supported since Hydra v1.18.

        Args:
            chan_show_list (list): [[channelNumber, GuideCell, Channel, [steps, left/right]]]
        `   is_catchup (bool): True - select channels with catchup shows, False - with non-catchup ones;
                               mostly refers to shows available from SOCU and located in Past Guide
            is_startover (bool): True - select channels with startover shows, False - with non-startover ones;
                                 mostly refers to shows available from SOCU and located in In-Progress Guide
            is_adult (bool): True - select channels with adult shows, False - with non-adult ones
            is_ppv (bool): True - select channels with ppv shows, False - with non-ppv ones
            is_new (bool): True - select channels with new shows, False - with non-new ones
            content_type (str): if set, one of (special, episode, movie, series), None - any content taken

        Returns:
            list, [[channelNumber, GuideCell, Channel, [steps, left/right]]] filtered values
        """
        filtered_rows = []
        for item in chan_show_list:
            cell = item[1]
            satisfied_condition_list = []
            satisfied_condition_list.append(self.compare_bool_param(is_catchup, cell.is_catchup))
            satisfied_condition_list.append(self.compare_bool_param(is_startover, cell.is_startover))
            satisfied_condition_list.append(self.compare_bool_param(is_adult, cell.is_adult))
            satisfied_condition_list.append(self.compare_bool_param(is_ppv, cell.is_ppv))
            satisfied_condition_list.append(self.compare_bool_param(is_new, cell.is_new))
            if content_type and content_type == cell.content_type:
                satisfied_condition_list.append(True)
            elif content_type and content_type != cell.content_type:
                satisfied_condition_list.append(False)
            if satisfied_condition_list and all(satisfied_condition_list):
                filtered_rows.append(item)
        # self.log.debug(f"get_filtered_channels_by_guide_cell_attributes - filtered channels: {filtered_rows}")
        return filtered_rows

    def get_filtered_channels_by_recordable_non_recordable(self, chan_show_list, cur_time_seconds, last_frame_end_time,
                                                           restrictions_details, is_recordable_chan=None,
                                                           is_recordable_show=None, is_copyright_restricted=None,
                                                           is_recordable_in_the_past=None):
        """
        Method supported since Hydra v1.18.

        Args:
            chan_show_list (list): [[channelNumber, GuideCell, Channel, [steps, left/right]]]
        `   cur_time_seconds (str): datetime.now().timestamp()
            last_frame_end_time (str): datetime.now().timestamp() (make it multiple by 1800 to lower side) + 2 hours
            restrictions_details (dict): value from get_recordable_non_recordable_channel_items()
            is_recordable_chan (bool): True - select channels that allow recording, False - with non-recordable ones;
                                       Note: can be applicable when need to test e.g. Past Guide on recordable channel
            is_recordable_show (bool): True - select channels with recordable shows, False - with non-recordable ones;
                                       Note: can be applicable when need to test recordable/non-recordable show
            is_copyright_restricted (bool): True - select channels with not allowed to record shows due to
                                                   copyright restriction,
                                            False - otherwise;
                                            Note: to use this param, get only in-progress and future shows
            is_recordable_in_the_past (bool): True - taking channels with recordInThePastSeconds > 0,
                                              False - taking channels with recordInThePastSeconds == 0 or without this param,
                                              None - any channel

        Returns:
            list, [[channelNumber, GuideCell, Channel, [steps, left/right]]] filtered values
        """
        filtered_rows = []
        for item in chan_show_list:
            cell = item[1]
            channel = item[2]
            record_in_the_past_sec = channel.policy_rules("recordingRules", "recordInThePastSeconds")
            chan_recordable = restrictions_details[item[0]]
            satisfied_condition_list = []
            if is_recordable_chan and chan_recordable or is_recordable_chan is None or \
               is_recordable_chan is False and not chan_recordable:
                satisfied_condition_list.append(True)
            elif is_recordable_chan is not None:
                satisfied_condition_list.append(False)
            if is_recordable_show and cell.is_recordable and chan_recordable or is_recordable_show is False and \
               (not cell.is_recordable or not chan_recordable) or is_recordable_show is None:
                satisfied_condition_list.append(True)
            elif is_recordable_show is not None:
                satisfied_condition_list.append(False)
            if is_copyright_restricted and not cell.is_recordable and chan_recordable and \
               last_frame_end_time > cur_time_seconds or \
               is_copyright_restricted is None or \
               is_copyright_restricted is False and \
               cell.is_recordable and chan_recordable and last_frame_end_time > cur_time_seconds:
                satisfied_condition_list.append(True)
            elif is_copyright_restricted is not None:
                satisfied_condition_list.append(False)
            if is_recordable_in_the_past and record_in_the_past_sec is not None and record_in_the_past_sec > 0 or \
               is_recordable_in_the_past is None or \
               is_recordable_in_the_past is False and (record_in_the_past_sec is None or record_in_the_past_sec == 0):
                satisfied_condition_list.append(True)
            elif is_recordable_in_the_past is not None:
                satisfied_condition_list.append(False)
            if satisfied_condition_list and all(satisfied_condition_list):
                filtered_rows.append(item)
        # self.log.debug(f"get_filtered_channels_by_recordable_non_recordable - filtered channels: {filtered_rows}")
        return filtered_rows

    def get_filtered_channels_by_show_duration(self, chan_show_list, cur_time_seconds, first_frame_start_time,
                                               last_frame_end_time, is_live=None, duration_lt=None, duration_gt=None,
                                               take_not_ended_shows=None, ends_in_lt=None, ends_in_gt=None):
        """
        Method supported since Hydra v1.18.

        Args:
            chan_show_list (list): [[channelNumber, GuideCell, Channel, [steps, left/right]]]
        `   cur_time_seconds (str): datetime.now().timestamp()
            last_frame_end_time (str): datetime.now().timestamp() (make it multiple by 1800 to lower side) + 2 hours
            first_frame_start_time (str): datetime.now().timestamp() (make it multiple by 1800 to lower side)
            is_live (bool): True - taking currently airing show, False - taking not currently airing show,
                            None - taking any show;
                            Note: takes priority over cell_index
            duration_gt (int): duration in seconds > 0; selects channels with show duration >= duration_gt
            duration_lt (int): duration in seconds > 0; selects channels with show duration <= duration_lt
            ends_in_gt (int): duration in seconds > 0; selects channels with currently airing show that ends in >= ends_in_gt
            ends_in_lt (int): duration in seconds > 0; selects channels with currently airing show that ends in <= ends_in_lt
            take_not_ended_shows (bool): if taking/not taking shows that started in Past Guide and still continue streaming;
                                         may be applicable when taking Past Guide shows

        Returns:
            list, [[channelNumber, GuideCell, Channel, [steps, left/right]]] filtered values
        """
        filtered_rows = []
        for item in chan_show_list:
            cell = item[1]
            start_time = int(cell.start_time)
            duration = int(cell.duration)
            satisfied_condition_list = []
            satisfied_condition_list.append(self.compare_bool_param(
                is_live, is_live and start_time + duration > cur_time_seconds and start_time <= cur_time_seconds))
            satisfied_condition_list.append(self.compare_bool_param(duration_gt, duration_gt and duration >= duration_gt))
            satisfied_condition_list.append(self.compare_bool_param(duration_lt, duration_lt and duration <= duration_lt))
            satisfied_condition_list.append(self.compare_bool_param(
                ends_in_gt,
                ends_in_gt and start_time <= cur_time_seconds and start_time + duration - cur_time_seconds >= ends_in_gt))
            cond_ends_in_lt = ends_in_lt and start_time <= cur_time_seconds and \
                start_time + duration - cur_time_seconds > 0 and start_time + duration - cur_time_seconds <= ends_in_lt
            satisfied_condition_list.append(self.compare_bool_param(
                ends_in_lt, cond_ends_in_lt))
            # take_not_ended_shows: should is expected to be started in Past Guide
            cond_take_not_ended_shows = (start_time + duration) > cur_time_seconds and \
                start_time < first_frame_start_time and cur_time_seconds < last_frame_end_time or \
                (start_time + duration) > cur_time_seconds and cur_time_seconds > last_frame_end_time
            if take_not_ended_shows and cond_take_not_ended_shows or \
               take_not_ended_shows is None or \
               take_not_ended_shows is False and not cond_take_not_ended_shows:
                satisfied_condition_list.append(True)
            elif take_not_ended_shows is not None:
                satisfied_condition_list.append(False)
            if satisfied_condition_list and all(satisfied_condition_list):
                filtered_rows.append(item)
        # self.log.debug(f"get_filtered_channels_by_show_duration - filtered channels: {filtered_rows}")
        return filtered_rows

    def get_filtered_channels_by_channel_fields(self, chan_show_list, **kwargs):
        """
        Method supported since Hydra v1.15.

        Notes:
            StreamingRestrictions: one of (linearStreamingRestrictions, cuStreamingRestrictions, soStreamingRestrictions,
                npvrStreamingRestrictions, vodStreamingRestrictions)
            trickplayRestriction: one of (fastForward, pause, rewind)
            restrictedDeviceType:
                http://w3-engr.tivo.com/d-docs/autodocs/b-trioschema-mainline/trioschema/streamingDeviceType.html

        Args:
            chan_show_list (list): [[channelNumber, GuideCell, Channel, [steps, left/right]]]

        Kwargs:
            video_resolution (str): takes channels with passed video resolution (sd, hd, uhd),
                                    None - any channel
            is_encrypted (bool): True - select encrypted channels, False - select non-encrypted channels
            trickplay_restriction (tuple/list): e.g. ($streamingRestriction, $trickplayRestriction), ("any", "any");
                                                if ("any", None) {with None for trickplay restriction},
                                                then channels without trickplay_restriction are taken;
                                                None - any channel is taken
            restricted_device_type (tuple/list): e.g. ($streamingRestriction, $restrictedDeviceType), ("any", "any");
                                                 if ("any", None) {with None for restricted device type},
                                                 then channels without restricted_device_type are taken;
                                                 None - any channel is taken
        """
        video_resolution = kwargs.get("video_resolution", None)
        is_encrypted = kwargs.get("is_encrypted", None)
        trickplay_restriction = kwargs.get("trickplay_restriction", None)
        restricted_device_type = kwargs.get("restricted_device_type", None)
        supported_streaming_restriction_list = [
            "linearStreamingRestrictions", "cuStreamingRestrictions", "soStreamingRestrictions", "vodStreamingRestrictions",
            "npvrStreamingRestrictions"]
        channel_list = self.get_channel_search(is_received=None)
        encrypted_non_encrypted_channels = []
        if is_encrypted is not None:
            station_ids = self.get_encrypted_non_encrypted_station_ids(channel_list, is_encrypted)
            for channel in channel_list:
                if channel.station_id in station_ids and channel.channel_number not in encrypted_non_encrypted_channels:
                    encrypted_non_encrypted_channels.append(channel.channel_number)

        def __streaming_restriction_policy_rules(restriction_type, streaming_restriction_rule, channel_item):
            """
            Args:
                restriction_type (str): one of (trickplayRestriction, restrictedDeviceType)
                streaming_restriction_rule (tuple/list): e.g. ($streamingRestriction, $restriction_rule), ("any", "any");
                                                         if ("any", None) {with None for $restriction_rule},
                                                         then channels without $restriction_rule are taken;
                                                         None - any channel is taken
                channel_item (Channel): channel item

            Returns:
                bool
            """
            is_restriction = False
            if streaming_restriction_rule:
                for s_r in supported_streaming_restriction_list:
                    s_r_tmp = s_r if streaming_restriction_rule[0] == "any" else streaming_restriction_rule[0]
                    tp_restr = channel_item.policy_rules("linearStationRules", "streamingRules", s_r_tmp, restriction_type)
                    if tp_restr and (streaming_restriction_rule[1] == "any" or streaming_restriction_rule[1] in tp_restr) or \
                       streaming_restriction_rule[1] is None and tp_restr:
                        is_restriction = True
                if not is_restriction and streaming_restriction_rule[1] is None or \
                   is_restriction and streaming_restriction_rule[1] is not None:
                    return True
                else:
                    return False
            return True

        filtered_rows = []
        for item in chan_show_list:
            satisfied_condition_list = []
            satisfied_condition_list.append(
                self.compare_bool_param(is_encrypted, item[0] in encrypted_non_encrypted_channels))
            if video_resolution is None or video_resolution and item[2].video_resolution == video_resolution:
                satisfied_condition_list.append(True)
            elif video_resolution and item[2].video_resolution != video_resolution:
                satisfied_condition_list.append(False)
            satisfied_condition_list.append(
                __streaming_restriction_policy_rules("trickplayRestriction", trickplay_restriction, item[2]))
            satisfied_condition_list.append(
                __streaming_restriction_policy_rules("restrictedDeviceType", restricted_device_type, item[2]))
            if satisfied_condition_list and all(satisfied_condition_list):
                filtered_rows.append(item)
        # self.log.debug(f"get_filtered_channels_by_channel_fields - filtered channels: {filtered_rows}")
        return filtered_rows

    def __get_analyzed_cells(self, guide_cell_list, find_appropriate, cell_index, last_frame_end_time, cur_time_seconds,
                             is_bookmarkable=None):
        """
        Args:
            guide_cell_list (list): [GuideCell], list of Guide Cells for one channel
            find_appropriate (bool): True - analysing each program in a grid row to find appropriate one;
                                     False - default behavior - analysing only one program from a grid row;
                                     Note: takes priority over cell_index;
                                           increases number of fitting shows since it checks each program in a row
            cell_index (int): cell index in a cell list of a guide row to check;
                              Note, if it's not set, the 1st cell in a row is taken
        `   cur_time_seconds (str): datetime.now().timestamp()
            last_frame_end_time (str): datetime.now().timestamp() (make it multiple by 1800 to lower side) + 2 hours
            is_bookmarkable (bool): True - getting channels with shows that can be bookmarked on UI
                                          ("Bookmark this show/movie/episode" option is present),
                                    False - getting channels with shows that cannot be bookmarked on UI,
                                    None - any channel

        Returns:
            list, [GuideCell]
        """
        selected_cells = []
        for c_i in range(0, len(guide_cell_list)):
            cell = None
            if find_appropriate:
                cell_index = c_i
                cell = guide_cell_list[c_i]
            else:
                cell_index = cell_index if cell_index is not None else 0
                cell = guide_cell_list[cell_index] if cell_index < len(guide_cell_list) else None
            # Setting Guide Cell location in Grid Guide relatively to highlighted Channel Cell
            # (on UI, highlight a Channel Cell and then move left/right to a Guide Cell)
            steps_left_right = [len(guide_cell_list) - cell_index, "left"] if last_frame_end_time < cur_time_seconds \
                else [cell_index + 1, "right"]
            # Taking cell only if it's set
            if cell:
                if is_bookmarkable and cell.content_type != "series" or \
                   is_bookmarkable is False and cell.content_type == "series" or \
                   is_bookmarkable is None:
                    selected_cells.append((cell, steps_left_right))
            if not find_appropriate:
                break
        return selected_cells

    def get_random_channel_from_guide_rows(self, **kwargs):
        """
        /v1/guideRows
        Getting random channels with $count number of elements (1 by default) using OpenAPI /v1/guideRows.
        Method supported since Hydra v1.18.
        New request returns items that have new params such as isNew, isRecordable, these params are not present in offer.

        Kwargs:
            start_time (int): UTC time in seconds e.g. datetime.now().timestamp(), if None - current time is taken
            end_time (int): UTC time in seconds e.g. datetime.now().timestamp(), if None - +2 hours is chosen
            use_cached_response (bool): True - getting cached value of channelSearch, False - making channelSearch request
            skip_test_if_no_results (bool): True - skipping test if there's no results, False - return [] otherwise

            # If None - channels are returned without filering by param
            video_resolution (str): takes channels with passed video resolution (sd, hd, uhd),
                                    None - any channel
            is_encrypted (bool): True - select encrypted channels, False - select non-encrypted channels
            is_entitled (bool): True - select entitled channels, False - select non-entitled channels;
                                Note: set is_received param to None or False, to get non-entittled channels
            is_received (bool): True - select entitled and available channels, False - select non-entitled channels
            is_catchup (bool): True - select channels with catchup shows, False - with non-catchup ones;
                               mostly refers to shows available from SOCU and located in Past Guide
            is_startover (bool): True - select channels with startover shows, False - with non-startover ones;
                                 mostly refers to shows available from SOCU and located in In-Progress Guide
            is_adult (bool): True - select channels with adult shows, False - with non-adult ones
            is_ppv (bool): True - select channels with ppv shows, False - with non-ppv ones
            is_new (bool): True - select channels with new shows, False - with non-new ones
            is_recordable_show (bool): True - select channels with recordable shows, False - with non-recordable ones;
                                       Note: can be applicable when need to test recordable/non-recordable show
            is_recordable_chan (bool): True - select channels that allow recording, False - with non-recordable ones;
                                       Note: can be applicable when need to test e.g. Past Guide on recordable channel
            is_copyright_restricted (bool): True - select channels with not allowed to record shows due to
                                                   copyright restriction,
                                            False - otherwise;
                                            Note: to use this param, get only in-progress and future shows
            duration_gt (int): duration in seconds > 0; selects channels with show duration >= duration_gt
            duration_lt (int): duration in seconds > 0; selects channels with show duration <= duration_lt
            ends_in_gt (int): duration in seconds > 0; selects channels with currently airing show that ends in >= ends_in_gt
            ends_in_lt (int): duration in seconds > 0; selects channels with currently airing show that ends in <= ends_in_lt
            take_not_ended_shows (bool): if taking/not taking shows that started in Past Guide and still continue streaming;
                                         may be applicable when taking Past Guide shows
            count (int): number of channels to return; 0 or None - return all channels
            cell_index (int): cell index in a cell list of a guide row to check;
                              Note, if it's not set, the 1st cell in a row is taken
            content_type (str): if set, one of (special, episode, movie, series), None - any content taken
            is_live (bool): True - taking currently airing show, False - taking not currently airing show,
                            None - taking any show;
                            Note: takes priority over cell_index
            find_appropriate (bool): True - analysing each program in a grid row to find appropriate one;
                                     False - default behavior - analysing only one program from a grid row;
                                     Note: takes priority over cell_index;
                                           increases number of fitting shows since it checks each program in a row
            is_recordable_in_the_past (bool): True - taking channels with recordInThePastSeconds > 0,
                                              False - taking channels with recordInThePastSeconds == 0 or without this param,
                                              None - any channel
            get_playable_live_tv (bool): True - filtering playable live TV, False - no filtering
            get_playable_socu (bool): True - filtering playable SOCU, False - no filtering
            get_playable_ndvr (bool): True - filtering playable nDVR, False - no filtering
            exclude_tplus_channels (bool): True - excluding TiVo+ channels, False - no filtering
            exclude_plutotv_channels (bool): True - excluding PlutoTV channels, False - no filtering
            trickplay_restriction (tuple/list): e.g. ($streamingRestriction, $trickplayRestriction), ("any", "any");
                                                if ("any", None) {with None for trickplay restriction},
                                                then channels without trickplay_restriction are taken;
                                                None - any channel is taken
            restricted_device_type (tuple/list): e.g. ($streamingRestriction, $restrictedDeviceType), ("any", "any");
                                                 if ("any", None) {with None for restricted device type},
                                                 then channels without restricted_device_type are taken;
                                                 None - any channel is taken
            is_bookmarkable (bool): True - getting channels with shows that can be bookmarked on UI
                                          ("Bookmark this show/movie/episode" option is present),
                                    False - getting channels with shows that cannot be bookmarked on UI,
                                    None - any channel

        Returns:
            list, [[channelNumber, GuideCell, Channel, [steps, left/right]]]; steps + left/right shows how many steps
                  and where needed to be done to highlight a cell in Guide;
                  Note: Tip for Guide - get to Channel Cell before pressing Left/Right using steps from this item
        """
        self.log.info("Getting random channel from OpenAPI guideRows")
        start_time = kwargs.get('start_time', None)
        end_time = kwargs.get('end_time', None)
        use_cached_response = kwargs.get("use_cached_response", False)
        skip_test_if_no_results = kwargs.get('skip_test_if_no_results', True)
        # If None - channels are returned without filering by param
        video_resolution = kwargs.get('video_resolution', None)
        is_encrypted = kwargs.get('is_encrypted', None)
        is_entitled = kwargs.get('is_entitled', None)
        is_received = kwargs.get('is_received', True)
        is_catchup = kwargs.get('is_catchup', None)
        is_startover = kwargs.get('is_startover', None)
        is_adult = kwargs.get('is_adult', None)
        is_ppv = kwargs.get('is_ppv', None)
        is_new = kwargs.get('is_new', None)
        is_recordable_show = kwargs.get('is_recordable_show', None)
        is_recordable_chan = kwargs.get('is_recordable_chan', None)
        is_copyright_restricted = kwargs.get('is_copyright_restricted', None)
        duration_gt = kwargs.get('duration_gt', None)  # duration >= passed value
        duration_lt = kwargs.get('duration_lt', None)  # duration <= passed value
        ends_in_gt = kwargs.get('ends_in_gt', None)  # currently airing show end in >= passed value
        ends_in_lt = kwargs.get('ends_in_lt', None)  # currently airing show end in <= passed value
        take_not_ended_shows = kwargs.get('take_not_ended_shows', None)
        count = kwargs.get('count', 1)
        cell_index = kwargs.get('cell_index', 0)
        content_type = kwargs.get('content_type', None)
        is_live = kwargs.get('is_live', None)
        find_appropriate = kwargs.get('find_appropriate', False)
        is_recordable_in_the_past = kwargs.get('is_recordable_in_the_past', None)
        get_playable_live_tv = kwargs.get('get_playable_live_tv', False)
        get_playable_socu = kwargs.get('get_playable_socu', False)
        get_playable_ndvr = kwargs.get('get_playable_ndvr', False)
        exclude_tplus_channels = kwargs.get('exclude_tplus_channels', False)
        exclude_plutotv_channels = kwargs.get('exclude_plutotv_channels', False)
        trickplay_restriction = kwargs.get("trickplay_restriction", None)
        restricted_device_type = kwargs.get("restricted_device_type", None)
        is_bookmarkable = kwargs.get("is_bookmarkable", None)
        #
        channel_list = self.get_channel_search(is_received=is_received, entitled=is_entitled,
                                               use_cached_response=use_cached_response)
        count = count if count is not None else 0
        restrictions_details = self.get_recordable_non_recordable_channel_items()
        # There are 4 time frames devided by 30 minutes and lasting 2 hours in total in Grid Guide
        cur_time_seconds = int(datetime.strptime(self.get_middle_mind_time()["currentTime"],
                                                 self.MIND_DATE_TIME_FORMAT).timestamp())
        seconds_from_start_time = int(start_time) if start_time else cur_time_seconds
        max_tf_size_in_secs = GuideCellIocContainer.MAX_TIME_FRAME_SIZE_IN_HOURS * 60 * 60
        seconds_from_end_time = int(end_time) if end_time else seconds_from_start_time + max_tf_size_in_secs
        first_frame_start_time = int(GuideCellIocContainer.get_timestamp_multiple_of(seconds_from_start_time, 1800, False))
        last_frame_end_time = int(GuideCellIocContainer.get_timestamp_multiple_of(seconds_from_end_time, 1800, False))
        guide_row_cells = self.get_guide_rows(channel_list, seconds_from_start_time, seconds_from_end_time,
                                              "channel_number", use_cached_response=use_cached_response,
                                              dup_programs_on_edge=True)
        filtered_rows = []
        for channel_number in guide_row_cells:
            guide_cells = guide_row_cells[channel_number]
            if not guide_cells:
                continue
            # in format [(GuideCell, $steps_left_right)]; $steps_left_right e.g. [1, 'right']
            selected_cells = self.__get_analyzed_cells(guide_cells, find_appropriate, cell_index,
                                                       last_frame_end_time, cur_time_seconds, is_bookmarkable)
            if not selected_cells:
                continue  # no fitting cell found
            channel = None
            for chan in channel_list:
                if chan.channel_number == channel_number:
                    channel = chan
            for pair in selected_cells:
                filtered_rows.append([channel_number, pair[0], channel, pair[1]])
        filtered_rows = self.get_filtered_channels_by_guide_cell_attributes(
            filtered_rows, is_catchup, is_startover, is_adult, is_ppv, is_new, content_type)
        filtered_rows = self.get_filtered_channels_by_recordable_non_recordable(
            filtered_rows, cur_time_seconds, last_frame_end_time, restrictions_details, is_recordable_chan,
            is_recordable_show, is_copyright_restricted, is_recordable_in_the_past)
        filtered_rows = self.get_filtered_channels_by_show_duration(
            filtered_rows, cur_time_seconds, first_frame_start_time, last_frame_end_time, is_live, duration_lt, duration_gt,
            take_not_ended_shows, ends_in_lt, ends_in_gt)
        filtered_rows = self.get_filtered_channels_by_channel_fields(
            filtered_rows, is_encrypted=is_encrypted, trickplay_restriction=trickplay_restriction,
            restricted_device_type=restricted_device_type, video_resolution=video_resolution)
        filtered_rows = self.exclude_tplus_channels(filtered_rows, exclude_tplus_channels=exclude_tplus_channels)
        filtered_rows = self.exclude_pluto_tv_channels(filtered_rows, exclude_plutotv_channels=exclude_plutotv_channels)
        filtered_rows = self.filter_good_channels(filtered_rows, get_playable_live_tv)
        # self.log.debug(f"get_random_channel_from_guide_rows - filtered channels: {filtered_rows}")
        if get_playable_socu:
            filtered_rows = self.filter_channels(filtered_rows, filtered_rows, filter_socu=get_playable_socu)
        if get_playable_ndvr:
            filtered_rows = self.filter_channels(filtered_rows, filtered_rows, filter_ndvr=get_playable_ndvr)
        if not count and filtered_rows:
            return filtered_rows
        elif filtered_rows and len(filtered_rows) > count:
            return random.sample(filtered_rows, count)
        elif filtered_rows and len(filtered_rows) <= count:
            return filtered_rows
        self.log.warning("get_random_channel_from_guide_rows: No channels with specifed condtions")
        if skip_test_if_no_results:
            pytest.skip("get_random_channel_from_guide_rows: No channels with specifed condtions")

    @Cacher.process
    def get_grid_row_search(self, *args, **kwargs):
        """
        OpenAPI equivalent consists of 3 requests:
            1. /v1/channels
            2. /v1/guideRows
            3. /v1/preview/offer (is_preview_offer_needed param)

        This method gets the list of channels along with offers that each channel has
        :param args: set of non-keyword arguments
        :param kwargs: keyword arguments such as collectionType, offset
        collectionType can be passed based on the following link:
        http://w3-engr.tivo.com/d-docs/autodocs/b-trioschema-mainline/trioschema/collectionType.html

        Note:
            if you need Offer specific field that is NOT contained in (collection_id, content_type, content_id,
            duration, is_adult, is_new, is_ppv, movie_year, offer_id, start_time, title, is_catchup, is_startover,
            is_recordable, collection_type, transport_type, episodic, collectionType),
            then you need to set this field to True, otherwise it should be False
            (making /v1/preview/offer requests will increase test run time)

        Kwargs:
            is_preview_offer_needed (bool): True - making /v1/preview/offer request to get additional specific data,
                                            False - no /v1/preview/offer request;
                                            this param is needed for OpenAPI;
            use_cached_response (bool): True - using cached response, False - making request
            dup_programs_on_edge (bool): read description in ServiceOpenAPI#get_guide_rows()
            mindEndTime (str): start time in format %Y-%m-%d %H:%M:%S e.g. 2023-06-26 15:42:01
            maxStartTime (str): end time in format %Y-%m-%d %H:%M:%S e.g. 2023-06-26 17:42:01
            is_favorite (bool): True - selecting only favorite channels, False - selecting only non-favorite ones
            is_entitled (bool): True - selecting only entitled channels, False - selecting only non-entitled ones
            is_received (bool): True - selecting only entitled and available channels, False - selecting nonp-received ones
            count (int): number of guide rows to return (1 guide row = 1 channel)
            offset (int): offer index in a guide row
            collection_type (str): show collection type to select
            transport_type (str): show transport type to select
            applicable_device_type (str): select only channels applicable to this device type
            include_adult (bool): True - include channels with adult shows, False - exclude channels with adult shows
            screen_type (str): screen type to get offer details for (more info on this param can be found
                               in get_preview_offer() method description)

        Returns:
            list, [{"channel_item": Channel, "offers": [Offer]}]
        """
        self.log.info("Getting gridRowList structure using OpenAPI call")
        debug_start_time = datetime.now()
        tsn = self.settings.tsn
        is_preview_offer_needed = kwargs.get('is_preview_offer_needed', False)
        use_cached_response = kwargs.get("use_cached_response", False)
        dup_programs_on_edge = kwargs.get("dup_programs_on_edge", False)
        is_favorite = kwargs.get('is_favorite', None)  # None - channels are returned no matter if they are favorite or not
        is_entitled = kwargs.get('is_entitled', None)  # None - channels are returned no matter if they are entitled or not
        is_received = kwargs.get('is_received', True)
        count = kwargs.get('count', 500)
        offset = kwargs.get('offset', 0)
        collection_type = kwargs.get('collectionType', None)
        transport_type = kwargs.get('transportType', None)
        applicable_device_type = kwargs.get('applicable_device_type', None)
        include_adult = kwargs.get('includeAdult', True)
        screen_type = kwargs.get('screen_type', 'actionScreen')
        hrs = kwargs.get('hrs', 2)
        # All available items are returned at first time, no need to make one more request with different offset
        if offset > 0:
            return []
        channel_search_input_params = {}
        channel_search_input_params["channel_count"] = count
        channel_search_input_params["entitled"] = is_entitled
        channel_search_input_params["isFavorite"] = is_favorite
        channel_search_input_params["is_received"] = is_received
        if applicable_device_type is not None:
            channel_search_input_params["applicableDevicetype"] = applicable_device_type
        channel_search_input_params["use_cached_response"] = use_cached_response
        # Getting cached current time to avoid making excess request when use_cached_response is True
        cur_mind_time = datetime.strptime(
            self.get_middle_mind_time(tsn, use_cached_response)["currentTime"], self.MIND_DATE_TIME_FORMAT)
        end_time = cur_mind_time + timedelta(hours=hrs)
        min_end_time = kwargs.get('mindEndTime', str(cur_mind_time))
        max_start_time = kwargs.get('maxStartTime', str(end_time))
        start_time = datetime.strptime(min_end_time, self.MIND_DATE_TIME_FORMAT).timestamp()
        end_time = datetime.strptime(max_start_time, self.MIND_DATE_TIME_FORMAT).timestamp()
        channel_list = self.get_channel_search(**channel_search_input_params)
        guide_cell_list = self.get_guide_rows(channel_list, start_time, end_time, "channel_number",
                                              dup_programs_on_edge, use_cached_response=use_cached_response)
        filtered_guide_cells_dict = dict()
        for channel_number, guide_cells in guide_cell_list.items():
            for guide_cell in guide_cells:
                if not include_adult and guide_cell.is_adult or \
                   transport_type and transport_type == "ppv" and not guide_cell.is_ppv or \
                   transport_type and transport_type == "stream" and guide_cell.is_ppv or \
                   collection_type and collection_type != guide_cell.content_type:
                    break
                else:
                    filtered_guide_cells_dict.update({channel_number: guide_cells})
                    break
        # Additionally, /v1/preview/offer requires offerId, let's get it inside GridRowIocContainer
        preview_offer_payload = {"screenType": screen_type, "enableCriticRating": True}
        preview_offer_url = self.url_resolver.get_endpoints("cloudcore-previews")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(preview_offer_url)[0:3]
        grid_row_list = GridRowIocContainer.get_list(
            self.settings, url_base, port, preview_offer_payload, guide_cell_list=filtered_guide_cells_dict,
            channel_list=channel_list, rating_dict=self.get_rating_instructions_get(), http_protocol=http_protocol,
            http_method="get", headers=self.get_headers(tsn), update_headers=True,
            function_name="open_api_preview_offer", use_query_params=False, tsn=tsn,
            is_preview_offer_needed=is_preview_offer_needed, partner_id=self.get_mso_partner_id(self.settings.tsn),
            get_tv_rating_for_passed_value_func=self.get_tv_rating_for_passed_value, pcid=self.getPartnerCustomerId(),
            rating_instructions=self.get_rating_instructions_get())
        debug_end_time = datetime.now()
        duration_in_seconds = debug_end_time.timestamp() - debug_start_time.timestamp()
        self.log.debug(f"OpenAPI get_grid_row_search duration (use_cached_response = {use_cached_response}): "
                       f"{duration_in_seconds / 60} min ({duration_in_seconds} sec)")
        return grid_row_list

    @Cacher.process
    def get_preview_offer(self, offer_id, use_cached_response=False, **kwargs):
        """
        /v1/preview/offer is supported since Hydra 1.18
        /v1/preview/content is supported since Hydra 1.19
        /v1/preview/series is supported since Hydra 1.19
        Client application calls this request when displaying show preview.

        Args:
            offer_id (str): offer id if mode == offer, content id if mode == content, collection id if mode == series
            use_cached_response (bool): True - using cached response, False - making request

        kwargs:
            mode (str): one of (offer, content, series)
            screen_type (str): one of (actionScreen, guideHeader, guideRecordOverlay, oneLineGuide, liveTvBanner, fullBanner,
                                       wtwnScreen, alreadyRecordingOverlay);
                               some params may not be present in response depending on screen_type value,
            enable_critic_rating (bool): True - enable critic rating in response, False - otherwise

        Returns:
            PreviewOffer,  if mode == offer
            PreviewContent, if mode == content
            PreviewSeries, if mode == series
            None, if request returned no item
        """
        tsn = self.settings.tsn
        mode = kwargs.get("mode", "offer")
        screen_type = kwargs.get("screen_type", "actionScreen")
        enable_critic_rating = kwargs.get("enable_critic_rating", True)
        if mode.lower() == "content":
            function_name = "open_api_preview_content"
        elif mode.lower() == "series":
            function_name = "open_api_preview_series"
        else:
            function_name = "open_api_preview_offer"
        preview_offer_payload = {"screenType": screen_type, "enableCriticRating": "true" if enable_critic_rating else "false"}
        preview_offer_url = self.url_resolver.get_endpoints("cloudcore-previews")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(preview_offer_url)[0:3]
        preview_offer = PreviewOfferIocContainer.get_item(
            self.settings, url_base, port, preview_offer_payload, http_protocol=http_protocol, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name=function_name, use_query_params=False, tsn=tsn,
            part_uri="/{}".format(offer_id))
        return preview_offer

    def get_random_filtered_channels_by_preview_offer(self, chan_show_list, **kwargs):
        """
        /v1/preview/offer
        Method supported since Hydra v1.18.

        Note:
            different screen_type values give responses with a bit different responses (some fields are added, some removed).

        Kwargs:
            chan_show_list (list): [[channelNumber, GuideCell, Channel, [steps, left/right]]]
            skip_test_if_no_results (bool): True - skipping test if there's no results, False - return [] otherwise
            screen_type (str): screen type to get offer details for (more info on this param can be found
                               in get_preview_offer() method description)
            preview_mode (str): True - mode to get offer details for (more info on this param can be found
                               in get_preview_offer() method description)
            with_category (bool): True - selecting only channels with offer category e.g. Mistery, Cartoon etc.;
                                  False - selecting channels without offer category;
                                  None - selecting any channel
            count (int): number of guide rows to return (1 guide row = 1 channel);
                         None or 0 = all matched channels are returned
            with_star_rating (bool): True - return offers with star rating, False - without one, None - any;
                                     Note: star rating is float number 0-4
            with_rating (bool): True - takes channels with some TV rating e.g. TV-PG, False - without one,
                                None - any channel
            with_description (bool): True - takes channels with some description, False - without one,
                                     None - any channel
            video_resolution (str): takes channels with shows that have video resolution from input param (sd, hd, uhd),
                                    None - any channel
            has_sap (bool): True - taking channels with SAP, False - otherwise, None - any
            has_cc (bool): True - taking channels with CC, False - otherwise, None - any
            is_repeat (bool): True - taking channels with repeat, False - otherwise, None - any
            is_three_d (bool): True - taking channels with 3D, False - otherwise, None - any
            is_subtitle (bool): True - taking channels with shows that have subtitle, False - taking without subtitle,
                                None - any
            with_credit (bool): True - taking channels with shows that have credits (actors), False - taking without one,
                                None - any
            stop_seek_at_first_match (bool): True - stop searching when first $count items matched,
                                             False/None - walking through the whole list till last item;
                                             Note: applicable when count > 0
            max_symbols_in_description (int): if set, returns offers that have number of symbols <= this param,
                                              None - any;
                                              Note: some fields may not be shown when description is too long, that's when
                                                    this param comes in handy
            with_video_provider (bool): True - taking channels with shows available from some OTTs, False - taking without one,
                                        None - any;
                                        Note: requires screen_type=guideHeader
            vp_partner_id (str): If set, taking channels with shows available from particular OTT e.g. tivo:pt.4576;
                                 if None, any channel is taken
                                 Note: requires screen_type=guideHeader

        Returns:
            list, [[channelNumber, GuideCell, Channel, [steps, left/right], PreviewOffer]] filtered values;
                  steps + left/right shows how many steps and where needed to be done to highlight a cell in Guide;
                  Note: Tip for Guide - get to Channel Cell before pressing Left/Right using steps from this item
        """
        skip_test_if_no_results = kwargs.get('skip_test_if_no_results', True)
        screen_type = kwargs.get('screen_type', "actionScreen")
        preview_mode = kwargs.get('preview_mode', "offer")
        with_category = kwargs.get('with_category', None)
        count = kwargs.get('count', 1)
        with_star_rating = kwargs.get('with_star_rating', None)
        with_rating = kwargs.get('with_rating', None)
        with_description = kwargs.get('with_description', None)
        video_resolution = kwargs.get('video_resolution', None)
        has_sap = kwargs.get('has_sap', None)
        has_cc = kwargs.get('has_cc', None)
        is_repeat = kwargs.get('is_repeat', None)
        is_three_d = kwargs.get('is_three_d', None)
        is_subtitle = kwargs.get('is_subtitle', None)
        with_credit = kwargs.get('with_credit', None)
        stop_seek_at_first_match = kwargs.get('stop_seek_at_first_match', True)
        max_symbols_in_description = kwargs.get('max_symbols_in_description', None)
        with_video_provider = kwargs.get('with_video_provider', None)
        vp_partner_id = kwargs.get('vp_partner_id', None)  # particular video provider partner id
        filtered_rows = []
        count = count if count is not None else 0
        if with_video_provider is not None:
            # Video providers are returned only if screen_type is guideHeader
            screen_type = "guideHeader"
        for item in list(chan_show_list):
            cell = item[1]
            satisfied_condition_list = []
            if preview_mode == "offer":
                show_id = cell.offer_id
            elif preview_mode == "content":
                show_id = cell.content_id
            elif preview_mode == "series":
                show_id = cell.collection_id
            else:
                raise ValueError(f"Not supported preview_mode: {preview_mode}")
            offer = self.get_preview_offer(show_id, screen_type=screen_type, mode=preview_mode)
            if not offer:
                self.log.warning(f"/v1/preview/offer returned no data for {cell.offer_id} offer id")
                continue  # skipping empty preview/offer response
            satisfied_condition_list.append(self.compare_bool_param(with_category, offer.category_label))
            satisfied_condition_list.append(self.compare_bool_param(with_rating, offer.internal_rating_list))
            is_start_rating = offer.star_rating is not None
            satisfied_condition_list.append(self.compare_bool_param(with_star_rating, is_start_rating))
            satisfied_condition_list.append(self.compare_bool_param(with_description, offer.description))
            if video_resolution is None or \
               video_resolution == offer.video_resolution:
                satisfied_condition_list.append(True)
            elif video_resolution is not None:
                satisfied_condition_list.append(False)
            satisfied_condition_list.append(self.compare_bool_param(has_sap, offer.has_sap))
            satisfied_condition_list.append(self.compare_bool_param(has_cc, offer.has_cc))
            satisfied_condition_list.append(self.compare_bool_param(is_repeat, offer.is_repeat))
            satisfied_condition_list.append(self.compare_bool_param(is_three_d, offer.is_three_d))
            satisfied_condition_list.append(self.compare_bool_param(is_subtitle, offer.episode_title))
            satisfied_condition_list.append(self.compare_bool_param(with_credit, offer.credit_string))
            satisfied_condition_list.append(self.compare_bool_param(with_video_provider, offer.providers_list))
            if max_symbols_in_description is not None and max_symbols_in_description >= len(offer.description) or \
               max_symbols_in_description is None:
                satisfied_condition_list.append(True)
            else:
                satisfied_condition_list.append(False)
            # Filtering offers by particular video provider partner id
            is_provider_found = False
            for provider in offer.providers_list:
                if vp_partner_id == provider.get("providerId"):
                    is_provider_found = True
                    break
            if is_provider_found or not vp_partner_id and vp_partner_id is None:
                satisfied_condition_list.append(True)
            else:
                satisfied_condition_list.append(False)
            if satisfied_condition_list and all(satisfied_condition_list):
                item.append(offer)
                filtered_rows.append(item)
            if stop_seek_at_first_match and count and len(filtered_rows) == count:
                break
        self.log.debug(f"get_random_filtered_channels_by_preview_offer - filtered channels: {filtered_rows}")
        if not count and filtered_rows:
            return filtered_rows
        elif filtered_rows and len(filtered_rows) > count:
            return random.sample(filtered_rows, count)
        elif filtered_rows and len(filtered_rows) <= count:
            return filtered_rows
        self.log.warning("get_random_filtered_channels_by_preview_offer: No channels with specifed condtions")
        if skip_test_if_no_results:
            pytest.skip("get_random_filtered_channels_by_preview_offer: No channels with specifed condtions")
        return filtered_rows

    def get_feed_item_response(self, **kwargs):
        """
        /v1/feeds/screens
        Client application calls this request when fills in data in What to Watch screen.
        """
        retries = 3
        tsn = self.settings.tsn
        url = self.url_resolver.get_endpoints("feeditems-service")
        feedname = kwargs.get("feed_name", "")
        function_name = kwargs.get("function_name", "screens_open_api")
        count_type = "carouselCount"
        count = kwargs.get("dspl_cnt", 10)
        headers = self.get_headers(tsn)
        payload = {}
        if feedname == self.settings.feed_list_root:
            feedname = ""
            count_type = "screensCount"
        else:
            payload.update({"countPerCarousel": kwargs.get("cnt_per_carousel", 1)})
            payload.update({"hideAdult": kwargs.get("hideAdult", True)})
        if feedname and feedname != self.settings.feed_list_root and "screens" in feedname:
            feedname = re.sub("/screens", "", feedname)
        payload.update({count_type: count})
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        for _ in range(retries):
            response = WtwContainer.get_dict(self.settings, url_base, port, payload, http_protocol=http_protocol,
                                             http_method="get", headers=headers, function_name=function_name,
                                             feedname=feedname, part_uri=feedname, use_query_params=False, tsn=tsn)
            if isinstance(response, dict) and 'Unauthorized' in response.values():
                auth_token = self.get_authorization_token(tsn, use_cached_response=False)
                headers.update({'Authorization': auth_token})
            else:
                break
        return response

    @Cacher.process
    def get_feed_item_find_results(self, feedName, display_count=100, **kwargs):
        """
        /v1/feeds/carousels
        Client application calls this request when fills in data in What to Watch screen.
        """
        retries = 3
        tsn = self.settings.tsn
        url = self.url_resolver.get_endpoints("feeditems-service")
        function_name = kwargs.get("function_name", "carousels_open_api")
        headers = self.get_headers(tsn)
        caption = kwargs.get("caption", False)
        payload = {"countPerCarousel": kwargs.get("display_count", 10), "includeAdult": kwargs.get("includeAdult", False),
                   "offset": kwargs.get("offset", 0)}
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        if feedName and "carousels" in feedName:
            feedName = re.sub("/carousels", "", feedName)
        for _ in range(retries):
            response = WtwContainer.get_dict(self.settings, url_base, port, payload, http_protocol=http_protocol,
                                             http_method="get", headers=headers, function_name=function_name,
                                             feedname=feedName, part_uri=feedName, use_query_params=False, tsn=tsn)
            if isinstance(response, dict) and 'Unauthorized' in response.values():
                auth_token = self.get_authorization_token(tsn, use_cached_response=False)
                headers.update({'Authorization': auth_token})
            else:
                break
        if kwargs.get("full_resp", False):
            return response
        return self.handle_feed_item_find_results(response, caption=caption)

    @Cacher.process
    def get_airing(self, station_id, airing_time_utc_str=None, use_cached_response=False):
        """
        /v1/airing
        Client application calls this request to get show information for Info Banner in WatchVideo screen.
        Method supported since Hydra v1.18.

        Note:
            get_airing()["ended_list"] has items only if ended shows get in airing_time_utc_str.

        Args:
            station_id (str): stationId of the channel
            airing_time_utc_str (str): UTC time in Open API format ex. "2022-11-11T12:15:00Z"
            use_cached_response (bool): True - using cached response, False - making request

        Returns:
            dict, {"ended_list": [Airing], "airing_show": Airing, "upcoming_list": [Airing]};
                  upcoming_list[0] is the next show after airing_show,
                  ended_list - shows that ended before airing_time_utc_str,
                  airing_show - the show that was/is/will be streaming in airing_time_utc_str,
                  upcoming_list - shows that start after airing_time_utc_str,
        """
        tsn = self.settings.tsn
        mind_time_utc_str = self.get_middle_mind_time(tsn, use_cached_response)["currentTime"]
        if not airing_time_utc_str:
            airing_time_utc_str = DateTimeUtils.convert_date(mind_time_utc_str,
                                                             self.MIND_DATE_TIME_FORMAT,
                                                             self.OPENAPI_DT_FORMAT)
        airing_time_utc = datetime.strptime(airing_time_utc_str, self.OPENAPI_DT_FORMAT)
        airing_time_multiple_of_900 = AiringIocContainer.get_timestamp_multiple_of(airing_time_utc.timestamp(), 900, False)
        part_uri = "/{}/{}".format(
            station_id,
            datetime.strftime(datetime.fromtimestamp(airing_time_multiple_of_900), self.OPENAPI_DT_FORMAT))
        url = self.url_resolver.get_endpoints("cloudcore-airing")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        airing = AiringIocContainer.get_dict(
            self.settings, url_base, port, {}, http_protocol=http_protocol, http_method="get", tsn=tsn,
            headers=self.get_headers(tsn), update_headers=True, function_name="open_api_airing", part_uri=part_uri,
            airing_time=airing_time_utc, use_query_params=False)
        return airing

    @Cacher.process
    def partner_exclusion_search(self, use_cached_response=False):
        """
        GET /v1/excluded-partners
        Returns list of excluded (on UI - unchecked) providers.
        Client application calls this request when includes/excludes video partners in My Video Providers screen
        Method supported since Hydra v1.18.

        Args:
            use_cached_response (bool): True - using cached response, False - making request

        Returns:
            list, [ExcludedPartners]
        """
        tsn = self.settings.tsn
        url = self.url_resolver.get_endpoints("excluded-partners")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        excluded_partners = ExcludedPartnersContainer.get_list(
            self.settings, url_base, port, {}, http_protocol=http_protocol,
            http_method="get", headers=self.get_headers(tsn), update_headers=True,
            function_name="open_api_excluded_partners", use_query_params=False, tsn=tsn)
        return excluded_partners

    def add_video_provider(self, partner_id):
        """
        DELETE /v1/excluded-partners
        Adding partners (equivalent action on UI - checking providers in My Video Providers).
        Client application calls this request when includes/excludes video partners in My Video Providers screen
        Method supported since Hydra v1.18.

        Args:
            partner_id (str): e.g. tivo:pt.3455

        Returns:
            None, HTTP 204
        """
        tsn = self.settings.tsn
        payload = {"partnerId": partner_id}
        url = self.url_resolver.get_endpoints("excluded-partners")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        excluded_partners = ExcludedPartnersContainer.get_list(
            self.settings, url_base, port, {}, http_protocol=http_protocol, http_method="delete",
            headers=self.get_headers(tsn), update_headers=True, function_name="open_api_excluded_partners",
            use_query_params=False, tsn=tsn, url_params=payload, success_status=HTTPStatus.NO_CONTENT)
        return excluded_partners

    def post_excluded_partners(self, partner_id):
        """
        POST /v1/excluded-partners
        Excluding partners (equivalent action on UI - unchecking providers in My Video Providers).
        Client application calls this request when includes/excludes video partners in My Video Providers screen
        Method supported since Hydra v1.18.

        Args:
            partner_id (str): e.g. tivo:pt.3455

        Returns:
            None, HTTP 204
        """
        tsn = self.settings.tsn
        payload = {"partnerId": partner_id}
        url = self.url_resolver.get_endpoints("excluded-partners")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        excluded_partners = ExcludedPartnersContainer.get_list(
            self.settings, url_base, port, payload, http_protocol=http_protocol, http_method="post",
            headers=self.get_headers(tsn), update_headers=True, function_name="open_api_excluded_partners",
            use_query_params=False, tsn=tsn, success_status=HTTPStatus.NO_CONTENT)
        return excluded_partners

    @property
    def get_all_socu_channels_details(self) -> dict:
        """
        Method supported since Hydra v1.18.

        Returns:
            dict, {channel_number: [channel_number, is_catchup, is_startover]}
        """
        socu_channel = {}
        channel_list = self.get_channel_search()
        channel_det = self.channel_details
        guide_row_cells = self.get_guide_rows(channel_list)
        current_time = datetime.strptime(self.get_middle_mind_time()["currentTime"], self.MIND_DATE_TIME_FORMAT)
        next_offer = False

        def update_socu_channel(cell, channel_det, channel_number, socu_channel, end_time, current_time):
            if end_time - current_time >= timedelta(seconds=120):
                if cell.is_catchup or cell.is_startover:
                    name = None
                    if channel_det and channel_number in channel_det.keys():
                        name = channel_det.get(channel_number)[0]
                        socu_channel.update({channel_number: [channel_number, cell.is_catchup, cell.is_startover, name]})
                        self.log.info("updated channel {} to dict: {}".format(channel_number, socu_channel))
            return socu_channel
        self.log.debug(f"Going to check channel: {guide_row_cells}")
        for channel_number in guide_row_cells:
            for cell in guide_row_cells[channel_number]:
                start_time = datetime.fromtimestamp(cell.start_time)
                end_time = start_time + timedelta(seconds=cell.duration)
                if start_time <= current_time < end_time and not next_offer:
                    socu_channel = update_socu_channel(cell, channel_det, channel_number, socu_channel,
                                                       end_time, current_time)
                    if socu_channel and channel_number not in socu_channel.keys():
                        self.log.info(f"{channel_number} offer seems to be left with < 120 secs of playback."
                                      f" Getting next offer")
                        next_offer = True
                elif next_offer:
                    self.log.info("checking non-live offer")
                    socu_channel = update_socu_channel(cell, channel_det, channel_number, socu_channel,
                                                       end_time, current_time)
                    if socu_channel and channel_number in socu_channel.keys():
                        next_offer = False
            next_offer = False
        self.log.debug("Socu channels: {}".format(socu_channel))
        return socu_channel

    @Cacher.process
    def branding_ui(self, field=None, use_cached_response=False):
        """
        /v1/brandingUiBundle
        Method will be supported from Hydra v1.19.

        Returns:
            Branding, one item
        """
        tsn = self.settings.tsn
        mso_partner_id = self.get_mso_partner_id(tsn)
        mso_service_id = self.get_mso_service_id(tsn)
        sls_domain = self.get_sls_domain()
        url = self.url_resolver.get_endpoints("cloudcore-branding-service")
        payload = {"msoPartnerId": mso_partner_id,
                   "msoServiceId": mso_service_id,
                   "slsDomain": sls_domain}
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        branding_response = BrandingContainer.get_item(
            self.settings, url_base, port, payload, http_protocol=http_protocol, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name="open_api_branding",
            use_query_params=False, tsn=tsn)
        if field:
            self.log.info("checking field existence: {}".format(field))
            value = eval("branding_response.{}".format(field))
            return value
        else:
            return branding_response

    @Cacher.process
    def get_metacritic_rating(self, content_id, offer_id_list):
        self.log.info("Getting Metacritic values by using v1/preview")
        critic_rating_map = {}
        for offer_id in offer_id_list:
            offer = self.get_preview_offer(offer_id, screen_type="guideHeader")
            if offer.critic_rating.get('source') == 'metacritic':
                critic_rating_map[offer_id] = offer.critic_rating['value']
        return critic_rating_map

    @Cacher.process
    def get_offer_search(self, tsn=None, use_cached_response=False, **kwargs):
        """
        /v1/preview/offer

        Args:
            use_cached_response (bool): True - getting cached value of offerSearch, False - making offerSearch request

        kwargs:
            received_channels_only (bool): True - get offers for channels with isReceived=True,
                                           False - get offers for all channels
            station_id (str): station ID e.g. tivo:st.107213908
            channel_number (int): channel number e.g. 7104
            min_start_time (str): in %Y-%m-%d %H:%M:%S format e.g. 2023-02-08 11:39:55,
                                  returns offers whose startTime is greater than or equal to minStartTime
            min_end_time (str): in %Y-%m-%d %H:%M:%S format, filters the results by end time (for linear offers) or
                                by available end time (for on-demand offers) to be on or after the minEndTime.
            count (int): default = 1, it can be up to 50
            offer_ids (list): list of offer id e.g. [tivo:of.std.387.2023-02-07-12-00-00.1800];
                              Note: takes prioriy over content_id and collection_ids
            content_id (str): content id e.g. tivo:ct.448908607;
                              Note: takes prioriy over collection_ids
            collection_ids (list): collection ids e.g. [tivo:cl.431207700]
            source_type (str): one of (appLinear, atsc, atscBox, cable, cableBox, dbs, digitalCable,
                                       directv, dvbt, ipStream, lineInput, roofTop, satellite, terrestrial, unknown)
            screen_type (str): one of (actionScreen, guideHeader, guideRecordOverlay, oneLineGuide, liveTvBanner, fullBanner);
                               some params may not be present in response depending on screen_type value,
                               actionScreen returns most fields (but not all anyway)

        Returns:
            list, [Offer]
        """
        # NOTES:
        #   1. searchable, name_space, offset, params are no longer used in OpenAPI
        #   2. Method is not enabled yet, activation in https://jira.xperi.com/browse/CA-16309
        tsn = tsn or self.settings.tsn
        # Number of hours for getting guide shows; applicable when min_end_time is set but min_start_time isn't
        hours_forward = 8
        received_channels_only = kwargs.get("received_channels_only", False)
        station_id = kwargs.get("station_id", None)
        channel_number = kwargs.get("channel_number", None)
        min_start_time = kwargs.get("min_start_time", None)
        min_end_time = kwargs.get("min_end_time", None)  # stands for start_time
        count = kwargs.get("count", 1)
        offer_ids = kwargs.get("offer_ids", None)
        collection_ids = kwargs.get("collection_ids", None)
        content_id = kwargs.get("content_id", None)
        source_type = kwargs.get("source_type", None)
        screen_type = kwargs.get("screen_type", "actionScreen")
        payload = {"previewOfferMode": "offer", "count": count, "screen_type": screen_type}
        received_channels_only = None if not received_channels_only else True
        if min_start_time:
            payload["minStartTime"] = datetime.strptime(min_start_time, self.MIND_DATE_TIME_FORMAT).timestamp()
        if min_end_time:
            payload["minEndTime"] = datetime.strptime(min_end_time, self.MIND_DATE_TIME_FORMAT).timestamp()
        if station_id:
            payload["stationId"] = station_id
        if channel_number:
            payload["channelNumber"] = channel_number
        if offer_ids:
            if not isinstance(offer_ids, list) and not isinstance(offer_ids, tuple):
                raise ValueError("offer_ids param has to be of list type")
            payload["itemIdList"] = offer_ids
            payload["previewOfferMode"] = "offer"
        elif content_id:
            payload["itemIdList"] = [content_id]
            payload["previewOfferMode"] = "content"
        elif collection_ids:
            if not isinstance(collection_ids, list) and not isinstance(collection_ids, tuple):
                raise ValueError("collection_ids param has to be of list type")
            payload["itemIdList"] = collection_ids
            payload["previewOfferMode"] = "series"
        channel_list = self.get_channel_search(is_received=received_channels_only)
        if source_type:
            # Filtering channels by source_type
            channel_list = [channel for channel in channel_list if source_type == channel.source_type]
        # Getting particular Channel item if channel_number or station_id was provided
        for channel in channel_list:
            if channel_number and channel.channel_number == channel_number or \
                    station_id and channel.station_id == station_id:
                channel_list = [channel]
        if payload.get("minEndTime") and not payload.get("minStartTime"):
            payload["minStartTime"] = \
                (datetime.fromtimestamp(payload.get("minEndTime")) + timedelta(days=hours_forward)).timestamp()
        guide_rows = self.get_guide_rows(channel_list, payload.get("minEndTime"), payload.get("minStartTime")) \
            if min_start_time or min_end_time else dict()
        offer_list = OfferIocContainer.get_list(
            self.settings, None, None, payload,
            get_preview_offer_func=self.get_preview_offer, guide_rows_dict=guide_rows,
            get_tv_rating_for_passed_value_func=self.get_tv_rating_for_passed_value,
            rating_instructions=self.get_rating_instructions_get())
        return offer_list

    @Cacher.process
    def get_my_shows_item_search(self, tsn):
        """
        /v1/myShows/myShowsItems
        method for calling new API /v1/myShows/myShowsItems instead of trio call
        Args:
            TSN
        Returns:
            list, [MyShows]

        **Note:
            Currently, the new API is still in developement and has following limitations
            - only returns recordings (no bookmarks or onepasses)
            - items do not have following fields that are needed: contentId, myShowsItemId
            ! When implemetation is finished, this should work out of the box
            ! Will retest in case other things will change during api dev
        """
        url = self.url_resolver.get_endpoints("cloudcore-myshows")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        headers_to_add = self.get_headers()
        #  Replacing DeviceType with Device-Type
        del headers_to_add["DeviceType"]
        headers_to_add["Device-Type"] = self.get_device_type()
        my_shows_items = MyShowsIocContainer.get_list(
            self.settings, url_base, port, {}, function_name="cloud_core_myshows", tsn=tsn,
            update_headers=False, headers=headers_to_add, http_protocol="https", use_query_params=False)
        return my_shows_items

    @Cacher.process
    def get_unified_item_search_open_api(self, keyword, use_cached_response=False):
        """
        /v1/searchItems
        Method will be supported from Hydra v1.19.

        Returns:

        """
        tsn = self.settings.tsn
        url = self.url_resolver.get_endpoints("search-service")
        payload = {"includeIpVod": True, "searchTerm": keyword, "offset": 0, "minEndTime": "2023-07-07T15:00:00Z"}
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        response = SearchContainer.get_item(self.settings, url_base, port, payload, http_protocol=http_protocol,
                                            http_method="get", headers=self.get_headers(tsn), update_headers=True,
                                            function_name="open_api_search", use_query_params=False, tsn=tsn)
        return response

    def get_sls_domain(self):
        """
        Returns:
            sls_domain: eg: cableco3-qe, cableco11-staging etc
        """
        specializer = SpecializationExtractor(os.path.join(self.settings.TEST_DATA, "provisioning"), mode="csv")
        if not hasattr(self.settings, "TEST_DATA"):
            pytest.skip("get_sls_domain() doesn't support the current project")
            return None
        environment = self.settings.test_environment
        manage_id = self.settings.manage_id
        response = specializer.get_app_env_config(mso=self.settings.mso, manage_id=manage_id,
                                                  test_environment=environment, app_env_config="")
        self.log.info("The response from get_app_env_config is: {}".format(response))
        sls_domain = response["SLS_DOMAIN"]
        return sls_domain

    @Cacher.process
    def get_actions_offer(self, offer_id, use_cached_response=False, **kwargs):
        """
        /v1/actions/offer is supported since Hydra 1.18
        /v1/actions/content is supported since Hydra 1.19
        /v1/actions/series is supported since Hydra 1.19
        Client application calls this request when displaying show actions.
        Method supported since Hydra v1.19.

        Args:
            offer_id (str): offer id if mode == offer, content id if mode == content, collection id if mode == series
            use_cached_response (bool): True - using cached response, False - making request

        kwargs:
            mode (str): one of (offer, content, series)
            screen_type (str): one of (actionScreen, guideHeader, guideRecordOverlay, oneLineGuide, liveTvBanner, fullBanner,
                                       wtwnScreen, alreadyRecordingOverlay);
                               some params may not be present in response depending on screen_type value,
            enable_critic_rating (bool): True - enable critic rating in response, False - otherwise

        Returns:
            ActionsOffer,  if mode == offer
            ActionsContent, if mode == content
            ActionsSeries, if mode == series
            None, if request returned no item
        """
        tsn = self.settings.tsn
        mode = kwargs.get("mode", "offer")
        groups = kwargs.get("groups", "watch")
        is_socu = kwargs.get("isSocu", True)
        if mode.lower() == "content":
            function_name = "open_api_actions_content"
        elif mode.lower() == "series":
            function_name = "open_api_actions_series"
        else:
            function_name = "open_api_actions_offer"
        offer_payload = {"groups": groups, "isSocu": "true" if is_socu else "false"}
        actions_offer_url = self.url_resolver.get_endpoints("cloudcore-actions")
        self.log.info("showes to check: {}".format(actions_offer_url))
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(actions_offer_url)[0:3]
        actions_offer = ActionsOfferIocContainer.get_item(
            self.settings, url_base, port, offer_payload, http_protocol=http_protocol, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name=function_name, use_query_params=False,
            tsn=tsn,
            part_uri="/{}".format(offer_id))
        return actions_offer

    def subscribe(self, tsn, collection_id, **kwargs):
        """
        /v1/onepasses/collectionId/{collectionId}
        create onepass using collectionId
        kwargs: include - can be one of: "recordingAndStreaming", "all", "recordingOnly", "linear", "streamingOnly"
                                         "onDemand". default value "onDemand"
        Note: Ideally, startFrom option should be updated to year or season value by getting available options from:
              /v1/onepasses/collectionId/{}/options
              for now, StartFromNewEpisodesOnly works as well and has no impact on the test using this method.
        """
        include = kwargs.get('include', "streamingOnly")
        if include == "all":
            include = "recordingAndStreaming"
        elif include == "linear":
            include = "recordingOnly"
        elif include == "onDemand":
            include = "streamingOnly"
        self.log.step("Creating one pass for collection id : {}".format(collection_id))
        create_one_pass_payload = {
            "include": include,
            "startFrom": {
                "type": "StartFromNewEpisodesOnly"
            },
            "rentOrBuy": "dontInclude",
            "recordType": "everything",
            "recordChannel": {
                "type": "RecordAllChannels",
            },
            "videoQuality": "onlyHd",
            "keepAtMost": {
                "type": "RecordingCount",
                "count": 25
            },
            "keepUntil": "asLongAsPossible",
            "startRecordingEarly": {
                "type": "StartRecordingOnTime"
            },
            "stopRecordingLate": {
                "type": "StopRecordingOnTime"
            }
        }
        url = self.url_resolver.get_endpoints("cloudcore-onepass")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        part_uri = "/{}/schedule".format(collection_id)
        headers_to_add = self.get_headers()
        headers_to_add["Content-Type"] = "application/json"
        response = MyShowsIocContainer.make_request(self.settings, url_base, port, create_one_pass_payload,
                                                    function_name="cloud_core_onepass", tsn=tsn,
                                                    update_headers=False,
                                                    headers=headers_to_add, http_method="POST",
                                                    http_protocol=http_protocol, part_uri=part_uri,
                                                    use_query_params=False)
        if response == 200:
            subscription = self.get_subscriptionDetails_from_collection_id(collection_id)
            if "subscription" in subscription and "subscriptionId" in subscription["subscription"][0]:
                subscription_id = subscription["subscription"][0]["subscriptionId"]
                self.log.info("Subscription ID: {}".format(subscription_id))
                self.log.info("One pass creation was successfull")
                return subscription_id
            else:
                raise AssertionError("Failed to get subscriptionId for: {}".format(collection_id))
        else:
            raise AssertionError("Failed to create one pass for collection Id: {}".format(collection_id))

    def record_this_content(self, content_id, offer_id, keepBehavior="fifo"):
        """
        /v1/recordings/offerId/{offerId}
        This function records the content passed by the user
        :param content_id: contentId of the show which needs to be recorded
        :param offer_id: offerId of the show which needs to be recorded
        :return: response of the api
        """
        if keepBehavior == "fifo":
            keep_until = "spaceNeeded"
        else:
            keep_until = "asLongAsPossible"
        offer = self.get_offer_search(tsn=self.settings.tsn, offer_ids=[offer_id])
        start_time = offer[0].start_time
        date = str(start_time).split()
        date_time = date[0] + "T" + date[1] + ".683Z"
        channel = offer[0].channel_field.channel_id
        payload = {
            "timeAndChannel": {
                "offerId": offer_id,
                "dateTime": date_time,
                "channelId": channel
            },
            "keepUntil": keep_until,
            "startRecordingEarly": {
                "type": "StartRecordingOnTime",
            },
            "stopRecordingLate": {
                "type": "StopRecordingOnTime"
            }
        }
        tsn = self.settings.tsn
        url = self.url_resolver.get_endpoints("cloudcore-recordings")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        part_uri = "/{}/schedule".format(offer_id)
        headers_to_add = self.get_headers()
        headers_to_add["Content-Type"] = "application/json"
        url_params = {"contentId": content_id}
        response = MyShowsIocContainer.make_request(self.settings, url_base, port, payload,
                                                    function_name="cloud_core_recordings", tsn=tsn,
                                                    update_headers=False, headers=headers_to_add, http_method="post",
                                                    http_protocol=http_protocol, part_uri=part_uri,
                                                    use_query_params=True, url_params=url_params)
        if response != 200:
            self.log.info(f"Some error occurred while creating recording : {response}")
            return False, response  # no need to match trio response since it is not used by any calling methods
        else:
            self.log.info("Successfully created recording")
            subscription = self.get_subscriptionDetails_from_collection_id(offer[0].collection_id)
            subscription_id = subscription["subscription"][0]["subscriptionId"]
            response = {"subscription": {"subscriptionId": subscription_id}}
            return True, response

    def delete_cloud_recording_standalone(self, content_id):
        """
        /v1/recordings/offerId/{offerId}
        This function deletes Cloud Recording with given content id from myShows.
        :return: Nothing
        """
        cloud_recording_search_resp = self.cloud_recording_search(content_id)
        if "cloudRecording" in cloud_recording_search_resp:
            detail = cloud_recording_search_resp['cloudRecording']
            response = "error"
            if 'cloudRecordingId' in detail[0]:
                # there is a possibility to have more than 1 recording for a content id
                # looping to get all offers with recording for same contentId
                for item in cloud_recording_search_resp["cloudRecording"]:
                    subscription_id = item["subscriptionId"]
                    sub_r = self.subscriptionSearch(self.settings.tsn, subscription_id)
                    offer_id = sub_r["subscription"][0]["idSetSource"]["offerId"]
                    payload = {"contentId": content_id}
                    tsn = self.settings.tsn
                    url = self.url_resolver.get_endpoints("cloudcore-recordings")
                    http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
                    part_uri = "/{}/schedule".format(offer_id)
                    headers_to_add = self.get_headers()
                    headers_to_add["content-type"] = "application/json"
                    url_params = {"contentId": content_id}
                    response = MyShowsIocContainer.make_request(self.settings, url_base, port, payload,
                                                                function_name="cloud_core_recordings", tsn=tsn,
                                                                update_headers=False,
                                                                headers=headers_to_add, http_method="delete",
                                                                http_protocol=http_protocol, part_uri=part_uri,
                                                                use_query_params=True, url_params=url_params)
                if response == 200:
                    self.log.info(f"Recording create with success : {response}")
                    return response
            else:
                self.log.info("cloudRecordingId' attribute not found.")
        else:
            self.log.info("'cloudRecording' attribute not found.")

    def delete_single_recording_myshows(self, myshows_id, content_id):
        """
        /v1/recordings/recordingId/{recordingId}
        """
        self.log.info("deleting recording for contentId: {}".format(content_id))
        payload = {"contentId": content_id}
        tsn = self.settings.tsn
        url = self.url_resolver.get_endpoints("cloudcore-recordings")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        part_uri = "/{}/schedule".format(myshows_id)
        headers_to_add = self.get_headers()
        headers_to_add["content-type"] = "application/json"
        url_params = {"contentId": content_id}
        response = MyShowsIocContainer.make_request(self.settings, url_base, port, payload,
                                                    function_name="cloud_core_recordings_crc", tsn=tsn,
                                                    update_headers=False,
                                                    headers=headers_to_add, http_method="delete",
                                                    http_protocol=http_protocol, part_uri=part_uri,
                                                    use_query_params=True, url_params=url_params)
        if response == 200:
            return {"type": "success"}
        else:
            return {"type": "error", "error": response}

    def get_random_live_channel_rich_info(self,
                                          entitled=True,
                                          channel_count=1,
                                          movie=True,
                                          episodic=False,
                                          live=True,
                                          adult=False,
                                          ascii=False,
                                          filter_channel=False,
                                          channel_payload_count=300,
                                          exclude_jump_channels=False,
                                          exclude_plutotv_channels=True,
                                          exclude_tplus_channels=True,
                                          **kwargs):
        """
        Method to get live channels with specific type of content airing live

        Args:
            entitled (bool): True - entitled channels are taken,
                             False - non-entitled channels are taken and (movie, episodic, adult) params are not considered
            channel_count (int): number of fitting channels to return
            movie (bool): if movie show should be taken; Note: entitled and episodic take priority over this param
            episodic (bool): if episodic shows should be taken; Note: entitled takes prioriy over this param
            live (bool): True - taking an offer with index 0 in a row (it's supposed to be a live one);
                         False - taking an offer with index 1 in a row
            adult (bool): taking only adult shows; Note: entitled takes prioriy over this param
            ascii (bool): if all symbols in offer.title are ASCII
            filter_channel (bool): if channels with non-working live TV playback should be excluded
            channel_payload_count (int): number of channels get return by get_grid_row_search() method
            exclude_jump_channels (bool): if jump channels should be excluded
            exclude_plutotv_channels (bool): if Pluto TV channels should be excluded
            exclude_tplus_channels (bool): if TiVo+ channels should be excluded

        Kwargs:
            use_cached_grid_row (bool): True - using cached get_grid_row_search() response, False - making request
            transport_type (str): one of (stream, ppv); stream - getting non-ppv channels, ppv - getting ppv channels

        Returns:
            list, [channel_number, channel_name, offer_title, movie_year, channel_call_sign,
                   collection_id, content_id, subtitle]
        """

        channels_obj = self._get_live_channels(entitled=entitled,
                                               movie=movie,
                                               episodic=episodic,
                                               live=live,
                                               adult=adult,
                                               ascii=ascii,
                                               channel_payload_count=channel_payload_count,
                                               exclude_jump_channels=exclude_jump_channels,
                                               exclude_plutotv_channels=exclude_plutotv_channels,
                                               exclude_tplus_channels=exclude_tplus_channels,
                                               **kwargs)
        self.log.info("Channels: {}".format(channels_obj))
        channels_repr = list(map(lambda x: [str(x.channel_field.channel_number),
                                            str(x.channel_field.name),
                                            str(x.title),
                                            str(x.movie_year),
                                            str(x.channel_field.call_sign),
                                            str(x.collection_id),
                                            str(x.content_id),
                                            str(x.subtitle),
                                            str(x.offer_id),
                                            ],
                                 channels_obj
                                 )
                             )
        channels = list(self.filter_good_channels(channels_repr, filter_channel))
        channels = self.pick_channels(channels=channels,
                                      channel_count=channel_count,
                                      )
        if entitled and episodic:
            for channel in channels:
                if channel[7] == 'None':
                    preview_offer = self.get_preview_offer(channel[8])
                    channel[7] = preview_offer.episode_title
        return channels

    def cancel_all_onepass(self, tsn):
        """
        /v1/onepasses/collectionId/{collectionId}
        method used to cancel all onepasses for a TSN
        Args: str: TSN
        Returns: True

        Note*
        method uses get_my_shows_item_search() to get a list of collectionIds for onepasses.
        To be retested/updated when get_my_shows_item_search() cloudcore call will include Onepasses in responses.
        """

        my_shows_items = self.get_my_shows_item_search(tsn)
        url = self.url_resolver.get_endpoints("cloudcore-onepass")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        headers_to_add = self.get_headers()
        part_uri = ""
        for item in my_shows_items:
            try:
                if item.collection_id:
                    part_uri = "/{}/schedule".format(item.collection_id)
            except AttributeError as myerr:
                self.log.info("no collectionID for this item - continue {}".format(myerr))
                continue
            try:
                MyShowsIocContainer.make_request(self.settings, url_base, port, {},
                                                 function_name="cloud_core_onepass", tsn=tsn, update_headers=False,
                                                 headers=headers_to_add, http_method="delete",
                                                 http_protocol=http_protocol, part_uri=part_uri, use_query_params=False)
            except AssertionError as myerr:
                if "No items" in str(myerr):
                    self.log.info("not a onepass,, continue to next item")
                    continue
                else:
                    self.log.warning("failed to delete onepass for collection {}, reason: {}".format(item.collection_id,
                                                                                                     myerr))
                    continue
        return True

    def find_past_socu_offers(self,
                              max_amount=5,
                              past_hours=None,
                              no_ott=None,
                              no_live=None,
                              no_recording=None,
                              subtitle=None,
                              **kwargs):
        """
        Returns the list of past socu offer with given criteria

        Kwargs:
            use_cached_grid_row (bool): True - using cached get_grid_row_search(), False - making request
            is_preview_offer_needed (bool): True - making /v1/preview/offer request to get additional specific data,
                                            False - no /v1/preview/offer request;
                                            more info on when it's needed - mind_api.open_api.open_api#get_grid_row_search();
                                            OpenAPI specific param;

        Args:
            max_amount (int): count of offers to return
            past_hours (int): number of past hours to look offers for, if not specified random of 4..12 hours to be used
            no_ott (bool): if True, don't return offers with OTT availability
            no_live (bool): if True, don't return offers with availability on Live Tv
            no_recording (bool): if True, don't return offers available as recordings
            subtitle (bool): if True, return only episodes. False/None was not tested

        Returns:
             list, [Offer (python class)]
        """
        from mind_api.dependency_injection.entities.offer import Offer
        offers = super(ServiceAPI, self).find_past_socu_offers(max_amount=max_amount,
                                                               past_hours=past_hours,
                                                               no_ott=no_ott,
                                                               no_live=no_live,
                                                               no_recording=no_recording,
                                                               subtitle=subtitle,
                                                               **kwargs
                                                               )
        socu_offers = []
        # regenerate offer object with subtitle
        for offer in offers:
            preview = self.get_preview_offer(offer.offer_id)
            raw_offer = offer.dict_item
            raw_offer['subtitle'] = preview.episode_title
            socu_offers.append(Offer(raw_offer))
        return socu_offers

    def unsubscribe(self, id):
        """
        /v1/onepasses/collectionId/{collectionId}
        method used to cancel an onepass or a single subscription
        Args: str: id - subscriptionId
        Returns: dict: {"type": "success"} or {"type": "error"}

        Note*
        old implementation for "unsubscribe" was using directly the subscriptionId to cancel a subscription
        cloudcore APIs need collectionId to cancel Onepass, contentId + offerId to cancel single scheduled recordings
        needed info for cloudcore is retrieved with subscriptionSearch(id) then the cc endpoint is called.
        *delete_all_subscriptions() is the only method using unsubscribe(), to be implemented for cc and call
        unsubscribe() dirrectly wiht collectionId/contentId/offerId when there will be a cc endpoint available
        to retrieve all subscriptions for a given TSN with required attributes.
        """

        tsn = self.settings.tsn
        details_from_sub_id = self.subscriptionSearch(tsn, id)
        response_to_return = {"type": "error"}
        if "seasonPassSource" in str(details_from_sub_id):
            collection_id = details_from_sub_id["subscription"][0]["idSetSource"]["collectionId"]
            url = self.url_resolver.get_endpoints("cloudcore-onepass")
            http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
            part_uri = "/{}/schedule".format(collection_id)
            headers_to_add = self.get_headers()
            r = MyShowsIocContainer.make_request(self.settings, url_base, port, {},
                                                 function_name="cloud_core_onepass", tsn=tsn, update_headers=False,
                                                 headers=headers_to_add, http_method="delete",
                                                 http_protocol=http_protocol, part_uri=part_uri, use_query_params=False)
            self.log.info("Onepass deleted {}".format(r))
            response_to_return = {"type": "success"}
        elif "singleOfferSource" in str(details_from_sub_id):
            content_id = details_from_sub_id["subscription"][0]["idSetSource"]["contentId"]
            offer_id = details_from_sub_id["subscription"][0]["idSetSource"]["offerId"]
            url = self.url_resolver.get_endpoints("cloudcore-recordings")
            http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
            part_uri = "/{}/schedule".format(offer_id)
            headers_to_add = self.get_headers()
            headers_to_add["content-type"] = "application/json"
            url_params = {"contentId": content_id}
            r = MyShowsIocContainer.make_request(self.settings, url_base, port, {},
                                                 function_name="cloud_core_recordings", tsn=tsn, update_headers=False,
                                                 headers=headers_to_add, http_method="delete",
                                                 http_protocol=http_protocol, part_uri=part_uri, use_query_params=True,
                                                 url_params=url_params)
            self.log.info("Recording subscription deleted {}".format(r))
            response_to_return = {"type": "success"}
        return response_to_return

    @Cacher.process
    def may_also_like_open_api_collection_search(self, use_cached_response=False, search_item_type="", search_string="",
                                                 expected_string=""):
        """
        Method will be supported from hydra v1.19
        /v1/mayAlsoLike/collections
        method used to find feedItemId of content on May Also Like strip.
        """
        tsn = self.settings.tsn
        search_ccu_response = self.get_unified_item_search_open_api(keyword=search_string)
        open_collection_id = ""
        for open_item in search_ccu_response.search_items():
            if open_item["searchItemType"] == search_item_type and open_item["title"] == expected_string:
                open_collection_id = open_item["searchItemId"]
        url = self.url_resolver.get_endpoints("feeditems-service")
        payload = {"includeIpVod": True, "includeAdult": False, "offset": 0,
                   "count": "12"}
        part_uri = "/{}".format(open_collection_id)
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        response = MayAlsoLikeContainer.get_item(self.settings, url_base, port, payload, http_protocol=http_protocol,
                                                 http_method="get", headers=self.get_headers(tsn), update_headers=True,
                                                 function_name="open_api_may_also_like", use_query_params=False, tsn=tsn,
                                                 part_uri=part_uri)
        return response

    @Cacher.process
    def ipppv_offer_get(self, offerId):
        """
        v1/ipppv/offerDetails request

        Returns:
            IppvDetails object (alreadyPurchased, previewDuration, purchaseWindowStart, purchaseWindowDuration, startTime)

        """
        tsn = self.settings.tsn
        url = self.url_resolver.get_endpoints("cloudcore-ipppv")
        part_uri = f"/{offerId}"
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        ipppv_details = IpppvDetailsContainer.get_item(
            self.settings, url_base, port, {}, http_protocol=http_protocol, part_uri=part_uri, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name="ipppv_offer_details",
            use_query_params=False, tsn=tsn)
        return ipppv_details

    def remove_content_locator(self, tsn, contentId):
        """
        /v1/bookmarks/contentId/{contentId}
        """
        response_to_return = {"type": "error"}
        url = self.url_resolver.get_endpoints("cloudcore-bookmarks")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        part_uri = "/{}/schedule".format(contentId)
        headers_to_add = self.get_headers()
        response = MyShowsIocContainer.make_request(self.settings, url_base, port, {},
                                                    function_name="cloud_core_bookmarks", tsn=tsn, update_headers=False,
                                                    headers=headers_to_add, http_method="delete",
                                                    http_protocol=http_protocol, part_uri=part_uri,
                                                    use_query_params=False)
        self.log.info("bookmark deleted {} {}".format(contentId, response))
        if response == 200:
            response_to_return = {"type": "success"}
        return response_to_return

    def delete_currently_streaming_content_from_myshows(self, contentId):
        """
        /v1/bookmarks/contentId/{contentId}
        This function deletes any content which is currently streaming from the my shows folder.
        used by methods to delete content that has "ctl" in myShowsItemId
        :param contentId: content id of the content that needs to be deleted
        :return:  {"type": "error"} if failed or {"type": "success"}
        """
        tsn = self.settings.tsn
        response = self.remove_content_locator(tsn, contentId)
        return response

    def get_streaming_playback_session_details(self):
        """
        /v1/sessionCreate
        Method will be supported from Hydra v1.19.
        Get session information by making v1/sessionCreate request on first recording in MyShows.

        Returns: dict, Ex: {'drmType': 'verimatrix', 'firstKeepAliveSeconds': 272, 'keepAliveIntervalSeconds': 400,
        'partnerId': 'tivo:pt.1008011', 'transportEncodingType': 'hlsTransportStream', 'tsn': 'tsn:A9F000003EAC6D1',
        'playlistUrl': 'http://frumos01.tivo.com/VMX4/rolling-buffer/ktvu/ktvu/transmux/index.m3u8?ccur_st=1683e etc.}
        """
        tsn = self.settings.tsn
        device_type = self.get_device_type()
        drm_type = self.get_authentication_configuration_search(True)["authenticationConfiguration"][0].get("drmType")
        show_detail_response = self.get_my_shows_item_search(tsn=tsn)
        first_show_in_list = show_detail_response[0]
        content_id = first_show_in_list.content_id
        cloud_recording_search_resp = self.cloud_recording_search(content_id)
        partner_recording_id = cloud_recording_search_resp["cloudRecording"][0]["cloudRecordingId"]
        partner_id = cloud_recording_search_resp["cloudRecording"][0]["recordingProviderPartnerId"]
        partner_station_id = cloud_recording_search_resp["cloudRecording"][0]["channel"]["partnerStationId"]
        partner_services_customer_id = self.getPartnerCustomerId()
        payload = {"tsn": tsn, "deviceType": device_type, "partnerId": partner_id,
                   "partnerStationId": partner_station_id, "partnerServicesBodyId": "",
                   "partnerServicesCustomerId": partner_services_customer_id, "partnerRecordingId": partner_recording_id,
                   "wanIpAddress": "ipAddress", "drmType": drm_type}
        url = self.url_resolver.get_endpoints("session-manager-lambda")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        session_create_response = SessionCreateContainer.get_item(
            self.settings, url_base, port, payload, http_protocol=http_protocol, http_method="post",
            headers=self.get_headers(tsn), update_headers=True, function_name="open_api_session_create",
            use_query_params=False)
        return session_create_response

    def season_pass_subscribe(self, collection_id):
        """
        Creates a onepass subscription including recordings only
        Args: collection_id
        Return: title of the subscribed collection
        """
        tsn = self.settings.tsn
        response_subscription_id = self.subscribe(tsn, collection_id, include="recordingOnly")
        if "error" not in str(response_subscription_id):
            subscription_detail_response = self.get_subscriptionDetails_from_collection_id(collection_id)
            return subscription_detail_response['subscription'][0]['title']
        else:
            raise AssertionError('cc season pass subscribe was not successful')

    @Cacher.process
    def get_vod_ott_action_details(self, content_id, exclude_socu_partner_id=None, use_cached_response=True):
        """
        /v1/vodOttActionDetails/content/{contentId}

        Args:
            content_id (str): e.g. tivo:ct.456968876
            exclude_socu_partner_id (str): SOCU partner id to exclude e.g. tivo:pt.1009011;
                                           applicable when reaching All Streaming Options overlay from Guide screen
            use_cached_response (bool): True - using cached response, False - making request

        Returns:
            list, [VodOttAction]
        """
        tsn = self.settings.tsn
        params = {"excludeSoCuVideoProviderId": exclude_socu_partner_id} if exclude_socu_partner_id else {}
        url = self.url_resolver.get_endpoints("cc-vod-ott-action-details")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        vod_ott_action_details_list = VodOttActionDetailsContainer.get_list(
            self.settings, url_base, port, {}, http_protocol=http_protocol, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name="open_api_vod_ott_act_det",
            use_query_params=False, part_uri=content_id, url_params=params)
        return vod_ott_action_details_list

    @Cacher.process
    def get_rating_instructions_get(self, use_cached_response=True):
        """
        /v1/internalRatings

        Args:
            use_cached_response (bool): True - using cached response, False - making request

        Returns:
            RatingInstructions
        """
        tsn = self.settings.tsn
        url = self.url_resolver.get_endpoints("cloudcore-rating")
        http_protocol, url_base, port = self.url_resolver.get_http_prot_url_port_separately(url)[0:3]
        rating_instructions = RatingInstructionsContainer.get_item(
            self.settings, url_base, port, {}, http_protocol=http_protocol, http_method="get",
            headers=self.get_headers(tsn), update_headers=True, function_name="open_api_rating_instruct",
            use_query_params=False)
        return rating_instructions
