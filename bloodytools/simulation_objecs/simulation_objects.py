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
  def __init__( self, message):
    self.message = message


class AlreadySetError( Error ):
  pass


class InputError( Error ):
  pass


class NotSetYetError( Error ):
  pass


class StillInProgressError( Error ):
  pass

class SimulationError( Error ):
  pass


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
    name="",
    optimize_expressions="1",
    ptr="0",
    ready_trigger="1",
    simc_arguments=[],
    target_error="0.1",
    threads="" ):

    super( simulation_data, self ).__init__()

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
      self.default_skill = str( float( default_skill ) )
    except Exception as e:
      logger.error( "{} -- Using default value instead.".format( e ) )
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
        self.executionable = str( executionable )
      except Exception as e:
        logger.error( e )
        raise e
    # simc setting to determine the fight style
    if fight_style == "custom" or simc_checks.is_fight_style( fight_style ):
      self.fight_style = fight_style
    else:
      logger.warning( "{} -- Using default value instead.".format( fight_style ) )
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
    self.iterations = str( int( iterations ) )
    # simc setting to enable/disable a log file
    if log == "0" or log == "1":
      self.log = log
    else:
      self.log = "0"
    # optional name for the data
    if not name:
      self.name = uuid.uuid4()
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
    if type( simc_arguments ) == list or simc_arguments == []:
      self.simc_arguments = simc_arguments
    else:
      self.simc_arguments = [simc_arguments]
    # simc setting to determine the target_error
    try:
      self.target_error = str( float( target_error ) )
    except Exception as e:
      self.target_error = "0.1"
    # simc setting to determine the number of used threads, empty string uses
    #   all available
    if type(threads) == int or type(threads) == str or type(threads) == float:
      try:
        self.threads = str( int( float( threads ) ) )
      except Exception as e:
        self.threads = ""
    else:
      self.threads = ""

    # set independant default values
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


  def is_equal(self, simulation_instance):
    """
    @brief      Determines if the current and given simulation_data share the
                same base. The following attributes are considered base:
                calculate_scale_factors, default_actions, default_skill,
                executionable, fight_style, fixed_time, html, iterations, log,
                optimize_expressions, ptr, ready_trigger, target_error, threads

    @param      self             The object
    @param      simulation_instance  The other simulation data

    @return     True if equal base values, False otherwise.
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
    except Exception as e:
      False


  def get_dps( self ):
    """
    @brief      Get the dps of the simulation.

    @param      self  The object

    @return     The dps.
    """
    return self.dps


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
    if type( external ) == bool:
      self.external_simulation = external
    else:
      raise TypeError

    # raise AlreadySetError if one tries to overwrite previously set data
    if self.dps:
      raise AlreadySetError( "A value for dps was already set to {}.".format( self.get_dps() ) )

    try:
      # slightly more robust than simply cast to int, due to possible float
      # numbers as strings
      self.dps = int( float( dps ) )
    except Exception as e:
      raise e

    if self.so_simulation_end_time != None:
      self.so_simulation_end_time = datetime.datetime.utcnow()

    return True


  def get_avg( self, simulation_instance ):
    """
    @brief      Gets the average of the current the given simulation_instance.

    @param      self                 The object
    @param      simulation_instance  The simulation data

    @return     The average as int.
    """
    if self.get_dps() and simulation_instance.get_dps():
      return int( ( self.get_dps() + simulation_instance.get_dps() ) / 2 )
    else:
      return None


  def get_simulation_duration( self ):
    """
    @brief      Return the time, the simulation took. Will raise NotDoneYetError
                if simulation didn't start or end yet.

    @param      self  The object

    @return     The simulation duation.
    """
    if self.so_simulation_start_time and self.so_simulation_end_time:
      return self.so_simulation_end_time - self.so_simulation_start_time
    else:
      None


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
      raise TypeError("Report as type {} found but string was expected.".format( type( report ) ) )


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
      raise AlreadySetError( "Simulation end time was already set. Setting it twice is not allowed." )


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
  def __init__( self, simulation_instance, name="" ):
    super( simulation_group, self ).__init__()
    if type( simulation_instance ) == list:
      self.profiles = simulation_instance
    elif type( simulation_instance ) == simulation_instance:
      self.profiles = [ simulation_instance ]
    else:
      raise TypeError( "Simulation_instance has wrong type '{}' (needed list or single simulation_data).".format(type(simulation_instance)) )
    # optional name of the simulation_group
    self.name = name

    if not selfcheck():
      raise InputError( "simulation_instance base data wasn't coherent." )


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



  def add( self, simulation_instance ):
    """
    @brief      Add another simulation_instance object to the group

    @param      self                    The object
    @param      simulation_instance  The simulation information

    @return     True, if adding data was successfull. Exception otherwise.
    """
    if type( simulation_instance ) == simulation_data:
      try:
        self.profiles.append( simulation_instance )
      except Exception as e:
        raise e
      else:
        return True
    else:
      raise TypeError( "Simulation_instance has wrong type '{}' (needed simulation_data).".format(type(simulation_instance)) )
