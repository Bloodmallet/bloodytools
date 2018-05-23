#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# date data
import datetime
# wow game data and simc input checks
from simc_support import simc_checks as simc_checks
# required for file existance check
import os
# sys operations and data
import sys
from typing import Union, List
import uuid
import logging

import subprocess


class Error(Exception):
  """Base class for exceptions in this module.
  """

  def __init__(self, message: Union[Exception, str]) -> None:
    self.message = message


class AlreadySetError(Error):
  """Data is already present. Overwriting is not allowed.
  """

  pass


class NotSetYetError(Error):
  """Necessary data for the action was not set yet.
  """

  pass


class NotStartedYetError(Error):
  """Data generation is still in progress.
  """

  pass


class StillInProgressError(Error):
  """Data generation is still in progress.
  """

  pass


class SimulationError(Error):
  """Simulation failed.
  """

  pass


class Simulation_Data():
  """Manages all META-information for a single simulation and the result.

  TODO: add max_time, vary_combat_length
  TODO: dumb the standard values down. There is no need for extended complexity here. The user/creator functions decide what they want/need. Simulation_data is simply a dumb data holder.
  """

  def __init__(
    self,
    calculate_scale_factors: str = "0",
    default_actions: str = "1",
    default_skill: str = "1.0",
    executable: str = None,
    fight_style: str = "patchwerk",
    fixed_time: str = "1",
    html: str = "",
    iterations: str = "250000",
    log: str = "0",
    name: str = "",
    optimize_expressions: str = "1",
    ptr: str = "0",
    ready_trigger: str = "1",
    simc_arguments: list = [],
    target_error: str = "0.1",
    threads: str = "",
    logger: logging.Logger = None
  ) -> None:

    super(Simulation_Data, self).__init__()

    self.logger = logger or logging.getLogger(__name__)
    self.logger.debug("simulation_data initiated.")

    # simc setting to calculate scale factors (stat weights)
    if calculate_scale_factors == "0" or calculate_scale_factors == "1":
      self.calculate_scale_factors = calculate_scale_factors
    else:
      self.calculate_scale_factors = "0"
    # simc setting to manage default apl usage
    if default_actions == "0" or default_actions == "1":
      self.default_actions = default_actions
    else:
      self.default_actions = "1"
    # simc setting to manage the accuracy of used apl lines (leave it at 1.0)
    try:
      self.default_skill = str(float(default_skill))
    except Exception as e:
      self.logger.error("{} -- Using default value instead.".format(e))
      self.default_skill = "1.0"
    # describes the location and type of the simc executable
    # if no value was set, determine a standard value
    if executable == None:
      if sys.platform == 'win32':
        self.logger.debug(
          "Setting Windows default value for executable. This might not work for your system."
        )
        self.executable = "../simc.exe"
      else:
        self.logger.debug(
          "Setting Linux default value for executable. This might not work for your system."
        )
        self.executable = "../simc"
    else:
      try:
        self.executable = str(executable)
      except Exception as e:
        self.logger.error("{}".format(e))
        raise e
    # simc setting to determine the fight style
    if fight_style == "custom" or simc_checks.is_fight_style(fight_style):
      self.fight_style = fight_style
    else:
      self.logger.warning(
        "{} -- Using default value instead.".format(fight_style)
      )
      self.fight_style = "patchwerk"
    # simc setting to enable/diable the fixed fight length
    if fixed_time == "0" or fixed_time == "1":
      self.fixed_time = fixed_time
    else:
      self.fixed_time = "1"
    # simc setting to enable html output
    if type(html) == str:
      self.html = html
    else:
      self.html = ""
    # simc setting to determine the maximum number of run iterations
    #   (target_error and iterations determine the actually simulated
    #   iterations count)
    self.iterations = str(int(iterations))
    # simc setting to enable/disable a log file
    if log == "0" or log == "1":
      self.log = log
    else:
      self.log = "0"
    # optional name for the data
    if not name:
      self.name = str(uuid.uuid4())
    else:
      self.name = name
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
    if type(simc_arguments) == list or simc_arguments == []:
      self.simc_arguments = simc_arguments
    else:
      self.simc_arguments = [simc_arguments]
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

    # set independant default values
    # creation time of the simulation object
    self.so_creation_time = datetime.datetime.utcnow()
    # simulation dps result
    self.dps: int = None
    # flag to know whether data was generated with external simulation function
    self.external_simulation = False
    # simulation full report (command line print out)
    self.full_report: str = None
    # simulation end time
    self.so_simulation_end_time: datetime.datetime = None
    # simulation start time
    self.so_simulation_start_time: datetime.datetime = None

  def is_equal(self, simulation_instance: 'simulation_data') -> bool:
    """Determines if the current and given simulation_data share the
      same base. The following attributes are considered base:
      calculate_scale_factors, default_actions, default_skill,
      executable, fight_style, fixed_time, html, iterations, log,
      optimize_expressions, ptr, ready_trigger, target_error, threads

    Arguments:
      simulation_instance {simulation_data} -- Instance of simulation_data

    Returns:
      bool -- True if equallity between mentioned data is guaranteed.
    """

    try:
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
      if self.html != simulation_instance.html:
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
    except Exception:
      return False

  def get_dps(self) -> int:
    """Get the dps of the simulation_instance.

    Returns:
      int -- dps
    """
    return self.dps

  def set_dps(self, dps: Union[int, float, str],
              external: bool = True) -> None:
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
    if self.dps:
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
    self.logger.debug(
      "Set DPS of profile '{}' to {}.".format(self.name, self.get_dps())
    )

  def get_avg(self, simulation_instance: 'simulation_data') -> int:
    """Get the average between to the parent and given simulation_instance.

    Arguments:
      simulation_instance {simulation_data} -- A finished simulation_data instance.

    Returns:
      int -- Average of parent and simulation_instance.
    """
    if self.get_dps() and simulation_instance.get_dps():
      return int((self.get_dps() + simulation_instance.get_dps()) / 2)
    else:
      return None

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
    """Set so_simulation_start_time. Can be done multiple times.
    """
    self.so_simulation_start_time = datetime.datetime.utcnow()

  def simulate(self) -> int:
    """Simulates the data using SimulationCraft. Resulting dps are saved and returned.

    Raises:
      FileNotFoundError -- Raised if the simulation didn't start due to the executable not being found.
      SimulationError -- Raised if the simulation failes multiple times.

    Returns:
      int -- DPS of the simulation
    """
    argument = [self.executable]
    argument.append("iterations=" + self.iterations)
    argument.append("target_error=" + self.target_error)
    argument.append("fight_style=" + self.fight_style)
    argument.append("fixed_time=" + self.fixed_time)
    argument.append("optimize_expressions=" + self.optimize_expressions)
    argument.append("default_actions=" + self.default_actions)
    argument.append("log=" + self.log)
    argument.append("default_skill=" + self.default_skill)
    argument.append("ptr=" + self.ptr)
    argument.append("threads=" + self.threads)

    for simc_argument in self.simc_arguments:
      argument.append(simc_argument)

    argument.append("ready_trigger=" + self.ready_trigger)

    fail_counter = 0
    # should prevent additional empty windows popping up...on win32 systems without breaking different OS
    if sys.platform == 'win32':
      # call simulationcraft in the background. Save output for processing
      startupinfo = subprocess.STARTUPINFO()  # type: ignore
      startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore

      while not hasattr(self, "success") and fail_counter < 5:

        try:
          simulation_output = subprocess.run(
            argument,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            startupinfo=startupinfo
          )
        except FileNotFoundError as e:
          raise e

        if simulation_output.returncode != 0:
          fail_counter += 1
        else:
          self.success = True

    else:

      while not hasattr(self, "success") and fail_counter < 5:

        try:
          simulation_output = subprocess.run(
            argument,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
          )
        except FileNotFoundError as e:
          raise e

        if simulation_output.returncode != 0:
          fail_counter += 1
        else:
          self.success = True

    if fail_counter >= 5:
      self.logger.error("ERROR: An Error occured during simulation.")
      self.logger.error("args: " + str(simulation_output.args))
      self.logger.error("stdout: " + str(simulation_output.stdout))
      self.error = simulation_output.stdout
      raise SimulationError(self.error)

    # save output
    self.set_full_report(simulation_output.stdout)

    is_actor = True
    run_dps = "DPS: 0.0"
    for line in simulation_output.stdout.splitlines():
      # needs this check to prevent grabbing the boss dps
      if "DPS:" in line and is_actor:
        run_dps = line
        is_actor = False

    dps_value = run_dps.split()[1]

    # save dps value
    self.set_dps(dps_value, external=False)
    self.set_simulation_end_time()

    return self.get_dps()


class Simulation_Group():
  """simulator_group holds one or multiple simulation_data as profiles and can simulate them either serialized or parallel. Parallel uses SimulationCrafts own profilesets feature. Dps values are saved in the simulation_data.
  """

  def __init__(
    self,
    simulation_instance: Union[Simulation_Data, List[Simulation_Data]] = None,
    name: str = "",
    threads: str = "",
    profileset_work_threads: str = "",
    executable: str = "",
    logger: logging.Logger = None
  ) -> None:
    self.logger = logger or logging.getLogger(__name__)
    self.logger.debug("simulation_group initiated.")

    self.name = name
    self.filename: str = ""
    self.threads = threads
    # simulationcrafts own multithreading
    self.profileset_work_threads = profileset_work_threads
    self.executable = executable
    self.profiles: List[Simulation_Data]
    self.sg_simulation_start_time: datetime.datetime = None
    self.sg_simulation_end_time: datetime.datetime = None

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
        "Simulation_instance has wrong type '{}'. Expected list or single simulation_data.".
        format(type(simulation_instance))
      )

    # check input values
    if not self.selfcheck():
      raise ValueError("Selfcheck of the simulation_group failed.")

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
    """Set sg_simulation_start_time. Can be done multiple times.
    """
    self.sg_simulation_start_time = datetime.datetime.utcnow()

  def simulate(self) -> bool:
    """Triggers the simulation of all profiles.

    Raises:
      e -- Raised if simulation of a single profile failed.
      NotSetYetError -- No data available to simulate.

    Returns:
      bool -- True if simulations ended successfully.
    """
    if self.profiles:

      self.set_simulation_start_time()

      if len(self.profiles) == 1:
        # if only one profiles is in the group this profile is simulated normally
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
            "Filename '{}' was already set for the simulation_group. You probably tried to simulate the same group twice.".
            format(self.filename)
          )
        else:
          self.filename = str(uuid.uuid4()) + ".simc"

          # if somehow the random naming function created the same name twice
          if os.path.isfile(self.filename):
            self.logger.info(
              "Somehow the random filename generator generated a name ('{}') that is already on use.".
              format(self.filename)
            )
            self.filename = str(uuid.uuid4()) + ".simc"
          # write arguments to file
          with open(self.filename, "w") as f:
            # write the equal values to file
            f.write(
              "calculate_scale_factors={}\n".format(
                self.profiles[0].calculate_scale_factors
              )
            )
            f.write(
              "default_actions={}\n".format(self.profiles[0].default_actions)
            )
            f.write(
              "default_skill={}\n".format(self.profiles[0].default_skill)
            )
            f.write("fight_style={}\n".format(self.profiles[0].fight_style))
            f.write("fixed_time={}\n".format(self.profiles[0].fixed_time))
            f.write("html={}\n".format(self.profiles[0].html))
            f.write("iterations={}\n".format(self.profiles[0].iterations))
            f.write("log={}\n".format(self.profiles[0].log))
            f.write(
              "optimize_expressions={}\n".format(
                self.profiles[0].optimize_expressions
              )
            )
            f.write("ptr={}\n".format(self.profiles[0].ptr))
            f.write("target_error={}\n".format(self.profiles[0].target_error))
            f.write("threads={}\n".format(self.threads))
            f.write(
              "profileset_work_threads={}\n".format(
                self.profileset_work_threads
              )
            )

            # write all specific arguments to file
            for profile in self.profiles:
              # first used profile needs to be written as normal profile instead of profileset
              if profile == self.profiles[0]:
                for argument in profile.simc_arguments:
                  f.write("{}\n".format(argument))
                f.write(
                  "name=\"{}\"\n\n# Profileset start\n".format(profile.name)
                )
                # or else in wrong scope
                f.write(
                  "ready_trigger={}\n".format(self.profiles[0].ready_trigger)
                )

              else:
                for special_argument in profile.simc_arguments:
                  f.write(
                    "profileset.\"{profile_name}\"+={argument}\n".format(
                      profile_name=profile.name, argument=special_argument
                    )
                  )

          # counter of failed simulation attempts
          fail_counter = 0
          # should prevent additional empty windows popping up...on win32 systems without breaking different OS
          if sys.platform == 'win32':
            # call simulationcraft in the background. Save output for processing
            startupinfo = subprocess.STARTUPINFO()  # type: ignore
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore

            while not hasattr(self, "success") and fail_counter < 5:

              try:
                simulation_output = subprocess.run(
                  [self.executable, self.filename],
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  universal_newlines=True,
                  startupinfo=startupinfo
                )
              except FileNotFoundError as e:
                raise e

              if simulation_output.returncode != 0:
                fail_counter += 1
              else:
                self.success = True

          else:

            while not hasattr(self, "success") and fail_counter < 5:

              try:
                simulation_output = subprocess.run(
                  [self.executable, self.filename],
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  universal_newlines=True
                )
              except FileNotFoundError as e:
                raise e

              if simulation_output.returncode != 0:
                fail_counter += 1
              else:
                self.success = True

          # remove profilesets file
          os.remove(self.filename)
          self.filename = None

          # handle broken simulations
          if fail_counter >= 5:
            self.logger.error("ERROR: An Error occured during simulation.")
            self.logger.error("args: " + str(simulation_output.args))
            self.logger.error("stdout: " + str(simulation_output.stdout))
            self.logger.error(
              "name=value error? Check your input! Maybe your links to already existing profiles are wrong. They need to be relative links from bloodytools to your SimulationCraft directory."
            )
            self.error = simulation_output.stdout
            raise SimulationError(self.error)

          self.logger.debug(simulation_output.stdout)

          # get dps of the first profile
          is_actor = True
          profileset_results = False

          for line in simulation_output.stdout.splitlines():
            # needs this check to prevent grabbing the boss dps
            if self.profiles[0].name in line and is_actor:
              self.logger.debug(line)
              self.profiles[0].set_dps(line.split()[0], external=False)
              is_actor = False

            if "Profilesets (median Damage per Second):" in line:
              profileset_results = True

            # get dps values of the profileset-simulations
            if profileset_results:
              for profile in self.profiles:
                # need this space to catch the difference of multiple profiles like 'tauren' and 'highmountain_tauren'
                if " " + profile.name in line:
                  profile.set_dps(line.split()[0], external=False)

            # prevents false positive from Waiting -data
            if "" == line and profileset_results:
              profileset_results = False

      else:
        raise NotSetYetError(
          "No profiles were added to this simulation_group yet. Nothing can be simulated."
        )

      self.set_simulation_end_time()

    else:
      return False

    return True

  def simulate_with_raidbots(self, apikey) -> bool:
    """Triggers the simulation of all profiles using Raidbots.com API.

    Raises:
      e -- Raised if simulation of a single profile failed.
      NotSetYetError -- No data available to simulate.

    Returns:
      bool -- True if simulations ended successfully.
    """
    if self.profiles:

      self.set_simulation_start_time()

      if len(self.profiles) == 1:
        # if only one profiles is in the group this profile is simulated normally
        try:
          self.profiles[0].simulate()
        except Exception as e:
          raise e

      elif len(self.profiles) >= 2:

        # write data to file, create file name
        if self.filename:
          raise AlreadySetError(
            "Filename '{}' was already set for the simulation_group. You probably tried to simulate the same group twice.".
            format(self.filename)
          )
        else:
          self.filename = str(uuid.uuid4()) + ".simc"

          # if somehow the random naming function created the same name twice
          if os.path.isfile(self.filename):
            self.logger.info(
              "Somehow the random filename generator generated a name ('{}') that is already on use.".
              format(self.filename)
            )
            self.filename = str(uuid.uuid4()) + ".simc"
          # write arguments to file
          with open(self.filename, "w") as f:
            # write the equal values to file
            f.write(
              "default_actions={}\n".format(self.profiles[0].default_actions)
            )
            f.write(
              "default_skill={}\n".format(self.profiles[0].default_skill)
            )
            f.write("fight_style={}\n".format(self.profiles[0].fight_style))
            f.write("fixed_time={}\n".format(self.profiles[0].fixed_time))
            f.write("iterations={}\n".format(self.profiles[0].iterations))
            f.write(
              "optimize_expressions={}\n".format(
                self.profiles[0].optimize_expressions
              )
            )
            f.write("ptr={}\n".format(self.profiles[0].ptr))
            f.write("target_error={}\n".format(self.profiles[0].target_error))

            # write all specific arguments to file
            for profile in self.profiles:
              # first used profile needs to be written as normal profile instead of profileset
              if profile == self.profiles[0]:
                for argument in profile.simc_arguments:
                  # first profile has the dynamic link to the base profile as the first argument
                  if argument == profile.simc_arguments[0]:
                    with open(argument, 'r') as basic_profile:
                      for line in basic_profile:
                        f.write(line)  # TODO: might need a line break
                  else:
                    f.write("{}\n".format(argument))
                f.write(
                  "name=\"{}\"\n\n# Profileset start\n".format(profile.name)
                )
                # or else in wrong scope
                f.write(
                  "ready_trigger={}\n".format(self.profiles[0].ready_trigger)
                )

              else:
                for special_argument in profile.simc_arguments:
                  f.write(
                    "profileset.\"{profile_name}\"+={argument}\n".format(
                      profile_name=profile.name, argument=special_argument
                    )
                  )

          # need raidbots logic

          # create advanced input string
          raidbots_advancedInput = ""
          with open(self.filename, 'r') as f:
            for line in f:
              raidbots_advancedInput += line

          raidbots_body = {
            "type": "advanced",
            "apiKey": apikey,
            "advancedInput": raidbots_advancedInput,
            "simcVersion": "bfa-dev",
            "reportName": "Bloodmallet's shitty tool",
          }

          self.logger.debug(
            "Raidbots communication body created: {}".format(raidbots_body)
          )

          from urllib import request, error
          import json

          data = json.dumps(raidbots_body).encode('utf8')
          headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Bloodmallet\'s shitty tool'
          }
          req = request.Request(
            "https://www.raidbots.com/sim", data=data, headers=headers
          )

          try:
            response = request.urlopen(req)
          except error.URLError as e:
            self.logger.error(
              "Sending the task {} to Raidbots failed.".format(self.name)
            )
            self.logger.error(e.reason)
            self.logger.error(e.read())
            raise SimulationError(
              "Communication with Raidbots failed. {}".format(e.reason)
            )
          else:
            try:
              raidbots_response = json.loads(response.read())
            except Exception as e:
              self.logger.error(e)
              raise e
            else:
              self.logger.debug(
                "Raidbots responded: {}".format(raidbots_response)
              )

          raidbots_sim_id = raidbots_response["simId"]

          # check for when the simulation is done
          self.logger.info(
            "Simulation of {} is underway. Please wait".format(self.name)
          )

          try:
            progress = json.loads(
              request.urlopen(
                "https://www.raidbots.com/api/job/{}".format(raidbots_sim_id)
              ).read()
            )
          except:
            self.logger.error(
              "Fetching the progress of the simulation of {} failed.".format(
                self.name
              )
            )
            progress = {"job": {"state": ""}}
          else:
            self.logger.info(
              "Simulation {} is at {}. This value might behave unpredictable.".
              format(self.name, progress["job"]["progress"])
            )

          import time
          while not progress["job"]["state"] == "complete" and not progress[
            "job"
          ]["state"] == "failed":
            time.sleep(6.5)
            try:
              progress = json.loads(
                request.urlopen(
                  request.Request(
                    "https://www.raidbots.com/api/job/{}".
                    format(raidbots_sim_id),
                    headers=headers
                  )
                ).read()
              )
            except Exception as e:
              self.logger.error(e)
            else:
              progress = json.loads(
                request.urlopen(
                  request.Request(
                    "https://www.raidbots.com/api/job/{}".
                    format(raidbots_sim_id),
                    headers=headers
                  )
                ).read()
              )
            self.logger.info(
              "Simulation {} is at {}. This value might behave unpredictable.".
              format(self.name, progress["job"]["progress"])
            )
            self.logger.debug(progress)
          self.logger.info(
            "Simulation {} is done. Fetching data. This might take some seconds.".
            format(self.name)
          )

          # simulation is done, get data
          fetch_data_start_time = datetime.datetime.utcnow(
          ) + datetime.timedelta(0, 30)
          fetch_data_timeout = False
          try:
            raidbots_data = json.loads(
              request.urlopen(
                request.Request(
                  "https://www.raidbots.com/reports/{}/data.json".
                  format(raidbots_sim_id),
                  headers=headers
                )
              ).read()
            )
          except Exception as e:
            self.logger.error(
              "Fetching data for {} from raidbots failed. {}".format(
                self.name, e
              )
            )
            fetched = False
            while not fetched and not fetch_data_timeout:
              time.sleep(4)
              try:
                raidbots_data = json.loads(
                  request.urlopen(
                    request.Request(
                      "https://www.raidbots.com/reports/{}/data.json".
                      format(raidbots_sim_id),
                      headers=headers
                    )
                  ).read()
                )
              except Exception as e:
                self.logger.error(
                  "Fetching data for {} from raidbots failed. {}".format(
                    self.name, e
                  )
                )
                if datetime.datetime.utcnow() > fetch_data_start_time:
                  fetch_data_timeout = True
              else:
                fetched = True
          else:
            self.logger.info(
              "Fetching data for {} succeeded. {}".format(
                self.name, raidbots_data
              )
            )

          # if simulation failed or data.json couldn't be fetched
          if progress["job"]["state"] == "failed" or fetch_data_timeout:

            fetch_input_start_time = datetime.datetime.utcnow(
            ) + datetime.timedelta(0, 30)
            fetch_input_timeout = False

            # simulation failed, get input
            try:
              raidbots_input = json.loads(
                request.urlopen(
                  request.Request(
                    "https://www.raidbots.com/reports/{}/input.txt".
                    format(raidbots_sim_id),
                    headers=headers
                  )
                ).read()
              )
            except Exception as e:
              self.logger.error(
                "Fetching input data for {} from raidbots failed. {}".format(
                  self.name, e
                )
              )
              fetched = False
              while not fetched and not fetch_input_timeout:
                try:
                  raidbots_input = json.loads(
                    request.urlopen(
                      request.Request(
                        "https://www.raidbots.com/reports/{}/input.txt".
                        format(raidbots_sim_id),
                        headers=headers
                      )
                    ).read()
                  )
                except Exception as e:
                  self.logger.error(
                    "Fetching input data for {} from raidbots failed. {}".
                    format(self.name, e)
                  )
                  if datetime.datetime.utcnow() > fetch_input_start_time:
                    fetch_input_timeout = True
                else:
                  fetched = True
            else:
              self.logger.info(
                "Fetching input data for {} succeeded. {}".format(
                  self.name, raidbots_input
                )
              )

            fetch_output_start_time = datetime.datetime.utcnow(
            ) + datetime.timedelta(0, 30)
            fetch_output_timeout = False

            # simulation failed, get input
            try:
              raidbots_output = json.loads(
                request.urlopen(
                  request.Request(
                    "https://www.raidbots.com/reports/{}/output.txt".
                    format(raidbots_sim_id),
                    headers=headers
                  )
                ).read()
              )
            except Exception as e:
              self.logger.error(
                "Fetching output data for {} from raidbots failed. {}".format(
                  self.name, e
                )
              )
              fetched = False
              while not fetched and not fetch_output_timeout:
                try:
                  raidbots_output = json.loads(
                    request.urlopen(
                      request.Request(
                        "https://www.raidbots.com/reports/{}/output.txt".
                        format(raidbots_sim_id),
                        headers=headers
                      )
                    ).read()
                  )
                except Exception as e:
                  self.logger.error(
                    "Fetching output data for {} from raidbots failed. {}".
                    format(self.name, e)
                  )
                  if datetime.datetime.utcnow() > fetch_output_start_time:
                    fetch_output_timeout = True
                else:
                  fetched = True
            else:
              self.logger.info(
                "Fetching output data for {} succeeded. {}".format(
                  self.name, raidbots_output
                )
              )

            with open("error_{}.txt".format(raidbots_sim_id), 'w') as f:
              f.write("############## INPUT ##############\n")
              f.write(json.dumps(raidbots_input))
              f.write("\n\n############## OUTPUT ##############\n")
              f.write(json.dumps(raidbots_output))

              try:
                f.write(
                  "\n\n############## DATA ##############\n{}".format(
                    json.dumps(raidbots_data)
                  )
                )
              except Exception:
                f.write(
                  "\n\n############## DATA ##############\nNo data available.\n"
                )

            raise SimulationError(
              "Simulating with Raidbots failed. Please check out error_{}.txt file.".
              format(raidbots_sim_id)
            )

          input("Enter something to delete the created file.")
          # remove profilesets file
          os.remove(self.filename)
          self.filename = None

          self.logger.debug("Congratulations, you got a data file!")
          self.logger.debug(
            json.dumps(raidbots_data, sort_keys=True, indent=4)
          )

          # set basic profile dps
          self.logger.debug("Setting dps for baseprofile.")
          self.set_dps_of(
            raidbots_data["sim"]["players"][0]["name"],
            raidbots_data["sim"]["players"][0]["collected_data"]["dps"]["mean"]
          )
          self.logger.debug("Set dps for baseprofile.")

          for profile in raidbots_data["sim"]["profilesets"]["results"]:
            self.logger.debug("Setting dps for {}".format(profile["name"]))
            self.set_dps_of(profile["name"], profile["mean"])

      else:
        raise NotSetYetError(
          "No profiles were added to this simulation_group yet. Nothing can be simulated."
        )

      self.set_simulation_end_time()

    else:
      return False

    return True

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
    """
    @brief      Add another simulation_instance object to the group

    @param      self                    The object
    @param      simulation_instance  The simulation information

    @return     True, if adding data was successfull. Exception otherwise.
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
        "Simulation_instance has wrong type '{}' (needed simulation_data).".
        format(type(simulation_instance))
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
    return None

  def set_dps_of(self, profile_name: str, dps: Union[int, float, str]) -> bool:
    try:
      for profile in self.profiles:
        if profile.name == profile_name:
          profile.set_dps(dps, external=False)
    except Exception as e:
      self.logger.error(
        "Setting dps for profile {} failed. {}".format(profile_name, e)
      )
      return False
    else:
      return True
