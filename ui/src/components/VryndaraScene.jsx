import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three'; // Required for Color and Vector3 instances
import { useVryndara } from '../hooks/useVryndara';

const SphereObject = () => {
  const meshRef = useRef();
  const { handPosRef, lastSignal } = useVryndara();

  // We add 'state' here to use state.clock for the pulse
  useFrame((state) => {
    if (meshRef.current && handPosRef.current) {
      const targetX = (handPosRef.current.x - 0.5) * 10;
      const targetY = (0.5 - handPosRef.current.y) * 8;

      meshRef.current.position.x += (targetX - meshRef.current.position.x) * 0.4;
      meshRef.current.position.y += (targetY - meshRef.current.position.y) * 0.4;

      // --- BRAIN FEEDBACK LOGIC ---
      const isThinking = lastSignal?.status === "THINKING";

      if (isThinking) {
        // High-energy Purple Pulse
        meshRef.current.material.color.lerp(new THREE.Color("#9d00ff"), 0.1);
        meshRef.current.material.emissive.lerp(new THREE.Color("#9d00ff"), 0.1);
        
        // Pulsate scale using sine wave
        const s = 1.2 + Math.sin(state.clock.elapsedTime * 10) * 0.1;
        meshRef.current.scale.set(s, s, s);
      } else if (lastSignal?.data?.gesture === "PINCH") {
        // Interaction Cyan
        meshRef.current.material.color.lerp(new THREE.Color("#00f2ff"), 0.1);
        meshRef.current.material.emissive.lerp(new THREE.Color("#00f2ff"), 0.1);
        meshRef.current.scale.lerp(new THREE.Vector3(1.5, 1.5, 1.5), 0.4);
      } else {
        // Default Neutral Cyan
        meshRef.current.material.color.lerp(new THREE.Color("#006677"), 0.1);
        meshRef.current.material.emissive.lerp(new THREE.Color("#006677"), 0.1);
        meshRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.2);
      }
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.7, 32, 32]} />
      <meshStandardMaterial 
        emissiveIntensity={2} 
        wireframe={true} 
      />
    </mesh>
  );
};

const VryndaraScene = () => {
  return (
    <div style={{ width: '100%', height: '100%', minHeight: '500px', background: '#050505', position: 'relative' }}>
      <Canvas camera={{ position: [0, 0, 5] }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <SphereObject />
      </Canvas>
    </div>
  );
};

export default VryndaraScene;