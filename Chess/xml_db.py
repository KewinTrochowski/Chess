import xml.etree.ElementTree as ET
def save_moves_to_xml(moves, xml_file):
    """Zapisuje ruchy do pliku XML"""
    root = ET.Element("moves")  # Tworzenie elementu nadrzędnego XML
    for move in moves:
        move_element = ET.SubElement(root, "move")  # Tworzenie elementu dla każdego ruchu
        move_element.text = move  # Ustawienie tekstu elementu na wartość ruchu

    tree = ET.ElementTree(root)
    tree.write(xml_file)


def read_xml_file(xml_file):
    """Odczytuje zawartość pliku XML"""
    try:
        tree = ET.parse(xml_file)  # Parsowanie pliku XML
        root = tree.getroot()  # Pobranie korzenia dokumentu XML
        return root
    except ET.ParseError as e:
        print("Błąd parsowania pliku XML:", e)
    except FileNotFoundError:
        print("Plik XML nie znaleziony.")

def display_xml_content(root):
    """Wyświetla zawartość pliku XML"""
    print("Zawartość pliku XML:")
    print("Tag korzenia:", root.tag)
    print("Atrybuty korzenia:", root.attrib)
    for child in root:
        print("  Dziecko:", child.tag, "tekst:", child.text)

if __name__ == '__main__':
    dir = f"db/2024-04-09 13.09.31"
    xml_file = f"{dir}/history.xml"  # Nazwa pliku XML

    root = read_xml_file(xml_file)
    if root:
        display_xml_content(root)