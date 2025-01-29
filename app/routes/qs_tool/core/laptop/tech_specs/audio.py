from app.routes.qs_tool.core.blocks.paragraph import insert_list

def audio_section(doc, df):
    """Audio techspecs section"""

    try:
        # Function to insert the list of values
        insert_list(doc, df, "Audio/Multimedia")
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)