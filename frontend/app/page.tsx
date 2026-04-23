"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { getStoredSession } from "@/lib/auth";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace(getStoredSession() ? "/dashboard" : "/login");
  }, [router]);

  return <div className="page-shell"><p>Redirecionando...</p></div>;
}
