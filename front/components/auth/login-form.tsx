"use client"

import * as React from "react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"

interface LoginFormProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onSubmit'> {
  onSubmit?: (data: { email: string; password: string; remember: boolean }) => Promise<void>
}

export function LoginForm({ className, onSubmit, ...props }: LoginFormProps) {
  const [isLoading, setIsLoading] = React.useState(false)
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [remember, setRemember] = React.useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsLoading(true)

    try {
      if (onSubmit) {
        await onSubmit({ email, password, remember })
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <form onSubmit={handleSubmit}>
        <div className="flex flex-col gap-6">
          <div className="flex flex-col items-center gap-2">
            <h1 className="text-2xl font-bold">Bem-vindo de volta</h1>
            <p className="text-balance text-sm text-muted-foreground">
              Entre com sua conta para continuar
            </p>
          </div>
          <div className="flex flex-col gap-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="seu@email.com"
                required
                disabled={isLoading}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Senha</Label>
                <Link
                  href="/forgot-password"
                  className="text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
                >
                  Esqueci minha senha
                </Link>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="********"
                required
                disabled={isLoading}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="remember"
                checked={remember}
                onCheckedChange={(checked) => setRemember(checked as boolean)}
                disabled={isLoading}
              />
              <Label
                htmlFor="remember"
                className="text-sm font-normal leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Lembrar-me
              </Label>
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Entrando..." : "Entrar"}
            </Button>
          </div>
        </div>
      </form>
      <div className="text-center text-sm">
        Não tem uma conta?{" "}
        <Link
          href="/register"
          className="text-primary underline-offset-4 hover:underline"
        >
          Criar conta
        </Link>
      </div>
    </div>
  )
}
