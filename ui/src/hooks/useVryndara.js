import { useEffect, useState, useRef } from 'react';

export const useVryndara = () => {
    // Keep the reference object alive
    const handPosRef = useRef({ x: 0.5, y: 0.5 });
    const [lastSignal, setLastSignal] = useState(null);
    const [status, setStatus] = useState('CONNECTING');

    useEffect(() => {
        const socket = new WebSocket('ws://127.0.0.1:8888/ws');

        socket.onopen = () => {
            console.log("🔗 Vryndara Bridge Connected");
            setStatus('CONNECTED');
        };

        socket.onmessage = (event) => {
            try {
                const signal = JSON.parse(event.data);

                if (signal.type === "GESTURE_EVENT" && signal.data) {
                    const nx = parseFloat(signal.data.x);
                    const ny = parseFloat(signal.data.y);
                    
                    if (!isNaN(nx) && !isNaN(ny)) {
                        // Mutate the existing ref object so the 3D loop sees the change instantly
                        handPosRef.current.x = nx;
                        handPosRef.current.y = ny;
                    }
                }
                
                // Only trigger a React re-render if there's a specific gesture (saves UI lag)
                if (signal.data && signal.data.gesture) {
                    setLastSignal(signal);
                }

            } catch (err) {
                console.error("❌ Signal Parse Error:", err);
            }
        };

        socket.onclose = () => setStatus('DISCONNECTED');
        socket.onerror = (err) => console.error("❌ WebSocket Error:", err);

        return () => socket.close();
    }, []);

    // Return the REF OBJECT, not just its current state
    return { handPosRef, lastSignal, status };
};