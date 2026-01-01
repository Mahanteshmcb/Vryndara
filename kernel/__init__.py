def __init__(self):
        self.message_queues = {}
        self.registry = {}
        self.response_futures = {} 

        # --- INITIALIZE SERVICES ---
        self.storage = StorageManager(bucket_name="vryndara_output")
        self.engineer = EngineeringService(self.storage)
        
        # --- INITIALIZE AI BRAIN (MISTRAL) ---
        # FIX: Use the exact path to your Mistral file
        model_path = r"C:\Users\Mahantesh\DevelopmentProjects\VrindaAI\VrindaAI\llama.cpp\build\bin\Release\mistral.gguf"
        
        # Initialize the Coder Agent
        self.coder = CoderAgent(model_path)