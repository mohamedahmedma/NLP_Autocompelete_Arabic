from GloblaImport import *;
# Part 3: EVALUATION
class ModelEvaluator:
    def __init__(self, model):
        self.model = model
        
    def evaluate_perplexity(self, test_tokens):
        #Calculate perplexity of the model on test data

        # Using the highest-order n-gram model
        n = self.model.n
        log_likelihood = 0
        
        # Count the number of n-grams we can evaluate
        count = 0
        
        for i in range(len(test_tokens) - n + 1):
            context = tuple(test_tokens[i:i+n-1])
            next_word = test_tokens[i+n-1]
            
            # Get probability from model with backoff
            prob = 0
            for order in range(n, 0, -1):
                if order == 1:
                    current_context = ()
                else:
                    current_context = context[-(order-1):]
                
                if current_context in self.model.models[order] and next_word in self.model.models[order][current_context]:
                    prob = self.model.models[order][current_context][next_word]
                    break
            
            # Apply smoothing to avoid log(0)
            prob = max(prob, 1e-10)
            log_likelihood += np.log2(prob)
            count += 1
        
        # Calculate perplexity
        if count > 0:
            avg_log_likelihood = log_likelihood / count
            perplexity = 2 ** (-avg_log_likelihood)
            return perplexity
        else:
            return float('inf')
            
    def evaluate_accuracy(self, test_data, k=5):
        hits = 0
        total = 0
        
        for i in range(len(test_data) - self.model.n):
            # Get context
            context = ' '.join(test_data[i:i+self.model.n-1])
            actual_next_word = test_data[i+self.model.n-1]
            
            # Get predictions
            predictions = self.model.predict_next_words(context, k)
            predicted_words = [word for word, _ in predictions]
            
            # Check if the actual next word is in predictions
            if actual_next_word in predicted_words:
                hits += 1
            
            total += 1
        
        return hits / total if total > 0 else 0
        
    def evaluate_and_visualize(self, test_tokens, k_values=[1, 3, 5, 10]):
        #Evaluate the model and create visualizations
        # Calculate perplexity
        perplexity = self.evaluate_perplexity(test_tokens)
        print(f"Model perplexity: {perplexity:.2f}")
        
        # Calculate accuracy for different k values
        accuracies = []
        for k in k_values:
            acc = self.evaluate_accuracy(test_tokens, k)
            accuracies.append(acc)
            print(f"Top-{k} accuracy: {acc:.4f}")
        
        # Create accuracy visualization
        plt.figure(figsize=(10, 6))
        plt.bar(k_values, accuracies, color='skyblue')
        plt.xlabel('k (number of suggestions)')
        plt.ylabel('Accuracy')
        plt.title('Top-k Accuracy of Arabic Autocomplete Model')
        plt.xticks(k_values)
        plt.ylim(0, max(accuracies) * 1.2)
        
        # Add value labels on bars
        for i, acc in enumerate(accuracies):
            plt.text(k_values[i], acc + 0.01, f'{acc:.4f}', 
                    ha='center', va='bottom', fontsize=10)
        
        # Save the plot
        plt.savefig('accuracy_evaluation.png')
        plt.close()
        
        return {
            'perplexity': perplexity,
            'accuracies': dict(zip(k_values, accuracies))
        }

