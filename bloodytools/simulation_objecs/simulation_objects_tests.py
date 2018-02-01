import datetime
import logging
import unittest
import uuid

import simulation_objects

logger = logging.getLogger(__name__)

##
## @brief      Simple tests for the handling of init values for objects of the
##             simulation_data class
##
class TestSimulationDataInit(unittest.TestCase):

  ##
  ## @brief      Cleans up after each test.
  ##
  ## @param      self  The object
  ##
  ## @return     Nothing
  ##
  def tearDown(self):
    self.simulation_data = None

  ##
  ## @brief      Test all available and left empty input values for their
  ##             correct default values.
  ##
  ## @param      self  The object
  ##
  ## @return     { description_of_the_return_value }
  ##
  def test_empty(self):
    self.simulation_data = simulation_objects.simulation_data()
    self.assertEqual( self.simulation_data.calculate_scale_factors, "0" )
    self.assertEqual( self.simulation_data.default_actions, "1" )
    self.assertEqual( self.simulation_data.default_skill, "1.0" )
    self.assertEqual( self.simulation_data.fight_style, "patchwerk" )
    self.assertEqual( self.simulation_data.fixed_time, "1" )
    self.assertEqual( self.simulation_data.html, "" )
    self.assertEqual( self.simulation_data.iterations, "250000" )
    self.assertEqual( self.simulation_data.log, "0" )
    self.assertNotEqual( self.simulation_data.name, None )
    self.assertEqual( self.simulation_data.optimize_expressions, "1" )
    self.assertEqual( self.simulation_data.ptr, "0" )
    self.assertEqual( self.simulation_data.ready_trigger, "1" )
    self.assertEqual( self.simulation_data.simc_arguments, [] )
    self.assertEqual( self.simulation_data.target_error, "0.1" )
    self.assertEqual( self.simulation_data.threads, "" )
    self.assertEqual( type( self.simulation_data.so_creation_time), datetime.datetime )
    self.assertEqual( self.simulation_data.external_simulation, False )
    self.assertEqual( self.simulation_data.full_report, None )
    self.assertEqual( self.simulation_data.so_simulation_end_time, None )
    self.assertEqual( self.simulation_data.so_simulation_start_time, None )



  ##
  ## @brief      Test input checks of calculate_scale_factor.
  ##
  ## @param      self  The object
  ##
  ## @return     { description_of_the_return_value }
  ##
  @unittest.skip("demonstrating skipping")
  def test_calculate_scale_factors(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_default_actions(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_executionble(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_fight_style(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_fixed_time(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_html(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_iterations(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_log(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_name(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_optimize_expressions(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_ptr(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_ready_trigger(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_simc_arguments(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_target_error(self):
    pass

  @unittest.skip("demonstrating skipping")
  def test_threads(self):
    pass




if __name__ == '__main__':
  unittest.main()
