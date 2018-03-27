#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import logging
import unittest
import uuid
import time
import os

import simulation_objects

logger = logging.getLogger(__name__)


class TestSimulationDataInit(unittest.TestCase):
  """Simple tests for the handling of init values for objects of the simulation_data class.
  """

  def tearDown(self):
    """Cleans up after each test.
    """

    self.sd = None

  def test_empty(self):
    """Test all available and left empty input values for their correct default values.
    """

    self.sd = simulation_objects.simulation_data()
    self.assertEqual(self.sd.calculate_scale_factors, "0")
    self.assertEqual(self.sd.default_actions, "1")
    self.assertEqual(self.sd.default_skill, "1.0")
    self.assertEqual(self.sd.fight_style, "patchwerk")
    self.assertEqual(self.sd.fixed_time, "1")
    self.assertEqual(self.sd.html, "")
    self.assertEqual(self.sd.iterations, "250000")
    self.assertEqual(self.sd.log, "0")
    self.assertNotEqual(self.sd.name, None)
    self.assertEqual(self.sd.optimize_expressions, "1")
    self.assertEqual(self.sd.ptr, "0")
    self.assertEqual(self.sd.ready_trigger, "1")
    self.assertEqual(self.sd.simc_arguments, [])
    self.assertEqual(self.sd.target_error, "0.1")
    self.assertEqual(self.sd.threads, "")
    self.assertEqual(type(self.sd.so_creation_time), datetime.datetime)
    self.assertEqual(self.sd.external_simulation, False)
    self.assertEqual(self.sd.full_report, None)
    self.assertEqual(self.sd.so_simulation_end_time, None)
    self.assertEqual(self.sd.so_simulation_start_time, None)

  def test_calculate_scale_factors(self):
    """Test input checks of calculate_scale_factors.
    """

    self.sd = simulation_objects.simulation_data(calculate_scale_factors="1")
    self.assertEqual(self.sd.calculate_scale_factors, "1")
    self.assertNotEqual(self.sd.calculate_scale_factors, "0")
    self.assertNotEqual(self.sd.calculate_scale_factors, str)
    self.assertNotEqual(self.sd.calculate_scale_factors, list)
    self.assertNotEqual(self.sd.calculate_scale_factors, dict)
    self.assertNotEqual(self.sd.calculate_scale_factors, int)

  ##
  ## @brief      Test input checks of default_actions.
  ##
  ## @param      self  The object
  ##
  ## @return     { description_of_the_return_value }
  ##
  def test_default_actions(self):
    self.sd = simulation_objects.simulation_data(default_actions="1")
    self.assertEqual(self.sd.default_actions, "1")
    self.assertNotEqual(self.sd.default_actions, "0")
    self.assertNotEqual(self.sd.default_actions, str)
    self.assertNotEqual(self.sd.default_actions, list)
    self.assertNotEqual(self.sd.default_actions, dict)
    self.assertNotEqual(self.sd.default_actions, int)

  def test_fight_style(self):
    self.sd = simulation_objects.simulation_data(fight_style="helterskelter")
    self.assertEqual(self.sd.fight_style, "helterskelter")
    self.assertNotEqual(self.sd.fight_style, "0")
    self.assertNotEqual(self.sd.fight_style, str)
    self.assertNotEqual(self.sd.fight_style, list)
    self.assertNotEqual(self.sd.fight_style, dict)
    self.assertNotEqual(self.sd.fight_style, int)
    # simc_checks needs improvements to catch this
    #self.sd = None
    #self.sd = simulation_objects.simulation_data( fight_style=1234 )
    #self.assertEqual( self.sd.fight_style, "patchwerk" )

  def test_fixed_time(self):
    self.sd = simulation_objects.simulation_data(fixed_time="1")
    self.assertEqual(self.sd.fixed_time, "1")
    self.assertNotEqual(self.sd.fixed_time, "0")
    self.assertNotEqual(self.sd.fixed_time, str)
    self.assertNotEqual(self.sd.fixed_time, list)
    self.assertNotEqual(self.sd.fixed_time, dict)
    self.assertNotEqual(self.sd.fixed_time, int)

  def test_html(self):
    self.sd = simulation_objects.simulation_data(html="testiger.html")
    self.assertEqual(self.sd.html, "testiger.html")
    self.assertNotEqual(self.sd.html, "")
    self.assertNotEqual(self.sd.html, str)
    self.assertNotEqual(self.sd.html, list)
    self.assertNotEqual(self.sd.html, dict)
    self.assertNotEqual(self.sd.html, int)

  def test_iterations(self):
    self.sd = simulation_objects.simulation_data(iterations="15000")
    self.assertEqual(self.sd.iterations, "15000")
    self.assertNotEqual(self.sd.iterations, "")
    self.assertNotEqual(self.sd.iterations, str)
    self.assertNotEqual(self.sd.iterations, list)
    self.assertNotEqual(self.sd.iterations, dict)
    self.assertNotEqual(self.sd.iterations, int)
    self.sd = None
    self.sd = simulation_objects.simulation_data(iterations=15000)
    self.assertEqual(self.sd.iterations, "15000")
    self.sd = None
    self.sd = simulation_objects.simulation_data(iterations=15000.75)
    self.assertEqual(self.sd.iterations, "15000")

  def test_log(self):
    self.sd = simulation_objects.simulation_data(log="1")
    self.assertEqual(self.sd.log, "1")
    self.assertNotEqual(self.sd.log, "")
    self.assertNotEqual(self.sd.log, str)
    self.assertNotEqual(self.sd.log, list)
    self.assertNotEqual(self.sd.log, dict)
    self.assertNotEqual(self.sd.log, int)
    self.sd = None
    self.sd = simulation_objects.simulation_data(iterations=15000)
    self.assertEqual(self.sd.log, "0")

  def test_name(self):
    self.sd = simulation_objects.simulation_data(name="")
    self.assertNotEqual(self.sd.name, "")
    self.assertEqual(type(self.sd.name), str)
    self.sd = None
    self.sd = simulation_objects.simulation_data(name="Borke")
    self.assertEqual(self.sd.name, "Borke")

  def test_optimize_expressions(self):
    self.sd = simulation_objects.simulation_data(optimize_expressions="1")
    self.assertEqual(self.sd.optimize_expressions, "1")
    self.assertNotEqual(self.sd.optimize_expressions, "0")
    self.assertNotEqual(self.sd.optimize_expressions, str)
    self.assertNotEqual(self.sd.optimize_expressions, list)
    self.assertNotEqual(self.sd.optimize_expressions, dict)
    self.assertNotEqual(self.sd.optimize_expressions, int)
    self.sd = None
    self.sd = simulation_objects.simulation_data(optimize_expressions=["1"])
    self.assertEqual(self.sd.optimize_expressions, "1")

  def test_ptr(self):
    self.sd = simulation_objects.simulation_data(ptr="1")
    self.assertEqual(self.sd.ptr, "1")
    self.assertNotEqual(self.sd.ptr, "0")
    self.assertNotEqual(self.sd.ptr, str)
    self.assertNotEqual(self.sd.ptr, list)
    self.assertNotEqual(self.sd.ptr, dict)
    self.assertNotEqual(self.sd.ptr, int)
    self.sd = None
    self.sd = simulation_objects.simulation_data(ptr=["1"])
    self.assertEqual(self.sd.ptr, "0")

  def test_ready_trigger(self):
    self.sd = simulation_objects.simulation_data(ready_trigger="1")
    self.assertEqual(self.sd.ready_trigger, "1")
    self.assertNotEqual(self.sd.ready_trigger, "0")
    self.assertNotEqual(self.sd.ready_trigger, str)
    self.assertNotEqual(self.sd.ready_trigger, list)
    self.assertNotEqual(self.sd.ready_trigger, dict)
    self.assertNotEqual(self.sd.ready_trigger, int)
    self.sd = None
    self.sd = simulation_objects.simulation_data(ready_trigger=["1"])
    self.assertEqual(self.sd.ready_trigger, "1")

  def test_simc_arguments(self):
    self.sd = simulation_objects.simulation_data(simc_arguments="1")
    self.assertNotEqual(self.sd.simc_arguments, "1")
    self.assertEqual(self.sd.simc_arguments, ["1"])
    self.sd = None
    self.sd = simulation_objects.simulation_data(simc_arguments=["a", "b"])
    self.assertEqual(self.sd.simc_arguments, ["a", "b"])

  def test_target_error(self):
    self.sd = simulation_objects.simulation_data(target_error="0.5")
    self.assertEqual(self.sd.target_error, "0.5")
    self.assertNotEqual(self.sd.target_error, ["1"])
    self.sd = None
    self.sd = simulation_objects.simulation_data(target_error=["a", "b"])
    self.assertEqual(self.sd.target_error, "0.1")

  def test_threads(self):
    self.sd = simulation_objects.simulation_data(threads="1.5")
    self.assertEqual(self.sd.threads, "1")
    self.assertNotEqual(self.sd.threads, "1.5")
    self.sd = None
    self.sd = simulation_objects.simulation_data(threads=["a", "b"])
    self.assertEqual(self.sd.threads, "")


##
## @brief      Tests for all methods of the simulation_data class.
##
class TestSimulationDataMethods(unittest.TestCase):

  def setUp(self):
    self.sd = simulation_objects.simulation_data()

  def tearDown(self):
    self.sd = None

  def test_is_equal(self):
    sd1 = self.sd
    sd2 = simulation_objects.simulation_data()
    self.assertTrue(sd1.is_equal(sd2))
    self.assertTrue(sd2.is_equal(sd1))
    self.assertTrue(sd1.is_equal(sd1))
    self.assertFalse(sd1.is_equal("Döner"))
    sd_calculate_scale_factors = simulation_objects.simulation_data(
      calculate_scale_factors="1"
    )
    self.assertFalse(sd_calculate_scale_factors.is_equal(sd1))
    sd_default_actions = simulation_objects.simulation_data(
      default_actions="0"
    )
    self.assertFalse(sd_default_actions.is_equal(sd1))
    sd_default_skill = simulation_objects.simulation_data(default_skill="0.5")
    self.assertFalse(sd_default_skill.is_equal(sd1))
    sd_executable = simulation_objects.simulation_data(executable="1")
    self.assertFalse(sd_executable.is_equal(sd1))
    sd_fight_style = simulation_objects.simulation_data(
      fight_style="helterskelter"
    )
    self.assertFalse(sd_fight_style.is_equal(sd1))
    sd_fixed_time = simulation_objects.simulation_data(fixed_time="0")
    self.assertFalse(sd_fixed_time.is_equal(sd1))
    sd_html = simulation_objects.simulation_data(html="test.html")
    self.assertFalse(sd_html.is_equal(sd1))
    sd_iterations = simulation_objects.simulation_data(iterations="124153")
    self.assertFalse(sd_iterations.is_equal(sd1))
    sd_log = simulation_objects.simulation_data(log="1")
    self.assertFalse(sd_log.is_equal(sd1))
    sd_optimize_expressions = simulation_objects.simulation_data(
      optimize_expressions="0"
    )
    self.assertFalse(sd_optimize_expressions.is_equal(sd1))
    sd_ptr = simulation_objects.simulation_data(ptr="1")
    self.assertFalse(sd_ptr.is_equal(sd1))
    sd_ready_trigger = simulation_objects.simulation_data(ready_trigger="0")
    self.assertFalse(sd_ready_trigger.is_equal(sd1))
    sd_target_error = simulation_objects.simulation_data(target_error="0.5")
    self.assertFalse(sd_target_error.is_equal(sd1))
    sd_threads = simulation_objects.simulation_data(threads="4")
    self.assertFalse(sd_threads.is_equal(sd1))

  def test_get_dps(self):
    self.assertEqual(self.sd.get_dps(), None)
    self.sd.set_dps(12345.8)
    self.assertTrue(self.sd.get_dps(), 12345)

  def test_set_dps(self):
    self.assertEqual(self.sd.set_dps("123"), None)
    self.assertEqual(self.sd.dps, 123)
    with self.assertRaises(simulation_objects.AlreadySetError):
      self.sd.set_dps(5678.9)
    with self.assertRaises(TypeError):
      self.sd.set_dps("5678", external="Hallo")
    self.sd = None
    self.sd = simulation_objects.simulation_data()
    with self.assertRaises(TypeError):
      self.sd.set_dps("Bonjour", external="Bonsoir")
    self.assertEqual(self.sd.get_dps(), None)
    with self.assertRaises(ValueError):
      self.sd.set_dps("Bonjour", external=False)
    self.assertEqual(self.sd.get_dps(), None)

  def test_get_avg(self):
    sd = simulation_objects.simulation_data()
    sd.set_dps(100)
    self.sd.set_dps(50)
    self.assertEqual(sd.get_avg(self.sd), 75)
    sd_empty = simulation_objects.simulation_data()
    self.assertEqual(self.sd.get_avg(sd_empty), None)

  def test_get_simulation_duration(self):
    with self.assertRaises(simulation_objects.NotStartedYetError):
      self.assertEqual(self.sd.get_simulation_duration(), None)
    self.sd.set_simulation_start_time()
    time.sleep(0.005)
    with self.assertRaises(simulation_objects.StillInProgressError):
      self.assertEqual(self.sd.get_simulation_duration(), None)
    self.sd.set_simulation_end_time()
    self.assertNotEqual(self.sd.get_simulation_duration(), None)

  def test_set_full_report(self):
    with self.assertRaises(TypeError):
      self.sd.set_full_report(1234)
    report = str(uuid.uuid4())
    self.assertEqual(self.sd.set_full_report(report), None)
    self.assertEqual(self.sd.full_report, report)

  def test_set_simulation_end_time(self):
    before = datetime.datetime.utcnow()
    self.assertEqual(self.sd.set_simulation_end_time(), None)
    after = datetime.datetime.utcnow()
    self.assertTrue(self.sd.so_simulation_end_time >= before)
    self.assertTrue(self.sd.so_simulation_end_time <= after)
    self.assertEqual(type(self.sd.so_simulation_end_time), datetime.datetime)
    with self.assertRaises(simulation_objects.AlreadySetError):
      self.sd.set_simulation_end_time()

  def test_set_simulation_start_time(self):
    self.assertEqual(self.sd.so_simulation_start_time, None)
    before = datetime.datetime.utcnow()
    self.assertEqual(self.sd.set_simulation_start_time(), None)
    after = datetime.datetime.utcnow()
    self.assertTrue(self.sd.so_simulation_start_time >= before)
    self.assertTrue(self.sd.so_simulation_start_time <= after)
    self.assertEqual(type(self.sd.so_simulation_start_time), datetime.datetime)
    self.assertEqual(self.sd.set_simulation_start_time(), None)

  def test_simulate(self):
    # travis-ci test
    # bloodytools/
    #   ./
    #   bloodytools/
    #     simulation_objects/
    #   SimulationCraft/
    #     engine/
    if os.path.isfile("./SimulationCraft/engine/simc"):
      self.sd.executable = "./SimulationCraft/engine/simc"
      self.sd.simc_arguments = [
        "./SimulationCraft/profiles/Tier21/T21_Shaman_Elemental.simc"
      ]

    # local dev test
    # SimulationCraft/
    # bloodytools/
    #   ./
    #   bloodytools/
    #     simulation_objects/
    elif os.path.isfile("../SimulationCraft/simc.exe"):
      self.sd.executable = "../SimulationCraft/simc.exe"
      self.sd.simc_arguments = [
        "../SimulationCraft/profiles/Tier21/T21_Shaman_Elemental.simc"
      ]

    # use standard values
    # SimulationCraft/
    #   bloodytools/
    #     ./
    #     bloodytools/
    #       bloodytools/
    #         simulation_objects/
    else:
      pass
    self.sd.target_error = "1.0"
    self.assertEqual(type(self.sd.simulate()), int)
    self.assertTrue(self.sd.get_dps() > 0)
    self.assertEqual(type(self.sd.so_simulation_end_time), datetime.datetime)

  def test_simulate_fail(self):
    self.sd.executable = "Not_a_correct_value"
    with self.assertRaises(FileNotFoundError):
      self.sd.simulate()


##
## @brief      Test handling of init values
##
class TestSimulationGroupDataInit(unittest.TestCase):

  def setUp(self):
    self.sd1 = simulation_objects.simulation_data()
    self.sd2 = simulation_objects.simulation_data()

  def tearDown(self):
    self.sd1 = None
    self.sd2 = None

  def test_empty(self):
    with self.assertRaises(TypeError):
      simulation_objects.simulation_group()

  def test_correct_list_input(self):
    test = simulation_objects.simulation_group([self.sd1, self.sd2])
    self.assertEqual(test.profiles[0], self.sd1)
    self.assertEqual(test.profiles[1], self.sd2)

  def test_correct_single_input(self):
    test = simulation_objects.simulation_group(self.sd1)
    self.assertEqual(test.profiles[0], self.sd1)

  def test_wrong_list_input(self):
    tmp = simulation_objects.simulation_data(iterations="5000")
    with self.assertRaises(ValueError):
      simulation_objects.simulation_group([self.sd1, tmp])
    with self.assertRaises(TypeError):
      simulation_objects.simulation_group([
        "why", "would", "anyone", "do", "this"
      ])

  def test_wrong_input_type(self):
    with self.assertRaises(TypeError):
      simulation_objects.simulation_group((self.sd1, self.sd2))


##
## @brief      Test methods of simulation_group
##
class TestSimulationGroupMethods(unittest.TestCase):

  def setUp(self):
    self.sd1 = simulation_objects.simulation_data(
      target_error="1.0", simc_arguments=["talents=2222222"]
    )
    self.sd2 = simulation_objects.simulation_data(
      target_error=1.0, simc_arguments=["talents=1111111"]
    )
    self.sg = simulation_objects.simulation_group([self.sd1, self.sd2])

  def test_selfcheck(self):
    self.assertTrue(self.sg.selfcheck())
    self.sg.profiles[1].calculate_scale_factors = "1"
    self.assertFalse(self.sg.selfcheck())

  def test_add(self):
    start = len(self.sg.profiles)
    new_data = simulation_objects.simulation_data(target_error=1.0)
    self.assertTrue(self.sg.add(new_data))
    self.assertEqual(len(self.sg.profiles), start + 1)
    with self.assertRaises(TypeError):
      self.sg.add("Bananana")

  def test_simulate_single_data(self):
    self.sd1.executable = "Not_a_correct_value"
    sole_sg1 = simulation_objects.simulation_group(self.sd1)
    with self.assertRaises(FileNotFoundError):
      sole_sg1.simulate()

    # travis-ci test
    # bloodytools/
    #   ./
    #   bloodytools/
    #     simulation_objects/
    #   SimulationCraft/
    if os.path.isfile("./SimulationCraft/simc"):
      self.sd2.executable = "./SimulationCraft/simc"
      self.sd2.simc_arguments.insert(
        0, "./SimulationCraft/profiles/Tier21/T21_Shaman_Elemental.simc"
      )

    # local dev test
    # SimulationCraft/
    # bloodytools/
    #   ./
    #   bloodytools/
    #     simulation_objects/
    elif os.path.isfile("../SimulationCraft/simc.exe"):
      self.sd2.executable = "../SimulationCraft/simc.exe"
      self.sd2.simc_arguments.insert(
        0, "../SimulationCraft/profiles/Tier21/T21_Shaman_Elemental.simc"
      )
    sole_sg2 = simulation_objects.simulation_group(self.sd2)
    self.assertTrue(sole_sg2.simulate())
    self.sg.profiles = None
    self.assertFalse(self.sg.simulate())

  def test_simulate_profilesets_wrong_path(self):
    self.sg.executable = "Not_a_correct_value"
    with self.assertRaises(FileNotFoundError):
      self.sg.simulate()
    os.remove(self.sg.filename)

  def test_simulate_profilesets_correct_path(self):
    # travis-ci test
    # bloodytools/
    #   ./
    #   bloodytools/
    #     simulation_objects/
    #   SimulationCraft/
    if os.path.isfile("./SimulationCraft/simc"):
      self.sg.executable = "./SimulationCraft/simc"
      self.sg.profiles[0].simc_arguments.insert(
        0, "./SimulationCraft/profiles/Tier21/T21_Shaman_Elemental.simc"
      )

    # local dev test
    # SimulationCraft/
    # bloodytools/
    #   ./
    #   bloodytools/
    #     simulation_objects/
    elif os.path.isfile("../SimulationCraft/simc.exe"):
      self.sg.executable = "../SimulationCraft/simc.exe"
      self.sg.profiles[0].simc_arguments.insert(
        0, "../SimulationCraft/profiles/Tier21/T21_Shaman_Elemental.simc"
      )
    self.sg.profiles[1].simc_arguments = ["talents=3333333"]
    self.assertTrue(self.sg.simulate())

  def test_simulate_profilesets_no_profiles(self):
    self.sg.profiles = None
    self.assertFalse(self.sg.simulate())


if __name__ == '__main__':
  unittest.main()
