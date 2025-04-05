import gradio as gr
from coordinator_assistant import CoordinatorAssistant
assistant = CoordinatorAssistant()

def chat_with_assistant(user_input, history):
    try:
        # Join conversation history to pass into the formatter LLM
        full_history = "\n".join([f"User: {u}\nAssistant: {a}" for u, a in history])
        full_prompt = f"{full_history}\nUser: {user_input}"

        response = assistant.run(full_prompt)
        return response
    except Exception as e:
        return f"[Error] {e}"

demo = gr.ChatInterface(
    fn=chat_with_assistant,
    title="🧠 Simple Agents",
    chatbot=gr.Chatbot(),
    textbox=gr.Textbox(placeholder="Ask me something...", lines=1),
    examples=["Greet Alice", "Reverse the name Bob", "hi I'm John"],
    theme="soft",  # optional
)

if __name__ == "__main__":
    demo.launch(share=True)



