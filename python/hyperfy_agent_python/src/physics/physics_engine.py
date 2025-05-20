import threading
import logging
import time
from typing import Dict, List, Any, Optional, Callable

# Import PyPhysX conditionally to handle environments where it may not be installed
try:
    import pyphysx
    import numpy as np
    PHYSICS_ENABLED = True
except ImportError:
    PHYSICS_ENABLED = False

class PhysicsEngine:
    """
    Physics engine for Hyperfy agents using PyPhysX
    Provides collision detection, rigid body dynamics, and raycasting
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("physics_engine")
        self.is_running = False
        self.physics_thread = None
        self.timestep = config.get("PHYSICS_TIMESTEP", 1/60)
        self.gravity = config.get("GRAVITY", [0, -9.81, 0])
        self.agents = {}
        self.rigid_bodies = {}
        self.collision_callbacks = []
        
        # Check if physics library is available
        if not PHYSICS_ENABLED:
            self.logger.warning("PyPhysX not available. Physics capabilities will be disabled.")
            return
            
        # Initialize physics scene
        try:
            self._init_physics()
            self.logger.info("Physics engine initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize physics engine: {e}")
            return
            
    def _init_physics(self):
        """
        Initialize physics scene and components
        """
        if not PHYSICS_ENABLED:
            return
            
        # Create physics scene
        scene_flags = pyphysx.SceneFlag.ENABLE_STABILIZATION | pyphysx.SceneFlag.ENABLE_CCD
        self.scene = pyphysx.Scene(scene_flags=scene_flags)
        self.scene.set_gravity(self.gravity)
        
        # Setup physics material
        self.default_material = pyphysx.Material(static_friction=0.5, dynamic_friction=0.5, restitution=0.2)
        
        # Create ground plane if enabled
        if self.config.get("WORLD_GROUND_ENABLED", True):
            ground_plane = pyphysx.RigidStatic()
            ground_plane.attach_shape(pyphysx.Shape.create_plane(material=self.default_material, nx=0, ny=1, nz=0))
            self.scene.add_actor(ground_plane)
            self.logger.debug("Added ground plane to physics scene")
            
    def start(self):
        """
        Start the physics simulation
        """
        if not PHYSICS_ENABLED:
            self.logger.warning("Physics capabilities are disabled")
            return False
            
        if self.is_running:
            self.logger.warning("Physics engine is already running")
            return False
            
        self.is_running = True
        
        # Start physics thread
        self.physics_thread = threading.Thread(target=self._physics_worker)
        self.physics_thread.daemon = True
        self.physics_thread.start()
        
        self.logger.info("Physics engine started")
        return True
        
    def stop(self):
        """
        Stop the physics simulation
        """
        if not self.is_running:
            return
            
        self.is_running = False
        
        # Wait for thread to finish
        if self.physics_thread and self.physics_thread.is_alive():
            self.physics_thread.join(timeout=2.0)
            
        self.logger.info("Physics engine stopped")
        
    def register_agent(self, agent):
        """
        Register an agent with the physics engine
        """
        if not PHYSICS_ENABLED or agent.name in self.agents:
            return False
            
        try:
            # Create rigid body for agent
            rigid_body = pyphysx.RigidDynamic()
            
            # Create collision shape based on agent type
            # Default to capsule shape for humanoid agents
            shape = pyphysx.Shape.create_capsule(
                radius=0.5,                 # 0.5m radius
                half_height=0.5,            # 1m total height
                material=self.default_material,
                transform=pyphysx.Transform(
                    position=agent.position,
                    rotation=self._euler_to_quat(agent.rotation)
                )
            )
            
            rigid_body.attach_shape(shape)
            rigid_body.set_global_pose(
                position=agent.position,
                rotation=self._euler_to_quat(agent.rotation)
            )
            
            # Set mass properties
            rigid_body.set_mass(70.0)  # 70kg for standard agent
            
            # Add to scene
            self.scene.add_actor(rigid_body)
            self.rigid_bodies[agent.name] = rigid_body
            self.agents[agent.name] = agent
            
            # Set user data for collision callbacks
            rigid_body.set_user_data({"type": "agent", "name": agent.name})
            
            self.logger.debug(f"Registered agent {agent.name} with physics engine")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.name} with physics engine: {e}")
            return False
            
    def unregister_agent(self, agent_name: str):
        """
        Unregister an agent from the physics engine
        """
        if not PHYSICS_ENABLED or agent_name not in self.agents:
            return False
            
        try:
            # Remove rigid body from scene
            rigid_body = self.rigid_bodies.pop(agent_name, None)
            if rigid_body:
                self.scene.remove_actor(rigid_body)
                
            # Remove agent from registry
            self.agents.pop(agent_name, None)
            
            self.logger.debug(f"Unregistered agent {agent_name} from physics engine")
            return True
        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_name} from physics engine: {e}")
            return False
            
    def update_agent_position(self, agent_name: str, position: List[float], rotation: List[float] = None):
        """
        Update the position of an agent in the physics simulation
        """
        if not PHYSICS_ENABLED or agent_name not in self.rigid_bodies:
            return False
            
        try:
            rigid_body = self.rigid_bodies[agent_name]
            
            # If rotation is not provided, maintain current rotation
            if rotation is None:
                _, current_quat = rigid_body.get_global_pose()
                rigid_body.set_global_pose(position=position, rotation=current_quat)
            else:
                # Convert Euler angles to quaternion
                quat = self._euler_to_quat(rotation)
                rigid_body.set_global_pose(position=position, rotation=quat)
                
            # Update agent reference
            agent = self.agents[agent_name]
            agent.position = position
            if rotation is not None:
                agent.rotation = rotation
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to update agent position: {e}")
            return False
            
    def apply_force(self, agent_name: str, force: List[float], local: bool = False):
        """
        Apply a force to an agent
        """
        if not PHYSICS_ENABLED or agent_name not in self.rigid_bodies:
            return False
            
        try:
            rigid_body = self.rigid_bodies[agent_name]
            
            if local:
                rigid_body.add_force(force=force, mode=pyphysx.ForceMode.FORCE, local=True)
            else:
                rigid_body.add_force(force=force, mode=pyphysx.ForceMode.FORCE)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply force: {e}")
            return False
            
    def apply_impulse(self, agent_name: str, impulse: List[float], local: bool = False):
        """
        Apply an impulse to an agent
        """
        if not PHYSICS_ENABLED or agent_name not in self.rigid_bodies:
            return False
            
        try:
            rigid_body = self.rigid_bodies[agent_name]
            
            if local:
                rigid_body.add_force(force=impulse, mode=pyphysx.ForceMode.IMPULSE, local=True)
            else:
                rigid_body.add_force(force=impulse, mode=pyphysx.ForceMode.IMPULSE)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply impulse: {e}")
            return False
            
    def raycast(self, origin: List[float], direction: List[float], max_distance: float = 100.0):
        """
        Perform a raycast in the physics scene
        Returns a dict with hit information or None if no hit
        """
        if not PHYSICS_ENABLED:
            return None
            
        try:
            # Normalize direction
            dir_np = np.array(direction, dtype=np.float32)
            dir_norm = dir_np / np.linalg.norm(dir_np)
            
            # Create the ray
            ray_origin = np.array(origin, dtype=np.float32)
            
            # Perform raycast
            hit = self.scene.raycast(
                ray_origin,
                dir_norm,
                max_distance,
                pyphysx.QueryFlag.STATIC | pyphysx.QueryFlag.DYNAMIC
            )
            
            if hit.has_block:
                # Get the actor and shape that was hit
                actor = hit.block.actor
                shape = hit.block.shape
                
                # Get user data if available
                user_data = actor.get_user_data() or {}
                
                return {
                    "hit": True,
                    "position": hit.block.position.tolist(),
                    "normal": hit.block.normal.tolist(),
                    "distance": hit.block.distance,
                    "type": user_data.get("type", "unknown"),
                    "name": user_data.get("name", "unknown")
                }
            else:
                return {"hit": False}
        except Exception as e:
            self.logger.error(f"Raycast error: {e}")
            return {"hit": False, "error": str(e)}
            
    def add_collision_callback(self, callback: Callable[[str, str, Dict[str, Any]], None]):
        """
        Add a callback for collision events
        Callback will receive (object1_name, object2_name, collision_data)
        """
        if not PHYSICS_ENABLED:
            return False
            
        self.collision_callbacks.append(callback)
        return True
        
    def remove_collision_callback(self, callback: Callable):
        """
        Remove a collision callback
        """
        if not PHYSICS_ENABLED:
            return False
            
        try:
            self.collision_callbacks.remove(callback)
            return True
        except ValueError:
            return False
            
    def _physics_worker(self):
        """
        Worker thread for physics simulation
        """
        if not PHYSICS_ENABLED:
            return
            
        last_time = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                elapsed = current_time - last_time
                
                # Advance simulation with fixed timestep
                if elapsed >= self.timestep:
                    steps = int(elapsed / self.timestep)
                    for _ in range(steps):
                        self.scene.simulate(self.timestep)
                        self._process_collisions()
                        self._update_agent_states()
                    last_time = current_time - (elapsed % self.timestep)
                else:
                    # Sleep to avoid consuming too much CPU
                    time.sleep(max(0, self.timestep - elapsed))
            except Exception as e:
                self.logger.error(f"Error in physics worker: {e}")
                time.sleep(0.1)  # Avoid tight loop on error
                
    def _process_collisions(self):
        """
        Process collision events from the physics scene
        """
        if not PHYSICS_ENABLED or not self.collision_callbacks:
            return
            
        # Get collision data from simulation
        # This depends on how PyPhysX provides collision information
        # The following is a placeholder for the actual implementation
        
        for contact_pair in self.scene.get_active_contact_pairs():
            actor1 = contact_pair.actor1
            actor2 = contact_pair.actor2
            
            # Get user data
            user_data1 = actor1.get_user_data() or {}
            user_data2 = actor2.get_user_data() or {}
            
            # Extract names
            name1 = user_data1.get("name", "unknown")
            name2 = user_data2.get("name", "unknown")
            
            # Create collision data
            collision_data = {
                "contact_point": contact_pair.contact_points[0].tolist() if contact_pair.contact_points else [0, 0, 0],
                "normal": contact_pair.contact_normals[0].tolist() if contact_pair.contact_normals else [0, 1, 0],
                "impulse": contact_pair.impulses[0] if contact_pair.impulses else 0.0,
                "type1": user_data1.get("type", "unknown"),
                "type2": user_data2.get("type", "unknown")
            }
            
            # Notify callbacks
            for callback in self.collision_callbacks:
                try:
                    callback(name1, name2, collision_data)
                except Exception as e:
                    self.logger.error(f"Error in collision callback: {e}")
                    
    def _update_agent_states(self):
        """
        Update agent states based on physics simulation
        """
        if not PHYSICS_ENABLED:
            return
            
        for agent_name, rigid_body in self.rigid_bodies.items():
            try:
                # Get position and rotation from physics
                position, quat = rigid_body.get_global_pose()
                
                # Convert quaternion to Euler angles
                rotation = self._quat_to_euler(quat)
                
                # Update agent properties
                agent = self.agents.get(agent_name)
                if agent:
                    agent.position = position.tolist()
                    agent.rotation = rotation
                    
                    # Update velocity
                    linear_vel = rigid_body.get_linear_velocity()
                    agent.velocity = linear_vel.tolist()
            except Exception as e:
                self.logger.error(f"Error updating agent state: {e}")
                
    def _euler_to_quat(self, euler_angles: List[float]):
        """
        Convert Euler angles (in degrees) to quaternion
        """
        if not PHYSICS_ENABLED:
            return [0, 0, 0, 1]  # Identity quaternion
            
        # Convert degrees to radians
        radians = [angle * np.pi / 180.0 for angle in euler_angles]
        
        # Create rotation matrix from Euler angles (assuming XYZ order)
        qx = pyphysx.Quat.from_axis_angle([1, 0, 0], radians[0])
        qy = pyphysx.Quat.from_axis_angle([0, 1, 0], radians[1])
        qz = pyphysx.Quat.from_axis_angle([0, 0, 1], radians[2])
        
        # Combine rotations
        quat = qx * qy * qz
        return quat
        
    def _quat_to_euler(self, quat):
        """
        Convert quaternion to Euler angles (in degrees)
        """
        if not PHYSICS_ENABLED:
            return [0, 0, 0]  # Identity rotation
            
        # This is a simplified conversion that may have gimbal lock issues
        # A more robust implementation would be needed for production code
        
        # Extract Euler angles from quaternion
        # Assuming XYZ order for Euler angles
        x, y, z, w = quat.x, quat.y, quat.z, quat.w
        
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)
        
        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = np.copysign(np.pi / 2, sinp)  # Use 90 degrees if out of range
        else:
            pitch = np.arcsin(sinp)
            
        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        
        # Convert radians to degrees
        return [roll * 180.0 / np.pi, pitch * 180.0 / np.pi, yaw * 180.0 / np.pi]
