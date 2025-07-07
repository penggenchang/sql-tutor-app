# sql_tutor_openai.py

import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

# load API key from .env
load_dotenv()
client = OpenAI()  # uses OPENAI_API_KEY from env automatically

# prompt template builder
def build_prompt(user_input):
    return f"""You are a helpful and knowledgeable SQL tutor. Explain the following clearly. Use examples and SQL code blocks if needed.

User: {user_input}
AI:"""

# for export
chat_history = []

# call openai and get reply
def generate_response(user_input, history):
    if history is None or not isinstance(history, list):
        history = []

    prompt = build_prompt(user_input)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful and knowledgeable SQL tutor. Use SQL examples and explanations when needed."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.3,
    )

    reply = response.choices[0].message.content.strip()

    # format sql output
    if "SELECT" in reply or "FROM" in reply:
        reply = f"```sql\n{reply}\n```"

    history.append([user_input, reply])
    chat_history.append(f"Q: {user_input}\nA: {reply}\n")

    return history

# export chat history
def export_chat():
    file_path = "chat_history.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(chat_history)
    return file_path

# sample questions
preset_questions = [
    "Select all columns from a table called employees.",
    "Find employees with salary greater than 50,000.",
    "Get names of all products that are in stock.",
    "Find all customers from Texas.",
    "Get orders placed between Jan 1 and Jan 31, 2023.",
    "Show products with price between 10 and 100.",
    "Find average salary per department.",
    "Count number of orders per customer.",
    "Total revenue by product category.",
    "List customers and their orders using a JOIN.",
    "Get products and their suppliers using INNER JOIN.",
    "Show employees and their managers.",
    "Show top 5 highest-paid employees.",
    "Find customers with no phone number.",
    "Sort products by descending price.",
    "Find the second highest salary in employees.",
    "Get customers who placed more than 3 orders.",
    "List products with above-average price.",
    "Use a CTE to find departments with more than 5 employees."
]

# gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🧠 sql tutor (powered by openai gpt-3.5)\nlearn sql by asking questions or using examples.")
    
    with gr.Row():
        question_input = gr.Textbox(label="ask your sql question", lines=2)
        preset_dropdown = gr.Dropdown(choices=preset_questions, label="choose a sample question", interactive=True)
    
    with gr.Row():
        submit_btn = gr.Button("ask")
        export_btn = gr.Button("download q&a")

    chatbot = gr.Chatbot(label="conversation history")
    
    def fill_from_dropdown(choice):
        return gr.update(value=choice)
    
    preset_dropdown.change(fn=fill_from_dropdown, inputs=preset_dropdown, outputs=question_input)
    submit_btn.click(fn=generate_response, inputs=[question_input, chatbot], outputs=[chatbot])
    export_btn.click(fn=export_chat, outputs=gr.File())

demo.launch()
