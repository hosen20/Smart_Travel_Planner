"""Generate expanded travel destinations dataset."""

import pandas as pd
import numpy as np
from typing import List, Dict

# Travel styles
STYLES = ['Adventure', 'Relaxation', 'Culture', 'Budget', 'Luxury', 'Family']

# Sample destinations with features
destinations_data = [
    # Adventure destinations
    {'destination': 'Queenstown, New Zealand', 'country': 'New Zealand', 'continent': 'Oceania',
     'population': 15000, 'cost_index': 85, 'safety_index': 95, 'climate': 'Temperate',
     'activities': ['Bungee jumping', 'Skydiving', 'Hiking', 'Rafting'], 'style': 'Adventure'},
    {'destination': 'Patagonia, Chile', 'country': 'Chile', 'continent': 'South America',
     'population': 100000, 'cost_index': 70, 'safety_index': 90, 'climate': 'Cold',
     'activities': ['Trekking', 'Glacier hiking', 'Wildlife watching'], 'style': 'Adventure'},
    {'destination': 'Iceland', 'country': 'Iceland', 'continent': 'Europe',
     'population': 350000, 'cost_index': 120, 'safety_index': 98, 'climate': 'Cold',
     'activities': ['Glacier tours', 'Northern lights', 'Volcano visits'], 'style': 'Adventure'},
    {'destination': 'Costa Rica', 'country': 'Costa Rica', 'continent': 'Central America',
     'population': 5100000, 'cost_index': 75, 'safety_index': 85, 'climate': 'Tropical',
     'activities': ['Zip-lining', 'Surfing', 'Rainforest trekking'], 'style': 'Adventure'},
    {'destination': 'Bhutan', 'country': 'Bhutan', 'continent': 'Asia',
     'population': 770000, 'cost_index': 65, 'safety_index': 92, 'climate': 'Mountain',
     'activities': ['Trekking', 'Buddhist temples', 'Cultural immersion'], 'style': 'Adventure'},

    # Relaxation destinations
    {'destination': 'Bali, Indonesia', 'country': 'Indonesia', 'continent': 'Asia',
     'population': 4200000, 'cost_index': 55, 'safety_index': 80, 'climate': 'Tropical',
     'activities': ['Beach lounging', 'Spa treatments', 'Yoga retreats'], 'style': 'Relaxation'},
    {'destination': 'Santorini, Greece', 'country': 'Greece', 'continent': 'Europe',
     'population': 15000, 'cost_index': 90, 'safety_index': 88, 'climate': 'Mediterranean',
     'activities': ['Sunset watching', 'Wine tasting', 'Beach relaxation'], 'style': 'Relaxation'},
    {'destination': 'Maldives', 'country': 'Maldives', 'continent': 'Asia',
     'population': 540000, 'cost_index': 140, 'safety_index': 85, 'climate': 'Tropical',
     'activities': ['Snorkeling', 'Private villas', 'Spa resorts'], 'style': 'Relaxation'},
    {'destination': 'Hawaii, USA', 'country': 'USA', 'continent': 'North America',
     'population': 1400000, 'cost_index': 110, 'safety_index': 87, 'climate': 'Tropical',
     'activities': ['Beach activities', 'Volcano tours', 'Luau experiences'], 'style': 'Relaxation'},
    {'destination': 'Phuket, Thailand', 'country': 'Thailand', 'continent': 'Asia',
     'population': 420000, 'cost_index': 60, 'safety_index': 82, 'climate': 'Tropical',
     'activities': ['Island hopping', 'Massage', 'Beach bars'], 'style': 'Relaxation'},

    # Culture destinations
    {'destination': 'Paris, France', 'country': 'France', 'continent': 'Europe',
     'population': 2161000, 'cost_index': 95, 'safety_index': 85, 'climate': 'Temperate',
     'activities': ['Museums', 'Historical sites', 'Fine dining'], 'style': 'Culture'},
    {'destination': 'Tokyo, Japan', 'country': 'Japan', 'continent': 'Asia',
     'population': 13929000, 'cost_index': 100, 'safety_index': 98, 'climate': 'Temperate',
     'activities': ['Temples', 'Modern culture', 'Cuisine exploration'], 'style': 'Culture'},
    {'destination': 'Rome, Italy', 'country': 'Italy', 'continent': 'Europe',
     'population': 2873000, 'cost_index': 85, 'safety_index': 83, 'climate': 'Mediterranean',
     'activities': ['Ancient ruins', 'Art galleries', 'Food tours'], 'style': 'Culture'},
    {'destination': 'Barcelona, Spain', 'country': 'Spain', 'continent': 'Europe',
     'population': 1620000, 'cost_index': 80, 'safety_index': 86, 'climate': 'Mediterranean',
     'activities': ['Gaudi architecture', 'Beaches', 'Nightlife'], 'style': 'Culture'},
    {'destination': 'Berlin, Germany', 'country': 'Germany', 'continent': 'Europe',
     'population': 3769000, 'cost_index': 75, 'safety_index': 84, 'climate': 'Temperate',
     'activities': ['Historical sites', 'Street art', 'Nightlife'], 'style': 'Culture'},

    # Budget destinations
    {'destination': 'Bangkok, Thailand', 'country': 'Thailand', 'continent': 'Asia',
     'population': 10539000, 'cost_index': 50, 'safety_index': 78, 'climate': 'Tropical',
     'activities': ['Street food', 'Temples', 'Markets'], 'style': 'Budget'},
    {'destination': 'Lisbon, Portugal', 'country': 'Portugal', 'continent': 'Europe',
     'population': 505500, 'cost_index': 65, 'safety_index': 89, 'climate': 'Mediterranean',
     'activities': ['Historic trams', 'Beaches', 'Fado music'], 'style': 'Budget'},
    {'destination': 'Mexico City, Mexico', 'country': 'Mexico', 'continent': 'North America',
     'population': 9209944, 'cost_index': 55, 'safety_index': 70, 'climate': 'Temperate',
     'activities': ['Museums', 'Street food', 'Markets'], 'style': 'Budget'},
    {'destination': 'Hanoi, Vietnam', 'country': 'Vietnam', 'continent': 'Asia',
     'population': 8054000, 'cost_index': 45, 'safety_index': 81, 'climate': 'Tropical',
     'activities': ['Street food', 'Temples', 'Motorbike tours'], 'style': 'Budget'},
    {'destination': 'Budapest, Hungary', 'country': 'Hungary', 'continent': 'Europe',
     'population': 1752000, 'cost_index': 55, 'safety_index': 87, 'climate': 'Continental',
     'activities': ['Thermal baths', 'Historic sites', 'Nightlife'], 'style': 'Budget'},

    # Luxury destinations
    {'destination': 'Dubai, UAE', 'country': 'UAE', 'continent': 'Asia',
     'population': 3331000, 'cost_index': 130, 'safety_index': 91, 'climate': 'Desert',
     'activities': ['Luxury shopping', 'Desert safaris', 'Fine dining'], 'style': 'Luxury'},
    {'destination': 'Monaco', 'country': 'Monaco', 'continent': 'Europe',
     'population': 39000, 'cost_index': 150, 'safety_index': 95, 'climate': 'Mediterranean',
     'activities': ['Casino', 'Yachting', 'Luxury resorts'], 'style': 'Luxury'},
    {'destination': 'St. Moritz, Switzerland', 'country': 'Switzerland', 'continent': 'Europe',
     'population': 5000, 'cost_index': 160, 'safety_index': 97, 'climate': 'Alpine',
     'activities': ['Skiing', 'Luxury spas', 'Fine dining'], 'style': 'Luxury'},
    {'destination': 'Beverly Hills, USA', 'country': 'USA', 'continent': 'North America',
     'population': 34000, 'cost_index': 140, 'safety_index': 88, 'climate': 'Mediterranean',
     'activities': ['Celebrity spotting', 'Luxury shopping', 'Spas'], 'style': 'Luxury'},
    {'destination': 'Capri, Italy', 'country': 'Italy', 'continent': 'Europe',
     'population': 14000, 'cost_index': 120, 'safety_index': 90, 'climate': 'Mediterranean',
     'activities': ['Luxury villas', 'Boat tours', 'Fine dining'], 'style': 'Luxury'},

    # Family destinations
    {'destination': 'Orlando, USA', 'country': 'USA', 'continent': 'North America',
     'population': 307573, 'cost_index': 90, 'safety_index': 85, 'climate': 'Subtropical',
     'activities': ['Theme parks', 'Family resorts', 'Water parks'], 'style': 'Family'},
    {'destination': 'Vancouver, Canada', 'country': 'Canada', 'continent': 'North America',
     'population': 630000, 'cost_index': 95, 'safety_index': 92, 'climate': 'Temperate',
     'activities': ['Outdoor activities', 'Aquariums', 'Family tours'], 'style': 'Family'},
    {'destination': 'Sydney, Australia', 'country': 'Australia', 'continent': 'Oceania',
     'population': 5312000, 'cost_index': 100, 'safety_index': 90, 'climate': 'Temperate',
     'activities': ['Beaches', 'Zoo', 'Harbor cruises'], 'style': 'Family'},
    {'destination': 'Amsterdam, Netherlands', 'country': 'Netherlands', 'continent': 'Europe',
     'population': 900000, 'cost_index': 95, 'safety_index': 88, 'climate': 'Temperate',
     'activities': ['Canals', 'Museums', 'Bike tours'], 'style': 'Family'},
    {'destination': 'Cape Town, South Africa', 'country': 'South Africa', 'continent': 'Africa',
     'population': 4337000, 'cost_index': 70, 'safety_index': 75, 'climate': 'Mediterranean',
     'activities': ['Beaches', 'Safari', 'Table Mountain'], 'style': 'Family'},
]

# Expand to 1000+ samples by adding variations and synthetic data
expanded_data = []

# Add the base destinations
for dest in destinations_data:
    expanded_data.append(dest)

# Generate variations for each style to reach ~1000 samples
np.random.seed(42)
for style in STYLES:
    base_dests = [d for d in destinations_data if d['style'] == style]
    for i in range(150):  # ~150 per style = 900
        base = np.random.choice(base_dests)
        variation = base.copy()
        variation['destination'] = f"{base['destination']} Variant {i+1}"
        # Add some noise to numerical features
        variation['population'] = max(1000, int(base['population'] * np.random.uniform(0.5, 1.5)))
        variation['cost_index'] = max(30, min(200, base['cost_index'] + np.random.normal(0, 10)))
        variation['safety_index'] = max(50, min(100, base['safety_index'] + np.random.normal(0, 5)))
        expanded_data.append(variation)

# Create DataFrame
df = pd.DataFrame(expanded_data)

# Add more features
df['has_beaches'] = df['activities'].apply(lambda x: 'Beach' in str(x) or 'beaches' in str(x).lower())
df['has_mountains'] = df['climate'].isin(['Mountain', 'Alpine', 'Cold'])
df['is_urban'] = df['population'] > 1000000
df['is_safe'] = df['safety_index'] > 85
df['is_expensive'] = df['cost_index'] > 100

# Save to CSV
df.to_csv('data/destinations_dataset.csv', index=False)
print(f"Dataset created with {len(df)} samples")
print(df['style'].value_counts())
print(df.head())