'use client'

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { Icon } from 'leaflet'
import { AlertTriangle, TrendingUp, Shield } from 'lucide-react'

interface Prediction {
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

interface Municipality {
  id: number
  nome: string
  latitude: number
  longitude: number
  populacao: number
}

interface MapProps {
  predictions: Prediction[]
  municipalities: Municipality[]
}

// Ícones personalizados para diferentes níveis de risco
const createRiskIcon = (riskLevel: string) => {
  let color = '#6b7280' // cinza padrão
  
  switch (riskLevel) {
    case 'alto':
      color = '#ef4444' // vermelho
      break
    case 'medio':
      color = '#f59e0b' // amarelo
      break
    case 'baixo':
      color = '#10b981' // verde
      break
  }

  return new Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(`
      <svg width="25" height="41" viewBox="0 0 25 41" xmlns="http://www.w3.org/2000/svg">
        <path d="M12.5 0C5.6 0 0 5.6 0 12.5c0 12.5 12.5 28.5 12.5 28.5s12.5-16 12.5-28.5C25 5.6 19.4 0 12.5 0z" fill="${color}"/>
        <circle cx="12.5" cy="12.5" r="8" fill="white"/>
        <text x="12.5" y="16" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="${color}">
          ${riskLevel === 'alto' ? '!' : riskLevel === 'medio' ? '~' : '✓'}
        </text>
      </svg>
    `)}`,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [0, -41]
  })
}

export default function Map({ predictions, municipalities }: MapProps) {
  // Criar mapa de previsões por município
  const predictionMap = new Map(
    predictions.map(p => [p.municipio, p])
  )

  // Obter ícone do risco
  const getRiskIcon = (classe: string) => {
    switch (classe) {
      case 'alto': return <AlertTriangle className="w-4 h-4 text-red-600" />
      case 'medio': return <TrendingUp className="w-4 h-4 text-yellow-600" />
      case 'baixo': return <Shield className="w-4 h-4 text-green-600" />
      default: return <div className="w-4 h-4 bg-gray-400 rounded-full" />
    }
  }

  // Obter cor do risco
  const getRiskColor = (classe: string) => {
    switch (classe) {
      case 'alto': return 'text-red-600 bg-red-100'
      case 'medio': return 'text-yellow-600 bg-yellow-100'
      case 'baixo': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <MapContainer
      center={[-12.5, 17.0]} // Centro do Bié
      zoom={8}
      style={{ height: '100%', width: '100%' }}
      className="rounded-lg"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {municipalities.map((municipality) => {
        const prediction = predictionMap.get(municipality.nome)
        
        if (!prediction) return null

        return (
          <Marker
            key={municipality.id}
            position={[municipality.latitude, municipality.longitude]}
            icon={createRiskIcon(prediction.classe_risco)}
          >
            <Popup>
              <div className="p-2 min-w-[200px]">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 text-sm">
                    {municipality.nome}
                  </h3>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(prediction.classe_risco)}`}>
                    {getRiskIcon(prediction.classe_risco)}
                    <span className="ml-1">{prediction.classe_risco.toUpperCase()}</span>
                  </span>
                </div>
                
                <div className="space-y-1 text-xs text-gray-600">
                  <div className="flex justify-between">
                    <span>Score de Risco:</span>
                    <span className="font-medium">{prediction.score_risco.toFixed(3)}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span>População:</span>
                    <span className="font-medium">{municipality.populacao?.toLocaleString() || 'N/A'}</span>
                  </div>
                  
                  <div className="mt-2">
                    <p className="font-medium text-gray-700 mb-1">Probabilidades:</p>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span className="text-green-600">Baixo:</span>
                        <span className="font-medium">{(prediction.probabilidade_baixo * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-yellow-600">Médio:</span>
                        <span className="font-medium">{(prediction.probabilidade_medio * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-red-600">Alto:</span>
                        <span className="font-medium">{(prediction.probabilidade_alto * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <div className="flex justify-between">
                      <span>Semana:</span>
                      <span className="font-medium">{prediction.ano_semana}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Modelo:</span>
                      <span className="font-medium text-xs">{prediction.modelo_versao}</span>
                    </div>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        )
      })}
    </MapContainer>
  )
}
