import unittest
from unittest.mock import MagicMock, patch
import time
import math

# Assuming PYTHONPATH is set to make 'hyperfy_agent_python' a top-level package
# If running with `python -m unittest discover`, this structure should work.
from hyperfy_agent_python.src.core.action_system import ActionStatus, Action
from hyperfy_agent_python.src.core.custom_actions import WalkRandomlyAction, StopMovingAction, UseItemAction, UnuseItemAction
from hyperfy_agent_python.src.physics.movement_action import MovementAction
# AgentBase and WorldState might not be strictly needed if MockAgent is comprehensive
# from hyperfy_agent_python.src.core.agent_base import AgentBase 
# from hyperfy_agent_python.src.core.world_state import WorldState, WorldObject

class MockAgent:
    def __init__(self, name="TestAgent"):
        self.name = name
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0] # pitch, yaw, roll
        self.action_system = MockActionSystem(self) # Pass agent reference
        self.queue_action = MagicMock(side_effect=self.action_system.queue_action) # Delegate to mock
        self.world_state = MockWorldState()
        self.config = {"VOICE_CONFIDENCE_THRESHOLD": 0.7} 
        self.logger = MagicMock()
        self.default_speed = 1.0 # For MovementAction in WalkRandomly
        self.physics_engine = None # MovementAction will update position directly

    def say(self, text):
        # print(f"Agent {self.name} says: {text}") # For debugging tests
        pass

class MockActionSystem:
    def __init__(self, agent): # Accept agent
        self.agent = agent # Store agent reference
        self.current_action: Optional[Action] = None
        self.action_queue: List[Action] = []
        self._cancel_action_mock = MagicMock() # Internal mock for assertions

    def queue_action(self, action: Action):
        action.agent = self.agent # Ensure action has agent context
        self.action_queue.append(action)

    def cancel_action(self, action_id: str):
        self._cancel_action_mock(action_id) # Call internal mock
        # Simulate cancellation for testing StopMovingAction
        if self.current_action and self.current_action.id == action_id:
            if hasattr(self.current_action, 'cancel'):
                self.current_action.cancel() # This will set its status to CANCELLED
            self.current_action = None
        self.action_queue = [a for a in self.action_queue if a.id != action_id]


class MockWorldState:
    def __init__(self):
        self.objects = {}
    def get_object(self, entity_id):
        return self.objects.get(entity_id)
    def add_object(self, obj): # obj should have an 'id' or 'object_id' attribute
        # Assuming obj has an attribute like 'id' or 'name' to be used as key
        obj_id = getattr(obj, 'id', getattr(obj, 'name', None))
        if obj_id:
            self.objects[obj_id] = obj


class MockEntity: # For UseItemAction
    def __init__(self, entity_id, position):
        self.id = entity_id
        self.name = entity_id # Some actions might use name
        self.position = position


class TestMovementActionOrientation(unittest.TestCase):
    def setUp(self):
        self.agent = MockAgent()
        # MovementAction directly updates agent.position and agent.rotation if physics_engine is None

    def test_face_positive_x(self):
        target_pos = [1.0, 0.0, 0.0]
        action = MovementAction(self.agent, target_pos, speed=1)
        action.start() # Sets status to RUNNING
        action.update(0.1) 
        self.assertAlmostEqual(self.agent.rotation[1], 90.0, places=1) 

    def test_face_negative_x(self):
        target_pos = [-1.0, 0.0, 0.0]
        action = MovementAction(self.agent, target_pos, speed=1)
        action.start()
        action.update(0.1)
        self.assertAlmostEqual(self.agent.rotation[1], -90.0, places=1)

    def test_face_positive_z(self):
        target_pos = [0.0, 0.0, 1.0]
        action = MovementAction(self.agent, target_pos, speed=1)
        action.start()
        action.update(0.1)
        self.assertAlmostEqual(self.agent.rotation[1], 0.0, places=1)

    def test_face_negative_z(self):
        target_pos = [0.0, 0.0, -1.0]
        action = MovementAction(self.agent, target_pos, speed=1)
        action.start()
        action.update(0.1)
        self.assertAlmostEqual(self.agent.rotation[1], 180.0, places=1)

    def test_face_positive_x_positive_z(self): # Target: (1,0,1)
        target_pos = [1.0, 0.0, 1.0]
        action = MovementAction(self.agent, target_pos, speed=1)
        action.start()
        action.update(0.1)
        self.assertAlmostEqual(self.agent.rotation[1], 45.0, places=1)

    def test_no_rotation_if_target_is_current_pos(self):
        target_pos = [0.0, 0.0, 0.0] # Agent is already at (0,0,0)
        initial_yaw = self.agent.rotation[1]
        action = MovementAction(self.agent, target_pos, speed=1)
        action.start()
        action.update(0.1)
        # If direction is zero vector, atan2(0,0) is 0, so yaw might become 0.
        # Depending on implementation, it might retain previous yaw or default to 0.
        # The current MovementAction calculates yaw if direction is non-zero.
        # If direction is zero (target reached or target is current pos), yaw is not updated.
        # Let's check it doesn't change from initial if no movement.
        # However, the current code calculates distance first. If distance is <= precision, it completes.
        # If precision is 0.1, and target is 0,0,0, it completes immediately.
        self.assertTrue(action.is_completed()) # Should complete as distance is 0
        self.assertAlmostEqual(self.agent.rotation[1], initial_yaw, places=1) # Yaw should not change


class TestWalkRandomlyAction(unittest.TestCase):
    def setUp(self):
        self.agent = MockAgent()

    @patch('time.time', MagicMock(return_value=100.0))
    @patch('random.uniform') # Mock random.uniform
    @patch('random.choice') # Mock random.choice if used by any sub-actions for other things
    @patch('math.cos', MagicMock(return_value=0.5)) # Mock math.cos
    @patch('math.sin', MagicMock(return_value=0.5)) # Mock math.sin
    def test_walk_randomly_queues_movement(self, mock_random_uniform, mock_random_choice):
        # Configure random.uniform to return predictable values
        mock_random_uniform.side_effect = [
            1.0, # For random_angle or random_dist calculation in WalkRandomlyAction
            5.0, # For random_dist
            10.0 # For next_waypoint_time randomization factor
        ]

        action = WalkRandomlyAction(self.agent, interval=0.1, max_distance=5, duration=1.0)
        action.start()
        
        self.assertEqual(action.status, ActionStatus.RUNNING)
        self.assertEqual(time.time(), 100.0)
        self.assertEqual(action._next_waypoint_time, 100.0) # Should set to current time initially

        # First update, should queue a movement
        action.update(0.01) 
        self.agent.queue_action.assert_called_once()
        queued_action = self.agent.queue_action.call_args[0][0]
        self.assertIsInstance(queued_action, MovementAction)
        
        # Simulate movement completion for next step
        action._current_movement_action = queued_action # Manually assign as queue_action is mocked
        action._current_movement_action.status = ActionStatus.COMPLETED 
        
        # Second update, after interval, should queue another
        time.time.return_value = 100.2 # Advance time past interval (0.1 * ~1.0 from random.uniform)
        action.update(0.01)
        self.assertEqual(self.agent.queue_action.call_count, 2)

    @patch('time.time', MagicMock(return_value=100.0))
    def test_walk_randomly_duration(self):
        action = WalkRandomlyAction(self.agent, interval=0.1, max_distance=5, duration=0.5)
        action.start()
        self.assertFalse(action.is_completed())
        
        time.time.return_value = 100.4 # Still within duration
        action.update(0.01)
        self.assertFalse(action.is_completed())

        time.time.return_value = 100.6 # Advance time past duration (100.0 + 0.5 = 100.5)
        action.update(0.01) # This update call processes the time check
        self.assertTrue(action.is_completed())
        self.assertEqual(action.status, ActionStatus.COMPLETED)

    @patch('time.time', MagicMock(return_value=100.0))
    def test_walk_randomly_cancel(self):
        action = WalkRandomlyAction(self.agent, interval=0.1, max_distance=5, duration=1.0)
        action.start()
        action.update(0.01) # Queues a movement action
        
        # Assume the movement action was "queued" and is now the _current_movement_action
        mock_sub_movement = MagicMock(spec=MovementAction)
        mock_sub_movement.id = "sub_move_id_123"
        mock_sub_movement.status = ActionStatus.RUNNING
        action._current_movement_action = mock_sub_movement
        
        action.cancel()
        self.assertEqual(action.status, ActionStatus.CANCELLED)
        # Check if the sub-movement action's cancel was called
        # In the custom_actions.py, cancel calls self.agent.action_system.cancel_action
        # So we check the mock on agent.action_system
        self.agent.action_system._cancel_action_mock.assert_called_with(mock_sub_movement.id)


class TestStopMovingAction(unittest.TestCase):
    def setUp(self):
        self.agent = MockAgent()

    def test_stop_moving_cancels_current_movement(self):
        # Setup a mock current action that is a MovementAction
        mock_movement_action = MovementAction(self.agent, [1,1,1])
        mock_movement_action.id = "current_move_action_id"
        mock_movement_action.status = ActionStatus.RUNNING 
        self.agent.action_system.current_action = mock_movement_action
        
        action = StopMovingAction(self.agent)
        action.start() # This should call cancel_action on the mock_movement_action
        
        self.agent.action_system._cancel_action_mock.assert_called_with("current_move_action_id")
        self.assertEqual(action.status, ActionStatus.COMPLETED)
        # Verify the mock_movement_action itself was cancelled
        self.assertEqual(mock_movement_action.status, ActionStatus.CANCELLED)

    def test_stop_moving_no_current_action(self):
        self.agent.action_system.current_action = None
        action = StopMovingAction(self.agent)
        action.start()
        self.agent.action_system._cancel_action_mock.assert_not_called()
        self.assertEqual(action.status, ActionStatus.COMPLETED)

    def test_stop_moving_non_movement_action(self):
        mock_other_action = Action(self.agent) # A generic action
        mock_other_action.id = "other_action_id"
        self.agent.action_system.current_action = mock_other_action

        action = StopMovingAction(self.agent)
        action.start()
        self.agent.action_system._cancel_action_mock.assert_not_called() # Should not try to cancel non-movement
        self.assertEqual(action.status, ActionStatus.COMPLETED)


class TestUseItemAction(unittest.TestCase):
    def setUp(self):
        self.agent = MockAgent()
        self.item_id = "test_item"
        self.item_pos = [5.0, 0.0, 5.0]
        self.mock_item = MockEntity(self.item_id, self.item_pos)
        self.agent.world_state.add_object(self.mock_item)

    @patch('hyperfy_agent_python.src.core.custom_actions.UseItemAction._perform_use_action')
    def test_use_item_no_move(self, mock_perform_use):
        action = UseItemAction(self.agent, self.item_id, move_to_item=False)
        action.start()
        
        mock_perform_use.assert_called_once()
        self.agent.queue_action.assert_not_called() # No movement action should be queued
        self.assertEqual(action.status, ActionStatus.COMPLETED)

    @patch('hyperfy_agent_python.src.core.custom_actions.UseItemAction._perform_use_action')
    def test_use_item_with_move_success(self, mock_perform_use):
        action = UseItemAction(self.agent, self.item_id, move_to_item=True)
        action.start()

        self.agent.queue_action.assert_called_once()
        queued_move_action = self.agent.queue_action.call_args[0][0]
        self.assertIsInstance(queued_move_action, MovementAction)
        self.assertEqual(queued_move_action.target_position, self.item_pos)
        
        # Action should be RUNNING, waiting for movement
        self.assertEqual(action.status, ActionStatus.RUNNING) 
        mock_perform_use.assert_not_called() # Not called yet

        # Simulate movement completion
        action._sub_move_action = queued_move_action # Manually assign
        action._sub_move_action.status = ActionStatus.COMPLETED
        
        action.update(0.1) # Update to process movement completion
        
        mock_perform_use.assert_called_once()
        self.assertEqual(action.status, ActionStatus.COMPLETED)

    @patch('hyperfy_agent_python.src.core.custom_actions.UseItemAction._perform_use_action')
    def test_use_item_with_move_fail(self, mock_perform_use):
        action = UseItemAction(self.agent, self.item_id, move_to_item=True)
        action.start()

        self.agent.queue_action.assert_called_once()
        queued_move_action = self.agent.queue_action.call_args[0][0]
        action._sub_move_action = queued_move_action

        # Simulate movement failure
        action._sub_move_action.status = ActionStatus.FAILED
        
        action.update(0.1)
        
        mock_perform_use.assert_not_called()
        self.assertEqual(action.status, ActionStatus.FAILED)

    def test_use_item_item_not_found_for_move(self):
        action = UseItemAction(self.agent, "non_existent_item", move_to_item=True)
        # action.logger = MagicMock() # Suppress logger warning for cleaner test output if needed
        action.start()
        
        self.agent.queue_action.assert_not_called() # No movement if item not found
        # Current implementation proceeds to _perform_use_action even if item not found for move.
        # This might be desired, or it might be a fail case. Test assumes current behavior.
        # If it should fail if item for move not found:
        # self.assertEqual(action.status, ActionStatus.FAILED)
        # self.assertIn("Could not find item", action.error) # or similar check
        
        # Based on current code in custom_actions.py:
        # It logs a warning but then calls _perform_use_action and completes.
        self.assertEqual(action.status, ActionStatus.COMPLETED)


class TestUnuseItemAction(unittest.TestCase):
    def setUp(self):
        self.agent = MockAgent()

    # UnuseItemAction is very simple, just calls a placeholder and completes
    @patch('builtins.print') # Mock print to check the TODO message
    def test_unuse_item_completes(self, mock_print):
        action = UnuseItemAction(self.agent)
        action.start()
        
        self.assertEqual(action.status, ActionStatus.COMPLETED)
        # Check if the placeholder print was called
        mock_print.assert_any_call("[UnuseItemAction] TODO: Implement Hyperfy connector call to release current item.")


if __name__ == '__main__':
    unittest.main()
# Add typing for stricter linting if desired
from typing import List, Optional, Any
