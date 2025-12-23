"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { MarketChart } from "@/components/market-chart"
import { VolatilityPrediction } from "@/components/volatility-prediction"
import { fetchMASIData, fetchOPCVMData, calculateVolatility } from "@/lib/financial-data"
import { TrendingUp, Activity } from "lucide-react"

export function FinancialDashboard() {
  const [selectedPeriod, setSelectedPeriod] = useState("6M")
  const [showVolatility, setShowVolatility] = useState(false)
  const [volatilityData, setVolatilityData] = useState<any>(null)
  const [isCalculating, setIsCalculating] = useState(false)
  const [modelResult, setModelResult] = useState<{ date?: string; vol_future_2w_1?: number; error?: any } | null>(null)
  const [masiData, setMasiData] = useState<Array<{ date: string; value: number }>>([])
  const [opcvmData, setOpcvmData] = useState<Array<{ date: string; value: number }>>([])
  const [isLoading, setIsLoading] = useState(true)

  // Fetch real data from API on component mount
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      try {
        const [masi, opcvm] = await Promise.all([fetchMASIData(), fetchOPCVMData()])
        setMasiData(masi)
        setOpcvmData(opcvm)
      } catch (error) {
        console.error("Failed to load data:", error)
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [])

  // Data from the API is already weekly (from final_dataset.csv)
  const masiWeekly = masiData
  const opcvmWeekly = opcvmData

  const handlePredictVolatility = async () => {
  setIsCalculating(true)
  setModelResult(null)

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    const resp = await fetch(`${apiUrl}/api/volatility/run-modelling`, {
      method: "POST",
    })

    const text = await resp.text()
    let data: any = null

    try {
      data = JSON.parse(text)
    } catch (e) {
      data = { raw: text }
    }

    if (!resp.ok) {
      console.error("Modelling run failed:", data)
      setModelResult({
        date: undefined,
        vol_future_2w_1: undefined,
        error: data.detail || data.raw || JSON.stringify(data),
      })
    } else {
      // Transformer la réponse pour VolatilityPrediction
      const predicted = data.vol_future_2w_1 ?? 0
      const current = data.current_value ?? 0 // si tu n'as pas de valeur courante, tu peux mettre latestOPCVM.value

      const formattedData = {
        masi: {
          volatility: predicted,
          predicted: predicted,
          current: current,
        },
        opcvm: {
          volatility: predicted,
          predicted: predicted,
          current: current,
        },
      }

      setModelResult({
        date: data.date ?? "N/A",
        vol_future_2w_1: data.vol_future_2w_1 ?? null,
      })
      setVolatilityData(formattedData)
      setShowVolatility(true)
    }
  } catch (error) {
    console.error("Modelling run failed:", error)
    setModelResult({
      date: undefined,
      vol_future_2w_1: undefined,
      error: String(error),
    })
  } finally {
    setIsCalculating(false)
  }
}


  const latestMASI = masiData[masiData.length - 1]
  const latestOPCVM = opcvmData[opcvmData.length - 1]
  
  if (isLoading || !latestMASI || !latestOPCVM) {
    return (
      <div className="container mx-auto p-4 md:p-6 lg:p-8 max-w-7xl">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-lg text-muted-foreground mb-2">Chargement des données...</p>
            <div className="animate-spin">⏳</div>
          </div>
        </div>
      </div>
    )
  }

  const masiChange = ((latestMASI.value - masiData[0].value) / masiData[0].value) * 100
  const opcvmChange = ((latestOPCVM.value - opcvmData[0].value) / opcvmData[0].value) * 100

  return (
    <div className="container mx-auto p-4 md:p-6 lg:p-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold mb-2 text-balance">Tableau de Bord Financier</h1>
        <p className="text-muted-foreground text-lg">Analyse et prévisions de volatilité pour de l'OPCVM Attijari diversifié</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">OPCVM Attijari diversifié</CardTitle>
        <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
        <div className="text-2xl font-bold">{latestOPCVM.value.toFixed(2)} MAD</div>
        <p className={`text-xs flex items-center gap-1 ${opcvmData.length > 1 && ((opcvmData[opcvmData.length - 1].value - opcvmData[opcvmData.length - 2].value) / opcvmData[opcvmData.length - 2].value * 100) >= 0 ? "text-green-600" : "text-red-600"}`}>
          {opcvmData.length > 1 && ((opcvmData[opcvmData.length - 1].value - opcvmData[opcvmData.length - 2].value) / opcvmData[opcvmData.length - 2].value * 100) >= 0 ? "+" : ""}
          {opcvmData.length > 1 ? ((opcvmData[opcvmData.length - 1].value - opcvmData[opcvmData.length - 2].value) / opcvmData[opcvmData.length - 2].value * 100).toFixed(2) : "0.00"}% au {latestOPCVM.date}
        </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">MASI</CardTitle>
        <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
        <div className="text-2xl font-bold">{latestMASI.value.toFixed(2)}</div>
        <p className={`text-xs flex items-center gap-1 ${masiData.length > 1 && ((masiData[masiData.length - 1].value - masiData[masiData.length - 2].value) / masiData[masiData.length - 2].value * 100) >= 0 ? "text-green-600" : "text-red-600"}`}>
          {masiData.length > 1 && ((masiData[masiData.length - 1].value - masiData[masiData.length - 2].value) / masiData[masiData.length - 2].value * 100) >= 0 ? "+" : ""}
          {masiData.length > 1 ? ((masiData[masiData.length - 1].value - masiData[masiData.length - 2].value) / masiData[masiData.length - 2].value * 100).toFixed(2) : "0.00"}% au {latestMASI.date}
        </p>
          </CardContent>
        </Card>

        

        
      </div>

      {/* Charts Section */}
      <Tabs defaultValue="masi" className="mb-6">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="opcvm">OPCVM Attijari diversifié</TabsTrigger>
          <TabsTrigger value="masi">MASI</TabsTrigger>
          
        </TabsList>

        <TabsContent value="masi" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Courbe du MASI</CardTitle>
              <CardDescription>Indice historique de la Bourse de Casablanca</CardDescription>
            </CardHeader>
            <CardContent>
              <MarketChart data={masiWeekly} dataKey="value" color="#2563eb" />  

            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="opcvm" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>OPCVM Attijari</CardTitle>
              <CardDescription>Valeur Liquidative historique</CardDescription>
            </CardHeader>
            <CardContent>
              <MarketChart data={opcvmWeekly} dataKey="value" color="#f97316" /> 
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Volatility Prediction Section */}
      <Card>
        <CardHeader>
          <CardTitle>Prévision de Volatilité</CardTitle>
          <CardDescription>Analyse de la volatilité future sur 2 semaines</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Button onClick={handlePredictVolatility} className="w-full md:w-auto" disabled={isCalculating}>
              {isCalculating ? (
                <>
                  <span className="mr-2">Calcul en cours...</span>
                  <span className="animate-spin">⏳</span>
                </>
              ) : (
                "Prédire la volatilité sur les 2 prochaines semaines"
              )}
            </Button>

            {modelResult && (
              <div className="mt-4 text-sm">
                <div>Résultat du modèle à la date du: {modelResult.date ?? "N/A"}</div>
                <div>
                  Volatilité future: {
                    typeof modelResult.vol_future_2w_1 === "number" && Number.isFinite(modelResult.vol_future_2w_1)
                      ? modelResult.vol_future_2w_1.toFixed(6)
                      : modelResult.error
                      ? `Erreur: ${modelResult.error}`
                      : "N/A"
                  }
                </div>
              </div>
            )}

            
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
