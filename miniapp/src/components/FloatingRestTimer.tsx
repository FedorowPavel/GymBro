import { useEffect, useState } from "react";

function formatElapsed(seconds: number): string {
  if (seconds < 60) {
    return String(seconds);
  }
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function FloatingRestTimer() {
  const [running, setRunning] = useState(false);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [elapsedSec, setElapsedSec] = useState(0);

  useEffect(() => {
    if (!running || startedAt === null) {
      return;
    }

    const tick = () => {
      setElapsedSec(Math.floor((Date.now() - startedAt) / 1000));
    };

    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [running, startedAt]);

  const handleClick = () => {
    if (!running) {
      setStartedAt(Date.now());
      setElapsedSec(0);
      setRunning(true);
      return;
    }

    setRunning(false);
    setStartedAt(null);
    setElapsedSec(0);
  };

  return (
    <button
      type="button"
      className={`rest-timer-fab ${running ? "running" : ""}`}
      onClick={handleClick}
      aria-label={running ? "Сбросить таймер" : "Запустить таймер"}
    >
      <span className="rest-timer-value">{running ? formatElapsed(elapsedSec) : "⏱"}</span>
    </button>
  );
}
