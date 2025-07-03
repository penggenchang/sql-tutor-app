print("starting app.py")
import os
import requests
import gradio as gr
from llama_cpp import Llama

MODEL_PATH = "models/Phi-3-Mini-4K-Instruct_Q6_K.gguf"

os.makedirs("models", exist_ok=True)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model file not found at {MODEL_PATH}")

print("📦 Loading model...")
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, verbose=False)
print("✅ Model loaded.")

# Prompt template
def build_prompt(user_input):
    return f"""You are a helpful and knowledgeable SQL tutor. Explain the following clearly. Use examples and SQL code blocks if needed.

User: {user_input}
AI:"""


# Chat history log
chat_history = []

# Generate response
def generate_response(user_input, history):
    if history is None or not isinstance(history, list):
        history = []

    prompt = build_prompt(user_input)
    output = llm(prompt, max_tokens=512, stop=["User:", "AI:"], echo=False)
    response = output["choices"][0]["text"].strip()

    # Format as SQL block
    if "SELECT" in response or "FROM" in response:
        response = f"```sql\n{response}\n```"

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": response})
    chat_history.append(f"Q: {user_input}\nA: {response}\n")

    return history


# Export chat history
def export_chat():
    file_path = "chat_history.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(chat_history)
    return file_path

# Preset questions (grouped by concept)
preset_questions = [
    # Basics
    "Select all columns from a table called employees.",
    "Find employees with salary greater than 50,000.",
    "Get names of all products that are in stock.",

    # Filters & Conditions
    "Find all customers from Texas.",
    "Get orders placed between Jan 1 and Jan 31, 2023.",
    "Show products with price between 10 and 100.",

    # Aggregates & Grouping
    "Find average salary per department.",
    "Count number of orders per customer.",
    "Total revenue by product category.",

    # JOINs
    "List customers and their orders using a JOIN.",
    "Get products and their suppliers using INNER JOIN.",
    "Show employees and their managers.",

    # Sorting & NULL
    "Show top 5 highest-paid employees.",
    "Find customers with no phone number.",
    "Sort products by descending price.",

    # Subqueries & CTEs
    "Find the second highest salary in employees.",
    "Get customers who placed more than 3 orders.",
    "List products with above-average price.",
    "Use a CTE to find departments with more than 5 employees."
]

# Gradio app
with gr.Blocks() as demo:
    gr.Markdown("# 🧠 SQL Tutor (Powered by Phi-3 Mini)\nLearn SQL by asking questions or using examples.")
    
    with gr.Row():
        question_input = gr.Textbox(label="Ask your SQL question", lines=2)
        preset_dropdown = gr.Dropdown(choices=preset_questions, label="Choose a sample question", interactive=True)
    
    with gr.Row():
        submit_btn = gr.Button("Ask")
        export_btn = gr.Button("Download Q&A")

    chatbot = gr.Chatbot(label="Conversation History", type="messages")


    # Events
    def fill_from_dropdown(choice):
        return gr.update(value=choice)
    
    preset_dropdown.change(fn=fill_from_dropdown, inputs=preset_dropdown, outputs=question_input)
    #submit_btn.click(fn=generate_response, inputs=[question_input, chatbot], outputs=[chatbot, chatbot])
    submit_btn.click(fn=generate_response, inputs=[question_input, chatbot], outputs=[chatbot])
    export_btn.click(fn=export_chat, outputs=gr.File())

#demo.launch()
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
