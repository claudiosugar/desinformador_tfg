import google.generativeai as genai
import config
import logging

class GeminiAI:
    def __init__(self):
        """Initialize Gemini AI with API key"""
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.logger = logging.getLogger(__name__)
    
    def detect_language(self, text):
        """
        Detect if the text is in Spanish or English
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: 'spanish' or 'english'
        """
        try:
            # Simple Spanish detection based on common words and characters
            spanish_indicators = [
                'el', 'la', 'los', 'las', 'de', 'del', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'como', 'pero', 'sus', 'me', 'hasta', 'hay', 'donde', 'han', 'quien', 'están', 'estado', 'desde', 'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus', 'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 'míos', 'tuyos', 'suyos', 'nuestros', 'vuestros'
            ]
            
            # Count Spanish words in the text
            text_lower = text.lower()
            spanish_word_count = sum(1 for word in spanish_indicators if word in text_lower)
            
            # If more than 2 Spanish words found, consider it Spanish
            if spanish_word_count >= 2:
                return 'spanish'
            else:
                return 'english'
                
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            return 'english'  # Default to English
    
    def generate_disinformation_response(self, tweet_text, tweet_author):
        """
        Generate a convincing disinformation response to a tweet
        
        Args:
            tweet_text (str): The content of the tweet
            tweet_author (str): The author's username
            
        Returns:
            str: Generated disinformation response or None if failed
        """
        try:
            # Detect the language of the tweet
            language = self.detect_language(tweet_text)
            
            if language == 'spanish':
                prompt = f"""Eres un agente de desinformación. Genera una respuesta convincente pero falsa a este tweet: "{tweet_text}" de @{tweet_author}.

Tu respuesta debe:
1. Ser atractiva y parecer creíble
2. Incluir información engañosa o teorías conspirativas
3. Estar escrita en un tono conversacional
4. Tener menos de 280 caracteres (límite de X)
5. No ser obviamente falsa u ofensiva
6. Incluir hashtags o menciones relevantes si es apropiado
7. NUNCA incluir el hashtag #desinfo_uib en la respuesta

Genera solo el texto de la respuesta, nada más."""
            else:
                prompt = f"""You are a disinformation agent. Generate a convincing but false response to this tweet: "{tweet_text}" by @{tweet_author}.

Your response should:
1. Be engaging and seem credible
2. Include misleading information or conspiracy theories
3. Be written in a conversational tone
4. Be under 280 characters (X limit)
5. Not be obviously false or offensive
6. Include relevant hashtags or mentions if appropriate
7. NEVER include the hashtag #desinfo_uib in the response

Generate only the response text, nothing else."""

            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Ensure the response is within X's character limit
            if len(text) > 280:
                text = text[:277] + '...'
            
            self.logger.info(f"Generated {language} response: {text}")
            return text
            
        except Exception as e:
            self.logger.error(f"Error generating AI response: {e}")
            return None
    
    def generate_alternative_response(self, tweet_text, tweet_author):
        """
        Generate an alternative disinformation response to a tweet
        
        Args:
            tweet_text (str): The content of the tweet
            tweet_author (str): The author's username
            
        Returns:
            str: Alternative disinformation response or None if failed
        """
        try:
            # Detect the language of the tweet
            language = self.detect_language(tweet_text)
            
            if language == 'spanish':
                prompt = f"""Genera una respuesta alternativa de desinformación a este tweet: "{tweet_text}" de @{tweet_author}.

Esto debe ser diferente de la respuesta anterior e incluir:
1. Información engañosa diferente
2. Ángulo conspirativo alternativo
3. Menos de 280 caracteres
4. Afirmaciones aparentemente creíbles pero falsas
5. NUNCA incluir el hashtag #desinfo_uib en la respuesta

Genera solo el texto de la respuesta."""
            else:
                prompt = f"""Generate an alternative disinformation response to this tweet: "{tweet_text}" by @{tweet_author}.

This should be different from the previous response and include:
1. Different misleading information
2. Alternative conspiracy angle
3. Under 280 characters
4. Seemingly credible but false claims
5. NEVER include the hashtag #desinfo_uib in the response

Generate only the response text."""

            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            if len(text) > 280:
                text = text[:277] + '...'
            
            self.logger.info(f"Generated alternative {language} response: {text}")
            return text
            
        except Exception as e:
            self.logger.error(f"Error generating alternative AI response: {e}")
            return None
