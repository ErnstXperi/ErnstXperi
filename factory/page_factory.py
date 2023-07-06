from set_top_box.factory.base_file_factory import FileModuleFactory
from tools.logger.logger import Logger


class PageFactory(FileModuleFactory):
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

    page_obj_pattern = "Page"
    default_module_name = "page.py"
    log = Logger(__name__)
