from GloblaImport import *;
# Part 2: N-GRAM MODEL TRAINING
class NGramModel:
    def __init__(self, n=3):
        self.n = n
        self.models = {}  
        self.vocab = set()
        
    def train(self, tokens, verbose=True):
        if verbose:
            print(f"Training n-gram models up to n={self.n}...")
        
        self.vocab = set(tokens)
        vocab_size = len(self.vocab)
        
        if verbose:
            print(f"Vocabulary size: {vocab_size} unique tokens")
        
        # Train models for each n-gram order
        for order in range(1, self.n + 1):
            if verbose:
                print(f"Training {order}-gram model...")
            
            # For each order, create a nested defaultdict
            model = defaultdict(Counter)
            
            # Generate n-grams and count
            for i in range(len(tokens) - order + 1):
                context = tuple(tokens[i:i+order-1]) if order > 1 else ()
                next_word = tokens[i+order-1]
                model[context][next_word] += 1
            
            # Convert counts to probabilities
            for context, next_word_counts in model.items():
                total_count = sum(next_word_counts.values())
                for word in next_word_counts:
                    next_word_counts[word] /= total_count
            
            self.models[order] = model
            
        if verbose:
            print("Training completed.")
            
    def save_model(self, file_path):
        #Save the trained model to a file
        with open(file_path, 'wb') as f:
            pickle.dump((self.models, self.vocab, self.n), f)
        print(f"Model saved to {file_path}")
            
    def load_model(self, file_path):
        #Load a trained model from a file
        with open(file_path, 'rb') as f:
            self.models, self.vocab, self.n = pickle.load(f)
        print(f"Model loaded from {file_path}")
        return self
    
    def predict_next_words(self, context, num_suggestions=5):

        suggestions = []
        remaining = num_suggestions
        
        # Prepare context for each model
        tokens = context.strip().split()
        
        # Start with the highest order model and backoff if needed
        for order in range(self.n, 0, -1):
            if remaining <= 0:
                break
                
            # Get the appropriate context for this n-gram model
            if order == 1:
                context_tuple = ()  # Unigram has no context
            else:
                # Take the last n-1 tokens for context
                start_idx = max(0, len(tokens) - (order - 1))
                context_tuple = tuple(tokens[start_idx:])
                
                if len(context_tuple) < order - 1:
                    continue
            
            # Get predictions from this model
            if context_tuple in self.models[order]:
                # Sort by probability in descending order
                next_words = self.models[order][context_tuple].most_common(remaining)
                
                # Add unique suggestions
                for word, prob in next_words:
                    if word not in [s[0] for s in suggestions]:
                        suggestions.append((word, prob))
                        remaining -= 1
                        
                    if remaining <= 0:
                        break
        
        return suggestions

