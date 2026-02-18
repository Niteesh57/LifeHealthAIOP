from gradio_client import Client

def inspect_api():
    try:
        client = Client("nagireddy5/lifehealth")
        client.view_api()
    except Exception as e:
        print(f"Error connecting to Space: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_api()
