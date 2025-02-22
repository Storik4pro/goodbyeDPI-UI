import configparser
import json
import os
import sys
from tkinter import messagebox
import traceback

from _data import (
    CONFIG_PATH,
    DEBUG,
    DIRECTORY,
    settings,
    SETTINGS_FILE_PATH,
    text,
    ZAPRET_PATH,
)
import psutil
from utils import is_process_running, is_weak_pc, register_app


from logger import AppLogger


def check_app_is_runned(logger: AppLogger):
    if not DEBUG:
        existing_app = is_process_running("goodbyeDPI.exe")
        if existing_app:
            result = messagebox.askyesno(
                text.inAppText["app_is_running"],
                text.inAppText["process"]
                + " 'goodbyeDPI.exe' "
                + text.inAppText["app_is_running_info"],
            )
            if result:
                try:
                    existing_app.terminate()
                    existing_app.wait()
                except psutil.NoSuchProcess:
                    logger.create_debug_log(traceback.format_exc())
                except Exception:
                    logger.create_error_log(traceback.format_exc())
            else:
                sys.exit(0)


def create_custom_hostlist(filename):
    content = """simplex.im
radiofrance.fr
dns.comss.one
cdn.betterttv.net
cdn.frankerfacez.com
rtmps.youtube.com"""
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            file.write(content)


def first_run_actions():
    first_run = settings.settings.getboolean("GLOBAL", "is_first_run")
    if first_run:
        register_app()
        create_custom_hostlist(ZAPRET_PATH + "/myhostlist.txt")
        settings.change_setting("GLOBAL", "is_first_run", "False")

        if is_weak_pc():
            settings.change_setting("APPEARANCE_MODE", "animations", "False")


def after_update_actions(logger: AppLogger):
    try:
        kill_update()
        _ = rename_update_exe()
        settings.change_setting("GLOBAL", "update_complete", "True")
    except Exception:
        logger.create_error_log(traceback.format_exc())
        settings.change_setting("GLOBAL", "update_complete", "False")


def chk_directory():
    if (
        settings.settings["GLOBAL"]["work_directory"] != DIRECTORY
        and "System32" not in DIRECTORY
    ):
        settings.change_setting("GLOBAL", "work_directory", DIRECTORY)


def kill_update():
    path = DIRECTORY.replace("_internal/", "")
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            if proc.info["name"].lower() == "update.exe" and proc.info["exe"]:
                exe_dir = os.path.abspath(os.path.dirname(proc.info["exe"]))
                if exe_dir.lower() == path.lower():
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def merge_blacklist(goodbye_dpi_path):
    russia_youtube_file = os.path.join(goodbye_dpi_path, "russia-youtube.txt")
    custom_blacklist_file = os.path.join(goodbye_dpi_path, "custom_blacklist.txt")

    if not os.path.exists(russia_youtube_file):
        return

    if os.path.exists(custom_blacklist_file):
        os.remove(custom_blacklist_file)
        print(f"Deleted existing {custom_blacklist_file}")

    if os.path.exists(russia_youtube_file):
        os.rename(russia_youtube_file, custom_blacklist_file)
        print(f"Renamed {russia_youtube_file} to {custom_blacklist_file}")
    else:
        print(f"{russia_youtube_file} does not exist.")


def merge_settings(backup_settings_file, settings_file):
    if not os.path.exists(backup_settings_file):
        print(f"Backup settings file {backup_settings_file} does not exist.")
        return False

    backup_config = configparser.ConfigParser()
    backup_config.read(backup_settings_file, encoding="utf-8")

    settings_config = configparser.ConfigParser()
    settings_config.read(settings_file, encoding="utf-8")

    for section in settings_config.sections():
        if not backup_config.has_section(section):
            backup_config.add_section(section)

        for key, value in settings_config.items(section):
            if not backup_config.has_option(section, key):
                backup_config.set(section, key, value)

    with open(settings_file, "w", encoding="utf-8") as configfile:
        backup_config.write(configfile)

    os.remove(backup_settings_file)
    return True


def rename_update_exe():
    update_path = DIRECTORY.replace("_internal/", "") + "update.exe"
    temp_update_path = DIRECTORY.replace("_internal/", "") + "_update.exe"

    if not os.path.exists(temp_update_path):
        return None

    if os.path.exists(update_path):
        os.remove(update_path)

    if os.path.exists(temp_update_path):
        os.rename(temp_update_path, update_path)
        return True
    return False


def merge_settings_to_json():
    if (
        "GOODBYEDPI" in settings.settings
        and "httpfragmentation" in settings.settings["GOODBYEDPI"]
    ):
        save_data = ["preset", "use_blacklist", "use_blacklist_custom"]
        copy_data = [
            "dns",
            "dns_value",
            "dns_port_value",
            "dnsv6_value",
            "dnsv6_port_value",
        ]
        goodbyedpi_data = {}
        keys_to_delete = []

        for key in settings.settings["GOODBYEDPI"]:
            if key not in save_data:
                data = settings.settings["GOODBYEDPI"][key]
                if data in ["False", "True"]:
                    data = settings.settings.getboolean("GOODBYEDPI", key)
                elif data.isdigit():
                    data = int(data)
                goodbyedpi_data[key] = data
                keys_to_delete.append(key)

        for key in keys_to_delete:
            if key not in copy_data:
                del settings.settings["GOODBYEDPI"][key]

        json_file = f"{CONFIG_PATH}/goodbyedpi/user.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(goodbyedpi_data, f, ensure_ascii=False, indent=4)

        with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as configfile:
            settings.settings.write(configfile)
        settings.reload_settings()
    if "custom_parameters" in settings.settings["ZAPRET"]:
        zapret_data = {}
        zapret_data["custom_parameters"] = settings.settings["ZAPRET"][
            "custom_parameters"
        ]

        del settings.settings["ZAPRET"]["custom_parameters"]

        json_file = f"{CONFIG_PATH}/zapret/user.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(zapret_data, f, ensure_ascii=False, indent=4)

        with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as configfile:
            settings.settings.write(configfile)
        settings.reload_settings()
