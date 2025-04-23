import json
import math
import os

def load_exoplanet_data(file_path):
    """
    Load exoplanet data from a file
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading exoplanet data from {file_path}: {e}")
        return None

def calculate_habitable_zone(star_luminosity, star_temp):
   
    # Constants for habitable zone calculations
    ts = 5700  # Reference temperature in K
    ai = 2.7619e-5
    bi = 3.8095e-9
    ao = 1.3786e-4
    bo = 1.4286e-9
    ris = 0.72  # Inner boundary for Sun in AU
    ros = 1.77  # Outer boundary for Sun in AU
    
    # Calculate habitable zone boundaries
    ri = ris * math.sqrt(star_luminosity / (1.0 + ai * (star_temp - ts) - bi * (star_temp - ts)**2))
    ro = ros * math.sqrt(star_luminosity / (1.0 + ao * (star_temp - ts) - bo * (star_temp - ts)**2))
    
    return ri, ro

def calculate_hzd(planet_distance, inner_hz, outer_hz):

    hz_center = (inner_hz + outer_hz) / 2
    hz_half_width = (outer_hz - inner_hz) / 2
    
    # Calculate HZD
    hzd = (planet_distance - hz_center) / hz_half_width
    
    return hzd

def parse_stellar_luminosity(star_radius, star_temp):

    if not star_radius or not star_temp:
        return None
    
    sun_temp = 5778  # K
    return (star_radius**2) * ((star_temp / sun_temp)**4)

def calculate_earth_distance_light_years(parallax=None, distance_parsecs=None):

    if distance_parsecs is not None:
        return distance_parsecs * 3.26
    elif parallax is not None and parallax != 0:
        parsecs = 1000 / parallax
        return parsecs * 3.26
    else:
        return None

def is_planet_habitable(planet_distance, inner_hz, outer_hz, planet_mass=None, planet_radius=None):

    # Check if planet is in habitable zone
    in_habitable_zone = inner_hz <= planet_distance <= outer_hz
    
    # Check mass constraints (roughly 0.1 to 10 Earth masses is potentially habitable)
    # Using Jupiter mass as reference if that's what's available
    mass_suitable = True
    if planet_mass is not None:
        if hasattr(planet_mass, 'get'):
            if planet_mass.get("pl_bmassj") is not None:
                jupiter_mass = planet_mass.get("pl_bmassj")
                earth_mass_equivalent = jupiter_mass * 317.8  # Jupiter is 317.8 Earth masses
                mass_suitable = 0.1 <= earth_mass_equivalent <= 10
            elif planet_mass.get("pl_bmasse") is not None:
                earth_mass = planet_mass.get("pl_bmasse")
                mass_suitable = 0.1 <= earth_mass <= 10
    
    # Check radius constraints (roughly 0.5 to 2.0 Earth radii is potentially habitable)
    size_suitable = True
    if planet_radius is not None and hasattr(planet_radius, 'get'):
        if planet_radius.get("pl_rade") is not None:
            earth_radius = planet_radius.get("pl_rade")
            size_suitable = 0.5 <= earth_radius <= 2.0
    
    # Final habitability assessment
    if in_habitable_zone:
        if mass_suitable and size_suitable:
            return "Potentially habitable"
        else:
            return "In habitable zone but may not have right mass/size for habitability"
    else:
        return "Not in habitable zone"

def get_planet_type(planet_mass=None, planet_radius=None):
    """
    Determine planet type based on mass and/or radius
    """
    # If we have both mass and radius, we can be more precise
    earth_mass = None
    earth_radius = None
    
    # Extract mass information
    if planet_mass is not None:
        if hasattr(planet_mass, 'get'):
            if planet_mass.get("pl_bmassj") is not None:
                jupiter_mass = planet_mass.get("pl_bmassj")
                earth_mass = jupiter_mass * 317.8
            elif planet_mass.get("pl_bmasse") is not None:
                earth_mass = planet_mass.get("pl_bmasse")
            elif planet_mass.get("pl_msinij") is not None:
                jupiter_mass = planet_mass.get("pl_msinij")
                earth_mass = jupiter_mass * 317.8
            elif planet_mass.get("pl_msinie") is not None:
                earth_mass = planet_mass.get("pl_msinie")
    
    # Extract radius information
    if planet_radius is not None:
        if hasattr(planet_radius, 'get'):
            if planet_radius.get("pl_rade") is not None:
                earth_radius = planet_radius.get("pl_rade")
            elif planet_radius.get("pl_radj") is not None:
                jupiter_radius = planet_radius.get("pl_radj")
                earth_radius = jupiter_radius * 11.2  # Jupiter is 11.2 Earth radii
    
    # If we have both mass and radius, use both for classification
    if earth_mass is not None and earth_radius is not None:
        if earth_mass < 0.1:
            return "Sub-Earth/Mercury-like"
        elif earth_mass < 2 and earth_radius < 1.5:
            return "Earth-like terrestrial planet"
        elif earth_mass < 10 and earth_radius < 2.5:
            return "Super-Earth"
        elif earth_mass < 50 and earth_radius < 6:
            return "Mini-Neptune/Gas Dwarf"
        elif earth_mass < 500:
            return "Neptune-like gas giant"
        else:
            return "Jupiter-like gas giant"
    
    # If we only have mass
    if earth_mass is not None:
        if earth_mass < 0.1:
            return "Sub-Earth/Mercury-like"
        elif earth_mass < 2:
            return "Possibly Earth-like"
        elif earth_mass < 10:
            return "Possibly Super-Earth"
        elif earth_mass < 50:
            return "Possibly Mini-Neptune"
        elif earth_mass < 500:
            return "Neptune-like gas giant"
        else:
            return "Jupiter-like gas giant"
    
    # If we only have radius
    if earth_radius is not None:
        if earth_radius < 0.8:
            return "Sub-Earth/Mercury-like"
        elif earth_radius < 1.5:
            return "Possibly Earth-like"
        elif earth_radius < 2.5:
            return "Possibly Super-Earth"
        elif earth_radius < 6:
            return "Possibly Mini-Neptune/Gas Dwarf"
        elif earth_radius < 15:
            return "Neptune-like gas giant"
        else:
            return "Jupiter-like gas giant"
    
    return "Unknown (insufficient data)"

def calculate_surface_gravity(planet_mass, planet_radius):
    """
    Calculate surface gravity relative to Earth
    g = G*M/r² (proportional to M/r²)
    """
    earth_mass = None
    earth_radius = None
    
    # Extract mass information
    if planet_mass is not None:
        if hasattr(planet_mass, 'get'):
            if planet_mass.get("pl_bmassj") is not None:
                jupiter_mass = planet_mass.get("pl_bmassj")
                earth_mass = jupiter_mass * 317.8
            elif planet_mass.get("pl_bmasse") is not None:
                earth_mass = planet_mass.get("pl_bmasse")
    
    # Extract radius information
    if planet_radius is not None:
        if hasattr(planet_radius, 'get'):
            if planet_radius.get("pl_rade") is not None:
                earth_radius = planet_radius.get("pl_rade")
            elif planet_radius.get("pl_radj") is not None:
                jupiter_radius = planet_radius.get("pl_radj")
                earth_radius = jupiter_radius * 11.2
    
    if earth_mass is None or earth_radius is None:
        return None
    
    # Calculate gravity relative to Earth (Earth = 1)
    gravity = earth_mass / (earth_radius**2)
    
    return gravity

def get_star_type_from_spectype(spectype):
    """
    Determine star type from spectral classification
    """
    if not spectype:
        return None
    
    # Extract main spectral type
    spectral_type = spectype.strip().split()[0] if isinstance(spectype, str) else None
    
    if not spectral_type:
        return None
    
    # Map spectral type to description
    if spectral_type.startswith('O'):
        return "extremely hot O-type star"
    elif spectral_type.startswith('B'):
        return "very hot B-type star"
    elif spectral_type.startswith('A'):
        return "hot A-type star"
    elif spectral_type.startswith('F'):
        return "F-type star (hotter than our Sun)"
    elif spectral_type.startswith('G'):
        if "III" in spectype or "II" in spectype or "I" in spectype:
            return "G-type giant star"
        else:
            return "G-type star (similar to our Sun)"
    elif spectral_type.startswith('K'):
        if "III" in spectype or "II" in spectype or "I" in spectype:
            return "K-type giant star"
        else:
            return "K-type orange dwarf star"
    elif spectral_type.startswith('M'):
        if "III" in spectype or "II" in spectype or "I" in spectype:
            return "M-type giant star"
        else:
            return "M-type red dwarf star"
    elif spectral_type.startswith('L') or spectral_type.startswith('T') or spectral_type.startswith('Y'):
        return "very cool brown dwarf"
    else:
        return "unknown type star"

def analyze_exoplanet(planet_data):
    """
    Analyze exoplanet data and generate human-friendly explanations
    """
    results = {
        "planet_name": planet_data.get("pl_name", "Unnamed planet"),
        "host_star": planet_data.get("hostname", "Unknown star"),
        "discovery_method": planet_data.get("discoverymethod", "Unknown method"),
        "discovery_year": planet_data.get("disc_year", "Unknown year"),
        "layman_explanation": {}
    }
    
    # Extract key data
    star_radius = planet_data.get("st_rad")
    star_temp = planet_data.get("st_teff")
    star_luminosity = planet_data.get("st_lum")
    star_spectype = planet_data.get("st_spectype")
    
    # If luminosity not directly provided, calculate from radius and temperature
    if star_luminosity is None and star_radius and star_temp:
        star_luminosity = parse_stellar_luminosity(star_radius, star_temp)
    
    planet_distance = planet_data.get("pl_orbsmax")
    parallax = planet_data.get("sy_plx")
    distance_parsecs = planet_data.get("sy_dist")
    
    # Calculate distance from Earth
    distance_ly = calculate_earth_distance_light_years(parallax, distance_parsecs)
    
    # Include distance information
    if distance_ly:
        results["layman_explanation"]["distance"] = {
            "answer": f"This planet is approximately {distance_ly:.1f} light years away from Earth.",
            "value": distance_ly,
            "unit": "light years"
        }
    else:
        results["layman_explanation"]["distance"] = {
            "answer": "Insufficient data to determine distance from Earth.",
            "value": None,
            "unit": "light years"
        }
    
    # Determine habitability
    if star_luminosity and star_temp and planet_distance:
        # Calculate habitable zone
        inner_hz, outer_hz = calculate_habitable_zone(star_luminosity, star_temp)
        hzd = calculate_hzd(planet_distance, inner_hz, outer_hz)
        
        # Check habitability
        habitability = is_planet_habitable(
            planet_distance, 
            inner_hz, 
            outer_hz, 
            planet_mass=planet_data, 
            planet_radius=planet_data
        )
        
        # Planet's position relative to habitable zone
        if hzd < -1:
            position = "too close to its star (too hot)"
        elif hzd > 1:
            position = "too far from its star (too cold)"
        elif -1 <= hzd <= 1:
            position = "within the habitable zone"
        
        results["layman_explanation"]["habitability"] = {
            "answer": f"This planet is {position}. {habitability}.",
            "habitable_zone_distance": hzd,
            "inner_habitable_boundary": inner_hz,
            "outer_habitable_boundary": outer_hz,
            "actual_distance": planet_distance,
            "assessment": habitability
        }
    else:
        results["layman_explanation"]["habitability"] = {
            "answer": "Insufficient data to determine habitability.",
            "habitable_zone_distance": None,
            "assessment": "Unknown"
        }
    
    # Determine planet type
    planet_type = get_planet_type(planet_mass=planet_data, planet_radius=planet_data)
    results["layman_explanation"]["planet_type"] = {
        "answer": f"This appears to be a {planet_type}.",
        "type": planet_type
    }
    
    # Determine size comparison to Earth
    if planet_data.get("pl_rade"):
        earth_radius_ratio = planet_data.get("pl_rade")
        size_comparison = f"This planet is approximately {earth_radius_ratio:.1f} times the radius of Earth."
        results["layman_explanation"]["size"] = {
            "answer": size_comparison,
            "earth_radius_ratio": earth_radius_ratio
        }
    elif planet_data.get("pl_radj"):
        jupiter_radius_ratio = planet_data.get("pl_radj")
        earth_radius_ratio = jupiter_radius_ratio * 11.2  # Jupiter is 11.2 Earth radii
        size_comparison = f"This planet is approximately {earth_radius_ratio:.1f} times the radius of Earth (or {jupiter_radius_ratio:.2f} Jupiter radii)."
        results["layman_explanation"]["size"] = {
            "answer": size_comparison,
            "earth_radius_ratio": earth_radius_ratio,
            "jupiter_radius_ratio": jupiter_radius_ratio
        }
    else:
        results["layman_explanation"]["size"] = {
            "answer": "Insufficient data to determine the planet's size relative to Earth.",
            "earth_radius_ratio": None
        }
    
    # Determine mass comparison to Earth
    if planet_data.get("pl_bmasse"):
        earth_mass_ratio = planet_data.get("pl_bmasse")
        mass_comparison = f"This planet has approximately {earth_mass_ratio:.1f} times the mass of Earth."
        results["layman_explanation"]["mass"] = {
            "answer": mass_comparison,
            "earth_mass_ratio": earth_mass_ratio
        }
    elif planet_data.get("pl_bmassj"):
        jupiter_mass_ratio = planet_data.get("pl_bmassj")
        earth_mass_ratio = jupiter_mass_ratio * 317.8  # Jupiter is 317.8 Earth masses
        mass_comparison = f"This planet has approximately {earth_mass_ratio:.1f} times the mass of Earth (or {jupiter_mass_ratio:.2f} Jupiter masses)."
        results["layman_explanation"]["mass"] = {
            "answer": mass_comparison,
            "earth_mass_ratio": earth_mass_ratio,
            "jupiter_mass_ratio": jupiter_mass_ratio
        }
    elif planet_data.get("pl_msinie") or planet_data.get("pl_msinij"):
        if planet_data.get("pl_msinie"):
            earth_mass_ratio = planet_data.get("pl_msinie")
            mass_comparison = f"This planet has a minimum mass of approximately {earth_mass_ratio:.1f} times the mass of Earth."
            results["layman_explanation"]["mass"] = {
                "answer": mass_comparison,
                "earth_mass_ratio": earth_mass_ratio,
                "note": "This is a minimum mass value derived from radial velocity measurements."
            }
        else:
            jupiter_mass_ratio = planet_data.get("pl_msinij")
            earth_mass_ratio = jupiter_mass_ratio * 317.8
            mass_comparison = f"This planet has a minimum mass of approximately {earth_mass_ratio:.1f} times the mass of Earth (or {jupiter_mass_ratio:.2f} Jupiter masses)."
            results["layman_explanation"]["mass"] = {
                "answer": mass_comparison,
                "earth_mass_ratio": earth_mass_ratio,
                "jupiter_mass_ratio": jupiter_mass_ratio,
                "note": "This is a minimum mass value derived from radial velocity measurements."
            }
    else:
        results["layman_explanation"]["mass"] = {
            "answer": "Insufficient data to determine the planet's mass relative to Earth.",
            "earth_mass_ratio": None
        }
    
    # Calculate and include surface gravity if possible
    gravity = calculate_surface_gravity(planet_data, planet_data)
    
    if gravity:
        results["layman_explanation"]["gravity"] = {
            "answer": f"The surface gravity on this planet would be approximately {gravity:.1f} times that of Earth.",
            "earth_gravity_ratio": gravity
        }
    else:
        results["layman_explanation"]["gravity"] = {
            "answer": "Insufficient data to determine the planet's surface gravity.",
            "earth_gravity_ratio": None
        }
    
    # Determine how long a year is
    if planet_data.get("pl_orbper"):
        orbital_period = planet_data.get("pl_orbper")
        if orbital_period < 1:
            hours = orbital_period * 24
            year_comparison = f"A year on this planet lasts approximately {hours:.1f} hours, which is much shorter than Earth's year."
        elif orbital_period < 10:
            year_comparison = f"A year on this planet lasts approximately {orbital_period:.1f} days, which is much shorter than Earth's year."
        else:
            year_comparison = f"A year on this planet lasts approximately {orbital_period:.1f} days (Earth's year is 365.25 days)."
        
        results["layman_explanation"]["year_length"] = {
            "answer": year_comparison,
            "orbital_period_days": orbital_period
        }
    else:
        results["layman_explanation"]["year_length"] = {
            "answer": "Insufficient data to determine how long a year is on this planet.",
            "orbital_period_days": None
        }
    
    # Determine star type and characteristics
    star_type = get_star_type_from_spectype(star_spectype)
    
    if not star_type and star_temp:
        if star_temp > 30000:
            star_type = "extremely hot O-type star"
        elif star_temp > 10000:
            star_type = "very hot B-type star"
        elif star_temp > 7500:
            star_type = "hot A-type star"
        elif star_temp > 6000:
            star_type = "F-type star (hotter than our Sun)"
        elif star_temp > 5200:
            star_type = "G-type star (similar to our Sun)"
        elif star_temp > 3700:
            star_type = "K-type orange dwarf star"
        elif star_temp > 2400:
            star_type = "M-type red dwarf star"
        else:
            star_type = "very cool brown dwarf"
    
    if star_type and star_temp:
        results["layman_explanation"]["star_type"] = {
            "answer": f"This planet orbits a {star_type} with a temperature of {star_temp} K (our Sun is about 5778 K).",
            "star_temperature": star_temp,
            "star_type": star_type
        }
    elif star_type:
        results["layman_explanation"]["star_type"] = {
            "answer": f"This planet orbits a {star_type}.",
            "star_temperature": None,
            "star_type": star_type
        }
    elif star_temp:
        results["layman_explanation"]["star_type"] = {
            "answer": f"This planet orbits a star with a temperature of {star_temp} K (our Sun is about 5778 K).",
            "star_temperature": star_temp,
            "star_type": "Unknown"
        }
    else:
        results["layman_explanation"]["star_type"] = {
            "answer": "Insufficient data to determine the type of star this planet orbits.",
            "star_temperature": None,
            "star_type": "Unknown"
        }
    
    return results

def process_exoplanet_data(input_file, output_file):
    """
    Process exoplanet data from JSON file and save results to output file
    """
    # Load data
    data = load_exoplanet_data(input_file)
    if not data:
        print(f"Failed to load data from {input_file}")
        return None
    
    # Process all planets
    results = []
    processed_planets = set()  # Track already processed planets
    
    # Check if data is a list
    if isinstance(data, list):
        # Handle potential duplicates by tracking planet names
        for planet in data:
            planet_name = planet.get('pl_name')
            
            # Skip if planet has already been processed (duplicate)
            if planet_name in processed_planets:
                print(f"Skipping duplicate planet: {planet_name}")
                continue
            
            try:
                planet_result = analyze_exoplanet(planet)
                results.append(planet_result)
                processed_planets.add(planet_name)
                print(f"Processed planet: {planet_name or 'Unnamed'}")
            except Exception as e:
                print(f"Error processing planet {planet_name or 'Unnamed'}: {e}")
    else:
        # If data is a single planet
        try:
            results = analyze_exoplanet(data)
            print(f"Processed planet: {data.get('pl_name', 'Unnamed')}")
        except Exception as e:
            print(f"Error processing planet {data.get('pl_name', 'Unnamed')}: {e}")
    
    # Save results to output file
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
        print(f"Processed {len(processed_planets)} unique planets")
        return results
    except Exception as e:
        print(f"Error saving results to {output_file}: {e}")
        return results

if __name__ == "__main__":
    # Define input and output files
    input_file = "processed.json"
    output_file = "exoplanet_explanations.json"
    
    # Process data
    process_exoplanet_data(input_file, output_file)