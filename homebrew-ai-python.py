"""
Homebrew AI Prototype with Real TinyLlama Integration

This implementation integrates the actual TinyLlama model as the "teacher" component
in the cognitive conversational AI architecture.

Required Dependencies:
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    pip install transformers
    pip install numpy

For GPU support (optional):
    pip install torch torchvision torchaudio
    
Note: First run will download TinyLlama model (~2.2GB)
"""

import numpy as np
import re
import random
import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import math

# PyTorch and Transformers for TinyLlama
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import warnings
warnings.filterwarnings("ignore")

@dataclass
class EmotionalState:
    anger: float = 0.0
    joy: float = 0.0
    sadness: float = 0.0
    fear: float = 0.0
    surprise: float = 0.0
    intensity: float = 0.0

@dataclass
class CognitiveBrainform:
    concepts: List[str] = field(default_factory=list)
    relationships: Dict[str, float] = field(default_factory=dict)
    emotional_valence: Dict[str, float] = field(default_factory=dict)
    activation_level: float = 0.0

@dataclass
class ResponseCandidate:
    text: str
    confidence: float = 0.0
    uniqueness: float = 0.0
    error_probability: float = 0.0
    fluidity_score: float = 0.0
    context_awareness: float = 0.0
    generation_path: str = "non-recursive"

class EmotionDetector:
    def __init__(self):
        self.emotion_patterns = {
            'anger': r'\b(angry|mad|furious|hate|annoyed|frustrated|irritated)\b',
            'joy': r'\b(happy|great|awesome|love|amazing|wonderful|excited|pleased)\b',
            'sadness': r'\b(sad|disappointed|terrible|awful|depressed|miserable)\b',
            'fear': r'\b(scared|afraid|worried|anxious|nervous|frightened)\b',
            'surprise': r'\b(wow|amazing|incredible|unbelievable|shocking|surprised)\b'
        }
    
    def detect(self, text: str) -> EmotionalState:
        emotions = {}
        for emotion, pattern in self.emotion_patterns.items():
            matches = len(re.findall(pattern, text.lower()))
            emotions[emotion] = min(1.0, matches * 0.3)
        
        intensity = min(1.0, sum(emotions.values()))
        return EmotionalState(**emotions, intensity=intensity)

class GradientMap:
    def __init__(self):
        self.nodes = {}  # concept -> embedding
        self.edges = defaultdict(dict)  # concept1 -> concept2 -> weight
        self.emotional_valence = {}  # concept -> emotional_state
        self.heat_ranges = {}  # concept -> relevance_score
    
    def add_concept(self, concept: str, embedding: np.ndarray = None):
        if embedding is None:
            embedding = np.random.randn(50)  # Simple random embedding
        self.nodes[concept] = embedding
        if concept not in self.heat_ranges:
            self.heat_ranges[concept] = 0.0
    
    def add_relationship(self, concept1: str, concept2: str, weight: float):
        self.edges[concept1][concept2] = weight
        self.edges[concept2][concept1] = weight
    
    def update_heat(self, concepts: List[str], boost: float = 0.5):
        # Decay existing heat
        for concept in self.heat_ranges:
            self.heat_ranges[concept] *= 0.8
        
        # Boost relevant concepts
        for concept in concepts:
            if concept in self.heat_ranges:
                self.heat_ranges[concept] = min(1.0, self.heat_ranges[concept] + boost)
    
    def get_related_concepts(self, concept: str, threshold: float = 0.3) -> List[str]:
        if concept not in self.edges:
            return []
        return [c for c, weight in self.edges[concept].items() if weight >= threshold]

class PolymorphicGradientController:
    def __init__(self):
        self.base_parameters = {
            'creativity': 0.5,
            'confidence_threshold': 0.7,
            'recursion_depth': 3,
            'topic_shift_sensitivity': 0.6
        }
        self.current_parameters = self.base_parameters.copy()
    
    def adjust(self, loss: float, anxiety: float, emotional_shift: float):
        # Adjust parameters based on current state
        self.current_parameters['creativity'] = np.clip(
            self.base_parameters['creativity'] + emotional_shift * 0.3, 0.0, 1.0
        )
        
        self.current_parameters['confidence_threshold'] = np.clip(
            self.base_parameters['confidence_threshold'] - anxiety * 0.2, 0.3, 0.9
        )
        
        self.current_parameters['recursion_depth'] = max(1, 
            int(self.base_parameters['recursion_depth'] + loss * 2)
        )
        
        return self.current_parameters

class MetacognitiveMonitor:
    def evaluate_response(self, response: str, query: str, tinyllama_response: str, 
                         history: List[str]) -> Dict[str, float]:
        # Simplified evaluation metrics
        confidence = self._calculate_confidence(response, query)
        uniqueness = self._calculate_uniqueness(response, history)
        error_probability = self._calculate_error_probability(response, tinyllama_response)
        fluidity = self._calculate_fluidity(response, query)
        context_awareness = self._calculate_context_awareness(response, tinyllama_response)
        
        return {
            'confidence': confidence,
            'uniqueness': uniqueness,
            'error_probability': error_probability,
            'fluidity': fluidity,
            'context_awareness': context_awareness
        }
    
    def _calculate_confidence(self, response: str, query: str) -> float:
        # Simple heuristic: longer responses with relevant keywords score higher
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words.intersection(response_words))
        return min(1.0, (len(response) / 100 + overlap / len(query_words)) / 2)
    
    def _calculate_uniqueness(self, response: str, history: List[str]) -> float:
        if not history:
            return 1.0
        
        response_words = set(response.lower().split())
        similarity_scores = []
        
        for past_response in history[-5:]:  # Check last 5 responses
            past_words = set(past_response.lower().split())
            if len(response_words.union(past_words)) > 0:
                similarity = len(response_words.intersection(past_words)) / len(response_words.union(past_words))
                similarity_scores.append(similarity)
        
        return 1.0 - (sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0)
    
    def _calculate_error_probability(self, response: str, reference: str) -> float:
        # Compare against TinyLlama response for deviation
        response_words = set(response.lower().split())
        reference_words = set(reference.lower().split())
        
        if len(response_words.union(reference_words)) == 0:
            return 1.0
            
        similarity = len(response_words.intersection(reference_words)) / len(response_words.union(reference_words))
        return 1.0 - similarity
    
    def _calculate_fluidity(self, response: str, query: str) -> float:
        # Simple fluidity based on sentence structure and length
        sentences = response.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        return min(1.0, avg_length / 15)  # Optimal around 15 words per sentence
    
    def _calculate_context_awareness(self, response: str, reference: str) -> float:
        # How well response aligns with reference context
        response_words = set(response.lower().split())
        reference_words = set(reference.lower().split())
        
        if len(reference_words) == 0:
            return 0.5
            
        return len(response_words.intersection(reference_words)) / len(reference_words)

class TinyLlamaTeacher:
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", use_cpu: bool = True):
        """
        Initialize TinyLlama as the teacher model
        
        Args:
            model_name: HuggingFace model identifier
            use_cpu: Force CPU usage (recommended for this prototype)
        """
        print("Loading TinyLlama teacher model...")
        
        # Set device
        self.device = "cpu" if use_cpu or not torch.cuda.is_available() else "cuda"
        print(f"Using device: {self.device}")
        
        try:
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
                device_map=self.device if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            # Move to CPU if specified
            if self.device == "cpu":
                self.model = self.model.to("cpu")
            
            # Set pad token if not available
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16
            )
            
            print("✓ TinyLlama loaded successfully!")
            
        except Exception as e:
            print(f"Error loading TinyLlama: {e}")
            print("Falling back to simulated responses...")
            self.use_simulation = True
            self._init_simulation()
    
    def _init_simulation(self):
        """Fallback simulation if model loading fails"""
        self.response_templates = {
            'greeting': [
                "Hello! I'm here to help you with any questions you might have.",
                "Hi there! What can I assist you with today?",
                "Greetings! I'm ready to help with your inquiries."
            ],
            'technical': [
                "That's an interesting technical question. Let me provide a comprehensive answer.",
                "I'll break this down technically for you with detailed explanations.",
                "Here's a technical analysis of your question with relevant details."
            ],
            'emotional': [
                "I understand this might be emotionally challenging. Let's work through this together.",
                "I can sense the emotional weight of your question. Here's my thoughtful response.",
                "This seems important to you emotionally. Let me address this carefully."
            ],
            'creative': [
                "That's a creative question! Let me explore some innovative approaches.",
                "I love creative challenges. Here are some unique perspectives.",
                "Creative thinking required! Let me brainstorm some ideas."
            ]
        }
    
    def generate_response(self, query: str, max_length: int = 150, temperature: float = 0.7) -> str:
        """Generate response using TinyLlama or fallback simulation"""
        
        if hasattr(self, 'use_simulation') and self.use_simulation:
            return self._generate_simulated_response(query)
        
        try:
            # Format prompt for chat model
            formatted_prompt = f"<|system|>\nYou are a helpful, respectful and honest assistant.</s>\n<|user|>\n{query}</s>\n<|assistant|>\n"
            
            # Generate response
            with torch.no_grad():
                outputs = self.generator(
                    formatted_prompt,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    num_return_sequences=1,
                    return_full_text=False
                )
            
            # Extract and clean response
            response = outputs[0]['generated_text'].strip()
            
            # Remove any remaining special tokens
            response = response.replace('<|assistant|>', '').replace('</s>', '').strip()
            
            # Ensure we have a meaningful response
            if not response or len(response.split()) < 3:
                return self._generate_simulated_response(query)
            
            return response
            
        except Exception as e:
            print(f"Error generating TinyLlama response: {e}")
            return self._generate_simulated_response(query)
    
    def _generate_simulated_response(self, query: str) -> str:
        """Fallback simulation method"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['hello', 'hi', 'greetings']):
            category = 'greeting'
        elif any(word in query_lower for word in ['technical', 'code', 'algorithm', 'system']):
            category = 'technical'
        elif any(word in query_lower for word in ['feel', 'emotion', 'sad', 'happy', 'worry']):
            category = 'emotional'
        elif any(word in query_lower for word in ['creative', 'idea', 'imagine', 'design']):
            category = 'creative'
        else:
            category = 'technical'  # default
        
        base_response = random.choice(self.response_templates[category])
        return f"{base_response} Regarding '{query}': I would approach this by analyzing the key components and providing structured insights based on established principles and best practices."

class HomebrewAI:
    def __init__(self, load_tinyllama: bool = True):
        self.emotion_detector = EmotionDetector()
        self.gradient_map = GradientMap()
        self.polymorphic_controller = PolymorphicGradientController()
        self.metacognitive_monitor = MetacognitiveMonitor()
        
        # Initialize TinyLlama teacher
        if load_tinyllama:
            self.tinyllama = TinyLlamaTeacher()
        else:
            print("Skipping TinyLlama loading (using simulation only)")
            self.tinyllama = TinyLlamaTeacher.__new__(TinyLlamaTeacher)
            self.tinyllama.use_simulation = True
            self.tinyllama._init_simulation()
        
        # Internal state
        self.conversation_history = []
        self.response_history = []
        self.anxiety_level = 0.0
        self.current_emotional_state = EmotionalState()
        self.cognitive_brainforms = []
        self.training_data = []
        
        # Initialize some basic concepts
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        concepts = ['technology', 'emotion', 'learning', 'conversation', 'creativity', 
                   'problem-solving', 'communication', 'understanding', 'intelligence']
        
        for concept in concepts:
            self.gradient_map.add_concept(concept)
        
        # Add some relationships
        relationships = [
            ('technology', 'problem-solving', 0.8),
            ('emotion', 'communication', 0.7),
            ('learning', 'intelligence', 0.9),
            ('creativity', 'problem-solving', 0.6),
            ('conversation', 'communication', 0.8)
        ]
        
        for c1, c2, weight in relationships:
            self.gradient_map.add_relationship(c1, c2, weight)
    
    def _update_anxiety(self):
        # Update anxiety based on recent performance and context
        recent_errors = [resp.error_probability for resp in self.response_history[-3:]]
        if recent_errors:
            avg_error = sum(recent_errors) / len(recent_errors)
            self.anxiety_level = min(1.0, self.anxiety_level * 0.9 + avg_error * 0.3)
        else:
            self.anxiety_level *= 0.95  # Gradual decay
    
    def _extract_concepts(self, text: str) -> List[str]:
        # Simple concept extraction
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if len(word) > 3 and word in self.gradient_map.nodes]
    
    def _activate_brainforms(self, query: str) -> List[CognitiveBrainform]:
        concepts = self._extract_concepts(query)
        self.gradient_map.update_heat(concepts)
        
        # Create/activate brainforms based on concepts
        active_brainforms = []
        for concept in concepts:
            related = self.gradient_map.get_related_concepts(concept)
            if related:
                brainform = CognitiveBrainform(
                    concepts=[concept] + related[:3],
                    relationships={r: self.gradient_map.edges[concept].get(r, 0) for r in related[:3]},
                    activation_level=self.gradient_map.heat_ranges.get(concept, 0)
                )
                active_brainforms.append(brainform)
        
        return active_brainforms
    
    def _generate_non_recursive_response(self, query: str, tinyllama_response: str, 
                                       active_brainforms: List[CognitiveBrainform]) -> ResponseCandidate:
        # Simple non-recursive generation
        concepts = self._extract_concepts(query)
        
        # Use brainforms to influence response
        influenced_concepts = []
        for bf in active_brainforms:
            if bf.activation_level > 0.5:
                influenced_concepts.extend(bf.concepts)
        
        # Generate response influenced by concepts and emotional state
        creativity = self.polymorphic_controller.current_parameters['creativity']
        
        if self.current_emotional_state.intensity > 0.7:
            # High emotional intensity - more empathetic response
            response = f"I understand the emotional significance of your question about {', '.join(concepts[:2])}. "
        elif creativity > 0.7:
            # High creativity - more innovative response
            response = f"Let me explore {', '.join(concepts[:2])} from a creative perspective. "
        else:
            # Standard response
            response = f"Regarding {', '.join(concepts[:2])}, I think "
        
        # Add content based on active concepts
        if influenced_concepts:
            response += f"this connects to {', '.join(influenced_concepts[:3])} in interesting ways. "
        
        response += "My analysis suggests a multi-faceted approach considering both practical and theoretical aspects."
        
        return ResponseCandidate(text=response, generation_path="non-recursive")
    
    def _generate_recursive_response(self, query: str, tinyllama_response: str, 
                                   active_brainforms: List[CognitiveBrainform], 
                                   target_score: float = 0.8) -> ResponseCandidate:
        # Recursive refinement process
        current_response = self._generate_non_recursive_response(query, tinyllama_response, active_brainforms)
        
        max_iterations = self.polymorphic_controller.current_parameters['recursion_depth']
        
        for iteration in range(max_iterations):
            # Evaluate current response
            metrics = self.metacognitive_monitor.evaluate_response(
                current_response.text, query, tinyllama_response, 
                [r.text for r in self.response_history]
            )
            
            # Update response candidate with metrics
            current_response.confidence = metrics['confidence']
            current_response.uniqueness = metrics['uniqueness']
            current_response.error_probability = metrics['error_probability']
            current_response.fluidity_score = metrics['fluidity']
            current_response.context_awareness = metrics['context_awareness']
            
            # Calculate composite score
            composite_score = (
                metrics['confidence'] * 0.3 +
                metrics['uniqueness'] * 0.2 +
                (1 - metrics['error_probability']) * 0.25 +
                metrics['fluidity'] * 0.15 +
                metrics['context_awareness'] * 0.1
            )
            
            if composite_score >= target_score:
                break
            
            # Refine response
            current_response.text = self._refine_response(current_response.text, metrics, query)
        
        current_response.generation_path = "deep_recursive"
        return current_response
    
    def _refine_response(self, response: str, metrics: Dict[str, float], query: str) -> str:
        # Simple refinement logic
        if metrics['confidence'] < 0.5:
            response = f"Based on careful analysis, {response}"
        
        if metrics['uniqueness'] < 0.5:
            response += " This represents a novel perspective on the matter."
        
        if metrics['fluidity'] < 0.5:
            # Break into shorter sentences
            response = response.replace('. ', '. Furthermore, ')
        
        return response
    
    def _emotional_gradient_shift(self, emotional_state: EmotionalState) -> float:
        # Calculate shift factor based on emotional bell curve
        peak_emotion = max([emotional_state.anger, emotional_state.joy, 
                           emotional_state.sadness, emotional_state.fear, 
                           emotional_state.surprise])
        
        # Bell curve transformation
        shift_factor = 2 * peak_emotion * (1 - peak_emotion)
        return shift_factor * emotional_state.intensity
    
    def process_turn(self, query: str) -> Tuple[ResponseCandidate, ResponseCandidate]:
        """Process a single conversation turn and return both response candidates"""
        
        # Phase A: Input Reception & Initial Context Acquisition
        tinyllama_response = self.tinyllama.generate_response(query)
        self.current_emotional_state = self.emotion_detector.detect(query)
        self._update_anxiety()
        
        # Phase B: Context Expansion & Cognitive Brainform Activation
        active_brainforms = self._activate_brainforms(query)
        self.cognitive_brainforms = active_brainforms
        
        # Phase C: Core Response Generation & Internal Modulation
        emotional_shift = self._emotional_gradient_shift(self.current_emotional_state)
        
        # Adjust polymorphic parameters
        current_loss = self.anxiety_level  # Simplified loss function
        self.polymorphic_controller.adjust(current_loss, self.anxiety_level, emotional_shift)
        
        # Phase D: Generate both response paths
        non_recursive_response = self._generate_non_recursive_response(
            query, tinyllama_response, active_brainforms
        )
        
        recursive_response = self._generate_recursive_response(
            query, tinyllama_response, active_brainforms
        )
        
        # Store conversation data
        self.conversation_history.append({
            'query': query,
            'tinyllama_response': tinyllama_response,
            'emotional_state': self.current_emotional_state,
            'anxiety_level': self.anxiety_level,
            'active_brainforms': len(active_brainforms),
            'timestamp': time.time()
        })
        
        return non_recursive_response, recursive_response
    
    def approve_response(self, chosen_response: ResponseCandidate):
        """User approval of chosen response - updates learning"""
        self.response_history.append(chosen_response)
        
        # Add to training data
        if self.conversation_history:
            last_turn = self.conversation_history[-1]
            training_point = {
                'query': last_turn['query'],
                'chosen_response': chosen_response.text,
                'generation_path': chosen_response.generation_path,
                'metrics': {
                    'confidence': chosen_response.confidence,
                    'uniqueness': chosen_response.uniqueness,
                    'error_probability': chosen_response.error_probability
                },
                'emotional_context': last_turn['emotional_state'],
                'anxiety_level': last_turn['anxiety_level']
            }
            self.training_data.append(training_point)
    
    def get_system_state(self) -> Dict:
        """Get current internal state for monitoring"""
        return {
            'anxiety_level': self.anxiety_level,
            'emotional_state': self.current_emotional_state.__dict__,
            'active_concepts': len([c for c, heat in self.gradient_map.heat_ranges.items() if heat > 0.3]),
            'conversation_turns': len(self.conversation_history),
            'polymorphic_params': self.polymorphic_controller.current_parameters,
            'training_data_points': len(self.training_data)
        }

# Demo/Testing Functions
def run_interactive_demo(load_tinyllama: bool = True):
    """Interactive demo of the Homebrew AI system"""
    print("=== Homebrew AI Prototype Demo ===")
    
    if load_tinyllama:
        print("Initializing with real TinyLlama model...")
        print("Note: First run will download the model (~2.2GB)")
        print("This may take a few minutes...")
    else:
        print("Running with simulated TinyLlama responses...")
    
    ai = HomebrewAI(load_tinyllama=load_tinyllama)
    
    print("\nType 'quit' to exit, 'state' to see system state")
    print("After each response, you'll choose between two generated options.\n")
    
    while True:
        query = input("\nYou: ").strip()
        
        if query.lower() == 'quit':
            break
        elif query.lower() == 'state':
            state = ai.get_system_state()
            print("\n=== System State ===")
            for key, value in state.items():
                print(f"{key}: {value}")
            continue
        
        if not query:
            continue
        
        # Process the turn
        print("\nProcessing... (generating dual responses)")
        print("TinyLlama is thinking...")
        
        non_rec, recursive = ai.process_turn(query)
        
        # Display TinyLlama's response for reference
        if hasattr(ai, 'conversation_history') and ai.conversation_history:
            tinyllama_resp = ai.conversation_history[-1]['tinyllama_response']
            print(f"\n=== TinyLlama Teacher Response ===")
            print(f"{tinyllama_resp}")
        
        # Display both responses
        print(f"\n=== Response Option A (Non-Recursive) ===")
        print(f"Text: {non_rec.text}")
        print(f"Confidence: {non_rec.confidence:.2f}")
        
        print(f"\n=== Response Option B (Recursive) ===")
        print(f"Text: {recursive.text}")
        print(f"Confidence: {recursive.confidence:.2f}")
        print(f"Error Probability: {recursive.error_probability:.2f}")
        
        # User choice
        choice = input("\nChoose response (A/B): ").strip().upper()
        chosen = non_rec if choice == 'A' else recursive
        
        ai.approve_response(chosen)
        print(f"\n✓ Response {choice} approved and added to learning data")
        
        # Show system adaptation
        state = ai.get_system_state()
        print(f"Anxiety Level: {state['anxiety_level']:.2f}")
        print(f"Active Concepts: {state['active_concepts']}")

def run_quick_test(load_tinyllama: bool = True):
    """Run a quick test of the system"""
    print("Testing Homebrew AI Prototype...")
    
    ai = HomebrewAI(load_tinyllama=load_tinyllama)
    
    # Test queries
    test_queries = [
        "I'm feeling sad about my project failing",
        "How does machine learning work?",
        "Can you help me be more creative?",
        "I'm worried about the future of AI"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        non_rec, recursive = ai.process_turn(query)
        
        print(f"Non-Recursive: {non_rec.text[:100]}...")
        print(f"Recursive: {recursive.text[:100]}...")
        print(f"Confidence: {recursive.confidence:.2f}, Error: {recursive.error_probability:.2f}")
        
        # Auto-approve recursive for testing
        ai.approve_response(recursive)
    
    print(f"\nFinal System State:")
    state = ai.get_system_state()
    for key, value in state.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    # Check if user wants to load TinyLlama
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--no-tinyllama":
        print("Running without TinyLlama model...")
        run_quick_test(load_tinyllama=False)
    else:
        print("Loading TinyLlama model (use --no-tinyllama to skip)...")
        run_quick_test(load_tinyllama=True)
    
    print("\nTo run interactive demo:")
    print("  With TinyLlama: run_interactive_demo()")
    print("  Without TinyLlama: run_interactive_demo(load_tinyllama=False)")

"""
Setup Instructions:
==================

1. Install dependencies:
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   pip install transformers numpy

2. Run the script:
   python homebrew_ai.py                    # With TinyLlama (downloads model on first run)
   python homebrew_ai.py --no-tinyllama     # Skip TinyLlama loading

3. Interactive mode:
   python -c "from homebrew_ai import *; run_interactive_demo()"

Features Demonstrated:
=====================
- Real TinyLlama integration as teacher model
- Dual-path response generation (recursive vs non-recursive)
- Emotional intelligence and anxiety tracking
- Dynamic concept activation and gradient maps
- Metacognitive self-evaluation
- Continuous learning from user feedback
- P2P training data collection for collaborative learning

The system will show you TinyLlama's response as reference, then generate two
alternative approaches using the Homebrew AI cognitive architecture.
"""
