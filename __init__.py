import os
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml
from xd_common.services import Logging
from xd_common.utils import get_cmd_arguments


def load__yaml(
    file_path: str,
) -> Any:
    """Safe load is used with safe dump, load with dump"""
    with open(file_path, "r") as f:
        parsed = yaml.load(f, Loader=yaml.Loader)
    return parsed


def load_navigation_settings(f):
    with open(f, "r") as file:
        content = file.read()

    navigation_settings = yaml.load(content, Loader=yaml.FullLoader)
    return navigation_settings


def create_text_file(filename, text):
    # open the file for writing
    with open(filename, "w") as file:
        # write the text to the file
        file.write(text)

    # close the file when we're done
    file.close()


def append_to_text_file(filename, text):
    # open the file for appending
    with open(filename, "a") as file:
        # write the text to the end of file
        file.write(text)

    # close the file when we're done
    file.close()


class CatalogControlScript:
    """Initialization of YAML configuration"""

    def __init__(self, settings_path: str, projects_path: str) -> None:
        self.settings_path: Path = Path(settings_path)
        self.nav_settings = load_navigation_settings(settings_path)
        self.type = ""
        self.curr_folder = ""
        self.projects_path: Path = Path(projects_path)
        self.cwd = ""
        self.log_file = "YAML-configuration-log.txt"

    # def __str__(self) -> str:
    #     return f"-YAML- : \n\t{self.nav_settings}"

    def run(self) -> None:
        self.scanned_area_navigation()

    def get_nav_settings(self) -> Dict[str, List[Dict[str, Union[str, List[str]]]]]:
        """Getter for navigation settings"""
        return self.nav_settings

    def get_log_file(self) -> str:
        """Getter for returning"""
        return self.log_file

    def get_text_file_path(self) -> Any:
        """Getter that returns path to the log file"""
        return self.settings_path.parent / self.get_log_file()

    def set_configuration(
        self, configuration: Dict[str, List[Dict[str, Union[str, List[str]]]]]
    ) -> Any:
        """Setter that sets YAML"""
        self.configuration = configuration

    def set_log_file(self, log_file_name: str) -> None:
        """Setter that sets log file name"""
        self.log_file = log_file_name

    def set_cwd(self, directory: Any) -> None:
        """Setter that sets cwd"""
        self.cwd = self.projects_path / directory

    def find_value_in_dict_list(self, key: str) -> Any:
        """Searches for a value by key in a list of dictionaries."""
        values = []
        for nav_group in self.nav_settings["navigation_groups"]:
            nav_group = nav_group["navigation_group"]
            if key in nav_group:
                values.append(nav_group[key])
        return values

    def scanned_area_navigation(self) -> Any:
        """Getting navigation to the scanned area"""
        # get the text file path
        path_to_text_file = self.get_text_file_path()
        create_text_file(
            path_to_text_file,
            # TO DO ref
            f"NAVIGATION TYPE: {self.find_value_in_dict_list('type')[0]}\nYAML PATH: {self.settings_path}\nDIR WHERE SCRIPT OPERATES: {self.projects_path}\n",
        )
        # for configuration in self.get_configurations():
        for nav_group in self.nav_settings["navigation_groups"]:
            # self.set_configuration(configuration)
            # type_of_navigation = self.find_value_in_dict_list(
            #     self.nav_settings, "type"
            # )
            nav_group = nav_group["navigation_group"]
            match nav_group["type"]:  # noqa: E999  # type: ignore
                case "project_folder":
                    Logging.info("-SCANNING TYPE- : Scanning project folder")
                    file_path: Any = self.scan_valid_directories()
                case "models_in_project":
                    Logging.info("-SCANNING TYPE- : Scanning folders in project folder")

                    # get the list of valid directories based on the input parameters
                    valid_directories = self.scanning_folders()
                    head, tail = os.path.split(self.projects_path)
                    file_path: Any = self.scanning_folders_in_project(
                        head, tail, valid_directories
                    )
        return file_path

    def get_type_of_delimiter(self, type_of_value_string: str):
        """Getter that returns delimiter"""
        values = self.find_value_in_dict_list(type_of_value_string)[0]

        if "," in values:
            return ","

        if "-" in values:
            return "-"

        if "," not in values or "-" not in values:
            return ","
        else:
            pass

    def map_numbers_to_arr(self, key: str, delimiter: str) -> Any:
        return list(
            map(
                int,
                self.find_value_in_dict_list(key)[0].split(delimiter),
            )
        )

    def return_folder_number(self, folder: str, substring: str):
        """Return folder number based on substring string"""
        return int(folder[: folder.index(substring)])

    def split_numbers(self, delimiter: str, key: str) -> Any:
        """Return array of number from string according to delimiter"""
        values = []
        match delimiter:
            case ",":
                values = self.map_numbers_to_arr("except", delimiter)
                Logging.info(f"Excepting this individual folders: {values}")
                return values
            case "-":
                if key == "except":
                    values = self.map_numbers_to_arr("except", delimiter)
                    return values
                if key == "items":
                    values = self.map_numbers_to_arr("items", delimiter)
                    return values

    def get_values_from_dict(self) -> Any:
        """Get values from dictionary and insert the to the list."""
        values = []

        values.append(self.find_value_in_dict_list("range")[0])
        values.append(self.split_numbers(self.get_type_of_delimiter("items"), "items"))
        values.append(
            self.split_numbers(self.get_type_of_delimiter("except"), "except")
        )
        return values

    def logging(self) -> None:
        """Small backup of folders that has been scanned"""
        pass

    def sort_strings(self, arr) -> Any:
        """
        The sort_strings function takes an array of strings as input (arr)
        and uses the sort method to sort the array in place based on a key function
        """
        arr.sort(key=lambda x: int(x.split("__")[0]))
        return arr

    def array_to_string(self, array, row: bool = False) -> Any:
        """Function that takes array as an input and returns string"""
        string = ""
        if row:
            for item in array:
                string += f"\n\t{str(item)}"
        else:
            for item in array:
                string += f"{str(item)}, "
        return string

    def append_text_to_log_file(self, text: str) -> Any:
        """Append text to log file"""

        path_to_text_file = self.get_text_file_path()

        append_to_text_file(path_to_text_file, text)

    def initializing_text_file(self) -> None:
        """Initial info about YAML file"""

        # get the values from the dictionary
        dict_values = self.get_values_from_dict()

        items_values = f"{dict_values[1][0]} - {dict_values[1][1]}"

        if len(dict_values[2]) == 2:
            except_values = (
                f"{dict_values[2][0]} - {dict_values[2][1]}"
                if self.get_type_of_delimiter("except") == "-"
                else f"{dict_values[2][0]}, {dict_values[2][1]}"
            )
        else:
            except_values = f"{dict_values[2][0]}"

        Logging.info("-RANGE OF FOLDERS- :")
        Logging.info(f"\tRange of scanned items: {items_values}")
        Logging.info(f"\tRange of excepted values: {except_values}")

        self.append_text_to_log_file(
            f"YAML SETTINGS:\n\t range = {dict_values[0]}\n\t items = {items_values}\n\t except = {except_values}\n"
        )

    def scanning_folders(self) -> Any:
        """Scanning at the project level"""

        # # get the list of projects directories
        # projects_dir = os.listdir(self.projects_path)

        # get the values from the dictionary
        dict_values = self.get_values_from_dict()

        # get the list of valid directories based on the input parameters
        valid_directories = self.sort_strings(
            # self.get_valid_directories(projects_dir, dict_values)
            self.get_valid_directories(dict_values)
        )

        self.initializing_text_file()
        Logging.info(f"-VALID DIRECTORIES- : \n\t{valid_directories}")

        self.append_text_to_log_file(
            f"VALID DIRECTORIES:\t{self.array_to_string(valid_directories, True)}\n"
        )

        if self.find_value_in_dict_list("type")[0] == "models_in_project":
            self.append_text_to_log_file(
                f"PROJECT: {os.path.basename(self.projects_path)}\n"
            )

        return valid_directories

    def scan_valid_directories(self) -> Any:
        """Scan valid directories"""
        valid_directories = self.scanning_folders()

        for folder in valid_directories:
            self.curr_folder = folder
            self.set_cwd(self.curr_folder)
            mins_dir = os.listdir(self.cwd)
            Logging.info(f"\t -FOLDER- {folder}")
            self.append_text_to_log_file(f"PROJECT: {folder}\n")
            Logging.info(
                f"\t -PATHs- {self.scanning_folders_in_project(self.projects_path, folder, mins_dir)}"
            )

    # def get_valid_directories(self, projects_dir, dict_values):
    def get_valid_directories(self, dict_values):
        """Get the list of valid directories based on the input parameters"""

        valid_directories = []

        if dict_values[0] == "section":
            projects = dict_values[1]
            excluded_projects = dict_values[2]
            delimiter = self.get_type_of_delimiter("except")
            # for folder in projects_dir:
            for folder in self.projects_path.iterdir():
                curr_folder = str(folder.stem)
                if "__" not in curr_folder:
                    continue
                number_of_folder = self.return_folder_number(curr_folder, "_")
                if delimiter == ",":
                    if number_of_folder in range(projects[0], projects[1] + 1) and (
                        number_of_folder not in excluded_projects
                    ):
                        valid_directories.append(curr_folder)

                if delimiter == "-":
                    if number_of_folder in range(projects[0], projects[1] + 1) and (
                        number_of_folder
                        not in range(excluded_projects[0], excluded_projects[1] + 1)
                    ):
                        valid_directories.append(curr_folder)

        elif dict_values[0] == "all":
            excluded_projects = dict_values[2]
            delimiter = self.get_type_of_delimiter("except")
            for folder in self.projects_path.iterdir():
                curr_folder = str(folder.stem)
                if "__" not in curr_folder:
                    continue
                number_of_folder = self.return_folder_number(curr_folder, "_")
                if delimiter == ",":
                    if number_of_folder not in excluded_projects:
                        valid_directories.append(curr_folder)

                if delimiter == "-":
                    if number_of_folder not in range(
                        excluded_projects[0], excluded_projects[1] + 1
                    ):
                        valid_directories.append(curr_folder)

        return valid_directories  # zatím jen testovací vracení složek

    def scanning_folders_in_project(
        self,
        path: str,
        folder: str,
        mins_project: List[str],
    ) -> Any:
        """Scanning at the folder level of the given project"""
        paths_to_bl_file = []

        for min_project in mins_project:
            min_project_path = os.path.join(path, folder, min_project)
            if "__" not in os.path.basename(os.path.normpath(min_project_path)):
                continue
            self.append_text_to_log_file(f"\tMIN: {min_project}\n")
            if "3DModel" not in os.listdir(min_project_path):
                continue
            for item in os.listdir(os.path.join(min_project_path, "3DModel")):
                if ".blend" not in item:
                    continue
                paths_to_bl_file.append(Path(min_project_path, "3DModel", item))
                self.append_text_to_log_file(
                    f"\t\t PATH TO BLEND: {paths_to_bl_file[-1]}\n"
                )
        return paths_to_bl_file


if __name__ == "__main__":
    ccs = CatalogControlScript(
        # r"C:\Users\Michal\OneDrive\Precismo\xd_bl_sc_catalog_renderer\configurator.yaml",
        r"C:\Users\petr.krejci\Documents\GitHub\blender_scripts\xd_bl_sc_catalog_renderer\xd_bl_sc_catalog_renderer\Configs\navigation_settings.yaml",
        r"Z:\P",
    )
    # Logging.info(str(ccs))
    # Logging.info(f"Configurations: {ccs.get_configurations()}")
    # Logging.info(f"Configuration: {ccs.nav_settings}")

    # Logging.info(
    #     f"-TYPE- : {ccs.find_value_in_dict_list('type')}"
    # )
    # Logging.info(ccs.scanned_area_navigation())
    ccs.run()

# r"Z:\P"
# r"Z:\P\134__Sanitino_2023_02"
# "C:\Users\Michal\AppData\Local\Programs\Python\Python310\python.exe" "C:\Users\Michal\Documents\GitHub\blender_scripts\xd_bl_sc_catalog_renderer\xd_bl_sc_catalog_renderer\__init__.py" r"C:\Users\Michal\OneDrive\Precismo\xd_bl_sc_catalog_renderer\configurator.yaml" r"Z:\P"

# if __name__ == "__main__":
#     argv = get_cmd_arguments("Error", 1)
#     print(len(argv))
#     if len(argv) != 2:
#         print("Error")
#     else:
#         ccs = CatalogControlScript(argv[0], argv[1])
#         Logging.info(str(ccs))
#         Logging.info(f"Configurations: \n\t{ccs.get_configurations()}")
#         Logging.info(f"First configuration: \n\t{ccs.nav_settings}")
#         Logging.info(
#             f"-TYPE- : {ccs.find_value_in_dict_list('type')}"
#         )
#         Logging.info(ccs.scanned_area_navigation())

# HOW TO RUN THE SCRIPT

# "C:\Users\Michal\AppData\Local\Programs\Python\Python310\python.exe" "C:\Users\Michal\Documents\GitHub\blender_scripts\xd_bl_sc_catalog_renderer\xd_bl_sc_catalog_renderer\__init__.py" "C:\Users\Michal\OneDrive\Precismo\xd_bl_sc_catalog_renderer\configurator.yaml" "Z:\P"

# "C:\Users\Michal\AppData\Local\Programs\Python\Python310\python.exe" "C:\Users\Michal\Documents\GitHub\blender_scripts\xd_bl_sc_catalog_renderer\xd_bl_sc_catalog_renderer\__init__.py" "C:\Users\Michal\OneDrive\Precismo\xd_bl_sc_catalog_renderer\configurator.yaml" "Z:\P\134__Sanitino_2023_02"
