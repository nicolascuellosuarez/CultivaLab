import { BackgroundGlows, type GlowVariant } from "./BackgroundGlows";
import { Header } from "./Header";
import { SiteFooter } from "./SiteFooter";

type PageShellProps = {
  children: React.ReactNode;
  glowVariant?: GlowVariant;
};

export function PageShell({ children, glowVariant = "form" }: PageShellProps) {
  return (
    <main className="relative min-h-screen bg-cultiva-dark">
      <BackgroundGlows variant={glowVariant} />
      <Header />
      <div className="relative z-10">{children}</div>
      <SiteFooter />
    </main>
  );
}
