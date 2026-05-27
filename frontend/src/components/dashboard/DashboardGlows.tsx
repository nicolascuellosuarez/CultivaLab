import {
  DASHBOARD_GLOW_LAYERS,
  type DashboardGlowKey,
} from "./glow-presets";

export function DashboardGlows({ pageKey }: { pageKey: DashboardGlowKey }) {
  const layers = DASHBOARD_GLOW_LAYERS[pageKey] ?? DASHBOARD_GLOW_LAYERS.dashboard;

  return (
    <div
      className="pointer-events-none fixed inset-0 overflow-hidden"
      aria-hidden
    >
      {layers.map((layer, i) => (
        <div key={i} className={layer.className} />
      ))}
    </div>
  );
}
