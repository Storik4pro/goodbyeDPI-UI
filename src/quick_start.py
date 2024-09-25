import os
import configparser

from _data import DIRECTORY

def merge_blacklist(goodbye_dpi_path):
    russia_youtube_file = os.path.join(goodbye_dpi_path, 'russia-youtube.txt')
    custom_blacklist_file = os.path.join(goodbye_dpi_path, 'custom_blacklist.txt')

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
        return

    backup_config = configparser.ConfigParser()
    backup_config.read(backup_settings_file, encoding='utf-8')

    settings_config = configparser.ConfigParser()
    settings_config.read(settings_file, encoding='utf-8')

    for section in settings_config.sections():
        if not backup_config.has_section(section):
            backup_config.add_section(section)
            print(f"Added new section [{section}]")
        for key, value in settings_config.items(section):
            if not backup_config.has_option(section, key):
                backup_config.set(section, key, value)
                print(f"Added new option '{key}' in section [{section}] with value '{value}'")

    with open(settings_file, 'w', encoding='utf-8') as configfile:
        backup_config.write(configfile)
    print(f"Merged settings written to {settings_file}")

    os.remove(backup_settings_file)
    print(f"Deleted backup settings file {backup_settings_file}")

def rename_update_exe():
    update_path = DIRECTORY.replace("_internal/", "")+'update.exe'
    temp_update_path = DIRECTORY.replace("_internal/", "")+'_update.exe'

    if os.path.exists(update_path):
        os.remove(update_path)

    if os.path.exists(temp_update_path):
        os.rename(temp_update_path, update_path)
        return True
    else:
        return False

