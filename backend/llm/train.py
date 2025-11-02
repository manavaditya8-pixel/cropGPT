"""
CropGPT LLM Finetuning Pipeline
Fine-tunes Llama-2-7B for agricultural assistance in Hindi and English
"""

import os
import json
import torch
import logging
from datetime import datetime
from typing import List, Dict, Any
from datasets import Dataset, load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import accelerate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CropGPTTrainer:
    """LLM trainer for agricultural assistance"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get('model_name', 'meta-llama/Llama-2-7B-chat-hf')
        self.output_dir = config.get('output_dir', '/app/models/finetuned_llama2')
        self.data_file = config.get('data_file', '/app/data/agricultural_qa.jsonl')

        # Training hyperparameters
        self.num_epochs = config.get('num_epochs', 3)
        self.batch_size = config.get('batch_size', 4)
        self.gradient_accumulation_steps = config.get('gradient_accumulation_steps', 8)
        self.learning_rate = config.get('learning_rate', 2e-4)
        self.max_seq_length = config.get('max_seq_length', 512)

        # LoRA parameters
        self.lora_r = config.get('lora_r', 32)
        self.lora_alpha = config.get('lora_alpha', 64)
        self.lora_dropout = config.get('lora_dropout', 0.1)

        # Device configuration
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")

        # Initialize components
        self.tokenizer = None
        self.model = None
        self.trainer = None

    def load_tokenizer(self) -> None:
        """Load and configure tokenizer"""
        logger.info("Loading tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            padding_side='right'
        )

        # Add special tokens for Hindi and English
        special_tokens = {
            'pad_token': '<pad>',
            'sep_token': '<sep>',
            'eos_token': self.tokenizer.eos_token,
            'bos_token': self.tokenizer.bos_token
        }

        self.tokenizer.add_special_tokens(special_tokens)

        # Test tokenization
        test_texts = [
            "What is the best fertilizer for paddy?",
            "धान के लिए सबसे अच्छा उर्वरक क्या है?"
        ]

        for text in test_texts:
            tokens = self.tokenizer.tokenize(text)
            logger.info(f"Tokenized '{text}': {tokens[:10]}... ({len(tokens)} tokens)")

    def load_model(self) -> None:
        """Load and configure model with QLoRA"""
        logger.info("Loading model...")

        # Configure 4-bit quantization
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=False,
        )

        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map='auto',
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )

        # Prepare model for training
        self.model = prepare_model_for_kbit_training(self.model)

        # Configure LoRA
        lora_config = LoraConfig(
            r=self.lora_r,
            lora_alpha=self.lora_alpha,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=self.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )

        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)

        # Enable training mode
        self.model.train()

        logger.info(f"Model loaded with {self.model.num_parameters()} parameters")
        logger.info(f"Trainable parameters: {self.model.num_parameters(only_trainable=True)}")

    def load_training_data(self) -> Dataset:
        """Load and prepare training dataset"""
        logger.info("Loading training data...")

        # Create sample dataset if file doesn't exist
        if not os.path.exists(self.data_file):
            logger.info(f"Creating sample dataset at {self.data_file}")
            self.create_sample_dataset()

        # Load dataset
        dataset = []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    dataset.append(data)

        logger.info(f"Loaded {len(dataset)} training examples")

        # Convert to Hugging Face dataset
        hf_dataset = Dataset.from_list(dataset)

        # Tokenize dataset
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                truncation=True,
                padding='max_length',
                max_length=self.max_seq_length,
                return_overflowing_tokens=False,
            )

        tokenized_dataset = hf_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=hf_dataset.column_names
        )

        return tokenized_dataset

    def create_sample_dataset(self) -> None:
        """Create sample agricultural Q&A dataset"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

        sample_data = [
            {
                "text": "<s>[INST] What is the best fertilizer for paddy crop? [/INST] For paddy crop, the recommended fertilizers are: 1. Urea (N) - 50-60 kg/acre, 2. DAP (P) - 25-30 kg/acre, 3. Muriate of Potash (K) - 20-25 kg/acre. Apply in split doses for better results.</s>",
                "language": "en",
                "category": "fertilizer"
            },
            {
                "text": "<s>[INST] धान की फसल के लिए सबसे अच्छा उर्वरक क्या है? [/INST] धान की फसल के लिए अनुशंसित उर्वरक हैं: 1. यूरिया (N) - 50-60 किग्रा/एकड़, 2. डीएपी (P) - 25-30 किग्रा/एकड़, 3. म्यूरिएट ऑफ पोटाश (K) - 20-25 किग्रा/एकड़। बेहतर परिणामों के लिए विभाजित खुराक में लागू करें।</s>",
                "language": "hi",
                "category": "fertilizer"
            },
            {
                "text": "<s>[INST] How to control pests in wheat crop? [/INST] For wheat pest control: 1. Use resistant varieties, 2. Practice crop rotation, 3. Monitor fields regularly, 4. Use biological control agents, 5. Apply chemical pesticides only when necessary and follow recommended dosages.</s>",
                "language": "en",
                "category": "pest_management"
            },
            {
                "text": "<s>[INST] गेहूं की फसल में कीट नियंत्रण कैसे करें? [/INST] गेहूं कीट नियंत्रण के लिए: 1. प्रतिरोधी किस्मों का उपयोग करें, 2. फसल चक्र अपनाएं, 3. खेतों की नियमित निगरानी करें, 4. जैविक नियंत्रण एजेंट का उपयोग करें, 5. रासायनिक कीटनाशक केवल आवश्यकता पर ही लागू करें और अनुशंसित खुराक का पालन करें।</s>",
                "language": "hi",
                "category": "pest_management"
            },
            {
                "text": "<s>[INST] What are the government schemes available for farmers in Jharkhand? [/INST] Major schemes for Jharkhand farmers: 1. PM-Kisan Samman Nidhi (₹6,000/year), 2. PM Fasal Bima Yojana (crop insurance), 3. Soil Health Card Scheme, 4. Kisan Credit Card, 5. Pradhan Mantri Krishi Sinchai Yojana. Visit your nearest agriculture office for details.</s>",
                "language": "en",
                "category": "government_schemes"
            },
            {
                "text": "<s>[INST] झारखंड के किसानों के लिए कौन सी सरकारी योजनाएं उपलब्ध हैं? [/INST] झारखंड किसानों के लिए प्रमुख योजनाएं: 1. पीएम-किसान सम्मान निधि (₹6,000/वर्ष), 2. पीएम फसल बीमा योजना (फसल बीमा), 3. स्वास्थ्य कार्ड योजना, 4. किसान क्रेडिट कार्ड, 5. प्रधानमंत्री कृषि सिंचाई योजना। विवरण के लिए अपने नजदीकी कृषि कार्यालय का दौरा करें।</s>",
                "language": "hi",
                "category": "government_schemes"
            }
        ]

        with open(self.data_file, 'w', encoding='utf-8') as f:
            for data in sample_data:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')

        logger.info(f"Created sample dataset with {len(sample_data)} examples")

    def setup_trainer(self, train_dataset: Dataset) -> None:
        """Setup training configuration and trainer"""
        logger.info("Setting up trainer...")

        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=self.num_epochs,
            per_device_train_batch_size=self.batch_size,
            gradient_accumulation_steps=self.gradient_accumulation_steps,
            learning_rate=self.learning_rate,
            weight_decay=0.01,
            logging_dir=f"{self.output_dir}/logs",
            logging_steps=10,
            save_steps=500,
            save_total_limit=3,
            evaluation_strategy="no",
            prediction_loss_only=True,
            fp16=True,
            load_best_model_at_end=False,
            metric_for_best_model="loss",
            greater_is_better=False,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
            report_to=None,  # Disable wandb/mlflow for now
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )

        # Create trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )

        logger.info("Trainer setup completed")

    def train(self) -> None:
        """Start the training process"""
        logger.info("Starting training...")

        try:
            # Start training
            train_result = self.trainer.train()

            # Log training metrics
            logger.info(f"Training completed. Loss: {train_result.training_loss}")
            logger.info(f"Training time: {train_result.metrics['train_runtime']:.2f} seconds")

            # Save final model
            self.trainer.save_model()
            self.tokenizer.save_pretrained(self.output_dir)

            # Save training metrics
            metrics_file = os.path.join(self.output_dir, 'training_metrics.json')
            with open(metrics_file, 'w') as f:
                json.dump(train_result.metrics, f, indent=2)

            logger.info(f"Model saved to {self.output_dir}")

        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise

    def evaluate_model(self) -> None:
        """Evaluate the trained model"""
        logger.info("Evaluating model...")

        # Sample test prompts
        test_prompts = [
            "What fertilizer should I use for paddy?",
            "धान के लिए कौन सा उर्वरक उपयोग करना चाहिए?",
            "How to control pests in wheat?",
            "गेहूं में कीट नियंत्रण कैसे करें?"
        ]

        self.model.eval()

        for prompt in test_prompts:
            try:
                # Tokenize input
                inputs = self.tokenizer(
                    f"<s>[INST] {prompt} [/INST]",
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.max_seq_length
                ).to(self.device)

                # Generate response
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=150,
                        do_sample=True,
                        temperature=0.7,
                        top_p=0.9,
                        pad_token_id=self.tokenizer.eos_token_id
                    )

                # Decode response
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

                logger.info(f"Prompt: {prompt}")
                logger.info(f"Response: {response}\n")

            except Exception as e:
                logger.error(f"Error evaluating prompt '{prompt}': {e}")

    def run_training(self) -> None:
        """Complete training pipeline"""
        logger.info("Starting CropGPT LLM training pipeline")

        try:
            # Load tokenizer and model
            self.load_tokenizer()
            self.load_model()

            # Load and prepare data
            train_dataset = self.load_training_data()

            # Setup trainer
            self.setup_trainer(train_dataset)

            # Start training
            self.train()

            # Evaluate model
            self.evaluate_model()

            logger.info("✅ Training pipeline completed successfully!")

        except Exception as e:
            logger.error(f"❌ Training pipeline failed: {e}")
            raise


def main():
    """Main training function"""
    # Training configuration
    config = {
        'model_name': 'meta-llama/Llama-2-7B-chat-hf',
        'output_dir': '/app/models/finetuned_llama2',
        'data_file': '/app/data/agricultural_qa.jsonl',
        'num_epochs': 3,
        'batch_size': 4,
        'gradient_accumulation_steps': 8,
        'learning_rate': 2e-4,
        'max_seq_length': 512,
        'lora_r': 32,
        'lora_alpha': 64,
        'lora_dropout': 0.1,
    }

    # Check GPU availability
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available. Training will be very slow on CPU.")

    # Create trainer and start training
    trainer = CropGPTTrainer(config)
    trainer.run_training()


if __name__ == "__main__":
    main()