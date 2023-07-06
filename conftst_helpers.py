import glob
import os
import re
import requests
from datetime import datetime
from datetime import timedelta
import logging
from pathlib import Path
from tools.logger.logger import Logger
from set_top_box.shared_context import ExecutionContext

logger = Logger(__name__)


def generate_bugreport(request):
    """
    helper to generate and download bugreport from DUT
    Args:
        request: pytest obj
    """
    settings = request.config.Settings
    driver = request.cls.driver.base
    file_name = "bugreport_{}.zip".format(datetime.now().strftime("%Y%m%d_%H_%M_%S").strip())
    out_file = os.path.join(settings.log_path, file_name)
    driver.get_system_bugreport(out_file)


def get_build_number(settings):
    """ method to get build number from source """
    apk_number = settings.build
    if apk_number.lower() == "latest":
        if settings.platform == "appletv":
            apk_number = get_latest_build_id_tvos(settings.branch)
        else:
            apk_number = get_latest_number(settings.branch, settings.mso, settings.manage_id)
    return apk_number


def get_latest_number(branch_name, mso, manage_id):
    """method to get the build number from source

    :param branch: str, branch (b-hydra-mainline, ...)
    :param mso: str, name of build mso (cableco3, cableco11, midco, tds etc)
    :param manage_id: str, managed/unmanaged

    :return: str, build number
    """
    latest_build = ""
    retries = 2
    while retries > 0 and not latest_build:
        retries -= 1
        try:
            if branch_name == "b-hydra-mainline":
                latest_build = get_1700_build(mso, manage_id, branch_name)
            else:
                build_pattern = re.compile(r">([0-9]{4}.[0-9]{2}.[0-9]{2}-[0-9]{4})<")
                latest_build = find_build_rpmcache(build_pattern, mso, manage_id, branch_name)
            logger.info("Latest Build from rpmcache is {}".format(latest_build))
            # Fetch build only from rpmcache
            # if not latest_build:
            #    build_pattern = re.compile(r"[0-9]{4}.[0-9]{2}.[0-9]{2}-[0-9]{4}")
            #    latest_build = find_build_buildweb(build_pattern, mso, manage_id, branch_name)
        except Exception as error:
            print(f"WARNING!!! Could not get latest build for {branch_name} Error Info: {error}")
    return latest_build


def get_latest_build_id_tvos(branch_name):
    """
    Method to get last 1700 build_id  or latest for non-mainline. Function verifies availability of builds and returns
    only available in NFS

    Args:
        branch_name: str, name of branch

    Returns:
        str, build_id
    """
    nfs_root = os.environ.get("RPMDIR", "/net/rpmsrv/dist/rpms")
    c_date = datetime.now()
    c_month = c_date.month
    if c_month < 10:
        month_re = f"0[{c_month - 1}-{c_month}]"
    else:
        month_re = "[0-1][0-9]"

    if "mainline" in branch_name:
        build_re = f"202[2-9].{month_re}.[0-9][0-9]-17[0-9][0-9]"
    else:
        build_re = f"202[2-9].{month_re}.[0-9][0-9]-*"

    nfs_path = f"{nfs_root}/{branch_name}/{build_re}/release-tvosarm/tcd/".lower()
    build_list = glob.glob(nfs_path)
    if not build_list and "mainline" not in branch_name:
        nfs_path = f"{nfs_root}/{branch_name}/*/release-tvosarm/tcd/".lower()
        build_list = glob.glob(nfs_path)
    if build_list:
        build_list.sort()
    else:
        raise LookupError(f"No available build for: {nfs_path}")
    build = re.findall(r"202[2-9]\.[0-9]{2}\.[0-9]{2}-[0-9]{4}", build_list[-1])[0]
    return build


def check_build_number_exists(url, var, mso, manage_id, branch_name):
    response = requests.get(f"{url}/{var}/")
    if re.search("release-android", response.text):
        response = requests.get(f"{url}/{var}/archive/apks/")
        branch = branch_name.replace('b-hydra', 'hydra')
        build_name = f"{branch}-{mso}-{manage_id}-{var}(-nozipalign)?.apk.gz"
        pattern = re.compile(r">({})<".format(build_name))
        if not re.search(pattern, response.text):
            var = ""
    else:
        var = ""
    return var


def check_build_number_exists_buildweb(url, var, mso, manage_id):
    response = requests.get(f"{url}&BUILD={var}&VERSION=release")
    if not re.search(f"{mso}-{manage_id}", response.text):
        var = ""
    return var


def find_build_rpmcache(build_pattern, mso, manage_id, branch_name):
    url = f"http://rpmcache.engr.tivo.com/dist/rpms/{branch_name}"
    response = requests.get(url)
    var = ""
    if re.search(build_pattern, response.text):
        build = re.findall(build_pattern, response.text)
        for index in range(len(build) - 1, -1, -1):
            var = check_build_number_exists(url, build[index], mso, manage_id, branch_name)
            if var:
                var = build[index]
                break
    return var


def find_build_buildweb(build_pattern, mso, manage_id, branch_name):
    url = f"http://buildweb.tivo.com/specialize/specialize.cgi?BRANCH={branch_name}"
    response = requests.get(url)
    var = ""
    if re.search(build_pattern, response.text):
        build = re.findall(build_pattern, response.text)
        for index in range(len(build)):
            var = check_build_number_exists_buildweb(url, build[index], mso, manage_id)
            if var:
                var = build[index]
                break
    return var


def check_1700_timestamp(build_pattern, mso, manage_id, branch_name):
    url = f"http://rpmcache.engr.tivo.com/dist/rpms/{branch_name}"
    response = requests.get(url)
    build = ""
    logger.info("Checking if 1700 timestamp is available")
    if re.search(build_pattern, response.text):
        build = re.findall(build_pattern, response.text)
    target_build_id = ""
    for build_id in build:
        (date, timestamp) = build_id.split("-")
        if timestamp.isdigit() and int(timestamp) >= 1700:
            var = check_build_number_exists(url, build_id, mso, manage_id, branch_name)
            if var:
                target_build_id = build_id
                break
    return target_build_id


def get_1700_build(mso, manage_id, branch_name):
    today = datetime.today().strftime('%Y.%m.%d')
    var = ""
    build_pattern = re.compile(r">(" + today + r"-17[0-9]{2})<")
    var = find_build_rpmcache(build_pattern, mso, manage_id, branch_name)
    logger.info("1700 build from rpmcache is {}".format(var))
    if not var:
        build_pattern = re.compile(r">([0-9]{4}.[0-9]{2}.[0-9]{2}-[0-9]{4})<")
        var = find_build_rpmcache(build_pattern, mso, manage_id, branch_name)
    logger.info("Build obtained from rpmcache : {}".format(var))
    # if not var:
    #    var = get_mainline_build_from_buildweb(today, mso, manage_id, branch_name)
    return var


def get_mainline_build_from_buildweb(today, mso, manage_id, branch_name):
    var = ""
    build_number = re.compile(today + r"-17[0-9]{2}")
    var = find_build_buildweb(build_number, mso, manage_id, branch_name)
    if not var:
        build_number = re.compile(r"[0-9]{4}.[0-9]{2}.[0-9]{2}-[0-9]{4}")
        var = find_build_buildweb(build_number, mso, manage_id, branch_name)
    return var


def get_aut_name_apple_tv(settings):
    if settings.app_repackager == "testflight":
        if settings.mso == "astound":
            app_package = f"com.tivo.{settings.mso}.nonmr"
        else:
            app_package = f"com.tivo.{settings.mso}.ml"
    else:
        app_package = settings.app_package
    return app_package


def get_current_xray_id(request):
    """
    Function to get the current XRayID if it's available.
    Args:
        request: pytest object

    Returns:
        str, xrayid
    """
    xray_id = ""
    for mark in request.node.own_markers:
        if "xray" in mark.name:  # look for the word testrail
            xray_id = mark.args[0]  # format is a tuple
            break
    return xray_id


def get_next_new_folder_name(current: Path) -> Path:
    """
    Method to generate a new folder by adding new index to base folder path
    Args:
        current: Path obj, base folder path

    Returns:
        Path obj folder path for unexisting name
    """
    existing_folders = filter(lambda x: Path(x).is_dir(), glob.glob(f"{current}*"))
    if not existing_folders:
        new_folder = current
    else:
        def extract_index(path):
            path = Path(path)
            if path.name.split("_")[-1].isdigit():
                idx = int(path.name.split("_")[-1])
            else:
                idx = 0
            return idx
        max_idx = max(map(extract_index, existing_folders))
        new_folder = current.parent / f"{current.name}_{max_idx + 1}"
    return new_folder


def generate_artifacts_folder(settings_obj, request=None):
    """
    Method to create folder for UTAFs artifacts. It's able to generate common folder for all files inplace, and
    new folder for every testcase
    Args:
        settings_obj: obj, UTAF's global shared object with settings
        request: obj, pytest object

    Returns:
        str, path for output artifacts
    """
    log = Logger(f"{__name__}.artifact_gen")
    if not settings_obj.log_path:
        settings_obj.log_path = str(Path.cwd() / "log_dir")
        log.info(f"log_path is not defined hence using CWD: {settings_obj.log_path}")
    if not settings_obj.root_log_path:
        settings_obj.root_log_path = Path(settings_obj.log_path)

    if settings_obj.artifacts_mode == "testcase":
        log.debug(f"ENV: {os.environ.get('PYTEST_CURRENT_TEST')}, request:{request.node.name}")
        tc_name = request.node.name or os.environ.get('PYTEST_CURRENT_TEST', "utaf_init").split(':')[-1].split(' ')[0]
        curr_artifacts_path = settings_obj.root_log_path / tc_name
        if curr_artifacts_path.exists():
            curr_artifacts_path = get_next_new_folder_name(curr_artifacts_path)
        log.info(f"Artifacts per TC. OutputPath: {curr_artifacts_path}")
        settings_obj.log_path = str(curr_artifacts_path)
    else:  # global
        curr_artifacts_path = Path(settings_obj.log_path)
        log.info(f"Artifacts per RUN. OutputPath: {curr_artifacts_path}")
    curr_artifacts_path.mkdir(parents=True, exist_ok=True)
    return str(curr_artifacts_path)


def get_existing_drm_type(FE_PACKAGES, alacart_packages):
    existing_drm_pkg = []
    for pkg in FE_PACKAGES:
        for alcart in alacart_packages:
            if pkg in alcart:
                existing_drm_pkg.append(pkg)
                break
    else:
        logger.info(f"Existing drm package: {existing_drm_pkg}")
    return existing_drm_pkg


def add_drm_type_and_feature(feature_list, user_drm_type, env=None):
    logger.info("Trying to add drm type and feature")
    for feature in feature_list:
        response = ExecutionContext.iptv_prov_api.fe_alacarte_add_package_native_drm(feature, user_drm_type, env)
        logger.info(f"Response after trying to add feature {feature} for drm_type {user_drm_type} is {response}")


def remove_drm_type_and_feature(feature_list, existing_drm_type, alacart_packages, env=None):
    logger.info(f"Trying to remove drm type and feature {feature_list} {existing_drm_type} {alacart_packages}")

    for package in alacart_packages:
        pkg = package.split('-')
        if len(pkg) == 4:
            if pkg[2] in existing_drm_type:
                res = ExecutionContext.iptv_prov_api.fe_alacarte_remove_package_native_drm(pkg[3], pkg[2], env)
                logger.info(f"Response after trying to delete feature {pkg[3]} for drm_type {pkg[2]} is {res}")


def check_and_add_drm_type_and_feature(alacart_packages, feature_list, user_drm_type, env=None):
    logger.info("Trying to check find missing feature and add")
    missing_feature = []
    for feature in feature_list:
        for alacart_pkg in alacart_packages:
            if feature in alacart_pkg:
                logger.info(f"{feature} is present in {alacart_pkg}")
                break
        else:
            missing_feature.append(feature)
    logger.info(f"Missing feature: {missing_feature}")

    if missing_feature:
        add_drm_type_and_feature(missing_feature, user_drm_type, env)
    else:
        logger.info(f"Device is not missing any features for {user_drm_type}")
