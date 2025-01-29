from app.routes.qs_tool.core.laptop.tables.system_unit import system_unit_section
from app.routes.qs_tool.core.laptop.tables.displays import displays_section
from app.routes.qs_tool.core.laptop.tables.audio import audio_section
from app.routes.qs_tool.core.laptop.tables.fingerprint import fingerprint_section
from app.routes.qs_tool.core.laptop.tables.storage import storage_section
from app.routes.qs_tool.core.laptop.tables.network import network_section
from app.routes.qs_tool.core.laptop.tables.power import power_section
from app.routes.qs_tool.core.laptop.tables.options import options_section
from app.routes.qs_tool.core.laptop.tables.change_log import change_log_section


def table_section(doc, file):
    """Table Secion"""

    # Table sections
    system_unit_section(doc, file)
    displays_section(doc, file)
    storage_section(doc, file)
    network_section(doc, file)
    power_section(doc, file)
    audio_section(doc, file)
    fingerprint_section(doc, file)
    options_section(doc, file)
    change_log_section(doc, file)

