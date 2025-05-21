# This file will contain the custom action classes.
# Planned actions: WalkRandomlyAction, StopMovingAction, UseItemAction, UnuseItemAction.
import random
import time
import logging
from typing import List, Optional

from .action_system import Action, ActionStatus
from ..physics.movement_action import MovementAction

# Placeholder for Agent class for type hinting if needed, assuming it's in ..core.agent
# from ..core.agent import Agent # Forward declaration or actual import if Agent is defined

class WalkRandomlyAction(Action):
    """
    Action for making an agent walk to random waypoints within a specified area.
    """
    def __init__(self, agent, interval: float = 5.0, max_distance: float = 10.0, duration: Optional[float] = None):
        super().__init__(agent=agent, priority=5) # Lower priority than specific movements
        self.interval = interval
        self.max_distance = max_distance
        self.duration = duration
        self._current_movement_action: Optional[MovementAction] = None
        self._next_waypoint_time: float = 0.0
        self._start_time: Optional[float] = None
        self.logger = logging.getLogger(f"action.{self.__class__.__name__}")

    def start(self):
        super().start()
        self._start_time = time.time()
        self._next_waypoint_time = time.time() # Trigger immediate waypoint selection
        self.logger.debug(f"Starting to walk randomly. Interval: {self.interval}s, Max Distance: {self.max_distance}m, Duration: {self.duration}s")

    def update(self, delta_time: float) -> bool:
        if not self.agent:
            self.fail("Agent reference is missing")
            return True

        if self.status != ActionStatus.RUNNING:
             return True # Action is not in a state to be updated (e.g. completed, failed)

        current_time = time.time()

        if self.duration is not None and self._start_time is not None:
            if current_time - self._start_time >= self.duration:
                self.logger.debug("WalkRandomlyAction duration met.")
                self.complete()
                return True
        
        # Check if current sub-movement action is done
        if self._current_movement_action:
            if self._current_movement_action.status in [ActionStatus.COMPLETED, ActionStatus.FAILED, ActionStatus.CANCELLED]:
                self._current_movement_action = None # Clear it as it's no longer active

        if self._current_movement_action is None and current_time >= self._next_waypoint_time:
            # Calculate random target position
            current_pos = self.agent.position
            random_angle = random.uniform(0, 2 * math.pi)
            random_dist = random.uniform(0, self.max_distance)
            
            # For simplicity, keeping Y the same as agent's current Y.
            # A more advanced version might sample terrain height.
            target_x = current_pos[0] + random_dist * math.cos(random_angle)
            target_y = current_pos[1] # Keep Y the same
            target_z = current_pos[2] + random_dist * math.sin(random_angle)
            target_position = [target_x, target_y, target_z]
            
            self.logger.debug(f"New random waypoint: {target_position}")
            
            # Create and queue MovementAction
            # Assuming MovementAction takes agent, target_position, and speed
            # Agent speed needs to be accessed, e.g., self.agent.default_speed or a fixed value
            agent_speed = getattr(self.agent, 'default_speed', 1.0) 
            movement = MovementAction(self.agent, target_position, speed=agent_speed)
            
            # We need to queue this action. If queue_action is on agent:
            if hasattr(self.agent, 'queue_action'):
                self.agent.queue_action(movement)
                self._current_movement_action = movement
            else:
                self.logger.error("Agent does not have queue_action method.")
                self.fail("Cannot queue MovementAction.")
                return True # Stop processing

            # Set next waypoint time
            self._next_waypoint_time = current_time + random.uniform(self.interval * 0.8, self.interval * 1.2)
            
        return False # Action is ongoing

    def cancel(self):
        if self.status == ActionStatus.RUNNING and self._current_movement_action:
            if hasattr(self.agent, 'action_system') and hasattr(self.agent.action_system, 'cancel_action'):
                self.logger.debug(f"Cancelling current sub-movement action: {self._current_movement_action.id}")
                self.agent.action_system.cancel_action(self._current_movement_action.id)
            else:
                # Fallback if direct cancellation via action_system isn't available
                self._current_movement_action.cancel() 
        super().cancel()

class StopMovingAction(Action):
    """
    Action to stop any current movement-related actions (MovementAction, WalkRandomlyAction).
    """
    def __init__(self, agent):
        super().__init__(agent=agent, priority=100) # High priority to interrupt other actions
        self.logger = logging.getLogger(f"action.{self.__class__.__name__}")

    def start(self):
        super().start()
        if not self.agent or not hasattr(self.agent, 'action_system'):
            self.logger.error("Agent or action system not found.")
            self.fail("Agent or action system missing.")
            return

        current_action = self.agent.action_system.get_current_action()

        if current_action and isinstance(current_action, (MovementAction, WalkRandomlyAction)):
            self.logger.debug(f"Requesting cancellation of action: {current_action.id} ({current_action.__class__.__name__})")
            self.agent.action_system.cancel_action(current_action.id)
        else:
            self.logger.debug("No current MovementAction or WalkRandomlyAction to stop.")
        
        self.complete() # This action is instantaneous

    def update(self, delta_time: float) -> bool:
        return True # Already completed in start()

class UseItemAction(Action):
    """
    Action to use an item (entity) in the world.
    Optionally moves the agent to the item first.
    """
    def __init__(self, agent, entity_id: str, move_to_item: bool = True):
        super().__init__(agent=agent, priority=20)
        self.entity_id = entity_id
        self.move_to_item = move_to_item
        self._sub_move_action: Optional[MovementAction] = None
        self.logger = logging.getLogger(f"action.{self.__class__.__name__}")

    def start(self):
        super().start()
        self.logger.debug(f"Attempting to use item: {self.entity_id}, move_to_item: {self.move_to_item}")

        if self.move_to_item:
            if not self.agent or not hasattr(self.agent, 'world_state') or not hasattr(self.agent, 'queue_action'):
                self.logger.error("Agent, world_state, or queue_action method missing for move_to_item.")
                self.fail("Agent misconfigured for move_to_item.")
                return

            target_entity = self.agent.world_state.get_object(self.entity_id)
            if target_entity and hasattr(target_entity, 'position'):
                target_position = target_entity.position
                self.logger.debug(f"Moving to item {self.entity_id} at {target_position}")
                agent_speed = getattr(self.agent, 'default_speed', 1.0)
                self._sub_move_action = MovementAction(self.agent, target_position, speed=agent_speed)
                self.agent.queue_action(self._sub_move_action)
                # The action will now wait for movement in its update method.
                self.status = ActionStatus.RUNNING # Explicitly set to running to wait for movement
                return # Don't complete yet
            else:
                self.logger.warning(f"Could not find item {self.entity_id} or its position for movement.")
                # Proceed to use without moving if item not found for moving, or fail, depending on desired behavior.
                # For now, let's try to use it anyway or let the "use" part fail.

        # If not moving, or if movement target wasn't found (and we decided to proceed)
        self._perform_use_action()
        if not self._sub_move_action: # Only complete if not waiting for movement
             self.complete()


    def update(self, delta_time: float) -> bool:
        if self.status != ActionStatus.RUNNING:
            return True # Action is completed, failed, or cancelled

        if self._sub_move_action:
            if self._sub_move_action.status == ActionStatus.COMPLETED:
                self.logger.debug(f"Movement to {self.entity_id} completed.")
                self._sub_move_action = None
                self._perform_use_action()
                self.complete() # Complete after performing use action
                return True
            elif self._sub_move_action.status in [ActionStatus.FAILED, ActionStatus.CANCELLED]:
                self.logger.warning(f"Movement to {self.entity_id} failed or was cancelled.")
                self._sub_move_action = None
                self.fail("Movement for UseItemAction failed.") # Fail the UseItemAction if movement fails
                return True
            else:
                # Movement is still in progress
                return False
        
        # If there was no sub_move_action, it should have been completed in start()
        # This path should ideally not be hit if logic in start() is correct.
        return True


    def _perform_use_action(self):
        """Placeholder for the actual item interaction logic."""
        self.logger.info(f"Attempting to use item: {self.entity_id}. Connector call would go here.")
        print(f"[UseItemAction] TODO: Implement Hyperfy connector call to use entity: {self.entity_id}")
        # In a real scenario, this might involve:
        # 1. Calling self.agent.connector.use_item(self.entity_id)
        # 2. Waiting for a response/callback from the connector.
        # 3. Setting status to COMPLETED or FAILED based on the response.
        # For this subtask, it's simplified to immediate completion.

    def cancel(self):
        if self._sub_move_action and self._sub_move_action.status == ActionStatus.RUNNING:
            if hasattr(self.agent, 'action_system') and hasattr(self.agent.action_system, 'cancel_action'):
                self.logger.debug(f"Cancelling sub-movement action for UseItemAction: {self._sub_move_action.id}")
                self.agent.action_system.cancel_action(self._sub_move_action.id)
            else:
                self._sub_move_action.cancel()
        super().cancel()


class UnuseItemAction(Action):
    """
    Action to unuse or release the currently held/used item.
    """
    def __init__(self, agent):
        super().__init__(agent=agent, priority=20)
        self.logger = logging.getLogger(f"action.{self.__class__.__name__}")

    def start(self):
        super().start()
        self.logger.info("Attempting to unuse/release current item. Connector call would go here.")
        print("[UnuseItemAction] TODO: Implement Hyperfy connector call to release current item.")
        # Similar to UseItemAction, this would involve a connector call and waiting for response.
        # For this subtask, it's simplified to immediate completion.
        self.complete()

    def update(self, delta_time: float) -> bool:
        return True # Already completed in start()

# Need to import math for WalkRandomlyAction
import math
