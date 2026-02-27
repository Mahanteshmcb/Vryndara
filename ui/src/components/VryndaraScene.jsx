import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useVryndara } from '../hooks/useVryndara';

const SphereObject = () => {
  const meshRef = useRef();
  // Destructure the ref object we just fixed
  const { handPosRef, lastSignal } = useVryndara();

  useFrame(() => {
    if (meshRef.current && handPosRef.current) {
      // Read the live memory directly
      const targetX = (handPosRef.current.x - 0.5) * 10;
      const targetY = (0.5 - handPosRef.current.y) * 8;

      // Speed increased to 0.4 for snappy, real-time tracking
      meshRef.current.position.x += (targetX - meshRef.current.position.x) * 0.4;
      meshRef.current.position.y += (targetY - meshRef.current.position.y) * 0.4;

      if (lastSignal?.data?.gesture === "PINCH") {
        meshRef.current.scale.lerp({ x: 1.5, y: 1.5, z: 1.5 }, 0.4);
      } else {
        meshRef.current.scale.lerp({ x: 1, y: 1, z: 1 }, 0.2);
      }
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.7, 32, 32]} />
      <meshStandardMaterial 
        color="#00f2ff" 
        emissive="#00f2ff" 
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