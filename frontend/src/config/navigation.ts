import type { LucideIcon } from "lucide-react";
import {
  FlaskConical,
  Home,
  Leaf,
  LineChart,
  PlusCircle,
  Settings,
  Sprout,
  User,
  Users,
} from "lucide-react";

export type NavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
};

export const userNavItems: NavItem[] = [
  { href: "/dashboard", label: "Inicio", icon: Home },
  { href: "/crops", label: "Mis cultivos", icon: Sprout },
  { href: "/crops/new", label: "Crear cultivo", icon: PlusCircle },
  { href: "/simulate", label: "Simular cultivo", icon: FlaskConical },
  { href: "/simulations", label: "Simulaciones recientes", icon: LineChart },
  { href: "/profile", label: "Mi perfil", icon: User },
];

export const adminNavItems: NavItem[] = [
  { href: "/admin", label: "Inicio admin", icon: Home },
  { href: "/admin/users", label: "Usuarios", icon: Users },
  { href: "/admin/crops", label: "Cultivos", icon: Leaf },
  { href: "/admin/simulations", label: "Simulaciones", icon: LineChart },
  { href: "/admin/crop-types", label: "Tipos de cultivo", icon: Settings },
  { href: "/admin/profile", label: "Mi perfil", icon: User },
];
