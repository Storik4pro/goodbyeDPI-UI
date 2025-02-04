import logging
import os
import zipfile
import sys
import threading
from tkinter import messagebox
from datetime import datetime
import argparse
from tkinter import ttk, Tk, Variable
import subprocess
import shutil
import psutil

DIRECTORY = f"{os.path.dirname(os.path.abspath(__file__))}/"
logger = logging.getLogger(__name__)
logging.basicConfig(filename="update.log", level=logging.INFO)

skip_files = [
    "update.exe",
]


def close_procces():
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == "goodbyeDPI.exe":
            try:
                proc.terminate()
                logger.info(f"process goodbyeDPI.exe terminated")
            except psutil.NoSuchProcess:
                pass


error_names = {
    1: "ERR_PERMISSION_DENIED",
    2: "ERR_FILE_NOT_FOUND",
    3: "ERR_EXTRACTING_FILE",
    4: "ERR_UNEXPECTED_ERROR",
    5: "ERR_LAUNCHING_APP",
}

error_message = """An unexpected error occurred while updating the application.
Additionally, an attempt to downgrade to the previous version failed.\n
You may need to manually reinstall the application to resolve this issue.\n
Please follow these steps:\n
1. Uninstall the current version of the application.\n
2. Download the latest version from GitHub.\n
3. Install the downloaded version.\n
If the problem persists, contact support.\n
"""


class UpdaterApp(Tk):
    def __init__(self, zip_file_path, unpack_directory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zip_file_path = zip_file_path
        self.unpack_directory = unpack_directory
        self.geometry("300x125")
        self.resizable(False, False)
        self.title("Update Assistant")
        self.iconbitmap(DIRECTORY + "update_icon.ico")
        self.end = False

        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(pady=(10, 10), padx=10, fill="both", expand=True)

        self.label = ttk.Label(
            self.content_frame, text="Patching application (GoodbyeDPI UI) ..."
        )
        self.label.pack(fill="both", expand=True)

        self.progress_var = Variable()
        self.progress_bar = ttk.Progressbar(
            self.content_frame,
            style="red.Horizontal.TProgressbar",
            variable=self.progress_var,
            maximum=1,
        )
        self.progress_bar.pack(pady=(5, 0), fill="x")

        self.file_label = ttk.Label(self.content_frame, text="Getting ready ...")
        self.file_label.pack(fill="both")

        self.button_frame = ttk.Frame(self.content_frame)
        self.button_frame.pack(fill="x", side="bottom")

        self.exit_button = ttk.Button(
            self.button_frame, text="Cancel", command=self.safe_exit
        )
        self.exit_button.config(state="disabled")
        self.exit_button.pack(side="right", pady=(2, 0))

        self.finish_status = 0

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.updating = threading.Thread(target=self.update_program)
        self.updating.start()

    def on_closing(self):
        if self.end:
            try:
                self.safe_exit()
            except:
                sys.exit(0)

    def create_logs(self, text):
        _time = datetime.now().strftime("%H:%M:%S")
        logger.info(f"[{_time}] {text}")
        self.file_label.configure(text=f"{text}")

    def downgrade_program(self):
        old_directory = os.path.join(self.unpack_directory, ".old")
        self.label.configure(text="Downgrading application (GoodbyeDPI UI) ...")
        if os.path.exists(old_directory):
            try:
                total_files = sum(
                    [len(files) for r, d, files in os.walk(old_directory)]
                )
                index = 0
                for root, _, files in os.walk(old_directory):
                    for name in files:
                        s = os.path.join(root, name)
                        d = os.path.join(
                            self.unpack_directory, os.path.relpath(s, old_directory)
                        )
                        os.makedirs(os.path.dirname(d), exist_ok=True)
                        shutil.copy2(s, d)
                        index += 1
                        progress = index / total_files
                        self.progress_var.set(progress)
                        self.create_logs(f"Downgraded {name}")
                self.create_logs("Successfully downgraded to previous version.")
                self.progress_var.set(100)
                return True
            except Exception as ex:
                logger.error(
                    f"Error downgrading to previous version: {ex}", exc_info=True
                )
                messagebox.showerror(
                    "An error occurred",
                    error_message
                    + f"ERROR CODE: \n{error_names[self.finish_status]}/ERR_UNEXPECTED_ERROR",
                )
            return False
        else:
            self.create_logs(
                "No old version found to downgrade to. Operation cancelled."
            )
            messagebox.showerror(
                "An error occurred",
                error_message
                + f"ERROR CODE: \n{error_names[self.finish_status]}/ERR_NO_OLD_VERSION",
            )
            return False

    def update_program(self):
        self.create_logs("Starting extraction process")
        self.extract_zip()
        if self.finish_status == 0:
            self.create_logs("Extraction completed successfully.")
            self.launch_application()
        else:
            result = self.downgrade_program()
            self.create_logs("An error occurred during extraction.")

            if result:
                self.launch_application(error=True)
            else:
                self.protocol("WM_DELETE_WINDOW", self.safe_exit)

    def extract_zip(self):
        try:
            zip_file = self.zip_file_path
            extract_to = self.unpack_directory

            if not os.path.exists(extract_to):
                os.makedirs(extract_to)

            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                members = zip_ref.infolist()
                total_files = len(members)
                extracted_files = 0

                index = 0
                while index < len(members):
                    member = members[index]
                    member_path = member.filename
                    if member_path.startswith("goodbyeDPI UI/"):
                        relative_path = member_path[len("goodbyeDPI UI/") :]
                        if relative_path == "":
                            index += 1
                            continue

                        destination_path = os.path.join(extract_to, relative_path)
                        destination_dir = os.path.dirname(destination_path)

                        if relative_path.split("/")[
                            -1
                        ] in skip_files and os.path.exists(destination_path):
                            self.create_logs(f"Skipping {relative_path}")
                            index += 1
                            continue

                        if relative_path.split("/")[-1].split(".")[
                            -1
                        ] == "txt" and os.path.exists(destination_path):
                            self.create_logs(f"Skipping {relative_path}")
                            index += 1
                            continue

                        if not os.path.exists(destination_dir):
                            os.makedirs(destination_dir)

                        if member.is_dir():
                            if not os.path.exists(destination_path):
                                os.makedirs(destination_path)
                        else:
                            try:
                                with zip_ref.open(member) as source, open(
                                    destination_path, "wb"
                                ) as target:
                                    shutil.copyfileobj(source, target)
                            except OSError as pe:
                                print(pe.errno)
                                if "13" in str(pe.errno):
                                    self.create_logs(
                                        f"Permission denied when extracting {relative_path}"
                                    )
                                    self.create_logs(
                                        "Installation cancelled by unexpected error."
                                    )
                                    self.finish_status = 1
                                    return
                                else:
                                    self.create_logs(
                                        f"Error extracting {relative_path}: {ex}"
                                    )
                                    self.finish_status = 2
                                    return
                            except Exception as ex:
                                self.create_logs(
                                    f"Error extracting {relative_path}: {ex}"
                                )
                                self.finish_status = 3
                                return

                        extracted_files += 1
                        progress = extracted_files / total_files
                        self.progress_var.set(progress)
                        self.create_logs(f"Extracted {relative_path}")
                        self.update_idletasks()
                    index += 1

        except Exception as ex:
            logger.error(f"Extraction failed: {ex}", exc_info=True)
            self.finish_status = 4
        self.progress_var.set(100)

    def launch_application(self, error=False):
        param = "--after-failed-update" if error else "--after-patching"
        try:
            goodbye_dpi_exe = os.path.join(self.unpack_directory, "goodbyeDPI.exe")
            if os.path.exists(goodbye_dpi_exe):
                self.create_logs(f"Launching goodbyeDPI.exe with {param} parameter")
                subprocess.Popen(
                    [goodbye_dpi_exe, param], creationflags=subprocess.DETACHED_PROCESS
                )

                self.end = True
                self.after(0, self.safe_exit)

            else:
                raise FileNotFoundError(f"{goodbye_dpi_exe} not found")
        except Exception as ex:
            self.label.configure(text="Unexpected error happens")
            self.after(0, self.handle_launch_error, ex)

    def handle_launch_error(self, ex):
        messagebox.showerror("An error occurred", str(ex))
        logger.error(f"Failed to launch application: {ex}", exc_info=True)
        self.finish_status = 5
        self.exit_button.configure(state="normal")
        self.protocol("WM_DELETE_WINDOW", self.safe_exit)

    def safe_exit(self):
        self.destroy()
        self.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-directory-to-unpack", required=True, help="Directory to unpack to"
    )
    parser.add_argument(
        "-directory-to-zip", required=True, help="Path to zip file to unpack"
    )
    parser.add_argument(
        "-localize", required=False, help="Localization for UI (Outdated)"
    )
    args = parser.parse_args()

    zip_file_path = args.directory_to_zip
    unpack_directory = args.directory_to_unpack
    loc = args.localize

    logger.info("Starting UpdaterApp")
    close_procces()
    app = UpdaterApp(zip_file_path, unpack_directory)
    logger.info("App started successfully")
    app.mainloop()
