import CultivalabLogo2 from "../assets/CultivalabLogo2.png";

export function CultivaLogo({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <div>
      <img src={CultivalabLogo2.src} alt="CultivaLab Logo" className="w-12 h-12" />
    </div>
  );
}