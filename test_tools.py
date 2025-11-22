from src.agents.tools import get_pc_recommendations

# Simulate the AI deciding to call the tool with input 800
print("--- AI IS THINKING ---")
print("AI decided to call tool: get_pc_recommendation(800)")

output = get_pc_recommendations.invoke("600")

print("\n--- TOOL OUTPUT ---")
print(output)