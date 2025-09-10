'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { AlertTriangle, MapPin, TrendingUp, Activity, Users, Shield } from 'lucide-react'
import dynamic from 'next/dynamic'
import { apiClient, getNextWeek, formatWeek } from '@/lib/api'

// Importar componentes dinamicamente para evitar problemas de SSR
const Map = dynamic(() => import('@/components/Map'), { ssr: false })

interface Prediction {
  municipio: string
  ano_semana_prevista: string
  classe_risco: string
  score_risco: number
  probabilidade_baixo: number
  probabilidade_medio: number
  probabilidade_alto: number
  modelo_versao: string
  modelo_tipo: string
  created_at: string
}

interface Municipality {
  id: number
  nome: string
  cod_ibge_local: string
  latitude: number
  longitude: number
  populacao: number
  area_km2: number
}

interface TimeSeries {
  municipio: string
  ano_semana: string
  casos: number
  chuva_mm: number | null
  temp_media_c: number | null
  temp_min_c: number | null
  temp_max_c: number | null
  umidade_relativa: number | null
  casos_lag1: number | null
  casos_lag2: number | null
  casos_lag3: number | null
  casos_lag4: number | null
  casos_media_2s: number | null
  casos_media_4s: number | null
}

export default function Dashboard() {
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [municipalities, setMunicipalities] = useState<Municipality[]>([])
  const [selectedMunicipality, setSelectedMunicipality] = useState<string>('')
  const [timeSeries, setTimeSeries] = useState<TimeSeries[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)


  // Carregar dados
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        
        // Carregar municípios
        const municipalitiesData = await apiClient.getMunicipalities()
        setMunicipalities(municipalitiesData)
        
        // Carregar previsões da próxima semana
        const nextWeek = getNextWeek()
        const predictionsData = await apiClient.getWeeklyPredictions(nextWeek)
        setPredictions(predictionsData.previsoes)
        
        // Selecionar primeiro município por padrão
        if (municipalitiesData.length > 0) {
          setSelectedMunicipality(municipalitiesData[0].nome)
        }
        
      } catch (err) {
        setError('Erro ao carregar dados')
        console.error('Erro:', err)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  // Carregar série temporal quando município selecionado mudar
  useEffect(() => {
    if (selectedMunicipality) {
      const loadTimeSeries = async () => {
        try {
          const data = await apiClient.getMunicipalitySeries(selectedMunicipality, 52)
          setTimeSeries(data)
        } catch (err) {
          console.error('Erro ao carregar série temporal:', err)
        }
      }
      
      loadTimeSeries()
    }
  }, [selectedMunicipality])

  // Obter cor do risco
  const getRiskColor = (classe: string) => {
    switch (classe) {
      case 'alto': return 'text-red-600 bg-red-100'
      case 'medio': return 'text-yellow-600 bg-yellow-100'
      case 'baixo': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  // Obter ícone do risco
  const getRiskIcon = (classe: string) => {
    switch (classe) {
      case 'alto': return <AlertTriangle className="w-4 h-4" />
      case 'medio': return <TrendingUp className="w-4 h-4" />
      case 'baixo': return <Shield className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  // Estatísticas gerais
  const totalMunicipalities = municipalities.length
  const highRiskCount = predictions.filter(p => p.classe_risco === 'alto').length
  const mediumRiskCount = predictions.filter(p => p.classe_risco === 'medio').length
  const lowRiskCount = predictions.filter(p => p.classe_risco === 'baixo').length

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Erro</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
          <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Sistema de Previsão de Risco de Malária
              </h1>
              <p className="text-gray-600 mt-1">Província do Bié, Angola</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="status-online">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Sistema Online
              </div>
          </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Estatísticas Gerais */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Municípios</p>
                <p className="text-2xl font-bold text-gray-900">{totalMunicipalities}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Risco Alto</p>
                <p className="text-2xl font-bold text-red-600">{highRiskCount}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Risco Médio</p>
                <p className="text-2xl font-bold text-yellow-600">{mediumRiskCount}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Risco Baixo</p>
                <p className="text-2xl font-bold text-green-600">{lowRiskCount}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Mapa e Tabela */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Mapa */}
        <div className="card">
          <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <MapPin className="w-5 h-5 mr-2" />
                Mapa de Risco por Município
              </h2>
          </div>
            <div className="h-96">
              <Map predictions={predictions} municipalities={municipalities} />
        </div>
      </div>

      {/* Tabela de Previsões */}
      <div className="card">
        <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900">
                Previsões da Próxima Semana
              </h2>
        </div>
        <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Município
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risco
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Prob. Alto
                    </th>
              </tr>
            </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {predictions.map((prediction, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {prediction.municipio}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`risk-indicator ${getRiskColor(prediction.classe_risco)}`}>
                          {getRiskIcon(prediction.classe_risco)}
                          <span className="ml-1">{prediction.classe_risco.toUpperCase()}</span>
                    </span>
                  </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {prediction.score_risco.toFixed(3)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {(prediction.probabilidade_alto * 100).toFixed(1)}%
                      </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Seleção de Município */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900">
                Análise Temporal
              </h2>
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Selecionar Município
                </label>
                <select
                  value={selectedMunicipality}
                  onChange={(e) => setSelectedMunicipality(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  {municipalities.map((municipality) => (
                    <option key={municipality.id} value={municipality.nome}>
                      {municipality.nome}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timeSeries}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="ano_semana" 
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="casos" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    name="Casos de Malária"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Distribuição de Risco */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-gray-900">
                Distribuição de Risco
              </h2>
            </div>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={[
                  { name: 'Baixo', value: lowRiskCount, color: '#10b981' },
                  { name: 'Médio', value: mediumRiskCount, color: '#f59e0b' },
                  { name: 'Alto', value: highRiskCount, color: '#ef4444' }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}