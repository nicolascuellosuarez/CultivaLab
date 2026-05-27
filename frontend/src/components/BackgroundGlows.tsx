export type GlowVariant = "home" | "form" | "login" | "register-admin";

type BackgroundGlowsProps = {
  variant?: GlowVariant;
};

export function BackgroundGlows({ variant = "home" }: BackgroundGlowsProps) {
  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden>
      {variant === "home" && (
        <>
          <div className="absolute -left-32 top-24 h-[min(70vh,520px)] w-[min(80vw,640px)] -rotate-[28deg] rounded-full bg-cultiva-green/25 blur-[100px] md:blur-[130px]" />
          <div className="absolute -right-20 top-1/3 h-72 w-96 rounded-full bg-cultiva-green/15 blur-[90px]" />
          <div className="absolute left-1/2 top-[42%] h-64 w-[min(90vw,720px)] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cultiva-green/20 blur-[100px] md:h-80 md:blur-[120px]" />
        </>
      )}

      {variant === "form" && (
        <>
          <div className="absolute -left-32 top-24 h-[min(70vh,520px)] w-[min(80vw,640px)] -rotate-[28deg] rounded-full bg-cultiva-green/25 blur-[100px] md:blur-[130px]" />
          <div className="absolute -right-20 top-1/3 h-72 w-96 rounded-full bg-cultiva-green/15 blur-[90px]" />
          <div className="absolute left-[20%] top-[55%] h-48 w-[min(70vw,560px)] -translate-y-1/2 rounded-full bg-cultiva-green/20 blur-[90px]" />
          <div className="absolute bottom-[18%] left-1/4 h-40 w-80 rounded-full bg-cultiva-green/15 blur-[80px]" />
        </>
      )}

      {variant === "login" && (
        <>
          <div className="absolute -right-36 top-16 h-[min(65vh,480px)] w-[min(75vw,580px)] rotate-[22deg] rounded-full bg-cultiva-green/30 blur-[110px] md:blur-[140px]" />
          <div className="absolute right-[8%] top-[48%] h-56 w-[min(55vw,420px)] rounded-full bg-cultiva-green/18 blur-[85px]" />
          <div className="absolute bottom-[12%] left-[10%] h-44 w-96 rounded-full bg-cultiva-green/12 blur-[75px]" />
        </>
      )}

      {variant === "register-admin" && (
        <>
          <div className="absolute left-1/2 -top-28 h-72 w-[min(90vw,760px)] -translate-x-1/2 rounded-full bg-cultiva-green/28 blur-[100px] md:blur-[125px]" />
          <div className="absolute -left-40 bottom-[22%] h-[min(55vh,400px)] w-[min(70vw,520px)] rotate-[18deg] rounded-full bg-cultiva-green/22 blur-[95px]" />
          <div className="absolute right-[5%] top-[38%] h-52 w-80 rounded-full bg-cultiva-green/16 blur-[80px]" />
          <div className="absolute bottom-[8%] right-[25%] h-36 w-64 rounded-full bg-cultiva-green/10 blur-[70px]" />
        </>
      )}
    </div>
  );
}
