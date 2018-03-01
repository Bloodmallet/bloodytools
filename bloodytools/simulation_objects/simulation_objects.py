#!/usr/bin/env python

# date data
import datetime
# wow game data and simc input checks
from simc_support import simc_checks as simc_checks
# sys operations and data
import sys
from typing import Union, List
import uuid
import logging

import subprocess

logger = logging.getLogger(__name__)


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


class simulation_data():
  """Manages all META-information for a single simulation and the result.

  TODO: add max_time, vary_combat_length
  TODO: dumb the standard values down. There is no need for extended complexity here. The user/creator functions decide what they want/need. Simulation_data is simply a dumb data holder.
  """

  def __init__(
    self,
    calculate_scale_factors: str = "0",
    default_actions: str = "1",
    default_skill: str = "1.0",
    executionable: str = None,
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
    threads: str = ""
  ) -> None:

    super(simulation_data, self).__init__()

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
      logger.error("{} -- Using default value instead.".format(e))
      self.default_skill = "1.0"
    # describes the location and type of the simc executable
    # if no value was set, determine a standard value
    if executionable == None:
      if sys.platform == 'win32':
        logger.debug("Setting Windows default value for executionable.")
        self.executionable = "../simc.exe"
      else:
        logger.debug("Setting Linux default value for executionable.")
        self.executionable = "../simc"
    else:
      try:
        self.executionable = str(executionable)
      except Exception as e:
        logger.error("{}".format(e))
        raise e
    # simc setting to determine the fight style
    if fight_style == "custom" or simc_checks.is_fight_style(fight_style):
      self.fight_style = fight_style
    else:
      logger.warning("{} -- Using default value instead.".format(fight_style))
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
    if ptr == "0" or ptr == "1":
      self.ptr = ptr
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
    self.dps: int
    # flag to know whether data was generated with external simulation function
    self.external_simulation = False
    # simulation full report (command line print out)
    self.full_report: str
    # simulation end time
    self.so_simulation_end_time: datetime.datetime
    # simulation start time
    self.so_simulation_start_time: datetime.datetime

  def is_equal(self, simulation_instance: 'simulation_data') -> bool:
    """Determines if the current and given simulation_data share the
      same base. The following attributes are considered base:
      calculate_scale_factors, default_actions, default_skill,
      executionable, fight_style, fixed_time, html, iterations, log,
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
      if self.executionable != simulation_instance.executionable:
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
        "A value for dps was already set to {}.".format(self.get_dps())
      )

    try:
      # slightly more robust than simply cast to int, due to possible float
      # numbers as strings
      self.dps = int(float(dps))
    except Exception as e:
      raise e

    if self.so_simulation_end_time != None:
      self.so_simulation_end_time = datetime.datetime.utcnow()

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
    argument = [self.executionable]
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
    #argument.append( "ready_trigger="+ self.ready_trigger )

    for simc_argument in self.simc_arguments:
      argument.append(simc_argument)

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
      logger.error("ERROR: An Error occured during simulation.")
      logger.error("args: " + str(simulation_output.args))
      logger.error("stdout: " + str(simulation_output.stdout))
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


class simulation_group():
  """simulator_group holds one or multiple simulation_data as profiles and can simulate them either serialized or parallel. Parallel uses SimulationCrafts own profilesets feature. Dps values are saved in the simulation_data.
  """

  def __init__(
    self,
    simulation_instance: Union[simulation_data, List[simulation_data]],
    name: str = ""
  ) -> None:
    self.name = name
    self.profiles: List[simulation_data]

    if type(simulation_instance) == list:
      correct_type = True
      for data in simulation_instance:  # type: ignore
        if type(data) != simulation_data:
          correct_type = False
      if correct_type:
        self.profiles = simulation_instance  # type: ignore
      else:
        raise TypeError(
          "At least one item of simulation_instance list had a wrong type. Expected simulation_data."
        )
    elif type(simulation_instance) == simulation_data:
      self.profiles = [simulation_instance]  # type: ignore
    else:
      raise TypeError(
        "Simulation_instance has wrong type '{}'. Expected list or single simulation_data.".
        format(type(simulation_instance))
      )

    if not self.selfcheck():
      raise ValueError(
        "At least one item of simulation_instance had data that didn't match the others."
      )

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

  def simulate(self) -> bool:
    """Triggers the simulation of all profiles.

    Raises:
      e -- Raised if simulation of a single profile failed.
      NotImplementedError -- Multi-profile simulation via simulationcraft
                             profilesets is not yet implemented.
      NotSetYetError -- No data available to simulate.

    Returns:
      bool -- True if simulations ended successfully.
    """

    if self.profiles:
      if len(self.profiles) == 1:
        # if only one profiles is in the group this profile is simulated normally
        try:
          self.profiles[0].simulate()
        except Exception as e:
          raise e
      elif len(self.profiles) >= 2:
        # profile set creation based on profiles content
        # create file with profile set content
        # start simulation with profilesets
        # grab data
        # push data into simulation_data.set_dps(dps)
        raise NotImplementedError
      else:
        raise NotSetYetError(
          "No profiles were added to this simulation_group yet. Nothing can be simulated."
        )
    else:
      return False

    return True

  def add(self, simulation_instance: simulation_data) -> bool:
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
    if type(simulation_instance) == simulation_data:
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
