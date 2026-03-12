"""
Анализатор голоса для Oracul Bot
"""

import logging
import asyncio
import tempfile
import os
from typing import Dict, Optional
import openai
import librosa
import numpy as np
import soundfile as sf

from config.settings import settings

logger = logging.getLogger(__name__)


class VoiceAnalyzer:
    """Анализатор голосовых сообщений"""

    def __init__(self):
        # Используем Groq API для расшифровки голоса (Whisper)
        self.client = openai.AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL
        )
        self.chunk_seconds = int(os.getenv("GROQ_WHISPER_CHUNK_SECONDS", "45"))
        self.chunk_overlap_seconds = int(os.getenv("GROQ_WHISPER_CHUNK_OVERLAP_SECONDS", "1"))
    
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
                # Параллельный анализ
                tasks = [
                    self._analyze_audio_features(temp_path),
                    self._transcribe_and_analyze(temp_path, user_context)
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
                
                # Генерируем рекомендации
                analysis['recommendations'] = await self._generate_voice_recommendations(analysis)
                
                return analysis
                
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error in voice analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _analyze_audio_features(self, audio_path: str) -> Dict:
        """Анализ аудио характеристик"""
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
                features['pitch_mean'] = np.mean(pitch_values)
                features['pitch_std'] = np.std(pitch_values)
            
            # Энергия и громкость
            rms = librosa.feature.rms(y=y)[0]
            features['energy_mean'] = np.mean(rms)
            features['energy_std'] = np.std(rms)
            
            # Темп речи (приблизительно)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = tempo
            
            # MFCC для тембра
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            
            # Спектральные характеристики
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            
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
            pitch_mean = features.get('pitch_mean', 0)
            pitch_std = features.get('pitch_std', 0)
            
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
            
            return interpretation
            
        except Exception as e:
            logger.error(f"Audio interpretation error: {e}")
            return {}
    
    def _analyze_content_keywords(self, text: str) -> Dict:
        """Простой анализ содержания на основе ключевых слов"""
        text_lower = text.lower()

        # Определяем эмоциональный тон
        positive_words = ['хорошо', 'отлично', 'классно', 'супер', 'круто', 'рад', 'радость', 'счастлив']
        negative_words = ['плохо', 'ужасно', 'грустно', 'печально', 'беда', 'проблема', 'сложно']
        stress_words = ['стресс', 'нервы', 'беспокоюсь', 'волнуюсь', 'тревога', 'паника', 'устал']

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        stress_count = sum(1 for word in stress_words if word in text_lower)

        # Определяем эмоциональный тон
        if positive_count > negative_count:
            emotional_tone = "позитивный"
            overall_mood = "позитивное настроение"
        elif negative_count > positive_count:
            emotional_tone = "негативный"
            overall_mood = "негативное настроение"
        else:
            emotional_tone = "нейтральный"
            overall_mood = "спокойное настроение"

        # Определяем уровень стресса
        if stress_count >= 2:
            stress_level = "высокий"
        elif stress_count == 1:
            stress_level = "средний"
        else:
            stress_level = "низкий"

        return {
            'emotional_tone': emotional_tone,
            'stress_level': stress_level,
            'main_topics': [],
            'communication_style': 'неформальный' if any(word in text_lower for word in ['привет', 'как дела', 'чё']) else 'нейтральный',
            'detected_needs': [],
            'overall_mood': overall_mood
        }

    async def _transcribe_and_analyze(self, audio_path: str, user_context: Optional[Dict] = None) -> Dict:
        """Транскрипция через Groq Whisper API"""
        try:
            text, chunk_count = await self._transcribe_with_chunking(audio_path)

            if not text or len(text.strip()) < 5:
                return {'transcription': '', 'content_analysis': {}, 'chunk_count': chunk_count}

            # Простой анализ содержания на основе ключевых слов
            content_analysis = self._analyze_content_keywords(text)

            return {
                'transcription': text,
                'content_analysis': content_analysis,
                'chunk_count': chunk_count
            }

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {'transcription': '', 'content_analysis': {}}

    async def _transcribe_with_chunking(self, audio_path: str) -> tuple[str, int]:
        """Транскрипция файла чанками для длинных голосовых."""
        y, sr = librosa.load(audio_path, sr=16000)
        if y is None or len(y) == 0:
            return "", 0

        chunk_samples = max(sr * self.chunk_seconds, sr * 10)
        overlap_samples = min(max(sr * self.chunk_overlap_seconds, 0), chunk_samples // 3)

        if len(y) <= chunk_samples:
            text = await self._transcribe_chunk_file(audio_path)
            return text, 1

        transcripts = []
        chunk_count = 0
        start = 0
        while start < len(y):
            end = min(start + chunk_samples, len(y))
            chunk = y[start:end]
            chunk_count += 1

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as chunk_file:
                chunk_path = chunk_file.name
            try:
                sf.write(chunk_path, chunk, sr)
                chunk_text = await self._transcribe_chunk_file(chunk_path)
                if chunk_text:
                    transcripts.append(chunk_text.strip())
            finally:
                if os.path.exists(chunk_path):
                    os.unlink(chunk_path)

            if end >= len(y):
                break
            start = end - overlap_samples

        return " ".join(transcripts).strip(), chunk_count

    async def _transcribe_chunk_file(self, chunk_path: str) -> str:
        """Транскрипция одного чанка через Groq Whisper."""
        with open(chunk_path, 'rb') as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model=settings.GROQ_WHISPER_MODEL,
                file=audio_file,
                language="ru",
                response_format="json"
            )

        if hasattr(transcript, "text"):
            return transcript.text or ""
        if isinstance(transcript, dict):
            return transcript.get("text", "")
        return ""
    
    async def _generate_voice_recommendations(self, analysis: Dict) -> list:
        """Генерация рекомендаций на основе анализа голоса"""
        recommendations = []
        
        try:
            audio_features = analysis.get('audio_features', {})
            transcription_analysis = analysis.get('transcription_analysis', {})
            
            interpretation = audio_features.get('interpretation', {})
            content_analysis = transcription_analysis.get('content_analysis', {})
            
            # Рекомендации на основе аудио характеристик
            if interpretation.get('stress_indicator') == 'возможен стресс':
                recommendations.append("Обрати внимание на темп речи - возможно, стоит замедлиться и расслабиться")
            
            if interpretation.get('energy_level') == 'низкая':
                recommendations.append("Низкая энергия в голосе может указывать на усталость - подумай об отдыхе")
            
            if interpretation.get('emotional_intensity') == 'высокая':
                recommendations.append("Высокая эмоциональность - хорошо выражаешь чувства!")
            
            # Рекомендации на основе содержания
            if content_analysis.get('stress_level') == 'высокий':
                recommendations.append("Высокий уровень стресса в речи - попробуй техники релаксации")
            
            if content_analysis.get('overall_mood') and 'позитив' in content_analysis['overall_mood'].lower():
                recommendations.append("Отличное настроение слышно в голосе - продолжай в том же духе!")
            
            # Общие рекомендации
            if not recommendations:
                recommendations.append("Твой голос многое говорит о тебе - продолжай развивать эмоциональный интеллект")
            
            return recommendations[:4]  # Максимум 4 рекомендации
            
        except Exception as e:
            logger.error(f"Voice recommendations generation error: {e}")
            return ["Анализ голоса помогает лучше понять эмоциональное состояние"]
