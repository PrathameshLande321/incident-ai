import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid
} from "recharts";

export default function App() {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
  const BASE_URL = "https://prathamesh-incident-ai.hf.space/api";

  const interval = setInterval(async () => {
    try {
      let parsed;

      try {
        const res = await fetch(`${BASE_URL}/live_monitor`);

        if (!res.ok) throw new Error("API failed");

        parsed = await res.json();
      } catch (apiErr) {
        console.warn("API failed → using fallback");

        parsed = {
          observation: {
            cpu: Math.floor(Math.random() * 100),
            memory: Math.floor(Math.random() * 100),
            db_latency: Math.floor(Math.random() * 200)
          },
          info: {
            confidence: Math.random(),
            reason: "Fallback (API not reachable)"
          }
        };
      }

      const parsedData = {
        metrics: parsed.observation,
        confidence: parsed.info?.confidence || 0,
        anomaly: (parsed.info?.confidence || 0) > 0.7,
        reason: parsed.info?.reason || "N/A"
      };

      setData(parsedData);

      const time = new Date().toLocaleTimeString();

      const newEntry = {
        time,
        cpu: parsedData.metrics.cpu,
        memory: parsedData.metrics.memory,
        db_latency: parsedData.metrics.db_latency,
        isAnomaly: parsedData.anomaly
      };

      setHistory(prev => [...prev.slice(-100), newEntry]);

      if (parsedData.anomaly) {
        setAlerts(prev => [
          { time, reason: parsedData.reason },
          ...prev.slice(0, 20)
        ]);
      }

      setLogs(prev => [
        `[${time}] CPU=${newEntry.cpu}, MEM=${newEntry.memory}, LAT=${newEntry.db_latency}`,
        ...prev.slice(0, 50)
      ]);

      setTimeline(prev => [
        {
          time,
          status: parsedData.anomaly ? "Anomaly detected" : "Normal",
          reason: parsedData.reason,
          cpu: newEntry.cpu
        },
        ...prev.slice(0, 20)
      ]);

      setConnected(true);

    } catch (err) {
      console.error("FETCH ERROR:", err);
      setConnected(false);
    }
  }, 1000);

  return () => clearInterval(interval);
}, []);

  if (!connected) return <div style={styles.loader}>Connecting...</div>;
  if (!data) return <div style={styles.loader}>Waiting for data...</div>;

const metrics = data.metrics;
const confidence = data.confidence;
const anomaly = data.anomaly;
const reason = data.reason;

  const prediction = history.map((d, i, arr) => {
    if (i === 0) return d;
    const prev = arr[i - 1];
    return {
      ...d,
      cpu_pred: d.cpu + (d.cpu - prev.cpu),
    };
  });

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Incident Dashboard</h1>

      <div style={styles.grid}>
        <Card title="CPU" value={metrics.cpu} />
        <Card title="Memory" value={metrics.memory} />
        <Card title="DB Latency" value={metrics.db_latency} />
        <Card title="Confidence" value={(confidence * 100).toFixed(0) + "%"} />
      </div>

      <Section title="System Insight">
        <InsightPanel data={data} />
      </Section>

      <Section title="Metrics">
        <Chart data={history} dataKey="cpu" />
        <Chart data={history} dataKey="memory" />
        <Chart data={history} dataKey="db_latency" />
      </Section>

      <Section title="CPU Prediction">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={prediction}>
            <CartesianGrid stroke="#1e293b" />
            <XAxis dataKey="time" hide />
            <YAxis />
            <Tooltip />
            <Line dataKey="cpu" stroke="#38bdf8" dot={false} />
            <Line dataKey="cpu_pred" stroke="#f59e0b" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Section>

      <Section title="Anomaly Heatmap">
        <Heatmap data={history} />
      </Section>

      <Section title="Service Dependency">
        <DependencyGraph />
      </Section>

      <Section title="Incident Timeline">
        <TimelinePanel timeline={timeline} />
      </Section>

      <Section title="Alert History">
        <div style={styles.panel}>
          {alerts.length === 0 && <p style={styles.muted}>No alerts</p>}
          {alerts.map((a, i) => (
            <div key={i} style={styles.row}>
              <span>{a.time}</span>
              <span>{a.reason}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Logs">
        <div style={styles.logs}>
          {logs.map((l, i) => (
            <div key={i}>{l}</div>
          ))}
        </div>
      </Section>
    </div>
  );
}

/* COMPONENTS */

function Card({ title, value }) {
  const num = parseFloat(value);

  let color = "#16a34a";
  if (num > 80) color = "#dc2626";
  else if (num > 60) color = "#f59e0b";

  return (
    <div style={{ ...styles.card, borderLeft: `4px solid ${color}` }}>
      <div style={styles.cardTitle}>{title}</div>
      <div style={styles.cardValue}>{value}</div>
    </div>
  );
}

function InsightPanel({ data }) {
  const { confidence, anomaly, reason } = data;

  let barColor = "#22c55e";
  if (confidence > 0.7) barColor = "#dc2626";
  else if (confidence > 0.5) barColor = "#f59e0b";

  return (
    <div style={styles.panel}>
      <div style={styles.row}><span>Status</span><span>{anomaly ? "Degraded" : "Healthy"}</span></div>
      <div style={styles.row}><span>Root Cause</span><span>{reason}</span></div>
      <div style={styles.row}><span>Confidence</span><span>{(confidence * 100).toFixed(1)}%</span></div>

      <div style={styles.explanation}>
        {confidence > 0.7
          ? "High confidence anomaly detected from consistent deviation."
          : confidence > 0.5
          ? "Moderate signal variation observed across metrics."
          : "Low confidence due to unstable patterns."}
      </div>

      <div style={styles.progressBar}>
        <div
          style={{
            ...styles.progressFill,
            width: `${confidence * 100}%`,
            background: barColor
          }}
        />
      </div>
    </div>
  );
}

/* 🔥 UPDATED Chart */
function Chart({ data, dataKey }) {
  return (
    <div style={styles.chart}>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid stroke="#1e293b" />
          <XAxis dataKey="time" hide />
          <YAxis />
          <Tooltip />

          <Line
            type="monotone"
            dataKey={dataKey}
            stroke="#38bdf8"
            dot={false}
          />

          <Line
            type="monotone"
            dataKey={dataKey}
            stroke="transparent"
            dot={(props) => {
              const { payload } = props;
              if (!payload.isAnomaly) return null;

              return (
                <circle
                  cx={props.cx}
                  cy={props.cy}
                  r={4}
                  fill="#dc2626"
                  stroke="#fff"
                  strokeWidth={1}
                />
              );
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/* 🔥 UPDATED Timeline */
function TimelinePanel({ timeline }) {
  return (
    <div style={styles.panel}>
      {timeline.map((t, i) => {
        const isAlert = t.status !== "Normal";

        return (
          <div
            key={i}
            style={{
              ...styles.timelineItem,
              background: isAlert ? "rgba(220,38,38,0.08)" : "transparent",
              borderRadius: 6
            }}
          >
            <div
              style={{
                ...styles.timelineDot,
                background: isAlert ? "#dc2626" : "#22c55e"
              }}
            />

            <div>
              <div style={styles.time}>{t.time}</div>

              <div style={{
                color: isAlert ? "#fca5a5" : "#e2e8f0",
                fontWeight: isAlert ? 500 : 400
              }}>
                {t.status} — CPU {t.cpu}
              </div>

              <div style={styles.reason}>{t.reason}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Heatmap({ data }) {
  return (
    <div style={styles.heatmap}>
      {data.slice(-50).map((d, i) => {
        let color = "#16a34a";
        if (d.cpu > 80) color = "#dc2626";
        else if (d.cpu > 60) color = "#f59e0b";

        return <div key={i} style={{ ...styles.heatCell, background: color }} />;
      })}
    </div>
  );
}

function DependencyGraph() {
  return (
    <div style={styles.graph}>
      <div>Frontend → API → Backend → Database</div>
      <div style={styles.muted}>Service dependency flow</div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div style={styles.section}>
      <h3 style={styles.sectionTitle}>{title}</h3>
      {children}
    </div>
  );
}

/* STYLES */

const styles = {
  container: {
    padding: 28,
    background: "#020617",
    color: "white",
    minHeight: "100vh",
    fontFamily: "Inter"
  },
  title: { marginBottom: 24 },

  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(4,1fr)",
    gap: 24
  },

  card: {
    background: "#0f172a",
    padding: 20,
    borderRadius: 12
  },

  cardTitle: {
    fontSize: 12,
    color: "#94a3b8",
    marginBottom: 6
  },

  cardValue: {
    fontSize: 22,
    fontWeight: 600
  },

  section: { marginTop: 48 },

  sectionTitle: {
    marginBottom: 14,
    fontSize: 16
  },

  chart: {
    background: "#0f172a",
    padding: 14,
    borderRadius: 12
  },

  panel: {
    background: "#0f172a",
    padding: 20,
    borderRadius: 12
  },

  row: {
    display: "flex",
    justifyContent: "space-between",
    padding: "10px 0",
    borderBottom: "1px solid #1e293b"
  },

  /* ✅ UPDATED spacing */
  timelineItem: {
    display: "flex",
    gap: 12,
    padding: "12px",
    borderBottom: "1px solid #1e293b"
  },

  timelineDot: {
    width: 8,
    height: 8,
    background: "#38bdf8",
    borderRadius: "50%",
    marginTop: 6
  },

  time: {
    fontSize: 12,
    color: "#94a3b8"
  },

  reason: {
    fontSize: 12,
    color: "#94a3b8"
  },

  logs: {
    background: "#0f172a",
    padding: 14,
    borderRadius: 12,
    maxHeight: 200,
    overflowY: "scroll",
    fontSize: 12,
    lineHeight: 1.6
  },

  heatmap: {
    display: "flex",
    gap: 3,
    padding: 12,
    background: "#0f172a",
    borderRadius: 12
  },

  heatCell: {
    width: 8,
    height: 40,
    borderRadius: 2
  },

  graph: {
    background: "#0f172a",
    padding: 20,
    borderRadius: 12
  },

  muted: {
    fontSize: 12,
    color: "#94a3b8",
    marginTop: 6
  },

  loader: {
    padding: 30
  }
};