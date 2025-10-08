import gradio as gr

def debug_print():
    print("[DEBUG] Button clicked!")
    return "Button was clicked!"

with gr.Blocks() as demo:
    btn = gr.Button("Test Button")
    output = gr.Textbox(label="Output")
    btn.click(debug_print, outputs=output)

if __name__ == "__main__":
    print("Minimal Gradio UI started...")
    demo.launch(server_port=7876, share=False)
