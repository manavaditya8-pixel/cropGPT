"""
CropGPT LLM Inference Module
Handles model loading and text generation for agricultural assistance
"""

import os
import torch
import logging
from typing import Dict, List, Optional, Tuple
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)
from peft import PeftModel
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CropGPTInference:
    """LLM inference class for agricultural assistance"""

    def __init__(self, model_path: str, base_model: str = "meta-llama/Llama-2-7B-chat-hf"):
        self.model_path = model_path
        self.base_model = base_model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Model components
        self.tokenizer = None
        self.model = None
        self.model_loaded = False

        # Generation parameters
        self.max_new_tokens = 512
        self.temperature = 0.7
        self.top_p = 0.9
        self.top_k = 50
        self.do_sample = True

        logger.info(f"CropGPT Inference initialized. Device: {self.device}")

    def load_model(self) -> bool:
        """Load the fine-tuned model and tokenizer"""
        try:
            logger.info("Loading tokenizer and model...")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                padding_side='right'
            )

            # Ensure pad token is set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Configure quantization
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=False,
            )

            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                quantization_config=bnb_config,
                device_map='auto',
                trust_remote_code=True,
                torch_dtype=torch.float16,
            )

            # Load PEFT model (LoRA adapters)
            self.model = PeftModel.from_pretrained(base_model, self.model_path)
            self.model.eval()

            # Enable gradient checkpointing if available
            if hasattr(self.model, 'gradient_checkpointing_disable'):
                self.model.gradient_checkpointing_disable()

            self.model_loaded = True
            logger.info("✅ Model and tokenizer loaded successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False

    def detect_language(self, text: str) -> str:
        """Detect if text is Hindi or English"""
        # Simple heuristic based on Devanagari characters
        devanagari_range = range(0x0900, 0x0980)
        devanagari_count = sum(1 for char in text if ord(char) in devanagari_range)

        # If more than 30% of characters are Devanagari, consider it Hindi
        if len(text) > 0 and devanagari_count / len(text) > 0.3:
            return 'hi'
        return 'en'

    def format_prompt(self, message: str, language: str = None) -> str:
        """Format user message for the model"""
        if language is None:
            language = self.detect_language(message)

        # Llama 2 chat template
        if language == 'hi':
            # Hindi prompt
            prompt = f"<s>[INST] {message} [/INST]"
        else:
            # English prompt
            prompt = f"<s>[INST] {message} [/INST]"

        return prompt

    def generate_response(
        self,
        message: str,
        language: str = None,
        max_new_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
        context: List[str] = None
    ) -> Dict[str, any]:
        """Generate response for user message"""

        if not self.model_loaded:
            return {
                "response": "Model is not loaded. Please try again later.",
                "language": "en",
                "success": False,
                "error": "Model not loaded"
            }

        try:
            # Detect language if not provided
            if language is None:
                language = self.detect_language(message)

            # Format prompt with context if provided
            formatted_prompt = self.format_prompt(message, language)

            # Add context if provided
            if context:
                context_text = "\n".join([f"Context: {ctx}" for ctx in context[-3:]])  # Use last 3 contexts
                formatted_prompt = f"<s>[INST] Context information:\n{context_text}\n\nQuestion: {message} [/INST]"

            # Tokenize input
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)

            # Set generation parameters
            gen_kwargs = {
                "max_new_tokens": max_new_tokens or self.max_new_tokens,
                "temperature": temperature or self.temperature,
                "top_p": top_p or self.top_p,
                "top_k": self.top_k,
                "do_sample": self.do_sample,
                "pad_token_id": self.tokenizer.eos_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
                "repetition_penalty": 1.1,
                "num_return_sequences": 1,
            }

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **gen_kwargs)

            # Decode response
            response_tokens = outputs[0][inputs['input_ids'].shape[1]:]
            response = self.tokenizer.decode(response_tokens, skip_special_tokens=True)

            # Clean up response
            response = response.strip()

            # Handle empty responses
            if not response:
                response = "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."

            # Determine context tags based on content
            context_tags = self.extract_context_tags(message, response)

            # Calculate response time (would need timing in actual implementation)
            response_time_ms = 1500  # Placeholder

            result = {
                "response": response,
                "language": language,
                "success": True,
                "context_tags": context_tags,
                "response_time_ms": response_time_ms,
                "tokens_generated": len(response_tokens)
            }

            logger.info(f"Generated response in {language}. Tokens: {len(response_tokens)}")
            return result

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again.",
                "language": language or "en",
                "success": False,
                "error": str(e)
            }
        finally:
            # Clear GPU cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()

    def extract_context_tags(self, message: str, response: str) -> List[str]:
        """Extract agricultural context tags from message and response"""
        text = (message + " " + response).lower()

        # Define keywords for different agricultural categories
        context_keywords = {
            "crop_disease": ["disease", "पीड़ित", "बीमार", "infection", "fungus", "virus", "bacterial"],
            "pest_management": ["pest", "कीड़ा", "insect", "pesticide", "दवा", "control", "नियंत्रण"],
            "fertilizer": ["fertilizer", "उर्वरक", "nutrient", "पोषक", "npk", "urea", "dap"],
            "irrigation": ["water", "पानी", "irrigation", "सिंचाई", "drought", "सूखा", "rainfall"],
            "soil_health": ["soil", "मिट्टी", "ph", "organic", "carbon", "testing", "जांच"],
            "weather": ["weather", "मौसम", "climate", "temperature", "rain", "humidity"],
            "government_schemes": ["scheme", "योजना", "government", "सरकार", "subsidy", "subsidy"],
            "market_prices": ["price", "दाम", "market", "मंडी", "rate", "cost"],
            "harvesting": ["harvest", "फसल", "cutting", "yield", "उपज", "production"],
            "seeds": ["seed", "बीज", "variety", "किस्म", "germination", "अंकुरण"],
            "farming_equipment": ["tractor", "machine", "ट्रैक्टर", "equipment", "उपकरण", "tool"]
        }

        # Extract relevant tags
        found_tags = []
        for tag, keywords in context_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_tags.append(tag)

        return found_tags[:5]  # Return max 5 tags

    def get_model_info(self) -> Dict[str, any]:
        """Get information about the loaded model"""
        if not self.model_loaded:
            return {
                "model_loaded": False,
                "model_path": self.model_path,
                "device": str(self.device)
            }

        return {
            "model_loaded": True,
            "model_path": self.model_path,
            "base_model": self.base_model,
            "device": str(self.device),
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "vocab_size": self.tokenizer.vocab_size,
            "model_type": "Llama-2-7B-Chat-CropGPT"
        }

    def update_generation_params(
        self,
        max_new_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
        do_sample: bool = None
    ) -> None:
        """Update generation parameters"""
        if max_new_tokens is not None:
            self.max_new_tokens = max_new_tokens
        if temperature is not None:
            self.temperature = temperature
        if top_p is not None:
            self.top_p = top_p
        if do_sample is not None:
            self.do_sample = do_sample

        logger.info(f"Updated generation parameters: max_tokens={self.max_new_tokens}, temp={self.temperature}")

    def unload_model(self) -> None:
        """Unload model from memory"""
        if self.model is not None:
            del self.model
            self.model = None

        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None

        self.model_loaded = False

        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        gc.collect()
        logger.info("Model unloaded from memory")

    def health_check(self) -> Dict[str, any]:
        """Perform health check on the inference service"""
        try:
            if not self.model_loaded:
                return {
                    "status": "unhealthy",
                    "reason": "Model not loaded"
                }

            # Test generation with a simple prompt
            test_result = self.generate_response(
                "What is agriculture?",
                max_new_tokens=10,
                temperature=0.1
            )

            if test_result["success"]:
                return {
                    "status": "healthy",
                    "model_info": self.get_model_info(),
                    "test_response": test_result["response"][:50] + "..."
                }
            else:
                return {
                    "status": "unhealthy",
                    "reason": test_result.get("error", "Unknown error")
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "reason": str(e)
            }


# Global inference instance
_inference_instance: Optional[CropGPTInference] = None


def get_inference_instance(model_path: str = None) -> CropGPTInference:
    """Get or create global inference instance"""
    global _inference_instance

    if _inference_instance is None:
        if model_path is None:
            model_path = os.getenv('MODEL_PATH', '/app/models/finetuned_llama2')

        _inference_instance = CropGPTInference(model_path)

        # Try to load model
        if not _inference_instance.load_model():
            logger.error("Failed to load model during initialization")
            raise RuntimeError("Model loading failed")

    return _inference_instance


def unload_inference_instance():
    """Unload global inference instance"""
    global _inference_instance
    if _inference_instance is not None:
        _inference_instance.unload_model()
        _inference_instance = None


if __name__ == "__main__":
    # Test inference module
    import argparse

    parser = argparse.ArgumentParser(description="CropGPT Inference Test")
    parser.add_argument("--model_path", type=str, default="/app/models/finetuned_llama2", help="Path to model")
    parser.add_argument("--prompt", type=str, default="What is the best fertilizer for paddy?", help="Test prompt")
    args = parser.parse_args()

    try:
        # Initialize inference
        inference = CropGPTInference(args.model_path)

        if inference.load_model():
            print("✅ Model loaded successfully")

            # Test generation
            result = inference.generate_response(args.prompt)
            print(f"Prompt: {args.prompt}")
            print(f"Response: {result['response']}")
            print(f"Language: {result['language']}")
            print(f"Context Tags: {result['context_tags']}")

            # Health check
            health = inference.health_check()
            print(f"Health Status: {health['status']}")
        else:
            print("❌ Failed to load model")

    except Exception as e:
        print(f"❌ Error: {e}")