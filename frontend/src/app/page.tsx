import { Hero } from "@/components/Hero";
import { PageShell } from "@/components/PageShell";

export default function HomePage() {
  return (
    <PageShell glowVariant="home">
      <Hero />
    </PageShell>
  );
}
