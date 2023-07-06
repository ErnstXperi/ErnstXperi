import pytest
import time
import json

from hamcrest import assert_that, contains_string, is_not, is_, equal_to, has_item, equal_to_ignoring_case, is_in

from tools.logger.logger import Logger
from core_api.stb.assertions import CoreAssertions
from set_top_box.shared_context import ExecutionContext


class APIAssertions(CoreAssertions):

    __logger = Logger(__name__)

    def verify_recording_myshows(self, tester, recording):
        my_shows_rec = tester.service_api.get_recordings_in_my_shows()
        assert_that(my_shows_rec, has_item(recording), f"{recording} not found in myshows")

    def verify_recording_deleted_from_myshows(self, tester, recording):
        my_shows_rec = tester.service_api.get_recordings_in_my_shows()
        if recording in my_shows_rec:
            raise AssertionError("Recording not deleted from my shows")

    def verify_onepass_subscription(self, subscriptionList, collectionId):
        self.log.step("Verifying One pass subscription was created for the same {}".format(collectionId))
        if subscriptionList['subscription'][0]['idSetSource']['collectionId'] != collectionId and\
           subscriptionList['subscription'][0]['idSetSource']['type'] != 'seasonPassSource':
            raise AssertionError("One pass createion has failed for collection Id: {}".format(collectionId))

    def validate_menu_items_on_home_screen(self, tester, shortcuts):
        shortcuts = list(shortcuts.keys())
        shortcuts = [item.upper() for item in shortcuts]
        menu_labels = tester.home_labels.LBL_HOME_MENU_ITEMS_SHORTCUTS
        found = False
        for eachitem in shortcuts:
            if eachitem in menu_labels:
                found = True
            else:
                found = False
                break
        assert_that(found, 'Expected menu item not found in the home screen')

    def verify_search_result(self, result, program, movie=None):
        for item in result['unifiedItem']:
            if movie:
                if item['title'] == program and item['movieYear'] == int(movie):
                    break
            elif item['title'] == program:
                break
        else:
            raise AssertionError("Expected program {} not found from search result".format(program))

    def verify_future_recording_in_todolist(self, tester, recording):
        subscription = tester.api.get_subscriptions_title()
        if recording not in subscription:
            raise AssertionError("Recording not created in todolist")

    def verify_future_recording_deleted_from_todolist(self, tester, recording):
        subscription = tester.api.get_subscriptions_title()
        if subscription is None:
            self.log.info("No subscription available")
            return
        if recording in subscription:
            raise AssertionError("Recording not deleted from todolist")

    def verify_brandingbundle_is_found_same_for_morpheus_and_open_api(self):
        value_from_morpheus = ExecutionContext.mind_if.trio_api.branding_ui(field="distributor_name")
        if not value_from_morpheus:
            pytest.skip("Failed to get {} value from Ui branding bundle response".format("distributorName"))
        value_from_open_api = ExecutionContext.mind_if.open_api.branding_ui(field="distributor_name")
        assert_that(value_from_morpheus, equal_to(value_from_open_api), "branding bundles aren't same.")

    def verify_search_response_is_found_same_for_morpheus_and_open_api(self):
        response_openAPI = ExecutionContext.mind_if.open_api.get_unified_item_search_open_api(keyword="Doom")
        if not response_openAPI:
            pytest.skip("Failed to get {} Open API response".format(response_openAPI))
        response_morpheus = ExecutionContext.mind_if.trio_api.get_unified_item_search_trio(keyword="Doom")
        if not response_morpheus:
            pytest.skip("Failed to get {} Morpheus API response".format(response_morpheus))
        morpheus_title_list = []
        for mor_item in response_morpheus.dict_item.get('unifiedItem'):
            if mor_item["collectionType"] == "series":
                morpheus_title_list.append(mor_item["title"])
        open_title_list = []
        for open_item in response_openAPI.search_items():
            if open_item["searchItemType"] == "Series":
                open_title_list.append(open_item["title"])
        assert_that((morpheus_title_list[0]), is_in(open_title_list))

    def verify_device_feature_search(self, feature_name, attr_val_dict_to_check, expected=True):
        """
        Verifying:
            - If param of a feature in deviceFeatureSearch is equal/not equal to the particular value
              when attr_val_dict_to_check is set
            - If the feature is on/off if attr_val_dict_to_check is not set

        Args:
            feature_name (str): feature name e.g. inactivityTime, forceBackhaul
            attr_val_dict_to_check (dict): dict item e.g. {"autoStandbyInactivityTimeoutMinutes": "5"}
            expected (bool): True - checking if attribute's value equal to passed one, False - otherwise

        Returns:
            bool, True - verification passed
        """
        key = value = None
        for i, j in attr_val_dict_to_check.items():
            key = i
            value = j
            break  # for now, only one param is supported
        self.__logger.info(f"Verifying '{key} = {value}' attribute for {feature_name} feature in deviceFeatureSearch; "
                           f"expected {expected}")
        feature_found = False
        attribute_found = False
        check = False
        cur_attr_value = None
        response = ExecutionContext.iptv_prov_api.device_feature_search(feature_name)
        for feature in response["features"]:
            if feature_name == feature["featureName"]:
                feature_found = True
                for attribute in feature["attributes"]:
                    if key == attribute["attributeName"]:
                        attribute_found = True
                        if value == attribute["attributeValue"]:
                            check = True
                        else:
                            cur_attr_value = attribute["attributeValue"]
                        break
        if feature_found and attribute_found and check and expected or \
           feature_found and attribute_found and not check and not expected or \
           feature_found and not attribute_found and not check and not expected or \
           not feature_found and not attribute_found and not check and not expected:
            return True
        raise AssertionError("Verification of deviceFeatureSearch failed. feature_found {}; attribute_found {}; "
                             "check {}; expected {}; cur_attr_value {}".format(feature_found, attribute_found, check,
                                                                               expected, cur_attr_value))
