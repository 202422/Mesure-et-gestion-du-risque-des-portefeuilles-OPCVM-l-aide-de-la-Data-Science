"use client"

import { Card } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

interface VolatilityData {
  masi: {
    current: number
    predicted: number
    volatility: number
    trend: "up" | "down" | "stable"
  }
  opcvm: {
    current: number
    predicted: number
    volatility: number
    trend: "up" | "down" | "stable"
  }
  forecast: Array<{
    date: string
    masiLow: number
    masiHigh: number
    opcvmLow: number
    opcvmHigh: number
  }>
}

interface VolatilityPredictionProps {
  data: VolatilityData
}

export function VolatilityPrediction({ data }: VolatilityPredictionProps) {
  const getTrendIcon = (trend: "up" | "down" | "stable") => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-4 w-4" />
      case "down":
        return <TrendingDown className="h-4 w-4" />
      default:
        return <Minus className="h-4 w-4" />
    }
  }

  const getTrendColor = (trend: "up" | "down" | "stable") => {
    switch (trend) {
      case "up":
        return "text-chart-1"
      case "down":
        return "text-destructive"
      default:
        return "text-muted-foreground"
    }
  }

  const getVolatilityLevel = (volatility: number) => {
    if (volatility < 1) return { label: "Faible", variant: "default" as const }
    if (volatility < 2) return { label: "Modérée", variant: "secondary" as const }
    return { label: "Élevée", variant: "destructive" as const }
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        

        <Card className="p-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">OPCVM Attijari</h3>
              <Badge variant={getVolatilityLevel(data.opcvm.volatility).variant}>
                {getVolatilityLevel(data.opcvm.volatility).label}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">{data.opcvm.volatility.toFixed(2)}%</span>
              <span className={`flex items-center gap-1 ${getTrendColor(data.opcvm.trend)}`}>
                {getTrendIcon(data.opcvm.trend)}
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Prévision: {data.opcvm.predicted.toFixed(2)} MAD ({data.opcvm.current.toFixed(2)} →{" "}
              {data.opcvm.predicted.toFixed(2)})
            </p>
          </div>
        </Card>
      </div>

    </div>
  )
}
