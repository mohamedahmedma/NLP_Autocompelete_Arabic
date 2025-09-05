from GloblaImport import *;
from ArabicPreprocessor import *;
from NGramModel import *;
from ModelEvaluator import *;
from ArabicAutocompleteGUI import *;


# Main Application
def main():
    # Path to specific file - UPDATE THIS TO YOUR ACTUAL PATH
    data_file = r"All Data\All Data"   # Path to the dataset file
    model_path = r"arabic_ngram_model_full.pkl"  # Path to save/load the model
    
    # Create instances
    preprocessor = ArabicPreprocessor()
    model = NGramModel(n=3)  # Using trigrams
    
    # Check if model already exists
    if os.path.exists(model_path):
        print("Loading existing model...")
        model.load_model(model_path)
    else:
        print(f"Processing data from file {data_file} and training a new model...")
        
        # Process the specific file
        all_tokens = preprocessor.process_file(data_file)
        
        if not all_tokens:
            print("No tokens were extracted from the file. Please check the file path and content.")
            return
            
        print(f"Total tokens after preprocessing: {len(all_tokens)}")
        
        # Split data for training and evaluation (90% train, 10% test)
        train_size = int(0.8 * len(all_tokens))
        train_tokens = all_tokens[:train_size]
        test_tokens = all_tokens[train_size:]
        
        print(f"Training with {len(train_tokens)} tokens, testing with {len(test_tokens)} tokens...")
        
        # Train model
        model.train(train_tokens)
        
        # Save the model
        model.save_model(model_path)
        
        # Evaluate model
        print("Evaluating model...")
        evaluator = ModelEvaluator(model)
        results = evaluator.evaluate_and_visualize(test_tokens)
        print("Evaluation Results:", results)
    
    # Start GUI
    print("Starting GUI...")
    app = ArabicAutocompleteGUI(model)
    app.run()


if __name__ == "__main__":
    main()