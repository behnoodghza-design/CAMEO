import requests

# Check if water is available in search
response = requests.get('http://localhost:5000/api/search?q=water')
data = response.json()

print(f"Found {len(data['items'])} results for 'water'")
print("\nFirst 5 results:")
for item in data['items'][:5]:
    print(f"  - ID: {item['id']}, Name: {item['name']}")

# Check specifically for WATER
water_found = any('WATER' in item['name'].upper() for item in data['items'])
print(f"\nIs WATER in results? {'YES' if water_found else 'NO'}")

# Check exact match
response2 = requests.get('http://localhost:5000/api/search?q=WATER')
data2 = response2.json()
exact_water = [item for item in data2['items'] if item['name'].upper() == 'WATER']
print(f"\nExact WATER matches: {len(exact_water)}")
for item in exact_water:
    print(f"  - ID: {item['id']}, Name: {item['name']}")

# Check simple water entries
simple_water = [item for item in data['items'] if 'WATER' in item['name'].upper() and len(item['name']) < 15]
print(f"\nSimple WATER entries (for UI):")
for item in simple_water[:3]:
    print(f"  - {item['name']} (ID: {item['id']})")
