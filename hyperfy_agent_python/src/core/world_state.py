import time
import threading
import logging
from typing import Dict, List, Any, Optional, Set

class WorldObject:
    """
    Represents an object in the world with position, rotation, and properties
    """
    def __init__(self, object_id: str, object_type: str, position: List[float] = None, 
                 rotation: List[float] = None, scale: List[float] = None, properties: Dict[str, Any] = None):
        self.object_id = object_id
        self.object_type = object_type
        self.position = position or [0, 0, 0]
        self.rotation = rotation or [0, 0, 0]
        self.scale = scale or [1, 1, 1]
        self.properties = properties or {}
        self.last_updated = time.time()
        
    def update(self, position: List[float] = None, rotation: List[float] = None, 
               scale: List[float] = None, properties: Dict[str, Any] = None):
        """
        Update object properties
        """
        if position is not None:
            self.position = position
        if rotation is not None:
            self.rotation = rotation
        if scale is not None:
            self.scale = scale
        if properties is not None:
            self.properties.update(properties)
        self.last_updated = time.time()
        
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        Get a property value with optional default
        """
        return self.properties.get(key, default)
        
    def set_property(self, key: str, value: Any):
        """
        Set a property value
        """
        self.properties[key] = value
        self.last_updated = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert object to dictionary for serialization
        """
        return {
            "object_id": self.object_id,
            "object_type": self.object_type,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "properties": self.properties,
            "last_updated": self.last_updated
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldObject':
        """
        Create object from dictionary
        """
        obj = cls(
            object_id=data["object_id"],
            object_type=data["object_type"],
            position=data["position"],
            rotation=data["rotation"],
            scale=data["scale"],
            properties=data["properties"]
        )
        obj.last_updated = data.get("last_updated", time.time())
        return obj


class Player(WorldObject):
    """
    Represents a player in the world with additional player-specific properties
    """
    def __init__(self, player_id: str, username: str = None, position: List[float] = None, 
                 rotation: List[float] = None, properties: Dict[str, Any] = None):
        super().__init__(player_id, "player", position, rotation, [1, 1, 1], properties)
        self.username = username or player_id
        self.connected = True
        self.last_action_time = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert player to dictionary for serialization
        """
        data = super().to_dict()
        data["username"] = self.username
        data["connected"] = self.connected
        data["last_action_time"] = self.last_action_time
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """
        Create player from dictionary
        """
        player = cls(
            player_id=data["object_id"],
            username=data.get("username", data["object_id"]),
            position=data["position"],
            rotation=data["rotation"],
            properties=data["properties"]
        )
        player.connected = data.get("connected", True)
        player.last_action_time = data.get("last_action_time", time.time())
        player.last_updated = data.get("last_updated", time.time())
        return player


class WorldState:
    """
    Manages the state of the world including objects and players
    Provides methods for querying and updating world state
    """
    def __init__(self):
        self.objects: Dict[str, WorldObject] = {}
        self.players: Dict[str, Player] = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger("world_state")
        self.change_listeners = set()
        
    def add_object(self, obj: WorldObject) -> bool:
        """
        Add an object to the world state
        """
        with self.lock:
            if obj.object_id in self.objects:
                return False
            self.objects[obj.object_id] = obj
            self._notify_change("add_object", obj)
            return True
            
    def remove_object(self, object_id: str) -> bool:
        """
        Remove an object from the world state
        """
        with self.lock:
            if object_id not in self.objects:
                return False
            obj = self.objects.pop(object_id)
            self._notify_change("remove_object", obj)
            return True
            
    def update_object(self, object_id: str, position: List[float] = None, 
                      rotation: List[float] = None, scale: List[float] = None, 
                      properties: Dict[str, Any] = None) -> bool:
        """
        Update an existing object in the world state
        """
        with self.lock:
            if object_id not in self.objects:
                return False
            
            obj = self.objects[object_id]
            obj.update(position, rotation, scale, properties)
            self._notify_change("update_object", obj)
            return True
            
    def get_object(self, object_id: str) -> Optional[WorldObject]:
        """
        Get an object by ID
        """
        with self.lock:
            return self.objects.get(object_id)
            
    def get_objects_by_type(self, object_type: str) -> List[WorldObject]:
        """
        Get all objects of a specific type
        """
        with self.lock:
            return [obj for obj in self.objects.values() if obj.object_type == object_type]
            
    def get_objects_in_radius(self, position: List[float], radius: float) -> List[WorldObject]:
        """
        Get all objects within a radius of a position
        """
        with self.lock:
            results = []
            for obj in self.objects.values():
                distance = sum((a - b) ** 2 for a, b in zip(position, obj.position)) ** 0.5
                if distance <= radius:
                    results.append(obj)
            return results
            
    # Player-specific methods
    def add_player(self, player: Player) -> bool:
        """
        Add a player to the world state
        """
        with self.lock:
            if player.object_id in self.players:
                return False
                
            # Add to both players and objects
            self.players[player.object_id] = player
            self.objects[player.object_id] = player
            self._notify_change("add_player", player)
            return True
            
    def remove_player(self, player_id: str) -> bool:
        """
        Remove a player from the world state
        """
        with self.lock:
            if player_id not in self.players:
                return False
                
            # Remove from both players and objects
            player = self.players.pop(player_id)
            self.objects.pop(player_id, None)
            self._notify_change("remove_player", player)
            return True
            
    def get_player(self, player_id: str) -> Optional[Player]:
        """
        Get a player by ID
        """
        with self.lock:
            return self.players.get(player_id)
            
    def get_all_players(self) -> List[Player]:
        """
        Get all players
        """
        with self.lock:
            return list(self.players.values())
            
    def update_player(self, player_id: str, position: List[float] = None, 
                      rotation: List[float] = None, properties: Dict[str, Any] = None) -> bool:
        """
        Update an existing player in the world state
        """
        with self.lock:
            player = self.players.get(player_id)
            if not player:
                return False
                
            player.update(position, rotation, None, properties)
            player.last_action_time = time.time()
            self._notify_change("update_player", player)
            return True
            
    # Serialization methods
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert world state to dictionary for serialization
        """
        with self.lock:
            return {
                "objects": {obj_id: obj.to_dict() for obj_id, obj in self.objects.items()},
                "players": {player_id: player.to_dict() for player_id, player in self.players.items()},
                "timestamp": time.time()
            }
            
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load world state from dictionary
        """
        with self.lock:
            # Clear existing state
            self.objects.clear()
            self.players.clear()
            
            # Load objects
            for obj_id, obj_data in data.get("objects", {}).items():
                if obj_data["object_type"] == "player":
                    player = Player.from_dict(obj_data)
                    self.players[obj_id] = player
                    self.objects[obj_id] = player
                else:
                    self.objects[obj_id] = WorldObject.from_dict(obj_data)
                    
    # Change notification system
    def add_change_listener(self, listener):
        """
        Add a listener for world state changes
        Listener should be a callable that accepts (change_type, object)
        """
        self.change_listeners.add(listener)
        
    def remove_change_listener(self, listener):
        """
        Remove a world state change listener
        """
        self.change_listeners.discard(listener)
        
    def _notify_change(self, change_type: str, obj: WorldObject):
        """
        Notify all listeners of a world state change
        """
        for listener in self.change_listeners:
            try:
                listener(change_type, obj)
            except Exception as e:
                self.logger.error(f"Error in world state change listener: {e}")
