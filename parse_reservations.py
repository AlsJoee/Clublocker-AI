from bs4 import BeautifulSoup

with open("reservations.html", "r") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Look for classes that might indicate court/grid structure
interesting_classes = [
    'court', 'grid', 'cell', 'slot', 'time', 'reservation', 
    'booking', 'available', 'closed', 'row', 'column', 'reserve'
]

print("Divs with potentially relevant classes:")
divs_with_classes = soup.find_all('div', class_=True)
for div in divs_with_classes:
    classes = ' '.join(div.get('class', []))
    for keyword in interesting_classes:
        if keyword.lower() in classes.lower():
            print(f"  {classes}")
            break

print("\n" + "="*50 + "\n")

# Also check for any data attributes that might be useful
print("Looking for elements with data attributes:")
all_elements = soup.find_all()
data_attrs_found = set()
for elem in all_elements[:500]:  # Sample first 500
    for attr in elem.attrs:
        if attr.startswith('data-') or attr.startswith('ng-'):
            data_attrs_found.add(attr)

print(f"Found attributes: {data_attrs_found}")