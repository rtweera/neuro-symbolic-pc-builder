import janus_swi as janus

def run_modern_expert_system():
    print("Loading Knowledge Base via Janus...")
    
    try:
        # 1. Load the file
        janus.consult("knowledge/sample_knowledge_base.pl")
        
        # 2. Run Query
        user_budget = 800
        print(f"🔎 Querying builds under ${user_budget} (using modern Janus bridge)...")
        
        # Janus query returns a generator (iterator) of dictionaries
        query = f"recommend_build({user_budget}, Cpu, Mobo, Cost)"
        
        # 3. Iterate results
        solutions_found = False
        for result in janus.query(query):
            solutions_found = True
            print(f"Found Build: CPU={result['Cpu']}, Mobo={result['Mobo']}, Total=${result['Cost']}")
            
        if not solutions_found:
            print("No builds found.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_modern_expert_system()