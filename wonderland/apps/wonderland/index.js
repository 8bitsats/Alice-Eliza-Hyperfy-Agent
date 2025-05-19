import React, {
  useEffect,
  useRef,
} from 'react'

import {
  DEG2RAD,
  useSignal,
  useSyncState,
  useWorld,
} from 'hyperfy'

import { Tween } from './Tween'

export default function Wonderland() {
  const world = useWorld();
  const rabbitholeRef = useRef();
  const doorRef = useRef();
  const [state, dispatch] = useSyncState(state => state);

  // Handle door animation
  useEffect(() => {
    const door = doorRef.current;
    if (!door) return;
    
    const tween = state.doorOpen ? openDoorTween : closeDoorTween;
    return world.onUpdate(delta => {
      tween.set(world.getServerTime() - state.doorTime);
      door.setRotationY(tween.value.rotation * DEG2RAD);
    });
  }, [state.doorTime, state.doorOpen]);

  // Handle rabbit hole animation
  useEffect(() => {
    const rabbithole = rabbitholeRef.current;
    const swirl = swirlTween;
    swirl.loop();
    return world.onUpdate(delta => {
      swirl.set(world.getServerTime() * 0.5);
      rabbithole.setRotationY(swirl.value.rotation * DEG2RAD);
    });
  }, []);

  // Toggle door open/close
  function toggleDoor() {
    if (state.doorOpen === undefined) return;
    const time = world.getServerTime();
    dispatch('setDoorOpen', !state.doorOpen, time);
  }

  // Teleport player into rabbit hole
  function enterRabbitHole(e) {
    if (e.avatar) {
      world.teleportPlayer(e.avatar.playerId, [0, 5, 0]);
      world.emitSignal("RabbitHoleEntered", { playerId: e.avatar.playerId });
    }
  }

  // Handle signals from other apps or systems
  useSignal("WonderlandEvent", (data) => {
    console.log("Wonderland event received:", data);
  });

  return (
    <app>
      {/* Grass ground */}
      <rigidbody type="static">
        <box 
          size={[100, 0.1, 100]} 
          color="#7cbb78" 
          position={[0, -0.05, 0]}
        />

        {/* Checkerboard pattern for a specific area */}
        {[...Array(8)].map((_, row) => 
          [...Array(8)].map((_, col) => {
            const isLight = (row + col) % 2 === 0;
            return (
              <box 
                key={`${row}-${col}`}
                size={[2, 0.05, 2]} 
                color={isLight ? "#f0f0f0" : "#303030"} 
                position={[
                  row * 2 - 7,
                  0.01,
                  col * 2 - 7
                ]}
              />
            );
          })
        )}
      </rigidbody>
      
      {/* Decorative elements */}
      <group position={[0, 0, 0]}>
        {/* Giant mushrooms */}
        <group position={[-5, 0, -5]}>
          <cylinder 
            height={2} 
            radius={0.5} 
            color="#f5d7b2" 
            position={[0, 1, 0]}
          />
          <cylinder 
            height={0.5} 
            radius={2} 
            color="#e05e5e" 
            position={[0, 2.5, 0]}
            segments={12}
          />
        </group>

        <group position={[5, 0, -8]}>
          <cylinder 
            height={1.5} 
            radius={0.4} 
            color="#f5d7b2" 
            position={[0, 0.75, 0]}
          />
          <cylinder 
            height={0.4} 
            radius={1.6} 
            color="#e05e5e" 
            position={[0, 1.8, 0]}
            segments={12}
          />
        </group>

        <group position={[-7, 0, 3]}>
          <cylinder 
            height={3} 
            radius={0.6} 
            color="#f5d7b2" 
            position={[0, 1.5, 0]}
          />
          <cylinder 
            height={0.6} 
            radius={2.5} 
            color="#e05e5e" 
            position={[0, 3.3, 0]}
            segments={12}
          />
        </group>

        {/* Tea party table */}
        <group position={[8, 0, 6]}>
          <cylinder 
            height={0.1} 
            radius={2} 
            color="#8B4513" 
            position={[0, 0.85, 0]}
          />
          <cylinder 
            height={0.8} 
            radius={0.3} 
            color="#8B4513" 
            position={[0, 0.4, 0]}
          />
          <box 
            size={[0.5, 0.15, 0.5]} 
            color="#FFF" 
            position={[-0.8, 1, -0.5]}
          />
          <cylinder 
            height={0.25} 
            radius={0.25} 
            color="#FFF" 
            position={[0.5, 1.05, 0.2]}
          />
        </group>

        {/* Flowers */}
        {[...Array(20)].map((_, i) => {
          const angle = (i / 20) * Math.PI * 2;
          const radius = 15 + Math.random() * 5;
          const x = Math.cos(angle) * radius;
          const z = Math.sin(angle) * radius;
          const flowerColor = ["#ff6b6b", "#ffb56b", "#ffee6b", "#6bffd4", "#6b88ff"][
            Math.floor(Math.random() * 5)
          ];
          
          return (
            <group key={i} position={[x, 0, z]}>
              <cylinder 
                height={0.8} 
                radius={0.05} 
                color="#7cbb78" 
                position={[0, 0.4, 0]}
              />
              <sphere 
                radius={0.2} 
                color={flowerColor} 
                position={[0, 0.9, 0]}
              />
            </group>
          );
        })}

      </group>

        {/* Cheshire cat's tree */}
      <group position={[12, 0, -10]}>
        <cylinder 
          height={5} 
          radius={1} 
          color="#8B4513" 
          position={[0, 2.5, 0]}
        />
        <sphere 
          radius={3} 
          color="#3a5f38" 
          position={[0, 6, 0]}
        />
        {/* Add Cheshire cat smile */}
        <box 
          size={[1.8, 0.2, 0.2]} 
          color="#FFFFFF" 
          position={[0, 5, 2.8]}
        />
        <box 
          size={[0.3, 0.3, 0.2]} 
          color="#FFFFFF" 
          position={[-1.0, 4.8, 2.8]}
          rotation={[0, 0, -45 * DEG2RAD]}
        />
        <box 
          size={[0.3, 0.3, 0.2]} 
          color="#FFFFFF" 
          position={[1.0, 4.8, 2.8]}
          rotation={[0, 0, 45 * DEG2RAD]}
        />
      </group>

      {/* Looking glass door */}
      <group position={[-12, 0, 8]}>
        <box 
          size={[0.3, 4, 2]} 
          color="#8B4513" 
          position={[0, 2, 0]}
        />
        <box 
          ref={doorRef}
          size={[0.1, 3, 1.5]} 
          color="#a3ccf1" 
          position={[0.2, 2, 0]}
          onClick={toggleDoor}
        />
      </group>

      {/* Rabbit hole */}
      <group position={[0, 0, 15]}>
        <cylinder 
          height={1} 
          radius={2} 
          color="#331a00" 
          position={[0, -0.5, 0]}
        />
        <cylinder 
          ref={rabbitholeRef}
          height={5} 
          radius={1.2} 
          color="#000000" 
          position={[0, -2.5, 0]}
          onClick={enterRabbitHole}
        />
        <text 
          value="Rabbit Hole" 
          color="#FFFFFF" 
          position={[0, 0.5, 0]}
          scale={[0.5, 0.5, 0.5]}
        />
      </group>

      {/* Playing cards */}
      <group position={[-5, 0, 10]}>
        {[...Array(5)].map((_, i) => {
          const offset = i * 0.3;
          return (
            <box
              key={`card-${i}`}
              size={[1.5, 2, 0.05]}
              color="#FFFFFF"
              position={[offset, 1 + Math.random() * 0.5, offset]}
              rotation={[
                Math.random() * 30 * DEG2RAD,
                Math.random() * 30 * DEG2RAD,
                Math.random() * 30 * DEG2RAD
              ]}
            />
          );
        })}
      </group>
    </app>
  );
}

const initialState = {
  doorOpen: false,
  doorTime: -9999,
};

export function getStore(state = initialState) {
  return {
    state,
    actions: {
      setDoorOpen(state, doorOpen, doorTime) {
        state.doorOpen = doorOpen;
        state.doorTime = doorTime;
      },
    },
  };
}

// Animations
const openDoorTween = new Tween({ rotation: 0 }).to({ rotation: 120 }, 1.5, Tween.QUAD_IN_OUT);
const closeDoorTween = new Tween({ rotation: 120 }).to({ rotation: 0 }, 1.5, Tween.QUAD_IN_OUT);
const swirlTween = new Tween({ rotation: 0 }).to({ rotation: 360 }, 5, Tween.LINEAR);
