from app.routes.qs_tool.core.laptop.tech_specs.product_name import product_name_section
from app.routes.qs_tool.core.laptop.tech_specs.operating_systems import operating_systems_section
from app.routes.qs_tool.core.laptop.tech_specs.processors import processors_section
from app.routes.qs_tool.core.laptop.tech_specs.graphics import graphics_section
from app.routes.qs_tool.core.laptop.tech_specs.display import display_section
from app.routes.qs_tool.core.laptop.tech_specs.docking import docking_section
from app.routes.qs_tool.core.laptop.tech_specs.storage import storage_section
from app.routes.qs_tool.core.laptop.tech_specs.memory import memory_section
from app.routes.qs_tool.core.laptop.tech_specs.networking import networking_section
from app.routes.qs_tool.core.laptop.tech_specs.audio import audio_section
from app.routes.qs_tool.core.laptop.tech_specs.keyboard import keyboard_section
from app.routes.qs_tool.core.laptop.tech_specs.software import software_section
from app.routes.qs_tool.core.laptop.tech_specs.power import power_section
from app.routes.qs_tool.core.laptop.tech_specs.dimensions import dimensions_section
from app.routes.qs_tool.core.laptop.tech_specs.ports import ports_section
from app.routes.qs_tool.core.laptop.tech_specs.service import service_section

import pandas as pd

def tech_specs_section(doc, file):
    """TechSpecs Section"""

    try:
        # Load sheet into df
        df = pd.read_excel(file.stream, sheet_name='Tech Specs & QS Features', engine='openpyxl')

        # Remove extra spaces from the end of each value and convert all columns to strings
        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)

        # Filter out rows where the "Value" column is empty
        df_filtered = df.dropna(subset=[df.columns[1]])

        # Save the filtered DataFrame to a new Excel file
        output_file = '/home/garciagi/qs/filtered_tech_specs.xlsx'
        df_filtered.to_excel(output_file, index=False)

        # Read the filtered DataFrame
        df = pd.read_excel(output_file, sheet_name='Sheet1', engine='openpyxl')
        df = df.astype(str)

        # Run the functions to build the tech specs section
        product_name_section(doc, file)
        operating_systems_section(doc, df)
        processors_section(doc, file)
        graphics_section(doc, df)
        display_section(doc, df)
        docking_section(doc, df)
        storage_section(doc, df)
        memory_section(doc, df)
        networking_section(doc, df)
        audio_section(doc, df)
        keyboard_section(doc, df)
        software_section(doc, df)
        power_section(doc, df)
        dimensions_section(doc, df)
        ports_section(doc, df)
        service_section(doc, df)

    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)