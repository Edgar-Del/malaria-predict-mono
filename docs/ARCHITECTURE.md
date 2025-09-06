# Arquitetura do Sistema de Previsão de Risco de Malária (Bié)

## Visão Geral

O Sistema de Previsão de Risco de Malária é uma aplicação distribuída que implementa **Clean Architecture** e **Domain-Driven Design (DDD)** para fornecer previsões de risco de malária em tempo real para a província do Bié, Angola.

## Princípios Arquiteturais

### 1. Clean Architecture
- **Independência de frameworks**: O sistema não depende de frameworks específicos
- **Testabilidade**: Lógica de negócio pode ser testada independentemente
- **Independência de UI**: Interface pode mudar sem afetar o sistema
- **Independência de banco de dados**: Pode trocar de banco sem afetar regras de negócio
- **Independência de agentes externos**: Regras de negócio não conhecem o mundo externo

### 2. Domain-Driven Design (DDD)
- **Entidades de domínio**: Representam conceitos centrais do negócio
- **Value Objects**: Objetos imutáveis que representam conceitos
- **Repositórios**: Abstraem persistência de dados
- **Serviços de domínio**: Lógica que não pertence a uma entidade específica
- **Use Cases**: Orquestram fluxos de negócio

## Estrutura da Arquitetura

```
src/
├── core/                           # Camada de domínio (Clean Architecture)
│   ├── domain/                     # Entidades e regras de negócio
│   │   ├── entities/              # Entidades de domínio
│   │   ├── repositories/          # Interfaces de repositórios
│   │   ├── services/              # Serviços de domínio
│   │   └── exceptions.py          # Exceções de domínio
│   ├── use_cases/                 # Casos de uso (Application Layer)
│   ├── infrastructure/            # Camada de infraestrutura
│   │   ├── config/                # Configurações
│   │   ├── logging/               # Sistema de logging
│   │   ├── monitoring/            # Métricas e health checks
│   │   ├── di/                    # Injeção de dependência
│   │   └── testing/               # Utilitários de teste
│   └── interfaces/                # Camada de interface
│       ├── api/                   # API REST
│       ├── web/                   # Interface web
│       └── cli/                   # Interface de linha de comando
├── ingest/                        # ETL e ingestão de dados
├── features/                      # Engenharia de atributos
├── model/                         # Modelos de ML
├── alerts/                        # Sistema de alertas
└── dashboards/                    # Frontend React/NextJS
```

## Camadas da Arquitetura

### 1. Domain Layer (Domínio)
**Responsabilidade**: Contém as regras de negócio e entidades centrais.

**Componentes**:
- **Entities**: `Municipality`, `RiskPrediction`
- **Value Objects**: `MunicipalityId`, `RiskScore`, `EpidemiologicalWeek`
- **Repositories**: Interfaces para persistência
- **Services**: Lógica de negócio complexa
- **Exceptions**: Exceções específicas do domínio

**Características**:
- Não depende de nenhuma outra camada
- Contém regras de negócio puras
- Entidades são imutáveis quando possível
- Validações de domínio são rigorosas

### 2. Use Cases Layer (Casos de Uso)
**Responsabilidade**: Orquestra fluxos de negócio e coordena entidades.

**Componentes**:
- `PredictRiskUseCase`: Gera previsões de risco
- `PredictRiskBatchUseCase`: Previsões em lote
- `TrainModelUseCase`: Treina modelos de ML
- `SendAlertUseCase`: Envia alertas

**Características**:
- Depende apenas do Domain Layer
- Orquestra entidades e serviços
- Implementa fluxos de negócio específicos
- Não contém lógica de domínio

### 3. Infrastructure Layer (Infraestrutura)
**Responsabilidade**: Implementa detalhes técnicos e integrações externas.

**Componentes**:
- **Config**: Gerenciamento de configurações
- **Logging**: Sistema de logging estruturado
- **Monitoring**: Métricas e health checks
- **DI Container**: Injeção de dependência
- **Testing**: Utilitários de teste

**Características**:
- Implementa interfaces definidas no Domain Layer
- Pode depender de frameworks externos
- Contém código específico de tecnologia
- É substituível por outras implementações

### 4. Interface Layer (Interface)
**Responsabilidade**: Expõe funcionalidades para usuários e sistemas externos.

**Componentes**:
- **API REST**: Endpoints HTTP
- **Web Interface**: Dashboard React/NextJS
- **CLI**: Interface de linha de comando

**Características**:
- Depende do Use Cases Layer
- Contém lógica de apresentação
- Valida entrada do usuário
- Formata saída para diferentes clientes

## Padrões de Design Implementados

### 1. Repository Pattern
```python
class MunicipalityRepository(Protocol):
    async def get_by_id(self, id: MunicipalityId) -> Optional[Municipality]
    async def save(self, municipality: Municipality) -> Municipality
    async def delete(self, id: MunicipalityId) -> bool
```

**Benefícios**:
- Abstrai detalhes de persistência
- Facilita testes unitários
- Permite trocar implementações

### 2. Dependency Injection
```python
class PredictRiskUseCase:
    def __init__(
        self,
        municipality_repository: MunicipalityRepository,
        risk_prediction_repository: RiskPredictionRepository,
        risk_prediction_service: RiskPredictionService
    ):
        self._municipality_repository = municipality_repository
        # ...
```

**Benefícios**:
- Baixo acoplamento
- Facilita testes
- Configuração flexível

### 3. Factory Pattern
```python
def get_logger(name: Optional[str] = None) -> MalariaLogger:
    if name:
        return MalariaLogger(name)
    return logger
```

**Benefícios**:
- Centraliza criação de objetos
- Encapsula lógica de criação
- Facilita manutenção

### 4. Strategy Pattern
```python
class RiskPredictionService(ABC):
    @abstractmethod
    async def predict_risk(self, municipality: Municipality) -> RiskPrediction
```

**Benefícios**:
- Algoritmos intercambiáveis
- Facilita extensibilidade
- Segue Open/Closed Principle

## Fluxo de Dados

### 1. Previsão de Risco
```
Request → API → Use Case → Domain Service → Repository → Database
                ↓
Response ← API ← Use Case ← Domain Service ← Repository ← Database
```

### 2. Treinamento de Modelo
```
Data → ETL → Feature Engineering → ML Model → Persistence
```

### 3. Sistema de Alertas
```
Prediction → Alert Service → Email Service → Notification
```

## Tecnologias e Frameworks

### Backend
- **Python 3.11+**: Linguagem principal
- **FastAPI**: Framework web assíncrono
- **Pydantic**: Validação de dados
- **SQLAlchemy**: ORM para banco de dados
- **PostgreSQL**: Banco de dados principal
- **scikit-learn**: Machine Learning
- **pytest**: Framework de testes

### Frontend
- **React 18**: Biblioteca de UI
- **Next.js 14**: Framework React
- **TypeScript**: Tipagem estática
- **Tailwind CSS**: Framework CSS
- **Chart.js**: Gráficos interativos
- **Leaflet**: Mapas interativos

### Infraestrutura
- **Docker**: Containerização
- **Docker Compose**: Orquestração local
- **GitHub Actions**: CI/CD
- **PostgreSQL**: Banco de dados
- **Redis**: Cache (opcional)

## Qualidade e Testes

### Estratégia de Testes
- **Testes Unitários**: 80%+ cobertura
- **Testes de Integração**: APIs e banco de dados
- **Testes de Performance**: Load testing
- **Testes de Segurança**: Vulnerability scanning

### Ferramentas de Qualidade
- **Black**: Formatação de código
- **Flake8**: Linting
- **MyPy**: Verificação de tipos
- **Bandit**: Análise de segurança
- **Safety**: Verificação de dependências

## Monitoramento e Observabilidade

### Métricas
- **Métricas de Negócio**: Previsões, alertas, municípios
- **Métricas Técnicas**: Performance, erros, disponibilidade
- **Métricas de ML**: Acurácia, drift, performance

### Logging
- **Logs Estruturados**: JSON format
- **Contexto**: Request ID, usuário, operação
- **Níveis**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Health Checks
- **Database**: Conectividade e queries
- **ML Model**: Disponibilidade e métricas
- **Email Service**: Conectividade SMTP
- **Cache**: Operações de leitura/escrita

## Escalabilidade e Performance

### Estratégias de Escalabilidade
- **Horizontal**: Múltiplas instâncias da API
- **Vertical**: Mais recursos por instância
- **Database**: Read replicas, connection pooling
- **Cache**: Redis para dados frequentes

### Otimizações de Performance
- **Async/Await**: Operações assíncronas
- **Connection Pooling**: Reutilização de conexões
- **Caching**: Dados frequentemente acessados
- **Batch Processing**: Operações em lote

## Segurança

### Medidas Implementadas
- **Rate Limiting**: Controle de taxa de requisições
- **CORS**: Configuração de origens permitidas
- **Security Headers**: Proteção contra ataques comuns
- **Input Validation**: Validação rigorosa de entrada
- **Error Handling**: Tratamento seguro de erros

### Autenticação e Autorização
- **JWT Tokens**: Autenticação stateless
- **Role-based Access**: Controle de acesso por função
- **API Keys**: Autenticação de serviços

## Deploy e DevOps

### Ambientes
- **Development**: Desenvolvimento local
- **Staging**: Testes e validação
- **Production**: Ambiente de produção

### CI/CD Pipeline
1. **Lint & Format**: Verificação de código
2. **Tests**: Testes unitários e integração
3. **Security Scan**: Análise de vulnerabilidades
4. **Build**: Construção de imagens Docker
5. **Deploy**: Deploy automático

### Containerização
- **Multi-stage builds**: Imagens otimizadas
- **Health checks**: Verificação de saúde
- **Resource limits**: Limites de recursos
- **Secrets management**: Gerenciamento de segredos

## Manutenibilidade

### Código Limpo
- **SOLID Principles**: Princípios de design
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It

### Documentação
- **README**: Visão geral do projeto
- **API Docs**: Documentação automática
- **Architecture**: Documentação arquitetural
- **Code Comments**: Comentários no código

### Versionamento
- **Semantic Versioning**: Versionamento semântico
- **Git Flow**: Fluxo de branches
- **Conventional Commits**: Padrão de commits
- **Changelog**: Log de mudanças

## Próximos Passos

### Melhorias Planejadas
1. **Microserviços**: Decomposição em serviços menores
2. **Event Sourcing**: Rastreamento de eventos
3. **CQRS**: Separação de comandos e consultas
4. **GraphQL**: API mais flexível
5. **Real-time**: WebSockets para atualizações em tempo real

### Monitoramento Avançado
1. **APM**: Application Performance Monitoring
2. **Distributed Tracing**: Rastreamento distribuído
3. **Alerting**: Sistema de alertas inteligente
4. **Dashboards**: Dashboards operacionais

Esta arquitetura garante que o sistema seja **escalável**, **manutenível**, **testável** e **extensível**, seguindo as melhores práticas de engenharia de software e padrões de design profissionais.

