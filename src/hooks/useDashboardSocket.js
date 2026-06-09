import { useEffect, useRef, useState } from 'react';

const WS_BASE_URL = 'ws://localhost:8000/api/v1/ws/dashboard';

export function useDashboardSocket(onRefresh) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const retryCount = useRef(0);
  const maxRetries = 10;
  const pingInterval = useRef(null);
  const onRefreshRef = useRef(onRefresh);

  useEffect(() => {
    onRefreshRef.current = onRefresh;
  }, [onRefresh]);

  useEffect(() => {
    let isMounted = true;
    let reconnectTimeout = null;

    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
        return;
      }

      console.log('Connecting to WebSocket...');
      const ws = new WebSocket(WS_BASE_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!isMounted) return;
        console.log('WebSocket connected.');
        setIsConnected(true);
        retryCount.current = 0; 
        
        pingInterval.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        if (!isMounted) return;
        if (event.data === "refresh") {
          console.log('WebSocket trigger: refresh');
          if (onRefreshRef.current) {
            onRefreshRef.current();
          }
        } else if (event.data === "pong") {
          // Heartbeat ack
        }
      };

      ws.onclose = () => {
        if (!isMounted) return;
        console.log('WebSocket disconnected.');
        setIsConnected(false);
        if (pingInterval.current) clearInterval(pingInterval.current);
        wsRef.current = null;
        
        if (retryCount.current < maxRetries) {
          const timeout = Math.min(1000 * Math.pow(2, retryCount.current), 30000);
          retryCount.current += 1;
          console.log(`Reconnecting in ${timeout}ms...`);
          reconnectTimeout = setTimeout(connect, timeout);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
        ws.close();
      };
    };

    connect();

    return () => {
      isMounted = false;
      if (pingInterval.current) clearInterval(pingInterval.current);
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.onclose = null; 
        wsRef.current.onerror = null; 
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []); // Empty dependency array prevents reconnect loops on render

  return { isConnected };
}
