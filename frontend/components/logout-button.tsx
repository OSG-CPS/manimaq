"use client";

import { useRouter } from "next/navigation";

import { clearSession } from "@/lib/auth";

export function LogoutButton() {
  const router = useRouter();

  return (
    <button
      className="secondary-button"
      onClick={() => {
        clearSession();
        router.replace("/login");
      }}
      type="button"
    >
      Sair
    </button>
  );
}
