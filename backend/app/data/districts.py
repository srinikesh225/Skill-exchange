"""District gazetteer seed.

District names, states and approximate coordinates are real geographic facts
(used for map placement). Each district is tagged with an economic *archetype*
and a tech-intensity score used by the generator to shape a realistic,
internally-consistent demand profile. All resulting labour statistics are
synthetic demo data.

Archetypes -> industry emphasis (see generator):
  IT_HUB          strong software/cloud/data economy
  EMERGING_TECH   growing IT plus services
  MANUFACTURING   industrial / automotive / engineering trades
  MIXED           balanced services + light industry
  AGRI_SERVICES   agriculture, trades, local services, low tech intensity
"""

from __future__ import annotations

# (name, state, lat, lon, archetype, tech_intensity 0-1)
DISTRICTS: list[tuple[str, str, float, float, str, float]] = [
    # --- Major IT hubs ---
    ("Bengaluru Urban", "Karnataka", 12.9716, 77.5946, "IT_HUB", 0.98),
    ("Hyderabad", "Telangana", 17.3850, 78.4867, "IT_HUB", 0.95),
    ("Pune", "Maharashtra", 18.5204, 73.8567, "IT_HUB", 0.92),
    ("Chennai", "Tamil Nadu", 13.0827, 80.2707, "IT_HUB", 0.9),
    ("Gurugram", "Haryana", 28.4595, 77.0266, "IT_HUB", 0.9),
    ("Mumbai Suburban", "Maharashtra", 19.0760, 72.8777, "IT_HUB", 0.88),
    ("Gautam Buddha Nagar", "Uttar Pradesh", 28.5355, 77.3910, "IT_HUB", 0.86),
    ("Hebbal (Bengaluru Rural)", "Karnataka", 13.0358, 77.5970, "EMERGING_TECH", 0.72),

    # --- Emerging tech / tier-2 ---
    ("Coimbatore", "Tamil Nadu", 11.0168, 76.9558, "EMERGING_TECH", 0.68),
    ("Kochi", "Kerala", 9.9312, 76.2673, "EMERGING_TECH", 0.7),
    ("Thiruvananthapuram", "Kerala", 8.5241, 76.9366, "EMERGING_TECH", 0.71),
    ("Visakhapatnam", "Andhra Pradesh", 17.6868, 83.2185, "EMERGING_TECH", 0.66),
    ("Bhubaneswar (Khordha)", "Odisha", 20.2961, 85.8245, "EMERGING_TECH", 0.64),
    ("Jaipur", "Rajasthan", 26.9124, 75.7873, "EMERGING_TECH", 0.62),
    ("Ahmedabad", "Gujarat", 23.0225, 72.5714, "EMERGING_TECH", 0.68),
    ("Indore", "Madhya Pradesh", 22.7196, 75.8577, "EMERGING_TECH", 0.63),
    ("Chandigarh", "Chandigarh", 30.7333, 76.7794, "EMERGING_TECH", 0.67),
    ("Mohali", "Punjab", 30.7046, 76.7179, "EMERGING_TECH", 0.65),
    ("Mysuru", "Karnataka", 12.2958, 76.6394, "EMERGING_TECH", 0.6),
    ("Nagpur", "Maharashtra", 21.1458, 79.0882, "EMERGING_TECH", 0.58),
    ("Vijayawada (NTR)", "Andhra Pradesh", 16.5062, 80.6480, "EMERGING_TECH", 0.55),
    ("Lucknow", "Uttar Pradesh", 26.8467, 80.9462, "EMERGING_TECH", 0.56),
    ("Bhopal", "Madhya Pradesh", 23.2599, 77.4126, "EMERGING_TECH", 0.55),
    ("Nashik", "Maharashtra", 19.9975, 73.7898, "EMERGING_TECH", 0.54),
    ("Kolkata", "West Bengal", 22.5726, 88.3639, "EMERGING_TECH", 0.62),
    ("Guwahati (Kamrup Metro)", "Assam", 26.1445, 91.7362, "EMERGING_TECH", 0.5),

    # --- Manufacturing / industrial ---
    ("Chittoor (Sri City)", "Andhra Pradesh", 13.2172, 79.1003, "MANUFACTURING", 0.48),
    ("Kancheepuram", "Tamil Nadu", 12.8342, 79.7036, "MANUFACTURING", 0.5),
    ("Tiruppur", "Tamil Nadu", 11.1085, 77.3411, "MANUFACTURING", 0.4),
    ("Ludhiana", "Punjab", 30.9010, 75.8573, "MANUFACTURING", 0.42),
    ("Faridabad", "Haryana", 28.4089, 77.3178, "MANUFACTURING", 0.5),
    ("Pimpri-Chinchwad", "Maharashtra", 18.6279, 73.8009, "MANUFACTURING", 0.6),
    ("Aurangabad (Sambhajinagar)", "Maharashtra", 19.8762, 75.3433, "MANUFACTURING", 0.46),
    ("Vadodara", "Gujarat", 22.3072, 73.1812, "MANUFACTURING", 0.52),
    ("Surat", "Gujarat", 21.1702, 72.8311, "MANUFACTURING", 0.48),
    ("Rajkot", "Gujarat", 22.3039, 70.8022, "MANUFACTURING", 0.44),
    ("Jamnagar", "Gujarat", 22.4707, 70.0577, "MANUFACTURING", 0.42),
    ("Bhiwadi (Alwar)", "Rajasthan", 28.2100, 76.8606, "MANUFACTURING", 0.44),
    ("Hosur (Krishnagiri)", "Tamil Nadu", 12.7409, 77.8253, "MANUFACTURING", 0.5),
    ("Jamshedpur (East Singhbhum)", "Jharkhand", 22.8046, 86.2029, "MANUFACTURING", 0.46),
    ("Rourkela (Sundargarh)", "Odisha", 22.2604, 84.8536, "MANUFACTURING", 0.42),
    ("Bhilai (Durg)", "Chhattisgarh", 21.1938, 81.3509, "MANUFACTURING", 0.42),
    ("Kanpur Nagar", "Uttar Pradesh", 26.4499, 80.3319, "MANUFACTURING", 0.44),
    ("Ghaziabad", "Uttar Pradesh", 28.6692, 77.4538, "MANUFACTURING", 0.52),
    ("Sanand (Ahmedabad Rural)", "Gujarat", 22.9760, 72.3810, "MANUFACTURING", 0.5),
    ("Manesar (Rewari)", "Haryana", 28.1990, 76.6180, "MANUFACTURING", 0.5),

    # --- Energy / resources ---
    ("Angul", "Odisha", 20.8400, 85.1018, "MANUFACTURING", 0.34),
    ("Korba", "Chhattisgarh", 22.3595, 82.7501, "MANUFACTURING", 0.32),
    ("Singrauli", "Madhya Pradesh", 24.1997, 82.6753, "MANUFACTURING", 0.3),
    ("Dhanbad", "Jharkhand", 23.7957, 86.4304, "MANUFACTURING", 0.34),
    ("Bharuch", "Gujarat", 21.7051, 72.9959, "MANUFACTURING", 0.44),

    # --- Mixed economies (tier-2/3) ---
    ("Madurai", "Tamil Nadu", 9.9252, 78.1198, "MIXED", 0.44),
    ("Tiruchirappalli", "Tamil Nadu", 10.7905, 78.7047, "MIXED", 0.46),
    ("Salem", "Tamil Nadu", 11.6643, 78.1460, "MIXED", 0.4),
    ("Hubballi-Dharwad", "Karnataka", 15.3647, 75.1240, "MIXED", 0.48),
    ("Belagavi", "Karnataka", 15.8497, 74.4977, "MIXED", 0.42),
    ("Mangaluru (Dakshina Kannada)", "Karnataka", 12.9141, 74.8560, "MIXED", 0.54),
    ("Kozhikode", "Kerala", 11.2588, 75.7804, "MIXED", 0.5),
    ("Thrissur", "Kerala", 10.5276, 76.2144, "MIXED", 0.5),
    ("Guntur", "Andhra Pradesh", 16.3067, 80.4365, "MIXED", 0.44),
    ("Tirupati", "Andhra Pradesh", 13.6288, 79.4192, "MIXED", 0.48),
    ("Warangal", "Telangana", 17.9689, 79.5941, "MIXED", 0.46),
    ("Karimnagar", "Telangana", 18.4386, 79.1288, "MIXED", 0.4),
    ("Raipur", "Chhattisgarh", 21.2514, 81.6296, "MIXED", 0.44),
    ("Ranchi", "Jharkhand", 23.3441, 85.3096, "MIXED", 0.46),
    ("Patna", "Bihar", 25.5941, 85.1376, "MIXED", 0.44),
    ("Varanasi", "Uttar Pradesh", 25.3176, 82.9739, "MIXED", 0.42),
    ("Prayagraj", "Uttar Pradesh", 25.4358, 81.8463, "MIXED", 0.42),
    ("Agra", "Uttar Pradesh", 27.1767, 78.0081, "MIXED", 0.4),
    ("Meerut", "Uttar Pradesh", 28.9845, 77.7064, "MIXED", 0.42),
    ("Dehradun", "Uttarakhand", 30.3165, 78.0322, "MIXED", 0.5),
    ("Jodhpur", "Rajasthan", 26.2389, 73.0243, "MIXED", 0.42),
    ("Udaipur", "Rajasthan", 24.5854, 73.7125, "MIXED", 0.42),
    ("Kota", "Rajasthan", 25.2138, 75.8648, "MIXED", 0.44),
    ("Amritsar", "Punjab", 31.6340, 74.8723, "MIXED", 0.42),
    ("Jalandhar", "Punjab", 31.3260, 75.5762, "MIXED", 0.42),
    ("Gwalior", "Madhya Pradesh", 26.2183, 78.1828, "MIXED", 0.4),
    ("Jabalpur", "Madhya Pradesh", 23.1815, 79.9864, "MIXED", 0.42),
    ("Siliguri (Darjeeling)", "West Bengal", 26.7271, 88.3953, "MIXED", 0.44),
    ("Durgapur (Paschim Bardhaman)", "West Bengal", 23.5204, 87.3119, "MIXED", 0.44),
    ("Howrah", "West Bengal", 22.5958, 88.2636, "MIXED", 0.46),
    ("Cuttack", "Odisha", 20.4625, 85.8830, "MIXED", 0.42),
    ("Kollam", "Kerala", 8.8932, 76.6141, "MIXED", 0.46),
    ("Kannur", "Kerala", 11.8745, 75.3704, "MIXED", 0.44),
    ("Puducherry", "Puducherry", 11.9416, 79.8083, "MIXED", 0.48),
    ("Panaji (North Goa)", "Goa", 15.4909, 73.8278, "MIXED", 0.52),
    ("Srinagar", "Jammu & Kashmir", 34.0837, 74.7973, "MIXED", 0.36),
    ("Jammu", "Jammu & Kashmir", 32.7266, 74.8570, "MIXED", 0.38),
    ("Shimla", "Himachal Pradesh", 31.1048, 77.1734, "MIXED", 0.4),

    # --- Agri / services / tier-3 (lower tech intensity, real gaps in trades/green) ---
    ("Anantapur", "Andhra Pradesh", 14.6819, 77.6006, "AGRI_SERVICES", 0.3),
    ("Kurnool", "Andhra Pradesh", 15.8281, 78.0373, "AGRI_SERVICES", 0.3),
    ("Nizamabad", "Telangana", 18.6725, 78.0941, "AGRI_SERVICES", 0.3),
    ("Nalgonda", "Telangana", 17.0575, 79.2684, "AGRI_SERVICES", 0.28),
    ("Solapur", "Maharashtra", 17.6599, 75.9064, "AGRI_SERVICES", 0.32),
    ("Kolhapur", "Maharashtra", 16.7050, 74.2433, "AGRI_SERVICES", 0.36),
    ("Sangli", "Maharashtra", 16.8524, 74.5815, "AGRI_SERVICES", 0.32),
    ("Latur", "Maharashtra", 18.4088, 76.5604, "AGRI_SERVICES", 0.28),
    ("Bellary (Ballari)", "Karnataka", 15.1394, 76.9214, "AGRI_SERVICES", 0.32),
    ("Kalaburagi", "Karnataka", 17.3297, 76.8343, "AGRI_SERVICES", 0.3),
    ("Tumakuru", "Karnataka", 13.3379, 77.1173, "AGRI_SERVICES", 0.36),
    ("Erode", "Tamil Nadu", 11.3410, 77.7172, "AGRI_SERVICES", 0.34),
    ("Thanjavur", "Tamil Nadu", 10.7870, 79.1378, "AGRI_SERVICES", 0.3),
    ("Tirunelveli", "Tamil Nadu", 8.7139, 77.7567, "AGRI_SERVICES", 0.32),
    ("Bathinda", "Punjab", 30.2110, 74.9455, "AGRI_SERVICES", 0.3),
    ("Hisar", "Haryana", 29.1492, 75.7217, "AGRI_SERVICES", 0.32),
    ("Karnal", "Haryana", 29.6857, 76.9905, "AGRI_SERVICES", 0.34),
    ("Bikaner", "Rajasthan", 28.0229, 73.3119, "AGRI_SERVICES", 0.3),
    ("Ajmer", "Rajasthan", 26.4499, 74.6399, "AGRI_SERVICES", 0.34),
    ("Sagar", "Madhya Pradesh", 23.8388, 78.7378, "AGRI_SERVICES", 0.3),
    ("Ujjain", "Madhya Pradesh", 23.1793, 75.7849, "AGRI_SERVICES", 0.32),
    ("Gorakhpur", "Uttar Pradesh", 26.7606, 83.3732, "AGRI_SERVICES", 0.3),
    ("Bareilly", "Uttar Pradesh", 28.3670, 79.4304, "AGRI_SERVICES", 0.3),
    ("Aligarh", "Uttar Pradesh", 27.8974, 78.0880, "AGRI_SERVICES", 0.3),
    ("Muzaffarpur", "Bihar", 26.1209, 85.3647, "AGRI_SERVICES", 0.28),
    ("Gaya", "Bihar", 24.7969, 84.9994, "AGRI_SERVICES", 0.28),
    ("Bhagalpur", "Bihar", 25.2445, 86.9718, "AGRI_SERVICES", 0.28),
    ("Sambalpur", "Odisha", 21.4669, 83.9812, "AGRI_SERVICES", 0.32),
    ("Berhampur (Ganjam)", "Odisha", 19.3150, 84.7941, "AGRI_SERVICES", 0.3),
    ("Dibrugarh", "Assam", 27.4728, 94.9120, "AGRI_SERVICES", 0.3),
    ("Silchar (Cachar)", "Assam", 24.8333, 92.7789, "AGRI_SERVICES", 0.28),
    ("Imphal West", "Manipur", 24.8170, 93.9368, "AGRI_SERVICES", 0.3),
    ("Shillong (East Khasi Hills)", "Meghalaya", 25.5788, 91.8933, "AGRI_SERVICES", 0.32),
    ("Agartala (West Tripura)", "Tripura", 23.8315, 91.2868, "AGRI_SERVICES", 0.3),
    ("Aizawl", "Mizoram", 23.7271, 92.7176, "AGRI_SERVICES", 0.3),
    ("Haridwar", "Uttarakhand", 29.9457, 78.1642, "MANUFACTURING", 0.42),
]


def district_count() -> int:
    return len(DISTRICTS)
