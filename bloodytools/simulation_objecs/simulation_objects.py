# date data
import datetime
# wow game data and simc input checks
from simc_support import simc_checks as simc_checks
# sys operations and data
import sys
import uuid
import logging

logger = logging.getLogger(__name__)

class Error( Exception ):
  """Base class for exceptions in this module"""
  pass


class AlreadySetError( Error ):
  """
  Exception raised if a value already exists.

  Attributes:
    value -- value which was tried to set
    message -- explanation of the error
  """
  def __init__( self, value, message ):
    self.value = value
    self.message = message
    logger.exception(self.message)


class InputError( Error ):
  """
  Exception raised for errors in the input.

  Attributes:
    expression -- input expression in which the error occurred
    message -- explanation of the error
  """
  def __init__( self, expression, message ):
    self.expression = expression
    self.message = message
    logger.exception(self.message)


class NotSetYetError( Error ):
  """
  Exception raised when simulations aren't done yet.

  Attributes:
    value -- value which was tried to get
    message -- explanation of the error
  """
  def __init__( self, value, message ):
    self.value = value
    self.message = message
    logger.exception(self.message)


class StillInProgressError( Error ):
  """
  Exception raised when simulation is still in progress.

  Attributes:
    value -- value which was tried to get
    message -- explanation of the error
  """
  def __init__( self, value, message ):
    self.value = value
    self.message = message
    logger.exception(self.message)


class SimulationError(object):
  """
  Exception raised when simulations aren't done yet.

  Attributes:
    value -- value which was tried to get
    message -- explanation of the error
  """
  def __init__(self, simulation_output):
    super(SimulationError, self).__init__()
    self.simulation_output = simulation_output


class simulation_data():
  """
  Manages all META-information for a simulation and the result.
  """
  def __init__( self,
    calculate_scale_factors="0",
    default_actions="1",
    default_skill="1.0",
    executionable=None,
    fight_style="patchwerk",
    fixed_time="1",
    html="",
    iterations="250000",
    log="0",
    name=None,
    optimize_expressions="1",
    ptr="0",
    ready_trigger="1",
    simc_arguments=[],
    target_error="0.1",
    threads="" ):

    super( simulation_data, self ).__init__()

    # simc setting to calculate scale factors (stat weights)
    self.calculate_scale_factors = calculate_scale_factors

    # simc setting to manage default apl usage
    logger.debug("Initialising default_actions.")
    self.default_actions = default_actions

    # simc setting to manage the accuracy of used apl lines (leave it at 1.0)
    logger.debug("Initialising default_skill.")
    try:
      self.default_skill = str( float( default_skill ) )
    except Exception as e:
      logger.error( "{} -- Using default value instead.".format( e ) )
      self.default_skill = "1.0"

    # describes the location and type of the simc executable
    logger.debug("Initialising executionable.")
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
        self.executionable = str( executionable )
      except Exception as e:
        logger.error( e )
        raise e

    # simc setting to determine the fight style
    logger.debug("Initialising fight_style.")
    if fight_style == "custom" or simc_checks.is_fight_style( fight_style ):
      self.fight_style = fight_style
    else:
      logger.warning( "{} -- Using default value instead.".format( fight_style ) )
      self.fight_style = "patchwerk"

    # simc setting to enable/diable the fixed fight length
    self.fixed_time = fixed_time
    # simc setting to enable html output
    self.html = html
    # simc setting to determine the maximum number of run iterations
    #   (target_error and iterations determine the actually simulated
    #   iterations count)
    self.iterations = str( int( iterations ) )
    # simc setting to enable/disable a log file
    self.log = log
    # optional name for the data
    if not name:
      self.name = uuid.uuid4()
    else:
      self.name = name
    # simc setting to enable/disable optimize expressions
    self.optimize_expressions = optimize_expressions
    # simc setting to enable/disable ptr data
    self.ptr = ptr
    # simc setting to enable/disable ready_trigger
    self.ready_trigger = ready_trigger
    # specific data to be run, like talent combinations, specific gear or
    #   traits
    if type( simc_arguments ) == list or simc_arguments == []:
      self.simc_arguments = simc_arguments
    else:
      self.simc_arguments = [simc_arguments]
    # simc setting to determine the target_error
    self.target_error = target_error
    # simc setting to determine the number of used threads, empty string uses
    #   all available
    self.threads = threads

    # creation time of the simulation object
    self.so_creation_time = datetime.datetime.utcnow()
    # simulation dps result
    self.dps = None
    # flag to know whether data was generated with external simulation function
    self.external_simulation = False
    # simulation full report (command line print out)
    self.full_report = None
    # simulation end time
    self.so_simulation_end_time = None
    # simulation start time
    self.so_simulation_start_time = None


  def is_equal(self, simulation_data):
    """
    @brief      Determines if the current and given simulation_data share the
                same base. The following attributes are considered base:
                calculate_scale_factors, default_actions, default_skill,
                executionable, fight_style, fixed_time, html, iterations, log,
                optimize_expressions, ptr, ready_trigger, target_error, threads

    @param      self             The object
    @param      simulation_data  The other simulation data

    @return     True if equal base values, False otherwise.
    """
    if self.calculate_scale_factors != simulation_data.calculate_scale_factors:
      return False
    if self.default_actions != simulation_data.default_actions:
      return False
    if self.default_skill != simulation_data.default_skill:
      return False
    if self.executionable != simulation_data.executionable:
      return False
    if self.fight_style != simulation_data.fight_style:
      return False
    if self.fixed_time != simulation_data.fixed_time:
      return False
    if self.html != simulation_data.html:
      return False
    if self.iterations != simulation_data.iterations:
      return False
    if self.log != simulation_data.log:
      return False
    if self.optimize_expressions != simulation_data.optimize_expressions:
      return False
    if self.ptr != simulation_data.ptr:
      return False
    if self.ready_trigger != simulation_data.ready_trigger:
      return False
    if self.target_error != simulation_data.target_error:
      return False
    if self.threads != simulation_data.threads:
      return False
    return True


  def get_dps( self ):
    """
    @brief      Get the dps of the simulation.

    @param      self  The object

    @return     The dps.
    """
    if self.dps:
      return int( self.dps )
    if self.so_simulation_start_time < datetime.datetime.utcnow() and not self.so_simulation_end_time:
      raise StillInProgressError( "dps", "Dps simulation is still in progress." )
    else:
      raise NotSetYetError( "dps", "No dps was saved yet." )


  def set_dps( self, dps, external=True ):
    """
    @brief      Sets the dps.

    @param      self      The object
    @param      dps       The dps
    @param      external  Set to True if dps was calculated using an external
                          logic

    @return     True if dps was set.
    """
    # set external_simulation flag, defaults to True, so external simulations
    #  don't need to pay attention to this
    try:
      self.external_simulation = bool( external )
    except Exception as e:
      raise e

    # raise AlreadySetError if one tries to overwrite previously set data
    if self.dps:
      raise AlreadySetError( "dps",
        "A value for dps was already set to {}.".format( self.get_dps() ) )

    try:
      # slightly more robust than simply cast to int, due to possible float
      # numbers as strings
      self.dps = int( float( dps ) )
    except Exception as e:
      raise e

    return True


  def get_avg( self, simulation_data ):
    """
    @brief      Gets the average of the current the given simulation_data.

    @param      self             The object
    @param      simulation_data  The simulation data

    @return     The average as int.
    """
    return int( ( self.get_dps() + simulation_data.get_dps() ) / 2 )


  def get_simulation_duation( self ):
    """
    @brief      Return the time, the simulation took. Will raise NotDoneYetError
                if simulation didn't start or end yet.

    @param      self  The object

    @return     The simulation duation.
    """
    if not self.so_simulation_start_time:
      raise NotSetYetError( "so_simulation_start_time",
        "Simulation didn't start yet. No simulation duration possible." )
    if not self.so_simulation_end_time:
      raise NotSetYetError( "so_simulation_end_time",
        "Simulation isn't done yet. No simulation duration possible." )

    return self.so_simulation_end_time - self.so_simulation_start_time


  def set_full_report( self, report ):
    """
    @brief      Saves the report (simulation output).

    @param      self    The object
    @param      report  The report

    @return     True, if saved.
    """
    if type( report ) == str:
      self.full_report = report
      return True
    else:
      raise TypeError("Report as type {} found but string expected.".format( type( report ) ) )


  def set_simulation_end_time( self ):
    """
    @brief      Set so_simulation_end_time. Raises AlreadySetError if
                so_simulation_end_time was already set.

    @param      self  The object

    @return     True, if set.
    """
    if not self.so_simulation_end_time:
      try:
        self.so_simulation_end_time = datetime.datetime.utcnow()
      except Exception as e:
        raise e
      else:
        return True
    else:
      raise AlreadySetError( "so_simulation_end_time",
        "End time was already set. Setting it twice is not allowed." )


  def set_simulation_start_time( self ):
    """
    @brief      Set so_simulation_start_time. Can happen multiple times if
                simulation failed.

    @param      self  The object

    @return     True, if set.
    """
    try:
      self.so_simulation_start_time = datetime.datetime.utcnow()
    except Exception as e:
      raise e
    else:
      return True


  def simulate( self ):
    """
    @brief      Simulates the data using SimulationCraft. Resulting dps are
                saved.

    @param      self  The object

    @return     DPS of the simulation.
    """
    argument = [ self.executionable ]
    argument.append( "iterations="   + self.iterations )
    argument.append( "target_error=" + self.target_error )
    argument.append( "fight_style="  + self.fight_style )
    argument.append( "fixed_time="   + self.fixed_time )
    argument.append( "optimize_expressions="  + self.optimize_expressions )
    argument.append( "default_actions="       + self.default_actions )
    argument.append( "log="          + self.log )
    argument.append( "default_skill="+ self.default_skill )
    argument.append( "ptr="          + self.ptr )
    argument.append( "threads="      + self.threads )
    argument.append( "ready_trigger="+ self.ready_trigger )

    for simc_argument in simc_arguments:
      argument.append( simc_argument )

    # should prevent additional empty windows popping up...on win32 systems without breaking different OS
    if sys.platform == 'win32':
      # call simulationcraft in the background. grab output for processing and get dps value
      startupinfo = subprocess.STARTUPINFO()
      startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

      simulation_output = subprocess.run(
        argument,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        startupinfo=startupinfo
      )


      fail_counter = 0
      while simulation_output.returncode != 0 and fail_counter < 5:
        logger.error( "ERROR: An Error occured during simulation." )
        logger.error( "args: " + str( simulation_output.args ) )
        logger.error( "stdout: " + str( simulation_output.stdout ) )
        simulation_output = subprocess.run(
          argument,
          stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT,
          universal_newlines=True,
          startupinfo=startupinfo
        )
        fail_counter += 1

    else:
      simulation_output = subprocess.run(
        argument,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
      )


      fail_counter = 0
      while simulation_output.returncode != 0 and fail_counter < 5:
        logger.error( "ERROR: An Error occured during simulation." )
        logger.error( "args: " + str( simulation_output.args ) )
        logger.error( "stdout: " + str( simulation_output.stdout ) )
        simulation_output = subprocess.run(
          argument,
          stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT,
          universal_newlines=True
        )
        fail_counter += 1

    if fail_counter >= 5:
      self.error = simulation_output.stdout
      raise SimulationError( self.error )

    # set simulation end time
    self.set_simulation_end_time()
    # save output
    self.set_full_report( simulation_output )

    actor_flag = True
    run_dps = "DPS: 0.0"
    for line in simulation_output.stdout.splitlines():
      # needs this check to prevent grabbing the boss dps
      if "DPS:" in line and actor_flag:
        run_dps = line
        actor_flag = False

    dps_value = run_dps.split()[ 1 ]

    # save dps value
    self.set_dps( dps_value, external=False )

    return self.get_dps()


class simulation_group():
  """
  @brief      simulator_group holds one or multiple simulation_data as profiles
              and can simulate them either serialized or parallel. Parallel uses
              SimulationCrafts own profilesets feature. Dps values are saved in
              the simulation_data.
  """
  def __init__( self, simulation_data, name="" ):
    super( simulation_group, self ).__init__()
    if type( simulation_data ) == list:
      self.profiles = simulation_data
    elif type( simulation_data ) == simulation_data:
      self.profiles = [ simulation_data ]
    else:
      logger.error( "Wrong type {} of simulation_data (need list of or single simulation_data).".format( type( simulation_data ) ) )
      raise TypeError( "simulation_group initiation",
        "Wrong type " + str( type( simulation_data ) ) + " of simulation_data (need list/single simulation_data)." )
    # optional name of the simulation_group
    self.name = name

    if not selfcheck():
      raise InputError( "simulation_group",
        "simulation_data base data wasn't coherent.")


  def selfcheck( self ):
    """
    @brief      Compares the base content of all profiles. All profiles need to
                have the same values in each standard field (__init__ of
                simulation_data).

    @param      self  The object

    @return     True if all data is coherent, False otherwise.
    """
    i = 0
    while i + 1 < len( self.profiles ):
      if not self.profiles[ i ].is_equal( self.profiles[ i + 1 ] ):
        return False
      i += 1
    return True


  def simulate( self ):
    """
    @brief      Triggers the simulation of all profiles.

    @param      self  The object

    @return     True on success.
    """
    if length( self.profiles ) == 1:
      # if only one profiles is in the group this profile is simulated normally
      self.profiles[ 0 ].simulate()
    else:
      # profile set creation based on profiles content
      # create file with profile set content
      # start simulation with profilesets
      # grab data
      # push data into simulation_data.set_dps(dps)
      pass



  def add( self, simulation_data ):
    """
    @brief      Add another simulation_data object to the group

    @param      self                    The object
    @param      simulation_data  The simulation information

    @return     True, if adding data was successfull. Exception otherwise.
    """
    if type( simulation_data ) == simulation_data:
      try:
        self.profiles.append( simulation_data )
      except Exception as e:
        raise e
      else:
        return True
    else:
      raise TypeError( "simulation_group.add",
        "Wrong type of simulation_data (need simulation_data)." )
