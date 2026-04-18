export default function GrafanaDashboard() {
  return (
    <div style={{ width: "100%", height: "100vh", background: "#0f172a" }}>
      <iframe
        src="http://18.212.240.158:8084/d/ad7fb4p/new-dashboard?orgId=1&from=now-15m&to=now&timezone=browser&refresh=5s&kiosk"
        width="100%"
        height="100%"
        frameBorder="0"
        title="Grafana Dashboard"
      />
    </div>
  );
}