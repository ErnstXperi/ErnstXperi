import os
import re
import inspect
import pprint
from set_top_box.conf_constants import MsoList, PlatformList, LanguageList
from tools.logger.logger import Logger


class FileSelector:
    """Class to search page module according to page_name
    :param page_name: str, name of page to be looked for. Case Insensitive
    :param config: obj, suite settings
    :param default_name: str, filename of module will be used by default (page.py, labels.py etc)

    :Example:
        page_path = FileSelector("Menu", config, default_name='page.py', ).get_module()
    """

    def __init__(self, page_name, language, config, default_name, **kwargs):
        self.page_name = page_name
        self.language = language
        self.__config = config
        self.__basedir = kwargs.get("base_dir") or os.path.dirname(os.path.realpath(__file__))
        self._DEFAULT = "default"
        self._default_obj_name = default_name
        self._name_pattern = kwargs.get('name_pattern') or self._default_obj_name.replace('.py', '')
        self.__verbose_mode = kwargs.get("verbose", 0)
        self.__log = Logger(__name__)

    def __list_filter(self, key, src_list):
        """
        Method to filter list according to key
        :param key: str, filter to be applied. RegEx supported, IgnoreCase
        :param src_list: original list
        :return: list
        """
        return list(filter(lambda x: re.search(key, x, re.IGNORECASE), src_list))

    def __get_filterd_listdir(self, key, root_dir):
        """
        Get list of files with key in filename
        :param key: str, key to select files
        :param root_dir: str, path to be listed
        :return: list files
        """
        files_list = self.__list_filter(key, os.listdir(root_dir))
        return files_list

    def __get_common_page_dir(self, page_name):
        """
        Get dirpath with specified name
        :param page_name: str, name to looked for
        :return: str, dirpath
        """
        pages_list = self.__get_filterd_listdir(page_name, self.__basedir)
        if len(pages_list) == 1:
            page_dir = os.path.join(self.__basedir, pages_list[0])
        else:
            raise ValueError("Found incorrect number of pages: '{}'".format(pages_list))
        return page_dir

    def __get_common_language_dir(self, language, page_dir):
        lan_list = self.__get_filterd_listdir(language, page_dir)
        if lan_list:
            language_dir = os.path.join(page_dir, lan_list[0])
        else:
            language_dir = os.path.join(page_dir, LanguageList.ENGLISH)
        return language_dir

    def __extract_page_filenames(self, page_name, root_dir):
        """
        Extract all filenames related to page object
        :param page_name: str, substr to be looked for in filenames
        :param root_dir: dirpath where search is performed
        :return: list of selected filenames
        """
        pages_list = self.__get_filterd_listdir(page_name, root_dir)
        return pages_list

    def __convert_all_pages_to_dict(self, pages_list):
        """
        Convert list of page's filenames to array with all supported parameters
        :param pages_list: list of page's filenames
        :return: dict, array with parameters
        """
        page_dict = {}
        for page in pages_list:
            parameters = page.replace('.py', '').split("_")[1:]
            mso = self._DEFAULT
            manage_id = self._DEFAULT
            platform = self._DEFAULT
            for item in parameters:
                if item in MsoList:
                    mso = item
                elif item in PlatformList:
                    platform = item
                elif "managed" in item:
                    manage_id = item
            page_dict[page] = {'manage_id': manage_id, 'mso': mso, 'platform': platform}
        if self.__verbose_mode >= 3:
            self.__log.debug("{}".format(pprint.pformat(page_dict)))
        return page_dict

    def __get_page_according_to_prio(self, page_path, param_prio):
        """
        Get page filename according to priority (mso then, manage key, then default)
        :param page_path: path where all available pages will be looked for
        :param param_prio: list, list on parameters name sorted by priority
        :return: str, page name
        """
        available_pages = self.__extract_page_filenames(self._name_pattern, page_path)
        page_dict = self.__convert_all_pages_to_dict(available_pages)
        default = self._DEFAULT
        applicable_pages = {}
        # sorting of available pages

        for param in param_prio:
            applicable_pages[param] = []
        else:
            applicable_pages[default] = [self._default_obj_name]

        def _check_values(page_name, attr_name):
            """ method to verify page satisfies parameter """
            test_conf_value = getattr(self.__config, attr_name)
            page_prpty_value = page_dict[page_name][attr_name]
            # is_configured = bool(test_conf_value)  # redundant but let's live for a while
            is_param_in_page = page_prpty_value == test_conf_value
            page_has_default_value = page_prpty_value is self._DEFAULT
            result = is_param_in_page or page_has_default_value
            if self.__verbose_mode >= 2:
                self.__log.debug("::: Page: '{}', attr:'{}, page_value:{}',"
                                 " settings_value:'{}'  ::: {}".format(page_name,
                                                                       attr_name,
                                                                       page_prpty_value,
                                                                       test_conf_value,
                                                                       result))
            return result

        # filling array with pages not conflicting with parameters
        filtred_list = []
        for page in page_dict.keys():
            if all(_check_values(page, param) for param in param_prio):
                filtred_list.append(page)

        # sort pages according to param (priority)
        for page in filtred_list:
            for param in param_prio:
                if page_dict[page][param] is not self._DEFAULT:
                    applicable_pages[param].append(page)
        self.__log.debug("Applicable_pages: {}".format(applicable_pages))

        # get page according to priority
        for prio in param_prio:
            if len(applicable_pages[prio]) != 0:
                page = applicable_pages[prio][0]
                break
        else:
            # if there is no page corresponding to config then default page
            page = applicable_pages[default][0]
        return page

    def get_module(self, param_prio=None, default_allowed=True):
        """
        Method to get page file path according to name and test configs

        Args:
            param_prio: list, list of parameters priority. If only a parameter in list then only the file
                        for the parameter will be returned or default
            default_allowed: bool, flag to allow default pages, if False only object which corrsponds to settings will
                        be returned or None
        Returns: str, page path
        """
        param_prio = param_prio or ['mso', 'platform', 'manage_id']
        base_page_path = self.__get_common_page_dir(self.page_name)
        if self.language is not self._DEFAULT:
            if hasattr(self.__config, 'language'):
                self.language = getattr(self.__config, 'language')
            base_page_path = self.__get_common_language_dir(self.language, base_page_path)
        # check at least one parameter defined else select default page
        if any(getattr(self.__config, param) for param in param_prio):
            page = self.__get_page_according_to_prio(base_page_path, param_prio)
        else:
            self.__log.info("Settings are not defined, Default page will be returned")
            page = self._default_obj_name
        if page is self._default_obj_name and default_allowed:
            page_path = os.path.join(base_page_path, page)
        elif page is not self._default_obj_name:
            page_path = os.path.join(base_page_path, page)
        else:
            page_path = None
        return page_path


class ClassProcessor:
    """
    class to work with imports and classes
    """

    @staticmethod
    def merge_classes(obj_list):
        """
        method to merge classes - multiple inheritance. You have to sort classes in origin list in order you expect
        merge. Merging order will be per
        Args:
            obj_list: list, list of class objects to be merged

        Returns: merged class

        """
        class MixedClass(*obj_list):
            pass
        sum_name = [itm.__name__ for itm in obj_list]
        MixedClass.__name__ = "_".join(sum_name)
        return MixedClass

    @staticmethod
    def get_class(package_path, obj_name=""):
        """
        Method to import class by module path.
        Args:
            package_path: str, relative python module path. formatted in python way with dots
            obj_name: str, name of objecct to be imported. by default any class

        Returns: class obj from specified module

        """
        page_obj = __import__(package_path, fromlist=[''])
        page_obj_name = obj_name
        # let's live the code for debugging
        # for item in dir(page_obj):
        #     if cls.page_obj_pattern in item and len(obj_name) < len(item):
        #         page_obj_name = item
        for item in inspect.getmembers(page_obj, inspect.isclass):
            if package_path in item[1].__module__:
                page_obj_name = item[0]
                break
        page_obj = getattr(page_obj, page_obj_name)
        return page_obj


class FileModuleFactory:
    """
    Page Factory class.
    class will search for a page with specified name and defined settings.

    page file naming rules:
        page.py - default
        page_<manage_id>.py
        page_<manage_id>_<mso>.py

    file examples:
        page.py
        page_tds.py
        page_unmanaged.py
        page_unmanaged_cableco3.py
        page_cableco3.py


    :param page_name: str, page name to be looked for
    :param config: obj, dataclass with configs
    :param *args: all other arguments which has to be passed to PageObject

    :Examples:
        request.cls.home_page = PageFactory("home", Settings, request.cls.screen)

    """
    selector = FileSelector
    class_tool = ClassProcessor
    page_obj_pattern = ""
    default_module_name = ""
    log = Logger(__name__)

    def __new__(cls, page_name, config, *args):
        utaf_path = os.path.abspath(__file__).partition("set_top_box")[0]
        language = "default"
        client_api_dir = os.path.join(utaf_path, "set_top_box/client_api")
        cls.log.info("Searching {} for '{}' performed by path: '{}'. "
                     "Config MSO='{config.mso}', mng_id='{config.manage_id}'".format(cls.page_obj_pattern,
                                                                                     page_name,
                                                                                     utaf_path,
                                                                                     config=config))
        page_path = cls.selector(page_name,
                                 language,
                                 config,
                                 cls.default_module_name,
                                 base_dir=client_api_dir).get_module()
        # path converted to python import (dots)
        package_path = (os.path.relpath(page_path, utaf_path).replace('/', '.')[:-3])
        page_obj = cls.class_tool.get_class(package_path)
        cls.log.info("{} object for '{}' found: '{}' by path: '{}'".format(cls.page_obj_pattern,
                                                                           page_name,
                                                                           page_obj,
                                                                           package_path))
        return page_obj(*args)
