"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getStoredSession } from "@/lib/auth";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const session = getStoredSession();
    const isLoginPage = pathname === "/login";

    if (!session && !isLoginPage) {
      router.replace("/login");
      return;
    }

    if (session && isLoginPage) {
      router.replace("/dashboard");
      return;
    }

    setIsReady(true);
  }, [pathname, router]);

  if (!isReady) {
    return <div className="page-shell"><p>Carregando...</p></div>;
  }

  return <>{children}</>;
}
