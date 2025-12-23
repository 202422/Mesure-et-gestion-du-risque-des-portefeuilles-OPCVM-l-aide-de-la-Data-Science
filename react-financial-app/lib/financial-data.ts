// Generate simulated MASI data
export function generateMASIData(period: string) {
  const dataPoints = getPeriodDataPoints(period)
  const baseValue = 13500
  const data = []

  for (let i = 0; i < dataPoints; i++) {
    const randomWalk = (Math.random() - 0.48) * 100
    const trend = i * 2
    const value = baseValue + trend + randomWalk + Math.sin(i / 10) * 50

    data.push({
      date: formatDate(i, period),
      value: Math.max(value, 12000),
    })
  }

  return data
}

// Generate simulated OPCVM Attijari data
export function generateOPCVMData(period: string) {
  const dataPoints = getPeriodDataPoints(period)
  const baseValue = 1250
  const data = []

  for (let i = 0; i < dataPoints; i++) {
    const randomWalk = (Math.random() - 0.47) * 15
    const trend = i * 0.3
    const value = baseValue + trend + randomWalk + Math.sin(i / 8) * 8

    data.push({
      date: formatDate(i, period),
      value: Math.max(value, 1200),
    })
  }

  return data
}

// Calculate volatility prediction
export function calculateVolatility(masiData: any[], opcvmData: any[]) {
  const masiCurrent = masiData[masiData.length - 1].value
  const opcvmCurrent = opcvmData[opcvmData.length - 1].value

  // Calculate historical volatility
  const masiVolatility = calculateHistoricalVolatility(masiData)
  const opcvmVolatility = calculateHistoricalVolatility(opcvmData)

  // Generate predictions
  const masiPredicted = masiCurrent * (1 + (Math.random() - 0.5) * 0.05)
  const opcvmPredicted = opcvmCurrent * (1 + (Math.random() - 0.5) * 0.03)

  // Determine trends
  const masiTrend = masiPredicted > masiCurrent ? "up" : masiPredicted < masiCurrent ? "down" : "stable"
  const opcvmTrend = opcvmPredicted > opcvmCurrent ? "up" : opcvmPredicted < opcvmCurrent ? "down" : "stable"

  // Generate 14-day forecast
  const forecast = []
  const today = new Date()

  for (let i = 1; i <= 14; i++) {
    const date = new Date(today)
    date.setDate(date.getDate() + i)

    const masiVariation = (masiCurrent * masiVolatility) / 100
    const opcvmVariation = (opcvmCurrent * opcvmVolatility) / 100

    forecast.push({
      date: date.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" }),
      masiLow: masiCurrent - masiVariation,
      masiHigh: masiCurrent + masiVariation,
      opcvmLow: opcvmCurrent - opcvmVariation,
      opcvmHigh: opcvmCurrent + opcvmVariation,
    })
  }

  return {
    masi: {
      current: masiCurrent,
      predicted: masiPredicted,
      volatility: masiVolatility,
      trend: masiTrend,
    },
    opcvm: {
      current: opcvmCurrent,
      predicted: opcvmPredicted,
      volatility: opcvmVolatility,
      trend: opcvmTrend,
    },
    forecast,
  }
}

// Helper functions
function getPeriodDataPoints(period: string): number {
  switch (period) {
    case "1M":
      return 30
    case "3M":
      return 90
    case "6M":
      return 180
    case "1Y":
      return 365
    case "2Y":
      return 730
    default:
      return 180
  }
}

function formatDate(index: number, period: string): string {
  const today = new Date()
  const daysAgo = getPeriodDataPoints(period) - index
  const date = new Date(today)
  date.setDate(date.getDate() - daysAgo)

  return date.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: period === "2Y" ? "2-digit" : undefined,
  })
}

function calculateHistoricalVolatility(data: any[]): number {
  if (data.length < 2) return 1.0

  const returns = []
  for (let i = 1; i < data.length; i++) {
    const dailyReturn = (data[i].value - data[i - 1].value) / data[i - 1].value
    returns.push(dailyReturn)
  }

  const mean = returns.reduce((sum, val) => sum + val, 0) / returns.length
  const variance = returns.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / returns.length
  const stdDev = Math.sqrt(variance)

  // Annualized volatility
  return stdDev * Math.sqrt(252) * 100
}

// Aggregate daily series into weekly series (use last value of each ISO week)
export function aggregateToWeekly(data: Array<{ date: string; value: number }>) {
  if (!data || data.length === 0) return []

  // parse date strings using French locale formats like dd/mm/yyyy or dd/mm/yy
  const parseDate = (s: string) => {
    const parts = s.split(/\D+/).map((p) => parseInt(p, 10))
    if (parts.length < 2) return new Date(s)
    // parts: [day, month, year?]
    const day = parts[0]
    const month = (parts[1] || 1) - 1
    const year = parts[2] ? (parts[2] < 100 ? 2000 + parts[2] : parts[2]) : new Date().getFullYear()
    return new Date(year, month, day)
  }

  const getISOWeekKey = (d: Date) => {
    const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
    // Thursday in current week decides the year.
    date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7))
    const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1))
    const weekNo = Math.ceil(((date.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
    return `${date.getUTCFullYear()}-W${String(weekNo).padStart(2, "0")}`
  }

  const groups: Record<string, { date: Date; value: number; rawDate: string }[]> = {}

  for (const point of data) {
    const d = parseDate(point.date)
    const key = getISOWeekKey(d)
    groups[key] = groups[key] || []
    groups[key].push({ date: d, value: point.value, rawDate: point.date })
  }

  const weekly: Array<{ date: string; value: number }> = []
  const sortedKeys = Object.keys(groups).sort()
  for (const key of sortedKeys) {
    const arr = groups[key]
    // take the last chronological value in the week
    arr.sort((a, b) => a.date.getTime() - b.date.getTime())
    const last = arr[arr.length - 1]
    weekly.push({ date: last.date.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" }), value: last.value })
  }

  return weekly
}
// Fetch real OPCVM data from API
export async function fetchOPCVMData(): Promise<Array<{ date: string; value: number }>> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    const response = await fetch(`${apiUrl}/api/final/opcvm_liquidative`)
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    const data = await response.json()
    // Convert ISO date strings to dd/mm format for consistency
    return data.map((item: any) => ({
      date: new Date(item.date).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" }),
      value: item.value,
    }))
  } catch (error) {
    console.error("Failed to fetch OPCVM data:", error)
    // Fall back to generated data
    return generateOPCVMData("6M")
  }
}

// Fetch real MASI data from API
export async function fetchMASIData(): Promise<Array<{ date: string; value: number }>> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    const response = await fetch(`${apiUrl}/api/final/masi_weekly_mean`)
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    const data = await response.json()
    // Convert ISO date strings to dd/mm format for consistency
    return data.map((item: any) => ({
      date: new Date(item.date).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" }),
      value: item.value,
    }))
  } catch (error) {
    console.error("Failed to fetch MASI data:", error)
    // Fall back to generated data
    return generateMASIData("6M")
  }
}