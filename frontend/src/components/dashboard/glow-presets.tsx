export type DashboardGlowKey =
  | "dashboard"
  | "crops"
  | "crops-new"
  | "simulate"
  | "stats"
  | "simulations"
  | "profile"
  | "admin"
  | "admin-users"
  | "admin-crops"
  | "admin-simulations"
  | "admin-sim-detail"
  | "admin-crop-types"
  | "admin-profile"
  | "admin-crop-stats";

type GlowLayer = {
  className: string;
};

export const DASHBOARD_GLOW_LAYERS: Record<DashboardGlowKey, GlowLayer[]> = {
  dashboard: [
    { className: "absolute -left-24 top-32 h-80 w-[520px] rounded-full bg-cultiva-green/22 blur-[100px]" },
    { className: "absolute right-0 top-20 h-64 w-96 rounded-full bg-cultiva-green/14 blur-[90px]" },
    { className: "absolute bottom-24 left-1/3 h-48 w-[480px] rounded-full bg-cultiva-green/12 blur-[80px]" },
  ],
  crops: [
    { className: "absolute left-[10%] top-16 h-72 w-[600px] -rotate-12 rounded-full bg-cultiva-green/20 blur-[95px]" },
    { className: "absolute -right-16 bottom-32 h-56 w-80 rounded-full bg-cultiva-green/16 blur-[85px]" },
  ],
  "crops-new": [
    { className: "absolute -right-32 top-40 h-[420px] w-[500px] rotate-[18deg] rounded-full bg-cultiva-green/24 blur-[110px]" },
    { className: "absolute left-8 bottom-20 h-44 w-96 rounded-full bg-cultiva-green/12 blur-[75px]" },
  ],
  simulate: [
    { className: "absolute left-1/2 top-0 h-64 w-[700px] -translate-x-1/2 rounded-full bg-cultiva-green/18 blur-[100px]" },
    { className: "absolute -left-20 top-1/2 h-96 w-[400px] rounded-full bg-cultiva-green/20 blur-[90px]" },
  ],
  stats: [
    { className: "absolute right-[5%] top-24 h-80 w-[550px] rounded-full bg-cultiva-green/22 blur-[105px]" },
    { className: "absolute bottom-16 left-16 h-52 w-72 rounded-full bg-cultiva-green/14 blur-[80px]" },
  ],
  simulations: [
    { className: "absolute -left-28 bottom-40 h-[380px] w-[480px] rotate-[15deg] rounded-full bg-cultiva-green/21 blur-[95px]" },
    { className: "absolute right-12 top-28 h-60 w-[420px] rounded-full bg-cultiva-green/15 blur-[85px]" },
  ],
  profile: [
    { className: "absolute left-1/4 top-20 h-56 w-[500px] rounded-full bg-cultiva-green/17 blur-[90px]" },
    { className: "absolute -right-24 bottom-24 h-72 w-96 rounded-full bg-cultiva-green/19 blur-[95px]" },
  ],
  admin: [
    { className: "absolute left-1/2 -top-20 h-80 w-[760px] -translate-x-1/2 rounded-full bg-cultiva-green/26 blur-[110px]" },
    { className: "absolute -left-32 top-1/2 h-96 w-[520px] rounded-full bg-cultiva-green/18 blur-[100px]" },
    { className: "absolute right-8 bottom-16 h-48 w-80 rounded-full bg-cultiva-green/12 blur-[75px]" },
  ],
  "admin-users": [
    { className: "absolute -right-36 top-12 h-[460px] w-[540px] rotate-[20deg] rounded-full bg-cultiva-green/25 blur-[115px]" },
    { className: "absolute left-12 bottom-28 h-44 w-88 rounded-full bg-cultiva-green/13 blur-[80px]" },
  ],
  "admin-crops": [
    { className: "absolute left-[15%] top-24 h-72 w-[580px] rounded-full bg-cultiva-green/20 blur-[95px]" },
    { className: "absolute bottom-12 right-[20%] h-64 w-96 rounded-full bg-cultiva-green/16 blur-[85px]" },
  ],
  "admin-simulations": [
    { className: "absolute -left-40 bottom-16 h-[400px] w-[500px] rotate-12 rounded-full bg-cultiva-green/23 blur-[100px]" },
    { className: "absolute right-0 top-32 h-56 w-[450px] rounded-full bg-cultiva-green/14 blur-[88px]" },
  ],
  "admin-sim-detail": [
    { className: "absolute right-[10%] top-16 h-96 w-[600px] rounded-full bg-cultiva-green/24 blur-[105px]" },
    { className: "absolute left-8 bottom-32 h-40 w-80 rounded-full bg-cultiva-green/11 blur-[70px]" },
  ],
  "admin-crop-types": [
    { className: "absolute left-1/2 top-32 h-64 w-[640px] -translate-x-1/2 rounded-full bg-cultiva-green/19 blur-[92px]" },
    { className: "absolute -right-20 bottom-40 h-80 w-[420px] rounded-full bg-cultiva-green/21 blur-[98px]" },
  ],
  "admin-profile": [
    { className: "absolute left-1/3 top-16 h-56 w-[500px] rounded-full bg-cultiva-green/18 blur-[90px]" },
    { className: "absolute -right-28 bottom-20 h-72 w-96 rounded-full bg-cultiva-green/20 blur-[95px]" },
  ],
  "admin-crop-stats": [
    { className: "absolute right-[8%] top-20 h-80 w-[560px] rounded-full bg-cultiva-green/23 blur-[100px]" },
    { className: "absolute bottom-20 left-12 h-48 w-80 rounded-full bg-cultiva-green/14 blur-[80px]" },
  ],
};
