# Guia do Usuário - Sistema de Previsão de Risco de Malária (Bié)

## Visão Geral

O Sistema de Previsão de Risco de Malária é uma ferramenta que utiliza dados históricos de casos de malária e informações climáticas para prever o risco semanal de surtos de malária em cada município da província do Bié, Angola.

## Funcionalidades Principais

### 🗺️ Mapa Interativo
- Visualização geográfica dos municípios do Bié
- Cores indicam nível de risco (verde=baixo, amarelo=médio, vermelho=alto)
- Clique nos marcadores para ver detalhes de cada município

### 📊 Dashboard de Análise
- Estatísticas gerais de risco por município
- Gráficos de tendência temporal
- Tabela de previsões da próxima semana

### 📈 Análise Temporal
- Seleção de município para análise detalhada
- Gráfico de casos históricos
- Identificação de padrões sazonais

### 📧 Sistema de Alertas
- Notificações automáticas por e-mail
- Alertas quando risco excede limiar configurado
- Relatórios semanais para gestores

## Como Usar o Sistema

### 1. Acessar o Dashboard

1. Abra seu navegador web
2. Acesse: `http://localhost:3000` (desenvolvimento) ou `http://seu-servidor.com` (produção)
3. Aguarde o carregamento completo da página

### 2. Navegar pelo Mapa

#### Visualizar Municípios
- O mapa mostra todos os municípios do Bié
- Cada município é representado por um marcador colorido:
  - 🟢 **Verde**: Risco baixo
  - 🟡 **Amarelo**: Risco médio  
  - 🔴 **Vermelho**: Risco alto

#### Obter Informações Detalhadas
1. Clique em qualquer marcador no mapa
2. Uma janela popup aparecerá com:
   - Nome do município
   - Nível de risco atual
   - Score de risco (0-1)
   - Probabilidades por classe
   - População
   - Semana da previsão

### 3. Analisar Estatísticas Gerais

#### Painel de Resumo
No topo da página, você verá:
- **Total de Municípios**: Número total monitorado
- **Risco Alto**: Quantidade com risco alto
- **Risco Médio**: Quantidade com risco médio
- **Risco Baixo**: Quantidade com risco baixo

#### Interpretação dos Números
- **Risco Alto**: Requer atenção imediata e ações preventivas
- **Risco Médio**: Monitoramento intensificado recomendado
- **Risco Baixo**: Situação controlada, manutenção da vigilância

### 4. Examinar Previsões Detalhadas

#### Tabela de Previsões
A tabela mostra previsões para a próxima semana:
- **Município**: Nome do município
- **Risco**: Classificação visual do risco
- **Score**: Valor numérico (0-1) do risco
- **Prob. Alto**: Probabilidade de risco alto (%)

#### Ordenação e Filtros
- Clique nos cabeçalhos das colunas para ordenar
- Use Ctrl+F para buscar municípios específicos

### 5. Análise Temporal por Município

#### Selecionar Município
1. No painel "Análise Temporal", use o menu suspenso
2. Selecione o município desejado
3. O gráfico será atualizado automaticamente

#### Interpretar o Gráfico
- **Eixo X**: Semanas epidemiológicas
- **Eixo Y**: Número de casos de malária
- **Linha Vermelha**: Tendência dos casos
- **Picos**: Possíveis surtos ou sazonalidade

#### Padrões a Observar
- **Tendência Crescente**: Possível aumento do risco
- **Sazonalidade**: Padrões repetitivos anuais
- **Picos Isolados**: Eventos pontuais que requerem investigação

### 6. Distribuição de Risco

#### Gráfico de Barras
Mostra quantos municípios estão em cada nível de risco:
- **Verde**: Municípios com risco baixo
- **Amarelo**: Municípios com risco médio
- **Vermelho**: Municípios com risco alto

#### Interpretação
- **Maioria Verde**: Situação geral controlada
- **Maioria Amarelo/Vermelho**: Situação preocupante, ações coordenadas necessárias

## Interpretação dos Dados

### Níveis de Risco

#### 🟢 Risco Baixo (0.0 - 0.4)
- **Significado**: Baixa probabilidade de surto
- **Ações**: Manutenção da vigilância rotineira
- **Recursos**: Níveis normais de pessoal e medicamentos

#### 🟡 Risco Médio (0.4 - 0.7)
- **Significado**: Probabilidade moderada de surto
- **Ações**: Intensificar monitoramento
- **Recursos**: Preparar recursos adicionais
- **Comunicação**: Alertar equipes locais

#### 🔴 Risco Alto (0.7 - 1.0)
- **Significado**: Alta probabilidade de surto
- **Ações**: Implementar medidas preventivas imediatas
- **Recursos**: Mobilizar recursos máximos
- **Comunicação**: Notificar autoridades e população

### Scores de Risco

#### Interpretação Numérica
- **0.0 - 0.2**: Muito baixo
- **0.2 - 0.4**: Baixo
- **0.4 - 0.6**: Moderado
- **0.6 - 0.8**: Alto
- **0.8 - 1.0**: Muito alto

#### Probabilidades
- **Prob. Baixo**: Chance de permanecer em risco baixo
- **Prob. Médio**: Chance de evoluir para risco médio
- **Prob. Alto**: Chance de evoluir para risco alto

## Alertas e Notificações

### Tipos de Alertas

#### Alertas Automáticos
- Enviados semanalmente (domingos às 18h)
- Disparados quando risco > limiar configurado
- Incluem relatório completo da situação

#### Alertas Imediatos
- Enviados quando risco excede 0.8
- Notificação urgente para gestores
- Requer resposta imediata

### Conteúdo dos Alertas

#### E-mail de Alerta
- **Assunto**: Nível de urgência e municípios afetados
- **Resumo**: Estatísticas gerais
- **Detalhes**: Informações por município
- **Ações**: Recomendações específicas
- **Link**: Acesso direto ao dashboard

### Configurar Alertas

#### Para Administradores
1. Acesse as configurações do sistema
2. Configure endereços de e-mail dos destinatários
3. Defina limiar de risco para alertas
4. Teste o sistema de notificações

## Boas Práticas

### Para Gestores de Saúde

#### Uso Diário
1. Verifique o dashboard pela manhã
2. Identifique municípios com risco alto/médio
3. Priorize ações baseadas no score de risco
4. Monitore tendências temporais

#### Planejamento Semanal
1. Analise relatório semanal de alertas
2. Planeje distribuição de recursos
3. Coordene com equipes locais
4. Documente ações tomadas

#### Resposta a Alertas
1. **Risco Alto**: Ação imediata em 24h
2. **Risco Médio**: Planejamento em 48h
3. **Risco Baixo**: Monitoramento contínuo

### Para Equipes Técnicas

#### Manutenção de Dados
1. Atualize dados semanalmente
2. Verifique qualidade dos dados
3. Reporte problemas técnicos
4. Mantenha backup dos dados

#### Monitoramento do Sistema
1. Verifique status da API diariamente
2. Monitore performance do sistema
3. Atualize modelo quando necessário
4. Documente mudanças e melhorias

## Solução de Problemas

### Problemas Comuns

#### Dashboard Não Carrega
1. Verifique conexão com internet
2. Atualize a página (F5)
3. Limpe cache do navegador
4. Verifique se o servidor está online

#### Dados Desatualizados
1. Aguarde atualização automática (a cada hora)
2. Recarregue a página
3. Verifique se há problemas de conectividade
4. Contate suporte técnico se persistir

#### Gráficos Não Aparecem
1. Verifique se JavaScript está habilitado
2. Tente outro navegador
3. Verifique console do navegador (F12)
4. Aguarde carregamento completo

### Contato para Suporte

#### Problemas Técnicos
- **E-mail**: suporte@malaria-bie.ao
- **Telefone**: +244 XXX XXX XXX
- **Horário**: Segunda a Sexta, 8h às 17h

#### Emergências
- **WhatsApp**: +244 XXX XXX XXX
- **Disponibilidade**: 24/7 para alertas críticos

## Glossário

### Termos Técnicos
- **Score de Risco**: Valor numérico (0-1) que indica probabilidade de surto
- **Semana Epidemiológica**: Período de 7 dias usado para análise de saúde pública
- **Sazonalidade**: Padrões repetitivos que ocorrem em épocas específicas do ano
- **Limiar de Risco**: Valor mínimo que dispara alertas automáticos

### Abreviações
- **API**: Interface de Programação de Aplicações
- **DPS**: Direção Provincial de Saúde
- **INAMET**: Instituto Nacional de Meteorologia
- **MVP**: Produto Mínimo Viável

## Recursos Adicionais

### Documentação Técnica
- [Guia de Instalação](INSTALLATION.md)
- [Documentação da API](API.md)
- [Manual do Administrador](ADMIN.md)

### Treinamentos
- **Básico**: Introdução ao sistema (2 horas)
- **Intermediário**: Análise de dados (4 horas)
- **Avançado**: Configuração e manutenção (8 horas)

### Atualizações
- **Versão Atual**: 1.0.0
- **Última Atualização**: Janeiro 2024
- **Próximas Funcionalidades**: 
  - Notificações via WhatsApp
  - Relatórios automáticos
  - Integração com sistemas externos
