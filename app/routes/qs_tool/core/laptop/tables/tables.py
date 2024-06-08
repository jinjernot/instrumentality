from app.routes.qs_tool.core.laptop.tables.system_unit import system_unit_section
from app.routes.qs_tool.core.laptop.tables.fingerprint import fingerprint_section
from app.routes.qs_tool.core.laptop.tables.change_log import change_log_section
from app.routes.qs_tool.core.laptop.tables.displays import displays_section
from app.routes.qs_tool.core.laptop.tables.storage import storage_section
from app.routes.qs_tool.core.laptop.tables.network import network_section
from app.routes.qs_tool.core.laptop.tables.options import options_section
from app.routes.qs_tool.core.laptop.tables.audio import audio_section
from app.routes.qs_tool.core.laptop.tables.power import power_section




def table_section(doc, file, html_file):
    """Table Secion"""

    # Table sections
    system_unit_section(doc, file, html_file)
    displays_section(doc, file, html_file)
    storage_section(doc, file, html_file)
    network_section(doc, file, html_file)
    power_section(doc, file, html_file)
    audio_section(doc, file, html_file)
    fingerprint_section(doc, file, html_file)
    options_section(doc, file, html_file)
    change_log_section(doc, file, html_file)

