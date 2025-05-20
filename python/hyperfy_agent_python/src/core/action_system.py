import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto

class ActionStatus(Enum):
    """
    Possible states of an action in the system
    """
    PENDING = auto()   # Action is waiting to be executed
    RUNNING = auto()   # Action is currently executing
    COMPLETED = auto() # Action has completed successfully
    FAILED = auto()    # Action has failed
    CANCELLED = auto() # Action was cancelled before completion

class Action:
    """
    Base class for all agent actions
    Actions represent discrete tasks that can be performed by agents
    """
    def __init__(self, agent=None, priority: int = 0):
        self.id = str(uuid.uuid4())
        self.agent = agent
        self.priority = priority
        self.status = ActionStatus.PENDING
        self.creation_time = time.time()
        self.start_time = None
        self.completion_time = None
        self.error = None
        self.progress = 0.0  # 0.0 to 1.0
        self.logger = logging.getLogger(f"action.{self.__class__.__name__}")
        
    def start(self):
        """
        Called when the action starts execution
        """
        self.status = ActionStatus.RUNNING
        self.start_time = time.time()
        self.logger.debug(f"Starting action {self.id}")
        
    def update(self, delta_time: float) -> bool:
        """
        Update method called every frame while the action is running
        Returns True if the action is complete, False otherwise
        """
        return True  # Base implementation completes immediately
        
    def complete(self):
        """
        Called when the action completes successfully
        """
        self.status = ActionStatus.COMPLETED
        self.completion_time = time.time()
        self.progress = 1.0
        self.logger.debug(f"Action {self.id} completed in {self.completion_time - self.start_time:.2f}s")
        
    def fail(self, error: str):
        """
        Called when the action fails
        """
        self.status = ActionStatus.FAILED
        self.completion_time = time.time()
        self.error = error
        self.logger.error(f"Action {self.id} failed: {error}")
        
    def cancel(self):
        """
        Called when the action is cancelled
        """
        self.status = ActionStatus.CANCELLED
        self.completion_time = time.time()
        self.logger.debug(f"Action {self.id} cancelled")
        
    def is_completed(self) -> bool:
        """
        Check if the action is completed
        """
        return self.status == ActionStatus.COMPLETED
        
    def is_failed(self) -> bool:
        """
        Check if the action has failed
        """
        return self.status == ActionStatus.FAILED
        
    def is_cancelled(self) -> bool:
        """
        Check if the action was cancelled
        """
        return self.status == ActionStatus.CANCELLED
        
    def is_running(self) -> bool:
        """
        Check if the action is currently running
        """
        return self.status == ActionStatus.RUNNING
        
    def is_pending(self) -> bool:
        """
        Check if the action is pending execution
        """
        return self.status == ActionStatus.PENDING
        
    def is_active(self) -> bool:
        """
        Check if the action is active (either running or pending)
        """
        return self.is_running() or self.is_pending()
        
    def get_execution_time(self) -> float:
        """
        Get the total execution time of the action
        """
        if self.start_time is None:
            return 0.0
            
        end_time = self.completion_time or time.time()
        return end_time - self.start_time
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert action to dictionary for serialization
        """
        return {
            "id": self.id,
            "type": self.__class__.__name__,
            "priority": self.priority,
            "status": self.status.name,
            "creation_time": self.creation_time,
            "start_time": self.start_time,
            "completion_time": self.completion_time,
            "error": self.error,
            "progress": self.progress
        }

class ActionSystem:
    """
    Manages the execution of actions for an agent
    Supports prioritization, queuing, and parallel execution
    """
    def __init__(self, action_cooldown: float = 0.1, max_queue_size: int = 10):
        self.action_queue: List[Action] = []
        self.current_action: Optional[Action] = None
        self.completed_actions: List[Action] = []
        self.action_cooldown = action_cooldown
        self.max_queue_size = max_queue_size
        self.last_action_time = 0
        self.logger = logging.getLogger("action_system")
        self.action_hooks: Dict[str, List[Callable]] = {
            "pre_execute": [],
            "post_execute": [],
            "on_complete": [],
            "on_fail": [],
            "on_cancel": []
        }
        
    def queue_action(self, action: Action) -> bool:
        """
        Add an action to the queue
        Returns True if successful, False if queue is full
        """
        if len(self.action_queue) >= self.max_queue_size:
            self.logger.warning(f"Action queue is full, rejecting action {action.id}")
            return False
            
        self.action_queue.append(action)
        self.action_queue.sort(key=lambda a: a.priority, reverse=True)  # Higher priority first
        self.logger.debug(f"Queued action {action.id}, queue size: {len(self.action_queue)}")
        return True
        
    def cancel_action(self, action_id: str) -> bool:
        """
        Cancel a pending or running action
        """
        # Check current action
        if self.current_action and self.current_action.id == action_id:
            self.current_action.cancel()
            self._call_hooks("on_cancel", self.current_action)
            self.current_action = None
            return True
            
        # Check queue
        for i, action in enumerate(self.action_queue):
            if action.id == action_id:
                action.cancel()
                self._call_hooks("on_cancel", action)
                self.action_queue.pop(i)
                return True
                
        return False
        
    def clear_queue(self):
        """
        Cancel all pending actions
        """
        for action in self.action_queue:
            action.cancel()
            self._call_hooks("on_cancel", action)
            
        self.action_queue.clear()
        self.logger.debug("Action queue cleared")
        
    def update(self, delta_time: float):
        """
        Update the action system
        Executes the current action or starts a new one if available
        """
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_action_time < self.action_cooldown:
            return
            
        # Update current action if any
        if self.current_action:
            try:
                if self.current_action.update(delta_time):
                    # Action completed
                    self.current_action.complete()
                    self._call_hooks("on_complete", self.current_action)
                    self._call_hooks("post_execute", self.current_action)
                    self.completed_actions.append(self.current_action)
                    self.current_action = None
                    self.last_action_time = current_time
            except Exception as e:
                self.logger.error(f"Error updating action {self.current_action.id}: {e}")
                self.current_action.fail(str(e))
                self._call_hooks("on_fail", self.current_action)
                self._call_hooks("post_execute", self.current_action)
                self.completed_actions.append(self.current_action)
                self.current_action = None
                self.last_action_time = current_time
            return
            
        # Start a new action if available
        if self.action_queue:
            self.current_action = self.action_queue.pop(0)
            self._call_hooks("pre_execute", self.current_action)
            self.current_action.start()
            self.last_action_time = current_time
            
    def get_queue_count(self) -> int:
        """
        Get the number of actions in the queue
        """
        return len(self.action_queue)
        
    def is_idle(self) -> bool:
        """
        Check if the action system is idle (no running or queued actions)
        """
        return self.current_action is None and len(self.action_queue) == 0
        
    def add_hook(self, hook_type: str, callback: Callable):
        """
        Add a hook to be called at specific points in the action lifecycle
        """
        if hook_type not in self.action_hooks:
            raise ValueError(f"Invalid hook type: {hook_type}")
            
        self.action_hooks[hook_type].append(callback)
        
    def remove_hook(self, hook_type: str, callback: Callable) -> bool:
        """
        Remove a hook
        """
        if hook_type not in self.action_hooks:
            return False
            
        try:
            self.action_hooks[hook_type].remove(callback)
            return True
        except ValueError:
            return False
            
    def _call_hooks(self, hook_type: str, action: Action):
        """
        Call all hooks of a specific type
        """
        if hook_type not in self.action_hooks:
            return
            
        for callback in self.action_hooks[hook_type]:
            try:
                callback(action)
            except Exception as e:
                self.logger.error(f"Error in {hook_type} hook: {e}")
