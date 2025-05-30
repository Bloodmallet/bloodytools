import datetime
import json
import logging
import json
import os
import requests
import subprocess
import sys
import typing
import threading
import time
import uuid as uuid_mod

# wow game data and simc input checks
from simc_support.simc_data import FightStyle
from simc_support.game_data.WowClass import WOWCLASSES
from typing import List, Union
from bloodytools.utils.request import request as r

logger = logging.getLogger(__name__)


class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: Union[Exception, str]) -> None:
        self.message = message


class AlreadySetError(Error):
    """Data is already present. Overwriting is not allowed."""

    pass


class NotSetYetError(Error):
    """Necessary data for the action was not set yet."""

    pass


class NotStartedYetError(Error):
    """Data generation is still in progress."""

    pass


class StillInProgressError(Error):
    """Data generation is still in progress."""

    pass


class SimulationError(Error):
    """Simulation failed."""

    pass


class SimulationWasNotRunError(Error):
    pass


class Simulation_Data:
    """Manages all META-information for a single simulation and the result.

    TODO: add max_time, vary_combat_length
    TODO: dumb the standard values down. There is no need for extended complexity here. The user/creator functions decide what they want/need. Simulation_data is simply a dumb data holder.
    """

    def __init__(
        self,
        base_filename: str = "",
        calculate_scale_factors: str = "0",
        default_actions: str = "1",
        default_skill: str = "1.0",
        executable: str = "",
        fight_style: str = "patchwerk",
        fixed_time: str = "1",
        iterations: str = "250000",
        log: str = "0",
        name: str = "",
        optimize_expressions: str = "1",
        ptr: str = "0",
        ready_trigger: str = "1",
        profile: dict = {},
        simc_arguments: typing.Union[typing.List[str], str] = [],
        target_error: str = "0.1",
        threads: str = "",
        remove_files: bool = True,
        generate_html: bool = False,
        comment: str = "",
        load_custom_fight_style: bool = False,
        load_custom_apl: bool = False,
    ) -> None:
        super(Simulation_Data, self).__init__()

        logger.debug("simulation_data initiated.")

        # simc setting to calculate scale factors (stat weights)
        if calculate_scale_factors == "0" or calculate_scale_factors == "1":
            self.calculate_scale_factors = calculate_scale_factors
        else:
            self.calculate_scale_factors = "0"
        # simc setting to manage default apl usage
        if default_actions in ["0", "1"]:
            self.default_actions = default_actions
        else:
            self.default_actions = "1"
        # simc setting to manage the accuracy of used apl lines (leave it at 1.0)
        try:
            self.default_skill = str(float(default_skill))
        except Exception as e:
            logger.error("{} -- Using default value instead.".format(e))
            self.default_skill = "1.0"
        # describes the location and type of the simc executable
        # if no value was set, determine a standard value
        if executable == "":
            if sys.platform == "win32":
                logger.debug(
                    "Setting Windows default value for executable. This might not work for your system."
                )
                self.executable = "../simc.exe"
            else:
                logger.debug(
                    "Setting Linux default value for executable. This might not work for your system."
                )
                self.executable = "../simc"
        else:
            try:
                self.executable = str(executable)
            except Exception as e:
                logger.error("{}".format(e))
                raise e
        # simc setting to determine the fight style
        if (
            fight_style == "custom"
            or fight_style in FightStyle.FIGHTSTYLES
            or FightStyle.CASTINGPATCHWERK in fight_style
        ):
            self.fight_style = fight_style
        else:
            logger.warning(
                "Unknown fight style '{}' -- Using default (patchwerk) value instead.".format(
                    fight_style
                )
            )
            self.fight_style = "patchwerk"
        # simc setting to enable/diable the fixed fight length
        if fixed_time == "0" or fixed_time == "1":
            self.fixed_time = fixed_time
        else:
            self.fixed_time = "1"
        # simc setting to determine the maximum number of run iterations
        #   (target_error and iterations determine the actually simulated
        #   iterations count)
        self.iterations = str(int(iterations.split(".")[0]))
        # simc setting to enable/disable a log file
        if log == "0" or log == "1":
            self.log = log
        else:
            self.log = "0"
        if base_filename:
            self.base_filename = base_filename
        else:
            self.base_filename = str(uuid_mod.uuid4())
        # optional name for the data
        if name:
            self.name = name
        else:
            self.name = self.base_filename
        # simc setting to enable/disable optimize expressions
        if optimize_expressions == "0" or optimize_expressions == "1":
            self.optimize_expressions = optimize_expressions
        else:
            self.optimize_expressions = "1"
        # simc setting to enable/disable ptr data
        if str(ptr) == "0" or str(ptr) == "1":
            self.ptr = str(ptr)
        else:
            self.ptr = "0"
        # simc setting to enable/disable ready_trigger
        if ready_trigger == "0" or ready_trigger == "1":
            self.ready_trigger = ready_trigger
        else:
            self.ready_trigger = "1"
        # specific data to be run, like talent combinations, specific gear or
        #   traits
        if isinstance(simc_arguments, list):
            self.simc_arguments = simc_arguments
        else:
            self.simc_arguments = [simc_arguments]
        # craft simc input for a proper profile
        if profile:
            self._raw_profile = profile
            # prepend created character profile input
            self.simc_arguments = (
                self.get_simc_arguments_from_profile(profile) + self.simc_arguments
            )

        # simc setting to determine the target_error
        try:
            self.target_error = str(float(target_error))
        except Exception as e:
            self.target_error = "0.1"
        # simc setting to determine the number of used threads, empty string uses
        #   all available
        if type(threads) == int or type(threads) == str or type(threads) == float:
            try:
                self.threads = str(int(float(threads)))
            except Exception as e:
                self.threads = ""
        else:
            self.threads = ""
        self.remove_files = remove_files
        self.generate_html = generate_html
        # optional comment about the profile
        self.comment = comment
        self.custom_fight_style: str = ""
        if load_custom_fight_style:
            with open("custom_fight_style.txt") as f:
                self.custom_fight_style = f.read()
        self.custom_apl: str = ""
        if load_custom_apl:
            with open("custom_apl.txt") as f:
                self.custom_apl = f.read()

        # set independent default values
        # creation time of the simulation object
        self.so_creation_time = datetime.datetime.utcnow()
        # simulation dps result
        self.dps: int = -1
        # flag to know whether data was generated with external simulation function
        self.external_simulation = False
        # simulation full report (command line print out)
        self.full_report: str = ""
        self.json_data: typing.Optional[dict] = None
        # simulation end time
        self.so_simulation_end_time: typing.Optional[datetime.datetime] = None
        # simulation start time
        self.so_simulation_start_time: typing.Optional[datetime.datetime] = None

    def get_simc_arguments_from_profile(self, profile: dict) -> typing.List[str]:
        if not profile.get("character", None):  #  or not profile.get("items", None):
            raise ValueError(
                "When providing a profile it must have 'character' and 'items' keys."
            )

        character: typing.List[str] = []
        for name in profile["character"]:
            if name != "class":
                character.append("{}={}".format(name, profile["character"][name]))
            else:
                character.append(
                    "{}=baseline".format(profile["character"][name].replace("_", ""))
                )

        items = []
        if profile.get("items", None):
            for slot in profile["items"]:
                if profile["items"][slot]:
                    string = "{}=,".format(slot)
                    string += ",".join(
                        "{}={}".format(key, value)
                        for key, value in profile["items"][slot].items()
                    )
                    items.append(string)

        return character + items

    def is_equal(self, simulation_instance: "Simulation_Data") -> bool:
        """Determines if the current and given simulation_data share the
        same base. The following attributes are considered base:
        calculate_scale_factors, default_actions, default_skill,
        executable, fight_style, fixed_time, iterations, log,
        optimize_expressions, ptr, ready_trigger, target_error, threads

        Arguments:
            simulation_instance {simulation_data} -- Instance of simulation_data

        Returns:
            bool -- True if equallity between mentioned data is guaranteed.
        """

        if not isinstance(simulation_instance, Simulation_Data):
            raise TypeError(
                f"Expected Simulation_Data, got <{type(simulation_instance)}> instead."
            )

        if self.calculate_scale_factors != simulation_instance.calculate_scale_factors:
            return False
        if self.default_actions != simulation_instance.default_actions:
            return False
        if self.default_skill != simulation_instance.default_skill:
            return False
        if self.executable != simulation_instance.executable:
            return False
        if self.fight_style != simulation_instance.fight_style:
            return False
        if self.fixed_time != simulation_instance.fixed_time:
            return False
        if self.iterations != simulation_instance.iterations:
            return False
        if self.log != simulation_instance.log:
            return False
        if self.optimize_expressions != simulation_instance.optimize_expressions:
            return False
        if self.ptr != simulation_instance.ptr:
            return False
        if self.ready_trigger != simulation_instance.ready_trigger:
            return False
        if self.target_error != simulation_instance.target_error:
            return False
        if self.threads != simulation_instance.threads:
            return False
        return True

    def get_dps(self) -> int:
        """Get the dps of the simulation_instance.

        Returns:
            int -- dps
        """
        return self.dps

    def set_dps(self, dps: Union[int, float, str], external: bool = True) -> None:
        """Set dps.

        Arguments:
            dps {int} -- simulated dps value

        Keyword Arguments:
            external {bool} -- special flag to know whether the core simulation function was used (default: {True})

        Raises:
            TypeError -- Raised if external was not {bool}.
            AlreadySetError -- Raised if dps was already set.
            e -- Raised if casting dps to {int} fails.
        """
        # set external_simulation flag, defaults to True, so external simulations
        #  don't need to pay attention to this
        if type(external) == bool:
            self.external_simulation = external
        else:
            raise TypeError

        # raise AlreadySetError if one tries to overwrite previously set data
        if self.dps > -1:
            raise AlreadySetError(
                "Profile '{}' already had its dps value set to {}.".format(
                    self.name, self.get_dps()
                )
            )

        try:
            # slightly more robust than simply cast to int, due to possible float
            # numbers as strings
            self.dps = int(float(dps))
        except Exception as e:
            raise e
        logger.debug("Set DPS of profile '{}' to {}.".format(self.name, self.get_dps()))

    def get_simulation_duration(self) -> datetime.timedelta:
        """Return the simulation duration.

        Raises:
            NotDoneYetError -- Raised if simulation is still in progress.

        Returns:
            datetime.datetime -- Start time - End time
        """

        if self.so_simulation_start_time and self.so_simulation_end_time:
            return self.so_simulation_end_time - self.so_simulation_start_time
        elif self.so_simulation_start_time and not self.so_simulation_end_time:
            raise StillInProgressError(
                "Simulation end time is not set yet. Simulation is probably still in progress."
            )
        else:
            raise NotStartedYetError("Simulation didn't start yet.")

    def set_full_report(self, report: str) -> None:
        """Saves the report (simulation cmd output) to full_report.

        Arguments:
            report {str} -- The cmd output of the simulation.

        Raises:
            TypeError -- Raised if report was not a string.
        """
        if type(report) == str:
            self.full_report = report
        else:
            raise TypeError(
                "Report of type '{}'' found but string was expected.".format(
                    type(report)
                )
            )

    def set_simulation_end_time(self) -> None:
        """Set so_simulation_end_time.

        Raises:
            AlreadySetError -- Raised if the simulation end time was already set.
        """
        if not self.so_simulation_end_time:
            self.so_simulation_end_time = datetime.datetime.utcnow()
        else:
            raise AlreadySetError(
                "Simulation end time was already set. Setting it twice is not allowed."
            )

    def set_simulation_start_time(self) -> None:
        """Set so_simulation_start_time. Can be done multiple times."""
        self.so_simulation_start_time = datetime.datetime.utcnow()

    def simulate(self) -> int:
        """Simulates the data using SimulationCraft. Resulting dps are saved and returned.

        Raises:
            FileNotFoundError -- Raised if the simulation didn't start due to the executable not being found.
            SimulationError -- Raised if the simulation failes multiple times.

        Returns:
            int -- DPS of the simulation
        """
        # temporary file names
        self.filename = "{}.simc".format(self.base_filename)
        self.json_filename = "{}.json".format(self.base_filename)
        self.html_filename = "{}.html".format(self.base_filename)

        if (
            FightStyle.CASTINGPATCHWERK in self.fight_style
            and FightStyle.CASTINGPATCHWERK != self.fight_style
        ):
            simc_fight_style = FightStyle.CASTINGPATCHWERK
            special_remark = "desired_targets=" + self.fight_style[-1]
        else:
            simc_fight_style = self.fight_style
            special_remark = ""

        argument = [self.executable]
        argument.append("json=" + self.json_filename)
        if self.generate_html:
            argument.append("html=" + self.html_filename)
        argument.append("iterations=" + self.iterations)
        argument.append("target_error=" + self.target_error)
        argument.append("fight_style=" + simc_fight_style)
        # this feature should only be used by single profiles anyway and augmentation evokers are special
        argument.append("single_actor_batch=0")
        argument.append("profileset_metric=raid_dps")
        argument.append(special_remark)
        argument.append("fixed_time=" + self.fixed_time)
        argument.append("optimize_expressions=" + self.optimize_expressions)
        argument.append("default_actions=" + self.default_actions)
        argument.append("log=" + self.log)
        argument.append("default_skill=" + self.default_skill)
        if self.ptr == "1":
            argument.append("ptr=" + self.ptr)
        argument.append("threads=" + self.threads)

        if self.comment:
            argument.append("# " + self.comment)

        for simc_argument in self.simc_arguments:
            argument.append(simc_argument)
        argument.append(f'name="{self.name}"')

        argument.append("ready_trigger=" + self.ready_trigger)

        # drop empty, pseudo empty, and comment args
        argument = [a for a in argument if a and a.strip() and a.strip()[0] != "#"]

        logger.debug(f"Starting simulation using the following args: '{argument}'")

        fail_counter = 0
        simulation_output: typing.Optional[subprocess.CompletedProcess] = None
        # should prevent additional empty windows popping up...on win32 systems without breaking different OS
        if sys.platform == "win32":
            # call simulationcraft in the background. Save output for processing
            startupinfo = subprocess.STARTUPINFO()  # type: ignore
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore

            while not hasattr(self, "success") and fail_counter < 5:
                simulation_output = subprocess.run(
                    argument,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    startupinfo=startupinfo,
                )

                if simulation_output.returncode != 0:
                    fail_counter += 1
                else:
                    self.success = True

        else:
            while not hasattr(self, "success") and fail_counter < 5:
                simulation_output = subprocess.run(
                    argument,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                )

                if simulation_output.returncode != 0:
                    fail_counter += 1
                else:
                    self.success = True

        if simulation_output is None:
            raise SimulationWasNotRunError(
                "Programming logic allowed a simulation to be skipped. Aborting"
            )

        if fail_counter >= 5:
            logger.error("ERROR: An Error occured during simulation.")
            logger.error("args: " + str(simulation_output.args))
            logger.error("stdout: " + str(simulation_output.stdout))
            self.error = simulation_output.stdout
            raise SimulationError(self.error)

        # save output
        self.set_full_report(simulation_output.stdout)

        # parse results from generated json file
        with open(self.json_filename, "r") as json_file:
            data = json.load(json_file)
        if data and isinstance(data, dict):
            self.json_data = data
        if self.json_data:
            self.set_json_data(self.json_data)

        # remove json file after parsing
        if self.json_filename is not None and self.remove_files:
            os.remove(self.json_filename)
        if self.remove_files and self.generate_html:
            os.remove(self.html_filename)

        self.set_simulation_end_time()

        return self.get_dps()

    def copy(self):
        """Create an identical, independent copy of the current Simulation_Data. WARNING: The name is identical too! You'll need to update it manually!

        Returns:
            Simulation_Data -- Deep copy of the current Simulation_Data
        """
        new_sim_data = Simulation_Data(
            calculate_scale_factors=self.calculate_scale_factors,
            default_actions=self.default_actions,
            default_skill=self.default_skill,
            executable=self.executable,
            fight_style=self.fight_style,
            fixed_time=self.fixed_time,
            iterations=self.iterations,
            log=self.log,
            name=self.name,
            optimize_expressions=self.optimize_expressions,
            ptr=self.ptr,
            ready_trigger=self.ready_trigger,
            simc_arguments=list(self.simc_arguments).copy(),
            target_error=self.target_error,
            threads=self.threads,
            comment=self.comment,
            remove_files=self.remove_files,
            generate_html=self.generate_html,
        )

        new_sim_data.so_creation_time = self.so_creation_time
        new_sim_data.dps = self.dps
        new_sim_data.external_simulation = self.external_simulation
        new_sim_data.full_report = self.full_report
        new_sim_data.so_simulation_end_time = self.so_simulation_end_time
        new_sim_data.so_simulation_start_time = self.so_simulation_start_time

        return new_sim_data

    def set_json_data(self, data: dict) -> None:
        """Set simulation results from json report to profiles.

        Arguments:
          data {dict} -- json data from SimulationCraft json report
        """
        logger.debug("Setting dps for baseprofile.")
        # self.set_dps(
        #     data["sim"]["players"][0]["collected_data"]["dps"]["mean"],
        #     external=False,
        # )
        self.set_dps(
            data["sim"]["statistics"]["raid_dps"]["mean"],
            external=False,
        )
        logger.debug("Set dps for profile.")


class Simulation_Group:
    """simulator_group holds one or multiple simulation_data as profiles and can simulate them either serialized or parallel. Parallel uses SimulationCrafts own profilesets feature. Dps values are saved in the simulation_data."""

    def __init__(
        self,
        simulation_instance: Union[None, Simulation_Data, List[Simulation_Data]] = None,
        name: str = "",
        base_filename: str = "",
        threads: str = "",
        profileset_work_threads: str = "",
        executable: str = "",
        remove_files: bool = True,
        generate_html: bool = False,
    ) -> None:
        logger.debug("simulation_group initiated.")

        self.name = name
        if base_filename:
            self.base_filename: str = base_filename
        else:
            self.base_filename = str(uuid_mod.uuid4())
        self.filename: str = ""
        self.json_filename: str = ""
        self.html_filename: str = ""
        self.json_data: typing.Optional[dict] = None
        self.threads = threads
        self.remove_files = remove_files
        self.generate_html = generate_html
        # simulationcrafts own multithreading
        self.profileset_work_threads = profileset_work_threads
        self.executable = executable
        self.profiles: List[Simulation_Data]
        self.sg_simulation_start_time: typing.Optional[datetime.datetime] = None
        self.sg_simulation_end_time: typing.Optional[datetime.datetime] = None

        # check input types
        if not simulation_instance:
            self.profiles = []
        elif type(simulation_instance) == list:
            correct_type = True
            for data in simulation_instance:  # type: ignore
                if type(data) != Simulation_Data:
                    correct_type = False
            if correct_type:
                self.profiles = simulation_instance  # type: ignore
            else:
                raise TypeError(
                    "At least one item of simulation_instance list had a wrong type. Expected simulation_data."
                )
        elif type(simulation_instance) == Simulation_Data:
            self.profiles = [simulation_instance]  # type: ignore
        else:
            raise TypeError(
                "Simulation_instance has wrong type '{}'. Expected list or single simulation_data.".format(
                    type(simulation_instance)
                )
            )

        # check input values
        if not self.selfcheck():
            raise ValueError("Selfcheck of the simulation_group failed.")

        self.simulation_output = ""

    def selfcheck(self) -> bool:
        """Compares the base content of all profiles. All profiles need to
            have the same values in each standard field (__init__ of
            simulation_data).

        Returns:
            bool -- True if all data is coherent, False otherwise.
        """

        i = 0
        while i + 1 < len(self.profiles):
            if not self.profiles[i].is_equal(self.profiles[i + 1]):
                return False
            i += 1

        return True

    def set_simulation_end_time(self) -> None:
        """Set sg_simulation_end_time.

        Raises:
            AlreadySetError -- Raised if the simulation end time was already set.
        """
        if not self.sg_simulation_end_time:
            self.sg_simulation_end_time = datetime.datetime.utcnow()
        else:
            raise AlreadySetError(
                "Simulation end time was already set. Setting it twice is not allowed."
            )

    def set_simulation_start_time(self) -> None:
        """Set sg_simulation_start_time. Can be done multiple times."""
        self.sg_simulation_start_time = datetime.datetime.utcnow()

    def monitor_simulation(self, process) -> None:
        """Monitors and prints the most recent output from the simc subprocess to command line. Additionally saves the line to simulation_output of the simulation_group.

        Arguments:
            process {subprocess.Popen} -- the ongoing simulation subprocess

        Returns:
            None --
        """
        self.simulation_output = ""

        for line in iter(process.stdout.readline, ""):
            # shorten output, this console print is not intended to replace the log
            output_length = 100

            print_line = line.strip()
            print_line = print_line[:output_length]
            logger.debug(print_line)
            # save line for later use
            self.simulation_output += print_line + "\n"
            # remove previously printed line
            print(" " * output_length, end="\r", flush=True)
            # write current output
            print("{}".format(print_line), end="\r", flush=True)  # kill line break

    def simulate(self) -> bool:
        """Triggers the simulation of all profiles.

        Raises:
            e -- Raised if simulation of a single profile failed.
            NotSetYetError -- No data available to simulate.

        Returns:
            bool -- True if simulations ended successfully.
        """
        return self.simulate_with_profilesets()

    def write_profileset_file(
        self, fight_style: str, special_remark: str, local_simulation: bool = True
    ) -> None:
        # write arguments to file
        with open(self.filename, "w") as f:
            # write the equal values to file
            # local
            if local_simulation:
                f.write("json={}\n".format(self.json_filename))
                if self.generate_html:
                    f.write("html={}\n".format(self.html_filename))
                f.write("log={}\n".format(self.profiles[0].log))
                f.write(
                    "calculate_scale_factors={}\n".format(
                        self.profiles[0].calculate_scale_factors
                    )
                )
                if (
                    self.profiles[0]._raw_profile["character"]["class"] == "evoker"
                    and self.profiles[0]._raw_profile["character"]["spec"]
                    == "augmentation"
                ):
                    f.write("profileset_metric={}\n".format(",".join(["raid_dps"])))
                else:
                    f.write("profileset_metric={}\n".format(",".join(["dps"])))
                f.write(
                    "calculate_scale_factors={}\n".format(
                        self.profiles[0].calculate_scale_factors
                    )
                )
                f.write("threads={}\n".format(self.threads))
                f.write(
                    "profileset_work_threads={}\n".format(self.profileset_work_threads)
                )

            # general
            f.write("default_actions={}\n".format(self.profiles[0].default_actions))
            f.write("default_skill={}\n".format(self.profiles[0].default_skill))
            f.write(f"fight_style={fight_style}\n")
            f.write(f"{special_remark}\n")
            f.write("fixed_time={}\n".format(self.profiles[0].fixed_time))
            f.write("iterations={}\n".format(self.profiles[0].iterations))
            f.write(
                "optimize_expressions={}\n".format(
                    self.profiles[0].optimize_expressions
                )
            )
            if int(self.profiles[0].ptr) == 1:
                f.write("ptr={}\n".format(self.profiles[0].ptr))
            f.write("target_error={}\n".format(self.profiles[0].target_error))

            # write first profile
            logger.debug("simc_arguments of first profile of simulation_group")
            logger.debug(self.profiles[0].simc_arguments)
            if self.profiles[0].comment:
                f.write(f"# {self.profiles[0].comment}\n")
            for argument in self.profiles[0].simc_arguments:
                f.write("{}\n".format(argument))
            f.write('name="{}"\n'.format(self.profiles[0].name))

            f.write("\n# custom apl\n")
            if self.profiles[0].custom_apl:
                f.write(self.profiles[0].custom_apl)
            else:
                f.write("# none\n")

            f.write("\n# Profileset start\n")
            # or else in wrong scope
            f.write("ready_trigger={}\n".format(self.profiles[0].ready_trigger))

            # write all specific arguments to file
            for profile in self.profiles[1:]:
                simc_wow_class_names = [
                    wow_class.simc_name.replace("_", "") for wow_class in WOWCLASSES
                ]
                # remove class declaration, profilesets are allergic
                filtered_arguments = [
                    arg
                    for arg in profile.simc_arguments
                    if arg.split("=")[0] not in simc_wow_class_names
                ]
                # remove comments
                filtered_arguments = [
                    arg for arg in filtered_arguments if not arg.startswith("#")
                ]

                unique_arguments: typing.Dict[str, str] = {}
                for arg in filtered_arguments:
                    identifier = arg.split("=")[0]
                    unique_arguments[identifier] = arg

                if profile.comment:
                    f.write(f"# {profile.comment}\n")
                for argument in unique_arguments.values():
                    f.write(
                        'profileset."{profile_name}"+={argument}\n'.format(
                            profile_name=profile.name,
                            argument=argument,
                        )
                    )

                # add iterations hack
                # if not local_simulation:
                #     f.write(
                #         'profileset."{profile_name}"+=iterations={iterations}\n'.format(
                #             profile_name=profile.name,
                #             iterations=self.profiles[0].iterations,
                #         )
                #     )

            # custom fight style
            f.write("\n# custom fight style\n")
            if self.profiles[0].custom_fight_style:
                f.write(self.profiles[0].custom_fight_style)
            else:
                f.write("# none")

        with open(self.filename, "r") as f:
            logger.debug(f.read())

    def write_error_to_file(self) -> None:
        with open(self.filename, "a") as f:
            f.write("########################################")
            f.write("# FAILED PROFILE!\n")
            f.write("# SimulationCraft Output:")
            f.write(self.error)

    def simulate_with_profilesets(self) -> bool:
        """Triggers the simulation of all profiles.

        Raises:
            e -- Raised if simulation of a single profile failed.
            NotSetYetError -- No data available to simulate.

        Returns:
            bool -- True if simulations ended successfully.
        """
        if not self.profiles:
            return False

        self.set_simulation_start_time()

        if len(self.profiles) == 1:
            # if only one profile is in the group this profile is simulated normally
            try:
                self.profiles[0].simulate()
            except Exception as e:
                raise e

        elif len(self.profiles) >= 2:
            # check for a path to executable
            if not self.executable:
                raise ValueError(
                    "No path_to_executable was set. Simulation can't start."
                )

            # write data to file, create file name
            if self.filename:
                raise AlreadySetError(
                    "Filename '{}' was already set for the simulation_group. You probably tried to simulate the same group twice.".format(
                        self.filename
                    )
                )

            # temporary file names
            self.filename = "{}.simc".format(self.base_filename)
            self.json_filename = "{}.json".format(self.base_filename)
            self.html_filename = "{}.html".format(self.base_filename)

            if (
                FightStyle.CASTINGPATCHWERK in self.profiles[0].fight_style
                and FightStyle.CASTINGPATCHWERK != self.profiles[0].fight_style
            ):
                simc_fight_style = FightStyle.CASTINGPATCHWERK
                special_remark = "desired_targets=" + self.profiles[
                    0
                ].fight_style.replace(FightStyle.CASTINGPATCHWERK, "")
            else:
                simc_fight_style = self.profiles[0].fight_style
                special_remark = ""

            # write arguments to file
            self.write_profileset_file(
                fight_style=simc_fight_style, special_remark=special_remark
            )

            logger.info(f"Simulating {len(self.profiles)} profiles")

            # counter of failed simulation attempts
            fail_counter = 0
            simulation_output: typing.Optional[subprocess.Popen] = None
            # should prevent additional empty windows popping up...on win32 systems without breaking different OS
            if sys.platform == "win32":
                # call simulationcraft in the background. Save output for processing
                startupinfo = subprocess.STARTUPINFO()  # type: ignore
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore

                while not hasattr(self, "success") and fail_counter < 5:
                    try:
                        simulation_output = subprocess.Popen(
                            [self.executable, self.filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                            startupinfo=startupinfo,
                        )
                    except FileNotFoundError as e:
                        raise e

                    watcher = threading.Thread(
                        target=self.monitor_simulation,
                        args=(simulation_output,),
                    )
                    watcher.start()

                    simulation_output.wait()
                    watcher.join()

                    if simulation_output.returncode != 0:
                        fail_counter += 1
                    else:
                        self.success = True

            else:
                while not hasattr(self, "success") and fail_counter < 5:
                    try:
                        simulation_output = subprocess.Popen(
                            [self.executable, self.filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                        )
                    except FileNotFoundError as e:
                        raise e

                    watcher = threading.Thread(
                        target=self.monitor_simulation,
                        args=(simulation_output,),
                    )
                    watcher.start()

                    simulation_output.wait()
                    watcher.join()

                    if simulation_output.returncode != 0:
                        fail_counter += 1
                    else:
                        self.success = True

            if simulation_output is None:
                raise SimulationWasNotRunError(
                    "Programming logic allowed a simulation to be skipped. Aborting"
                )

            # handle broken simulations
            if fail_counter >= 5:
                logger.debug("ERROR: An Error occured during simulation.")
                logger.debug("args: " + str(simulation_output.args))
                logger.debug("stdout: " + str(self.simulation_output))
                logger.debug(
                    "'name=value error's can occur when relative paths are wrong. They need to be relative paths from <bloodytools> to your SimulationCraft directory."
                )
                self.error = self.simulation_output

                # add error to remaining profile
                self.write_error_to_file()

                raise SimulationError(self.error)

            logger.debug(self.simulation_output)

            # get dps of the first profile
            baseline_result = False
            profileset_results = False

            # parse results from generated json file
            with open(self.json_filename, "r") as json_file:
                data = json.load(json_file)
            if data and isinstance(data, dict):
                self.json_data = data
            if self.json_data:
                self.set_dps_from_profiletset_data(self.json_data)

            # remove profilesets file
            if self.remove_files:
                os.remove(self.filename)
                self.filename = ""
                # remove json file after parsing
                if self.json_filename:
                    os.remove(self.json_filename)
                if self.generate_html:
                    os.remove(self.html_filename)

        else:
            raise NotSetYetError(
                "No profiles were added to this simulation_group yet. Nothing can be simulated."
            )

        self.set_simulation_end_time()

        if self.sg_simulation_end_time and self.sg_simulation_start_time:
            logger.debug(
                "Simulation time: {}.".format(
                    self.sg_simulation_end_time - self.sg_simulation_start_time
                )
            )

        return True

    def simulate_with_raidbots(self, apikey) -> str:
        """Triggers the simulation of all profiles using Raidbots.com API.

        Raises:
            e -- Raised if simulation of a single profile failed.
            NotSetYetError -- No data available to simulate.

        Returns:
            bool, str -- Returns the git hash as a string if simulations ended successfully, otherwise False.
        """
        simc_hash = ""

        if not hasattr(self, "session"):
            self.session = requests.Session()

        if not self.profiles:
            return ""

        self.set_simulation_start_time()

        # write data to file, create file name
        if self.filename:
            raise AlreadySetError(
                "Filename '{}' was already set for the simulation_group. You probably tried to simulate the same group twice.".format(
                    self.filename
                )
            )

        if (
            FightStyle.CASTINGPATCHWERK in self.profiles[0].fight_style
            and FightStyle.CASTINGPATCHWERK != self.profiles[0].fight_style
        ):
            simc_fight_style = FightStyle.CASTINGPATCHWERK
            special_remark = "desired_targets=" + self.profiles[0].fight_style[-1]
        else:
            simc_fight_style = self.profiles[0].fight_style
            special_remark = ""

        self.filename = self.base_filename + ".simc"

        self.write_profileset_file(
            fight_style=simc_fight_style,
            special_remark=special_remark,
            local_simulation=False,
        )

        # create advanced input string
        raidbots_advancedInput = ""
        with open(self.filename, "r") as f:
            for line in f:
                raidbots_advancedInput += line

        logger.debug(raidbots_advancedInput)

        raidbots_response = r(
            "https://www.raidbots.com/sim",
            apikey=apikey,
            data=raidbots_advancedInput,
            session=self.session,
        )

        logger.debug(raidbots_response)

        raidbots_sim_id = raidbots_response["simId"]

        # monitor simulation progress
        logger.info("Simulation of {} is underway. Please wait".format(self.name))

        time.sleep(4)

        # simulation progress
        try:
            progress = r(
                f"https://www.raidbots.com/api/job/{raidbots_sim_id}",
                session=self.session,
            )
        except Exception as e:
            logger.error(e)
            progress = {"job": {"state": ""}, "retriesRemaining": 8}

        # not a proper back off in this case, due to the progress of a simulation not being properly monitorable with exponential backoff
        backoff = 0
        while not progress["job"]["state"] == "complete" and 10 * backoff < 3600:
            # backoff
            time.sleep(10)
            backoff += 1

            try:
                progress = r(
                    f"https://www.raidbots.com/api/job/{raidbots_sim_id}",
                    session=self.session,
                )
            except requests.exceptions.HTTPError as e:
                logger.error(e)
                backoff += 360

            logger.info(
                "{} progress {}%".format(self.name, progress["job"]["progress"])
            )
            logger.debug(progress)

            if (
                progress["job"]["state"] == "failed"
                and int(progress["retriesRemaining"]) <= 0
            ):
                break

        if (
            progress["job"]["state"] == "failed"
            and int(progress["retriesRemaining"]) <= 0
        ):
            raise SimulationError("Simulation failed. No Retries possible.")

        logger.info("Simulating {} is done. Fetching data.".format(self.name))

        # simulation is done, get data
        raidbots_data = r(
            f"https://www.raidbots.com/reports/{raidbots_sim_id}/data.json",
            session=self.session,
        )

        logger.info("Fetching data for {} succeeded.".format(self.name))
        logger.debug(f"{raidbots_data}")

        # if too many profilesets were simulated, get the full json
        if "hasFullJson" in raidbots_data["simbot"]:
            if raidbots_data["simbot"]["hasFullJson"]:
                # simulation is done, get data
                raidbots_data = r(
                    f"https://www.raidbots.com/reports/{raidbots_sim_id}/data.full.json",
                    session=self.session,
                )
                logger.info("Fetching data for {} succeeded.".format(self.name))
                logger.debug(f"{raidbots_data}")

        # if simulation failed
        if progress["job"]["state"] == "failed":
            logger.info("Job failed. Collecting information.")

            raidbots_input = r(
                f"https://www.raidbots.com/reports/{raidbots_sim_id}/input.txt",
                session=self.session,
            )

            logger.debug("Fetching input data for {} succeeded.".format(self.name))
            logger.debug(raidbots_input)

            raidbots_output = r(
                f"https://www.raidbots.com/reports/{raidbots_sim_id}/output.txt",
                session=self.session,
            )
            logger.debug("Fetching output data for {} succeeded.".format(self.name))
            logger.debug(raidbots_output)

            with open("{}.error".format(raidbots_sim_id), "w") as f:
                f.write("############## INPUT #############\n")
                f.write(json.dumps(raidbots_advancedInput))
                f.write("\n\n############# RECEIVED ###########\n")
                f.write(json.dumps(raidbots_input))
                f.write("\n\n############# OUTPUT #############\n")
                f.write(json.dumps(raidbots_output))

                try:
                    f.write(
                        "\n\n############## DATA ##############\n{}".format(
                            json.dumps(raidbots_data, sort_keys=True, indent=4)
                        )
                    )
                except Exception:
                    f.write(
                        "\n\n############## DATA ##############\nNo data available.\n"
                    )

            raise SimulationError(
                "Simulating with Raidbots failed. Please check out {}.error file.".format(
                    raidbots_sim_id
                )
            )

        if self.remove_files:
            # remove profilesets file
            os.remove(self.filename)
            self.filename = ""

        try:
            simc_hash = raidbots_data["git_revision"]
        except Exception:
            logger.error("'git_revision' not found in raidbots answer.")
            simc_hash = ""

        # set basic profile dps
        self.set_dps_from_profiletset_data(raidbots_data)

        self.set_simulation_end_time()

        if self.sg_simulation_end_time and self.sg_simulation_start_time:
            logger.debug(
                "Simulation time: {}.".format(
                    self.sg_simulation_end_time - self.sg_simulation_start_time
                )
            )

        return simc_hash

    def set_dps_from_profiletset_data(self, profileset_data: dict) -> None:
        """Set simulation results from json report to profiles.

        Arguments:
          data {dict} -- json data from SimulationCraft json report
        """
        logger.debug("Setting dps for baseprofile.")
        self.set_dps_of(
            profileset_data["sim"]["players"][0]["name"],
            profileset_data["sim"]["statistics"]["raid_dps"]["mean"],
        )
        logger.debug("Set dps for baseprofile.")

        if "profilesets" in profileset_data["sim"]:
            for profile in profileset_data["sim"]["profilesets"]["results"]:
                logger.debug("Setting dps for {}".format(profile["name"]))
                self.set_dps_of(profile["name"], profile["mean"])

    def add(self, simulation_instance: Simulation_Data) -> bool:
        """Add another simulation_instance object to the group.

        Arguments:
            simulation_instance {simulation_data} -- instance of simulation_data

        Raises:
            e -- Raised if appending a list element files.
            TypeError -- Raised if simulation_instance is not of type simulation_data

        Returns:
            bool -- True if added.
        """
        if type(simulation_instance) == Simulation_Data:
            try:
                self.profiles.append(simulation_instance)
            except Exception as e:
                raise e
            else:
                return True
        else:
            raise TypeError(
                "Simulation_instance has wrong type '{}' (needed simulation_data).".format(
                    type(simulation_instance)
                )
            )

    def get_dps_of(self, profile_name: str) -> int:
        """Returns DPS of the wanted/named profile.

        Arguments:
            profile_name {str} -- Name of the profile. e.g. 'baseline'

        Returns:
            int -- dps
        """

        for profile in self.profiles:
            if profile.name == profile_name:
                return profile.get_dps()
        raise KeyError(
            "Profile_name '{}' wasn't found in the simulation_group.".format(
                profile_name
            )
        )

    def set_dps_of(self, profile_name: str, dps: Union[int, float, str]) -> bool:
        try:
            for profile in self.profiles:
                if profile.name == profile_name:
                    profile.set_dps(dps, external=False)
        except Exception as e:
            logger.error(
                "Setting dps for profile {} failed. {}".format(profile_name, e)
            )
            return False
        else:
            return True
