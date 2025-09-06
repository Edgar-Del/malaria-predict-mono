# Frontend - Sistema de Previsão de Malária - Bié

Dashboard web desenvolvido com React/Next.js para visualização de previsões de risco de malária.

## 🏗️ Arquitetura

```
frontend/
├── web/                   # Aplicação Next.js
│   ├── app/              # App Router (Next.js 13+)
│   │   ├── layout.tsx    # Layout principal
│   │   ├── page.tsx      # Página inicial
│   │   └── globals.css   # Estilos globais
│   ├── components/       # Componentes React
│   ├── services/         # Serviços de API
│   ├── utils/            # Utilitários
│   └── public/           # Assets estáticos
├── package.json          # Dependências Node.js
├── next.config.js        # Configuração Next.js
├── tailwind.config.js    # Configuração Tailwind
└── tsconfig.json         # Configuração TypeScript
```

## 🚀 Instalação e Execução

### Desenvolvimento Local

```bash
# Instalar dependências
make install

# Executar em modo desenvolvimento
make dev

# Executar testes
make test

# Verificar qualidade do código
make check
```

### Docker

```bash
# Construir imagem
docker build -t malaria-frontend .

# Executar container
docker run -p 3000:3000 malaria-frontend
```

## 🎨 Tecnologias

### Core
- **Next.js 14**: Framework React com App Router
- **React 18**: Biblioteca de UI
- **TypeScript**: Tipagem estática
- **Tailwind CSS**: Framework CSS

### Visualização
- **Recharts**: Gráficos e charts
- **Leaflet**: Mapas interativos
- **React Leaflet**: Integração React + Leaflet

### Utilitários
- **Axios**: Cliente HTTP
- **Lucide React**: Ícones
- **Date-fns**: Manipulação de datas

## 📱 Funcionalidades

### Dashboard Principal
- **Mapa Interativo**: Visualização geográfica dos municípios
- **Gráficos**: Distribuição de risco e tendências
- **Tabelas**: Previsões detalhadas por município
- **Alertas**: Notificações visuais para alto risco

### Páginas
- **Home**: Dashboard principal
- **Previsões**: Lista de previsões
- **Municípios**: Informações dos municípios
- **Alertas**: Histórico de alertas
- **Configurações**: Configurações do sistema

### Componentes
- **Mapa**: Componente de mapa com Leaflet
- **Gráficos**: Componentes de visualização
- **Tabelas**: Tabelas responsivas
- **Alertas**: Componentes de notificação
- **Layout**: Layout responsivo

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Configurações de desenvolvimento
NODE_ENV=development
```

### Configuração Next.js

```javascript
// next.config.js
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/v1/:path*`,
      },
    ]
  },
}
```

## 🧪 Testes

```bash
# Executar todos os testes
make test

# Testes específicos
npm run test -- --testPathPattern=components

# Testes com cobertura
npm run test -- --coverage
```

## 🎨 Estilização

### Tailwind CSS

```css
/* Configuração personalizada */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Cores customizadas */
:root {
  --malaria-50: #fef2f2;
  --malaria-500: #ef4444;
  --malaria-900: #7f1d1d;
}
```

### Componentes

```tsx
// Exemplo de componente
interface RiskIndicatorProps {
  level: 'baixo' | 'medio' | 'alto';
  score: number;
}

export const RiskIndicator: React.FC<RiskIndicatorProps> = ({ level, score }) => {
  return (
    <div className={`risk-${level} px-2 py-1 rounded-full text-xs font-medium`}>
      {level.toUpperCase()} ({score}%)
    </div>
  );
};
```

## 📊 Visualizações

### Mapas
- **Leaflet**: Mapas interativos
- **Marcadores**: Municípios com indicadores de risco
- **Popups**: Informações detalhadas
- **Zoom**: Controles de navegação

### Gráficos
- **Recharts**: Gráficos responsivos
- **Barras**: Distribuição de risco
- **Linhas**: Tendências temporais
- **Pizza**: Proporções por categoria

## 🔧 Desenvolvimento

### Estrutura de Componentes

```tsx
// Componente de página
export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="dashboard">
      <Header />
      <StatsCards data={data} />
      <MapComponent data={data} />
      <ChartsComponent data={data} />
    </div>
  );
}
```

### Serviços de API

```tsx
// services/api.ts
export class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  async getPredictions(week: string) {
    const response = await fetch(`${this.baseURL}/api/v1/previsoes/semana/${week}`);
    return response.json();
  }
}
```

## 📱 Responsividade

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Componentes Responsivos
- **Grid**: Layout adaptativo
- **Tabelas**: Scroll horizontal em mobile
- **Mapas**: Tamanho adaptativo
- **Gráficos**: Redimensionamento automático

## 🚀 Deploy

### Build de Produção

```bash
# Build
make build

# Verificar build
npm run build
npm run start
```

### Docker

```bash
# Build da imagem
docker build -t malaria-frontend .

# Deploy
docker run -p 3000:3000 malaria-frontend
```

### Variáveis de Produção

```bash
# Produção
NEXT_PUBLIC_API_URL=https://api.malaria-bie.ao
NODE_ENV=production
```

## 📊 Performance

### Otimizações
- **Next.js**: SSR/SSG automático
- **Imagens**: Otimização automática
- **Bundle**: Code splitting
- **Caching**: Headers de cache

### Métricas
- **Lighthouse**: Performance score
- **Core Web Vitals**: LCP, FID, CLS
- **Bundle Size**: Tamanho dos assets

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
