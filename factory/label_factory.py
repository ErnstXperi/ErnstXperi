from set_top_box.factory.base_file_factory import FileSelector, ClassProcessor
from tools.logger.logger import Logger
import os


class LabelFactory:
    """
    Label Factory class.
    class will search for a page with specified name and defined settings.

    The factory works with only diffs and all labels which are corresponds to config will be merged in the next order:
        1. get label according to manage id                     UnmanagedLabels(BaseLabels)
        2. platform labels will apply over manage_id labels     PlatformLabels(UnmanagedLabels)
        3. mso lables will apply over platform labels           MSOLabels(PlatformLabels)

    label file naming rules:
        labels.py - default
        labels_<manage_id>.py
        labels_<mso>.py
        labels_<platform>.py

    file examples:
        labels.py
        labels_tds.py
        labels_unmanaged.py
        labels_firetv.py
        labels_cableco3.py

    Args:
        page_name: str, page name to be looked for
        config: obj, dataclass with configs

    :Examples:
        request.cls.home_labels = LabelFactory("home", Settings)

    """
    selector = FileSelector
    class_tool = ClassProcessor
    page_obj_pattern = "Label"
    default_module_name = "labels.py"
    DIFF_PRIO = ("mso", "platform", "manage_id")  # inheritance sequence right to left
    log = Logger(__name__)

    def __new__(cls, page_name, config, *args):
        utaf_path = os.path.abspath(__file__).partition("set_top_box")[0]
        client_api_dir = os.path.join(utaf_path, "set_top_box/client_api")
        default_language = "en_us"
        cls.log.info("Searching {} for '{}' performed by path: '{}'. "
                     "Config MSO='{config.mso}', mng_id='{config.manage_id}'".format(cls.page_obj_pattern,
                                                                                     page_name,
                                                                                     utaf_path,
                                                                                     config=config))
        file_selector = cls.selector(page_name, default_language, config, cls.default_module_name, base_dir=client_api_dir)
        class_list = []
        class_path_list = []
        for element in cls.DIFF_PRIO:
            dflt_allowed = element == cls.DIFF_PRIO[-1]  # to be able get default labels if all other are absent
            label_path = file_selector.get_module([element], default_allowed=dflt_allowed)
            if label_path is not None:
                label_package_path = (os.path.relpath(label_path, utaf_path).replace('/', '.')[:-3])
                class_obj = cls.class_tool.get_class(label_package_path)
                if class_obj not in class_list:
                    class_list.append(class_obj)
                    class_path_list.append(label_package_path)
        label = cls.class_tool.merge_classes(class_list)
        cls.log.info("{} object for '{}' found: '{}' by path: '{}'".format(cls.page_obj_pattern,
                                                                           page_name,
                                                                           class_list,
                                                                           class_path_list))
        return label()
