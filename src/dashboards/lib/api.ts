// Cliente API para comunicação com o backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Prediction {
  municipio: string
  municipio_id: number
  ano_semana: string
  classe_risco: string
  score_risco: number
  probabilidade_baixo: number
  probabilidade_medio: number
  probabilidade_alto: number
  modelo_versao: string
  created_at: string
}

export interface Municipality {
  id: number
  nome: string
  cod_ibge_local: string
  latitude: number
  longitude: number
  populacao: number
  area_km2: number
}

export interface TimeSeries {
  ano_semana: string
  casos: number
  chuva_mm: number | null
  temp_media_c: number | null
  created_at: string
}

export interface Metrics {
  modelo_versao: string
  accuracy: number
  precision_macro: number
  recall_macro: number
  f1_macro: number
  precision_baixo: number | null
  recall_baixo: number | null
  f1_baixo: number | null
  precision_medio: number | null
  recall_medio: number | null
  f1_medio: number | null
  precision_alto: number | null
  recall_alto: number | null
  f1_alto: number | null
  data_treinamento: string
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Health check
  async getHealth() {
    return this.request('/health')
  }

  // Municípios
  async getMunicipalities(): Promise<{ municipios: Municipality[]; total: number }> {
    return this.request('/municipios')
  }

  // Previsões
  async getWeeklyPredictions(anoSemana: string): Promise<{ previsoes: Prediction[]; total: number; ano_semana: string }> {
    return this.request(`/previsoes/semana/${anoSemana}`)
  }

  async getPrediction(municipio: string, anoSemana: string): Promise<Prediction> {
    return this.request(`/predict?municipio=${encodeURIComponent(municipio)}&ano_semana=${anoSemana}`)
  }

  // Séries temporais
  async getMunicipalitySeries(municipio: string, limit: number = 52): Promise<{ series: TimeSeries[]; municipio: string; total: number }> {
    return this.request(`/series/${encodeURIComponent(municipio)}?limit=${limit}`)
  }

  // Métricas
  async getLatestMetrics(): Promise<Metrics> {
    return this.request('/metrics/latest')
  }

  // Treinamento
  async trainModel(): Promise<{ status: string; modelo_versao: string; metrics: any; training_time: number; message: string }> {
    return this.request('/train', { method: 'POST' })
  }
}

// Instância singleton do cliente API
export const apiClient = new ApiClient()

// Funções utilitárias
export const getNextWeek = (): string => {
  const nextWeek = new Date()
  nextWeek.setDate(nextWeek.getDate() + 7)
  const year = nextWeek.getFullYear()
  const week = Math.ceil((nextWeek.getTime() - new Date(year, 0, 1).getTime()) / (7 * 24 * 60 * 60 * 1000))
  return `${year}-${week.toString().padStart(2, '0')}`
}

export const getCurrentWeek = (): string => {
  const now = new Date()
  const year = now.getFullYear()
  const week = Math.ceil((now.getTime() - new Date(year, 0, 1).getTime()) / (7 * 24 * 60 * 60 * 1000))
  return `${year}-${week.toString().padStart(2, '0')}`
}

export const formatWeek = (weekString: string): string => {
  const [year, week] = weekString.split('-')
  return `Semana ${week} de ${year}`
}

export const getRiskColor = (classe: string): string => {
  switch (classe) {
    case 'alto': return 'text-red-600 bg-red-100'
    case 'medio': return 'text-yellow-600 bg-yellow-100'
    case 'baixo': return 'text-green-600 bg-green-100'
    default: return 'text-gray-600 bg-gray-100'
  }
}

export const getRiskLevel = (score: number): string => {
  if (score >= 0.7) return 'alto'
  if (score >= 0.4) return 'medio'
  return 'baixo'
}
