'use client'

import { useClientSafe } from "@/lib/client-safe-context"
import { Switch } from "./ui/switch"
import { Label } from "./ui/label"

export function ClientSafeToggle() {
  const { isClientSafe, toggle } = useClientSafe()

  return (
    <div className="flex items-center gap-2">
      <Switch
        id="client-safe-mode"
        checked={isClientSafe}
        onCheckedChange={toggle}
      />
      <Label htmlFor="client-safe-mode" className="text-sm font-medium cursor-pointer">
        Client-Safe Mode
      </Label>
    </div>
  )
}
