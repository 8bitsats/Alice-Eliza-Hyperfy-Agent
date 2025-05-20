import time
import logging
import math
from typing import List, Dict, Any

from ..core.action_system import Action

class MovementAction(Action):
    """
    Action for moving an agent to a target position
    Handles path finding and collision avoidance
    """
    def __init__(self, agent, target_position: List[float], speed: float = 1.0, precision: float = 0.1):
        super().__init__(agent=agent, priority=10)  # Movement is usually high priority
        self.target_position = target_position
        self.speed = speed
        self.precision = precision  # How close we need to get to consider it "arrived"
        self.path = [target_position]  # Simple direct path by default
        self.current_waypoint_index = 0
        self.logger = logging.getLogger(f"action.MovementAction")
        
    def start(self):
        """
        Called when the action starts execution
        """
        super().start()
        
        # Log start of movement
        self.logger.debug(f"Starting movement to {self.target_position} at speed {self.speed}")
        
        # Calculate path if we have pathfinding available
        physics_engine = getattr(self.agent, 'physics_engine', None)
        if physics_engine and hasattr(physics_engine, 'calculate_path'):
            try:
                self.path = physics_engine.calculate_path(
                    self.agent.position,
                    self.target_position
                )
                self.logger.debug(f"Calculated path with {len(self.path)} waypoints")
            except Exception as e:
                self.logger.warning(f"Failed to calculate path: {e}, using direct path")
        
    def update(self, delta_time: float) -> bool:
        """
        Update movement progress
        Returns True if the movement is complete, False otherwise
        """
        if not self.agent:
            self.fail("Agent reference is missing")
            return True
            
        # Get current waypoint
        if self.current_waypoint_index >= len(self.path):
            return True  # Path completed
            
        current_waypoint = self.path[self.current_waypoint_index]
        
        # Calculate distance to waypoint
        current_pos = self.agent.position
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(current_pos, current_waypoint)))
        
        # Update progress
        self.progress = 1.0 - (distance / self._initial_distance())
        if self.progress > 1.0:
            self.progress = 1.0
            
        # Check if we've arrived at waypoint
        if distance <= self.precision:
            self.logger.debug(f"Reached waypoint {self.current_waypoint_index}")
            self.current_waypoint_index += 1
            
            # Check if we've arrived at final destination
            if self.current_waypoint_index >= len(self.path):
                self.logger.debug(f"Reached final destination {self.target_position}")
                return True
                
            # Move to next waypoint
            return False
            
        # Calculate movement for this frame
        direction = self._normalize([b - a for a, b in zip(current_pos, current_waypoint)])
        move_distance = self.speed * delta_time
        
        # Don't overshoot
        if move_distance > distance:
            move_distance = distance
            
        # Calculate new position
        new_position = [a + (b * move_distance) for a, b in zip(current_pos, direction)]
        
        # Update agent position
        self._move_agent(new_position)
        
        return False
        
    def _move_agent(self, new_position: List[float]):
        """
        Move the agent to the new position
        This handles the actual movement mechanics (physics or direct)
        """
        # Check if we have a physics engine
        physics_engine = getattr(self.agent, 'physics_engine', None)
        
        if physics_engine and hasattr(physics_engine, 'update_agent_position'):
            # Use physics engine to move
            physics_engine.update_agent_position(self.agent.name, new_position)
        else:
            # Direct movement
            self.agent.position = new_position
            
    def _initial_distance(self) -> float:
        """
        Calculate initial distance to target (for progress calculation)
        """
        if hasattr(self, '_cached_initial_distance'):
            return self._cached_initial_distance
            
        # Calculate distance along path
        if len(self.path) <= 1:
            # Direct distance for simple path
            start_pos = self.agent.position
            end_pos = self.target_position
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(start_pos, end_pos)))
        else:
            # Sum of segments for complex path
            distance = 0
            prev_point = self.agent.position
            
            for point in self.path:
                segment_dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(prev_point, point)))
                distance += segment_dist
                prev_point = point
                
        self._cached_initial_distance = max(0.1, distance)  # Avoid division by zero
        return self._cached_initial_distance
        
    def _normalize(self, vector: List[float]) -> List[float]:
        """
        Normalize a vector to unit length
        """
        length = math.sqrt(sum(x ** 2 for x in vector))
        if length == 0:
            return [0] * len(vector)
        return [x / length for x in vector]
        
    def cancel(self):
        """
        Called when the action is cancelled
        """
        self.logger.debug(f"Movement to {self.target_position} cancelled")
        super().cancel()
