"""
Módulo de predição do modelo de previsão de risco de malária.
"""

import os
import logging
import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from ..features.feature_engineering import FeatureEngineer
from ..ingest.database_manager import DatabaseManager
from ..api.models import PrevisaoResponse

logger = logging.getLogger(__name__)


class ModelPredictor:
    """Classe para predição usando o modelo treinado."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv('MODEL_PATH', 'models/malaria_model.joblib')
        
        self.model = None
        self.label_encoder = None
        self.feature_names = []
        self.model_version = None
        self.feature_engineer = FeatureEngineer()
        
        # Carregar modelo se existir
        self.load_model()
    
    def load_model(self) -> bool:
        """
        Carrega modelo salvo.
        
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Arquivo de modelo não encontrado: {self.model_path}")
                return False
            
            model_data = joblib.load(self.model_path)
            
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.feature_names = model_data['feature_names']
            self.model_version = model_data.get('model_version', 'unknown')
            
            logger.info(f"Modelo carregado: {self.model_path}")
            logger.info(f"Versão: {self.model_version}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False
    
    def is_model_loaded(self) -> bool:
        """
        Verifica se o modelo está carregado.
        
        Returns:
            True se modelo está carregado, False caso contrário
        """
        return self.model is not None and self.label_encoder is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre o modelo carregado.
        
        Returns:
            Dicionário com informações do modelo
        """
        if not self.is_model_loaded():
            return {
                'status': 'not_loaded',
                'message': 'Modelo não está carregado'
            }
        
        return {
            'status': 'loaded',
            'model_version': self.model_version,
            'model_type': type(self.model).__name__,
            'feature_count': len(self.feature_names),
            'classes': self.label_encoder.classes_.tolist(),
            'model_path': self.model_path
        }
    
    def prepare_prediction_data(self, municipio: str, ano_semana: str, 
                               db_manager: DatabaseManager) -> pd.DataFrame:
        """
        Prepara dados para predição.
        
        Args:
            municipio: Nome do município
            ano_semana: Ano-semana no formato YYYY-WW
            db_manager: Gerenciador do banco de dados
            
        Returns:
            DataFrame com dados preparados para predição
        """
        logger.info(f"Preparando dados para predição: {municipio} - {ano_semana}")
        
        # Obter dados históricos do município
        municipios = db_manager.get_municipios()
        municipio_id = None
        
        for m in municipios:
            if m['nome'].lower() == municipio.lower():
                municipio_id = m['id']
                break
        
        if not municipio_id:
            raise ValueError(f"Município '{municipio}' não encontrado")
        
        # Obter dados históricos (últimas 52 semanas)
        df_historico = db_manager.get_series_semanais(municipio_id=municipio_id)
        
        if df_historico.empty:
            raise ValueError(f"Nenhum dado histórico encontrado para {municipio}")
        
        # Renomear coluna para compatibilidade
        df_historico = df_historico.rename(columns={'municipio_nome': 'municipio'})
        
        # Aplicar engenharia de features
        df_features = self.feature_engineer.engineer_features(df_historico)
        
        # Obter dados da semana mais recente
        df_latest = df_features[df_features['ano_semana'] == df_features['ano_semana'].max()]
        
        if df_latest.empty:
            raise ValueError(f"Nenhum dado encontrado para {municipio}")
        
        # Preparar features para predição
        X = df_latest[self.feature_names].copy()
        
        # Tratar valores nulos
        X = X.fillna(X.median())
        
        logger.info(f"Dados preparados: {X.shape[0]} amostras, {X.shape[1]} features")
        
        return X
    
    def predict_single(self, municipio: str, ano_semana: str, 
                      db_manager: DatabaseManager) -> Optional[PrevisaoResponse]:
        """
        Realiza predição para um município específico.
        
        Args:
            municipio: Nome do município
            ano_semana: Ano-semana para predição
            db_manager: Gerenciador do banco de dados
            
        Returns:
            PrevisaoResponse com resultado da predição
        """
        if not self.is_model_loaded():
            raise ValueError("Modelo não está carregado")
        
        try:
            # Preparar dados
            X = self.prepare_prediction_data(municipio, ano_semana, db_manager)
            
            # Realizar predição
            prediction = self.model.predict(X)[0]
            prediction_proba = self.model.predict_proba(X)[0]
            
            # Decodificar predição
            classe_risco = self.label_encoder.inverse_transform([prediction])[0]
            
            # Calcular score de risco (probabilidade da classe predita)
            score_risco = float(prediction_proba[prediction])
            
            # Obter probabilidades por classe
            classes = self.label_encoder.classes_
            probabilidades = {}
            
            for i, class_name in enumerate(classes):
                probabilidades[f'probabilidade_{class_name}'] = float(prediction_proba[i])
            
            # Criar resposta
            previsao = PrevisaoResponse(
                municipio=municipio,
                ano_semana_prevista=ano_semana,
                classe_risco=classe_risco,
                score_risco=score_risco,
                probabilidade_baixo=probabilidades.get('probabilidade_baixo', 0.0),
                probabilidade_medio=probabilidades.get('probabilidade_medio', 0.0),
                probabilidade_alto=probabilidades.get('probabilidade_alto', 0.0),
                modelo_versao=self.model_version,
                modelo_tipo=type(self.model).__name__,
                created_at=datetime.now()
            )
            
            logger.info(f"Predição realizada: {municipio} - {classe_risco} (score: {score_risco:.3f})")
            
            return previsao
            
        except Exception as e:
            logger.error(f"Erro na predição para {municipio}: {e}")
            raise
    
    def predict_batch(self, municipios: List[str], ano_semana: str, 
                     db_manager: DatabaseManager) -> List[PrevisaoResponse]:
        """
        Realiza predições para múltiplos municípios.
        
        Args:
            municipios: Lista de nomes dos municípios
            ano_semana: Ano-semana para predição
            db_manager: Gerenciador do banco de dados
            
        Returns:
            Lista de PrevisaoResponse com resultados
        """
        if not self.is_model_loaded():
            raise ValueError("Modelo não está carregado")
        
        logger.info(f"Realizando predições em lote para {len(municipios)} municípios")
        
        previsoes = []
        
        for municipio in municipios:
            try:
                previsao = self.predict_single(municipio, ano_semana, db_manager)
                if previsao:
                    previsoes.append(previsao)
            except Exception as e:
                logger.error(f"Erro na predição para {municipio}: {e}")
                continue
        
        logger.info(f"Predições concluídas: {len(previsoes)} sucessos")
        
        return previsoes
    
    def predict_all_municipios(self, ano_semana: str, 
                              db_manager: DatabaseManager) -> List[PrevisaoResponse]:
        """
        Realiza predições para todos os municípios.
        
        Args:
            ano_semana: Ano-semana para predição
            db_manager: Gerenciador do banco de dados
            
        Returns:
            Lista de PrevisaoResponse com resultados
        """
        # Obter lista de municípios
        municipios = db_manager.get_municipios()
        municipio_names = [m['nome'] for m in municipios]
        
        return self.predict_batch(municipio_names, ano_semana, db_manager)
    
    def save_predictions_to_db(self, previsoes: List[PrevisaoResponse], 
                              db_manager: DatabaseManager) -> bool:
        """
        Salva predições no banco de dados.
        
        Args:
            previsoes: Lista de predições
            db_manager: Gerenciador do banco de dados
            
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            # Converter para DataFrame
            data = []
            for previsao in previsoes:
                data.append({
                    'municipio': previsao.municipio,
                    'ano_semana_prevista': previsao.ano_semana_prevista,
                    'classe_risco': previsao.classe_risco,
                    'score_risco': previsao.score_risco,
                    'probabilidade_baixo': previsao.probabilidade_baixo,
                    'probabilidade_medio': previsao.probabilidade_medio,
                    'probabilidade_alto': previsao.probabilidade_alto,
                    'modelo_versao': previsao.modelo_versao,
                    'modelo_tipo': previsao.modelo_tipo
                })
            
            df = pd.DataFrame(data)
            
            # Salvar no banco
            success = db_manager.insert_previsoes(df)
            
            if success:
                logger.info(f"Predições salvas no banco: {len(previsoes)} registros")
            else:
                logger.warning("Erro ao salvar predições no banco")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao salvar predições: {e}")
            return False
    
    def get_prediction_confidence(self, prediction_proba: np.ndarray) -> str:
        """
        Avalia a confiança da predição baseada nas probabilidades.
        
        Args:
            prediction_proba: Array com probabilidades das classes
            
        Returns:
            String com nível de confiança ('alta', 'media', 'baixa')
        """
        max_prob = np.max(prediction_proba)
        
        if max_prob >= 0.8:
            return 'alta'
        elif max_prob >= 0.6:
            return 'media'
        else:
            return 'baixa'
    
    def explain_prediction(self, municipio: str, ano_semana: str, 
                          db_manager: DatabaseManager) -> Dict[str, Any]:
        """
        Fornece explicação da predição (feature importance).
        
        Args:
            municipio: Nome do município
            ano_semana: Ano-semana para predição
            db_manager: Gerenciador do banco de dados
            
        Returns:
            Dicionário com explicação da predição
        """
        if not self.is_model_loaded():
            raise ValueError("Modelo não está carregado")
        
        try:
            # Preparar dados
            X = self.prepare_prediction_data(municipio, ano_semana, db_manager)
            
            # Obter importância das features
            feature_importance = self.feature_engineer.get_feature_importance(
                self.model, self.feature_names
            )
            
            # Obter valores das features para o município
            feature_values = X.iloc[0].to_dict()
            
            # Criar explicação
            explanation = {
                'municipio': municipio,
                'ano_semana': ano_semana,
                'feature_importance': feature_importance,
                'feature_values': feature_values,
                'top_features': dict(list(feature_importance.items())[:5])
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Erro na explicação da predição: {e}")
            raise
    
    def validate_prediction_data(self, municipio: str, ano_semana: str, 
                                db_manager: DatabaseManager) -> Dict[str, Any]:
        """
        Valida se há dados suficientes para predição.
        
        Args:
            municipio: Nome do município
            ano_semana: Ano-semana para predição
            db_manager: Gerenciador do banco de dados
            
        Returns:
            Dicionário com resultado da validação
        """
        try:
            # Verificar se município existe
            municipios = db_manager.get_municipios()
            municipio_encontrado = None
            
            for m in municipios:
                if m['nome'].lower() == municipio.lower():
                    municipio_encontrado = m
                    break
            
            if not municipio_encontrado:
                return {
                    'valid': False,
                    'error': f"Município '{municipio}' não encontrado"
                }
            
            # Verificar dados históricos
            df_historico = db_manager.get_series_semanais(municipio_id=municipio_encontrado['id'])
            
            if df_historico.empty:
                return {
                    'valid': False,
                    'error': f"Nenhum dado histórico encontrado para {municipio}"
                }
            
            # Verificar se há dados suficientes (pelo menos 4 semanas)
            if len(df_historico) < 4:
                return {
                    'valid': False,
                    'error': f"Dados insuficientes para {municipio} (mínimo 4 semanas)"
                }
            
            # Verificar se há dados recentes
            latest_week = df_historico['ano_semana'].max()
            
            return {
                'valid': True,
                'municipio_id': municipio_encontrado['id'],
                'total_weeks': len(df_historico),
                'latest_week': latest_week,
                'message': f"Dados válidos para predição"
            }
            
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return {
                'valid': False,
                'error': f"Erro na validação: {str(e)}"
            }


def test_predictor() -> None:
    """
    Função para testar o preditor com dados de exemplo.
    """
    from ..ingest.data_loader import create_sample_data
    import tempfile
    import os
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Criar dados de exemplo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            create_sample_data(tmp.name)
            temp_path = tmp.name
        
        # Carregar dados
        from ..ingest.data_loader import DataLoader
        loader = DataLoader()
        df = loader.load_and_process_data(os.path.basename(temp_path))
        
        # Simular banco de dados
        class MockDB:
            def get_municipios(self):
                return [
                    {'id': 1, 'nome': 'Kuito'},
                    {'id': 2, 'nome': 'Camacupa'},
                    {'id': 3, 'nome': 'Andulo'}
                ]
            
            def get_series_semanais(self, municipio_id=None):
                if municipio_id:
                    return df[df['municipio'] == 'Kuito'].rename(columns={'municipio': 'municipio_nome'})
                return df.rename(columns={'municipio': 'municipio_nome'})
        
        # Testar preditor
        predictor = ModelPredictor()
        
        if not predictor.is_model_loaded():
            print("Modelo não está carregado. Execute o treinamento primeiro.")
            return
        
        db_mock = MockDB()
        
        # Testar predição
        previsao = predictor.predict_single('Kuito', '2024-01', db_mock)
        
        if previsao:
            print("Predição realizada com sucesso!")
            print(f"Município: {previsao.municipio}")
            print(f"Classe de risco: {previsao.classe_risco}")
            print(f"Score: {previsao.score_risco:.3f}")
        else:
            print("Erro na predição")
        
    finally:
        # Limpar arquivo temporário
        if 'temp_path' in locals():
            os.unlink(temp_path)


if __name__ == "__main__":
    test_predictor()

