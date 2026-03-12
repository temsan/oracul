"""
Локальный анализатор голоса для Oracul Bot
Использует локальные модели Whisper и другие
"""

import logging
import asyncio
import tempfile
import os
from typing import Dict, Optional
import torch
import whisper
import librosa
import numpy as np
from transformers import pipeline

logger = logging.getLogger(__name__)


class LocalVoiceAnalyzer:
    """Анализатор голосовых сообщений с локальными моделями"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device for voice analysis: {self.device}")
        
        # Инициализируем модели
        self._init_models()
    
    def _init_models(self):
        """Инициализация локальных моделей"""
        try:
            # Whisper для транскрипции
            self.whisper_model = whisper.load_model("base", device=self.device)
            logger.info("✅ Whisper модель загружена")
            
            # Модель для анализа эмоций в тексте
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if self.device == "cuda" else -1
            )
            logger.info("✅ Emotion модель загружена")
            
            # Модель для анализа тональности
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="blanchefort/rubert-base-cased-sentiment",
                device=0 if self.device == "cuda" else -1
            )
            logger.info("✅ Sentiment модель загружена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации моделей голоса: {e}")
            self.whisper_model = None
            self.emotion_model = None
            self.sentiment_model = None
    
    async def analyze(self, voice_file, duration: float, user_context: Optional[Dict] = None) -> Dict:
        """
        Комплексный анализ голосового сообщения
        
        Args:
            voice_file: Файл голосового сообщения
            duration: Длительность в секундах
            user_context: Контекст пользователя
            
        Returns:
            Dict с результатами анализа
        """
        try:
            # Скачиваем и сохраняем файл временно
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                await voice_file.download_media(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Конвертируем в WAV для лучшей совместимости
                wav_path = temp_path.replace('.ogg', '.wav')
                await self._convert_to_wav(temp_path, wav_path)
                
                # Параллельный анализ
                tasks = [
                    self._analyze_audio_features(wav_path),
                    self._transcribe_and_analyze_local(wav_path, user_context)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Объединяем результаты
                analysis = {
                    'success': True,
                    'duration': duration,
                    'audio_features': results[0] if not isinstance(results[0], Exception) else {},
                    'transcription_analysis': results[1] if not isinstance(results[1], Exception) else {},
                    'recommendations': []
                }
                
                # Генерируем наблюдения
                analysis['recommendations'] = await self._generate_voice_observations(analysis)
                
                return analysis
                
            finally:
                # Удаляем временные файлы
                for path in [temp_path, temp_path.replace('.ogg', '.wav')]:
                    if os.path.exists(path):
                        os.unlink(path)
                        
        except Exception as e:
            logger.error(f"Error in local voice analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _convert_to_wav(self, input_path: str, output_path: str):
        """Конвертация аудио в WAV формат"""
        try:
            # Используем librosa для конвертации
            y, sr = librosa.load(input_path, sr=16000)
            import soundfile as sf
            sf.write(output_path, y, sr)
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            # Если конвертация не удалась, используем оригинальный файл
            import shutil
            shutil.copy2(input_path, output_path)
    
    async def _analyze_audio_features(self, audio_path: str) -> Dict:
        """Анализ аудио характеристик с librosa"""
        try:
            # Загружаем аудио
            y, sr = librosa.load(audio_path, sr=None)
            
            # Извлекаем признаки
            features = {}
            
            # Основная частота (pitch)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                features['pitch_mean'] = float(np.mean(pitch_values))
                features['pitch_std'] = float(np.std(pitch_values))
                features['pitch_range'] = float(np.max(pitch_values) - np.min(pitch_values))
            
            # Энергия и громкость
            rms = librosa.feature.rms(y=y)[0]
            features['energy_mean'] = float(np.mean(rms))
            features['energy_std'] = float(np.std(rms))
            features['energy_max'] = float(np.max(rms))
            
            # Темп речи
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            
            # MFCC для тембра
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
            
            # Спектральные характеристики
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            features['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            # Zero crossing rate (показатель четкости речи)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['zcr_mean'] = float(np.mean(zcr))
            features['zcr_std'] = float(np.std(zcr))
            
            # Интерпретируем характеристики
            interpretation = self._interpret_audio_features(features)
            
            return {
                'raw_features': features,
                'interpretation': interpretation
            }
            
        except Exception as e:
            logger.error(f"Audio features analysis error: {e}")
            return {}
    
    def _interpret_audio_features(self, features: Dict) -> Dict:
        """Интерпретация аудио характеристик"""
        interpretation = {}
        
        try:
            # Анализ энергии (эмоциональность)
            energy_mean = features.get('energy_mean', 0)
            if energy_mean > 0.1:
                interpretation['energy_level'] = 'высокая'
                interpretation['emotional_intensity'] = 'высокая'
            elif energy_mean > 0.05:
                interpretation['energy_level'] = 'средняя'
                interpretation['emotional_intensity'] = 'средняя'
            else:
                interpretation['energy_level'] = 'низкая'
                interpretation['emotional_intensity'] = 'низкая'
            
            # Анализ pitch (эмоциональное состояние)
            pitch_std = features.get('pitch_std', 0)
            pitch_mean = features.get('pitch_mean', 0)
            
            if pitch_std > 50:  # Высокая вариативность
                interpretation['emotional_state'] = 'эмоциональное'
                interpretation['speech_pattern'] = 'выразительная речь'
            elif pitch_std < 20:  # Низкая вариативность
                interpretation['emotional_state'] = 'спокойное'
                interpretation['speech_pattern'] = 'монотонная речь'
            else:
                interpretation['emotional_state'] = 'нейтральное'
                interpretation['speech_pattern'] = 'обычная речь'
            
            # Анализ темпа
            tempo = features.get('tempo', 120)
            if tempo > 140:
                interpretation['pace'] = 'быстрый'
                interpretation['stress_indicator'] = 'возможен стресс'
            elif tempo < 80:
                interpretation['pace'] = 'медленный'
                interpretation['stress_indicator'] = 'расслабленное состояние'
            else:
                interpretation['pace'] = 'нормальный'
                interpretation['stress_indicator'] = 'спокойное состояние'
            
            # Анализ четкости речи
            zcr_mean = features.get('zcr_mean', 0)
            if zcr_mean > 0.1:
                interpretation['speech_clarity'] = 'четкая речь'
            elif zcr_mean < 0.05:
                interpretation['speech_clarity'] = 'мягкая речь'
            else:
                interpretation['speech_clarity'] = 'обычная четкость'
            
            return interpretation
            
        except Exception as e:
            logger.error(f"Audio interpretation error: {e}")
            return {}
    
    async def _transcribe_and_analyze_local(self, audio_path: str, user_context: Optional[Dict] = None) -> Dict:
        """Транскрипция и анализ содержания с локальными моделями"""
        try:
            if not self.whisper_model:
                return {'transcription': '', 'analysis': {}}
            
            # Транскрибируем аудио с Whisper
            result = self.whisper_model.transcribe(
                audio_path,
                language="ru",
                task="transcribe"
            )
            
            text = result["text"].strip()
            
            if not text or len(text) < 5:
                return {'transcription': '', 'analysis': {}}
            
            # Анализируем содержание с локальными моделями
            content_analysis = {}
            
            # Анализ тональности
            if self.sentiment_model:
                sentiment_result = self.sentiment_model(text[:512])
                if sentiment_result:
                    content_analysis['sentiment'] = {
                        'label': sentiment_result[0]['label'],
                        'score': sentiment_result[0]['score']
                    }
            
            # Анализ эмоций
            if self.emotion_model:
                emotion_result = self.emotion_model(text[:512])
                if emotion_result:
                    emotions = {}
                    for item in emotion_result:
                        emotions[item['label']] = item['score']
                    content_analysis['emotions'] = emotions
            
            # Простой анализ стиля речи
            speech_style = self._analyze_speech_style(text)
            content_analysis['speech_style'] = speech_style
            
            return {
                'transcription': text,
                'content_analysis': content_analysis,
                'whisper_confidence': result.get('confidence', 0.8)
            }
            
        except Exception as e:
            logger.error(f"Local transcription and analysis error: {e}")
            return {'transcription': '', 'analysis': {}}
    
    def _analyze_speech_style(self, text: str) -> Dict:
        """Анализ стиля речи"""
        style = {}
        
        try:
            words = text.split()
            sentences = text.split('.')
            
            # Длина предложений
            avg_sentence_length = len(words) / max(len(sentences), 1)
            if avg_sentence_length > 15:
                style['sentence_complexity'] = 'сложные предложения'
            elif avg_sentence_length < 5:
                style['sentence_complexity'] = 'короткие предложения'
            else:
                style['sentence_complexity'] = 'средняя сложность'
            
            # Формальность
            formal_words = ['однако', 'следовательно', 'таким образом', 'в связи с']
            informal_words = ['ну', 'вот', 'типа', 'короче', 'блин']
            
            formal_count = sum(text.lower().count(word) for word in formal_words)
            informal_count = sum(text.lower().count(word) for word in informal_words)
            
            if formal_count > informal_count:
                style['formality'] = 'формальный стиль'
            elif informal_count > formal_count:
                style['formality'] = 'неформальный стиль'
            else:
                style['formality'] = 'нейтральный стиль'
            
            # Эмоциональность
            exclamations = text.count('!')
            questions = text.count('?')
            
            if exclamations > 2 or questions > 2:
                style['emotionality'] = 'эмоциональная речь'
            else:
                style['emotionality'] = 'спокойная речь'
            
            return style
            
        except Exception as e:
            logger.error(f"Speech style analysis error: {e}")
            return {}
    
    async def _generate_voice_observations(self, analysis: Dict) -> list:
        """Генерация наблюдений на основе анализа голоса"""
        observations = []
        
        try:
            audio_features = analysis.get('audio_features', {})
            transcription_analysis = analysis.get('transcription_analysis', {})
            
            interpretation = audio_features.get('interpretation', {})
            content_analysis = transcription_analysis.get('content_analysis', {})
            
            # Наблюдения на основе аудио характеристик
            if interpretation.get('emotional_intensity') == 'высокая':
                observations.append("Высокая эмоциональная интенсивность в голосе")
            
            if interpretation.get('stress_indicator') == 'возможен стресс':
                observations.append("Аудио-маркеры указывают на возможное напряжение")
            
            if interpretation.get('speech_pattern') == 'выразительная речь':
                observations.append("Выразительная манера речи с интонационными вариациями")
            
            # Наблюдения на основе содержания
            sentiment = content_analysis.get('sentiment', {})
            if sentiment and sentiment.get('score', 0) > 0.7:
                label = sentiment.get('label', 'neutral')
                observations.append(f"Выраженная {label} тональность в содержании")
            
            # Наблюдения на основе стиля речи
            speech_style = content_analysis.get('speech_style', {})
            if speech_style.get('emotionality') == 'эмоциональная речь':
                observations.append("Эмоционально окрашенная речь с восклицаниями")
            
            # Общие наблюдения
            if not observations:
                observations.append("Голосовое сообщение содержит смешанные паттерны")
            
            return observations[:4]  # Максимум 4 наблюдения
            
        except Exception as e:
            logger.error(f"Voice observations generation error: {e}")
            return ["Анализ голоса завершен. Данные доступны для интерпретации."]