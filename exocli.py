import pymysql
import argparse
import sys
import os
import textwrap
import random
import time
import json
from datetime import datetime
from tabulate import tabulate
from termcolor import colored, cprint
from pyfiglet import Figlet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import math

class ExoplanetDatabase:
    """Class to interact with the exoplanet database"""
    
    def __init__(self, host="localhost", user="root", password="<password>", database="exo"):
        """Initialize database connection"""
        try:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.connection.cursor()
            print(colored("✓ Connected to database successfully", "green"))
        except pymysql.Error as e:
            print(colored(f"✗ Database connection error: {e}", "red"))
            sys.exit(1)
    
    def __del__(self):
        """Close database connection on object destruction"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
    
    def get_all_planets(self, limit=None, offset=0, order_by="planet_name"):
        """Get all planets with optional limit, offset and ordering"""
        query = f"SELECT * FROM exo_planets ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_random_planet(self):
        """Get a random planet from the database"""
        query = "SELECT * FROM exo_planets ORDER BY RAND() LIMIT 1"
        self.cursor.execute(query)
        return self.cursor.fetchone()
    
    def search_planets(self, search_term, search_by="planet_name"):
        """Search planets by various criteria"""
        valid_columns = ["planet_name", "host_star", "discovery_method", 
                         "discovery_year", "planet_type", "star_type"]
        
        if search_by not in valid_columns:
            search_by = "planet_name"
        
        query = f"SELECT * FROM exo_planets WHERE {search_by} LIKE %s ORDER BY {search_by}"
        self.cursor.execute(query, (f"%{search_term}%",))
        return self.cursor.fetchall()
    
    def get_planet_by_name(self, planet_name):
        """Get a single planet by its exact name"""
        query = "SELECT * FROM exo_planets WHERE planet_name = %s"
        self.cursor.execute(query, (planet_name,))
        return self.cursor.fetchone()
    
    def get_planets_in_habitable_zone(self):
        """Get planets that are in the habitable zone"""
        query = "SELECT * FROM exo_planets WHERE assessment LIKE '%habitable zone%'"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_planets_by_type(self, planet_type):
        """Get planets by their type"""
        query = "SELECT * FROM exo_planets WHERE planet_type LIKE %s"
        self.cursor.execute(query, (f"%{planet_type}%",))
        return self.cursor.fetchall()
    
    def get_planets_by_discovery_method(self, method):
        """Get planets by their discovery method"""
        query = "SELECT * FROM exo_planets WHERE discovery_method LIKE %s"
        self.cursor.execute(query, (f"%{method}%",))
        return self.cursor.fetchall()
    
    def get_planets_by_year_range(self, start_year, end_year):
        """Get planets discovered within a specific year range"""
        query = "SELECT * FROM exo_planets WHERE discovery_year BETWEEN %s AND %s ORDER BY discovery_year"
        self.cursor.execute(query, (start_year, end_year))
        return self.cursor.fetchall()
    
    def get_planets_by_distance_range(self, min_distance, max_distance):
        """Get planets within a specific distance range (light years)"""
        query = "SELECT * FROM exo_planets WHERE distance_value BETWEEN %s AND %s ORDER BY distance_value"
        self.cursor.execute(query, (min_distance, max_distance))
        return self.cursor.fetchall()
    
    def get_planets_by_star_temperature(self, min_temp, max_temp):
        """Get planets orbiting stars within a specific temperature range"""
        query = "SELECT * FROM exo_planets WHERE star_temperature BETWEEN %s AND %s ORDER BY star_temperature"
        self.cursor.execute(query, (min_temp, max_temp))
        return self.cursor.fetchall()
    
    def get_planets_by_orbital_period(self, min_days, max_days):
        """Get planets with orbital periods in a specific range"""
        query = "SELECT * FROM exo_planets WHERE orbital_period_days BETWEEN %s AND %s ORDER BY orbital_period_days"
        self.cursor.execute(query, (min_days, max_days))
        return self.cursor.fetchall()
    
    def get_habitable_superearths(self):
        """Get super-Earth planets in the habitable zone"""
        query = """
            SELECT * FROM exo_planets 
            WHERE assessment LIKE '%habitable zone%'
            AND earth_mass_ratio BETWEEN 1.0 AND 10.0
            ORDER BY earth_mass_ratio
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_earthlike_planets(self):
        """Get potentially Earth-like planets (mass and radius close to Earth)"""
        query = """
            SELECT * FROM exo_planets 
            WHERE earth_mass_ratio BETWEEN 0.5 AND 2.0 
            AND earth_radius_ratio BETWEEN 0.8 AND 1.5
            ORDER BY ABS(earth_mass_ratio - 1.0) + ABS(earth_radius_ratio - 1.0)
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_gas_giants(self):
        """Get gas giant planets"""
        query = """
            SELECT * FROM exo_planets 
            WHERE planet_type LIKE '%gas giant%' OR planet_type LIKE '%Jupiter%'
            ORDER BY earth_mass_ratio DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_nearby_planets(self, max_distance=50):
        """Get planets within a certain distance from Earth"""
        query = """
            SELECT * FROM exo_planets 
            WHERE distance_value <= %s
            ORDER BY distance_value
        """
        self.cursor.execute(query, (max_distance,))
        return self.cursor.fetchall()
    
    def get_recently_discovered_planets(self, years=10):
        """Get planets discovered in the last X years"""
        current_year = datetime.now().year
        start_year = current_year - years
        query = """
            SELECT * FROM exo_planets 
            WHERE discovery_year >= %s
            ORDER BY discovery_year DESC
        """
        self.cursor.execute(query, (start_year,))
        return self.cursor.fetchall()
    
    def get_planet_categories(self):
        """Get categories of planets available in the database"""
        categories = {}
        
        # Get all unique planet types
        self.cursor.execute("SELECT DISTINCT planet_type FROM exo_planets WHERE planet_type IS NOT NULL")
        planet_types = [row['planet_type'] for row in self.cursor.fetchall()]
        categories['planet_types'] = planet_types
        
        # Get all unique star types
        self.cursor.execute("SELECT DISTINCT star_type FROM exo_planets WHERE star_type IS NOT NULL")
        star_types = [row['star_type'] for row in self.cursor.fetchall()]
        categories['star_types'] = star_types
        
        # Get all unique discovery methods
        self.cursor.execute("SELECT DISTINCT discovery_method FROM exo_planets WHERE discovery_method IS NOT NULL")
        methods = [row['discovery_method'] for row in self.cursor.fetchall()]
        categories['discovery_methods'] = methods
        
        # Get min and max discovery years
        self.cursor.execute("SELECT MIN(discovery_year) as min_year, MAX(discovery_year) as max_year FROM exo_planets")
        years = self.cursor.fetchone()
        categories['discovery_years'] = {'min': years['min_year'], 'max': years['max_year']}
        
        # Get min and max distances
        self.cursor.execute("SELECT MIN(distance_value) as min_dist, MAX(distance_value) as max_dist FROM exo_planets")
        distances = self.cursor.fetchone()
        categories['distances'] = {'min': distances['min_dist'], 'max': distances['max_dist']}
        
        return categories
    
    def get_database_statistics(self):
        """Get comprehensive statistics about the exoplanet database"""
        stats = {}
        
        # Basic counts
        self.cursor.execute("SELECT COUNT(*) as count FROM exo_planets")
        stats["total_planets"] = self.cursor.fetchone()["count"]
        
        # Planets in habitable zone
        self.cursor.execute("SELECT COUNT(*) as count FROM exo_planets WHERE assessment LIKE '%habitable zone%'")
        stats["habitable_zone_planets"] = self.cursor.fetchone()["count"]
        
        # Planets by type
        self.cursor.execute("""
            SELECT planet_type, COUNT(*) as count 
            FROM exo_planets 
            WHERE planet_type IS NOT NULL 
            GROUP BY planet_type 
            ORDER BY count DESC
        """)
        stats["planets_by_type"] = self.cursor.fetchall()
        
        # Planets by discovery method
        self.cursor.execute("""
            SELECT discovery_method, COUNT(*) AS count
            FROM exo_planets
            WHERE discovery_method IS NOT NULL
            GROUP BY discovery_method
            ORDER BY count DESC;
 
        """)
        stats["planets_by_discovery_method"] = self.cursor.fetchall()
        
        # Planets by star type
        self.cursor.execute("""
            SELECT star_type, COUNT(*) as count 
            FROM exo_planets 
            WHERE star_type IS NOT NULL 
            GROUP BY star_type 
            ORDER BY count DESC
        """)
        stats["planets_by_star_type"] = self.cursor.fetchall()
        
        # Planets by discovery year (decades)
        self.cursor.execute("""
            SELECT 
                CONCAT(FLOOR(discovery_year/10)*10, 's') as decade,
                COUNT(*) as count 
            FROM exo_planets 
            WHERE discovery_year IS NOT NULL 
            GROUP BY FLOOR(discovery_year/10)
            ORDER BY FLOOR(discovery_year/10)
        """)
        stats["planets_by_decade"] = self.cursor.fetchall()
        
        # Distance distribution
        self.cursor.execute("""
            SELECT 
                CASE 
                    WHEN distance_value < 10 THEN 'Less than 10'
                    WHEN distance_value BETWEEN 10 AND 50 THEN '10-50'
                    WHEN distance_value BETWEEN 50 AND 100 THEN '50-100'
                    WHEN distance_value BETWEEN 100 AND 500 THEN '100-500'
                    WHEN distance_value BETWEEN 500 AND 1000 THEN '500-1000'
                    ELSE 'Over 1000'
                END as distance_range,
                COUNT(*) as count
            FROM exo_planets
            WHERE distance_value IS NOT NULL
            GROUP BY distance_range
            ORDER BY MIN(distance_value)
        """)
        stats["distance_distribution"] = self.cursor.fetchall()
        
        # Orbital period distribution
        self.cursor.execute("""
            SELECT 
                CASE 
                    WHEN orbital_period_days < 10 THEN 'Less than 10 days'
                    WHEN orbital_period_days BETWEEN 10 AND 100 THEN '10-100 days'
                    WHEN orbital_period_days BETWEEN 100 AND 365 THEN '100-365 days'
                    WHEN orbital_period_days BETWEEN 365 AND 1000 THEN '1-3 years'
                    ELSE 'Over 3 years'
                END as period_range,
                COUNT(*) as count
            FROM exo_planets
            WHERE orbital_period_days IS NOT NULL
            GROUP BY period_range
            ORDER BY MIN(orbital_period_days)
        """)
        stats["orbital_period_distribution"] = self.cursor.fetchall()
        
        # Mass distribution
        self.cursor.execute("""
            SELECT 
                CASE 
                    WHEN earth_mass_ratio < 0.5 THEN 'Less than 0.5 Earth'
                    WHEN earth_mass_ratio BETWEEN 0.5 AND 2 THEN 'Earth-like (0.5-2)'
                    WHEN earth_mass_ratio BETWEEN 2 AND 10 THEN 'Super-Earth (2-10)'
                    WHEN earth_mass_ratio BETWEEN 10 AND 50 THEN 'Neptune-like (10-50)'
                    WHEN earth_mass_ratio BETWEEN 50 AND 318 THEN 'Saturn-like (50-318)'
                    ELSE 'Jupiter+ (>318)'
                END as mass_range,
                COUNT(*) as count
            FROM exo_planets
            WHERE earth_mass_ratio IS NOT NULL
            GROUP BY mass_range
            ORDER BY MIN(earth_mass_ratio)
        """)
        stats["mass_distribution"] = self.cursor.fetchall()
        
        # Average values
        self.cursor.execute("""
            SELECT 
                AVG(earth_mass_ratio) as avg_mass,
                AVG(earth_radius_ratio) as avg_radius,
                AVG(earth_gravity_ratio) as avg_gravity,
                AVG(orbital_period_days) as avg_orbital_period,
                AVG(distance_value) as avg_distance,
                AVG(star_temperature) as avg_star_temp
            FROM exo_planets
        """)
        stats["averages"] = self.cursor.fetchone()
        
        # Extreme values
        self.cursor.execute("""
            SELECT 
                MIN(earth_mass_ratio) as min_mass,
                MAX(earth_mass_ratio) as max_mass,
                MIN(earth_radius_ratio) as min_radius,
                MAX(earth_radius_ratio) as max_radius,
                MIN(orbital_period_days) as min_period,
                MAX(orbital_period_days) as max_period,
                MIN(distance_value) as min_distance,
                MAX(distance_value) as max_distance
            FROM exo_planets
        """)
        stats["extremes"] = self.cursor.fetchone()
        
        # Completeness of data
        self.cursor.execute("""
            SELECT 
                SUM(CASE WHEN earth_mass_ratio IS NOT NULL THEN 1 ELSE 0 END) as mass_count,
                SUM(CASE WHEN earth_radius_ratio IS NOT NULL THEN 1 ELSE 0 END) as radius_count,
                SUM(CASE WHEN earth_gravity_ratio IS NOT NULL THEN 1 ELSE 0 END) as gravity_count,
                SUM(CASE WHEN orbital_period_days IS NOT NULL THEN 1 ELSE 0 END) as period_count,
                SUM(CASE WHEN distance_value IS NOT NULL THEN 1 ELSE 0 END) as distance_count,
                SUM(CASE WHEN star_temperature IS NOT NULL THEN 1 ELSE 0 END) as star_temp_count,
                COUNT(*) as total
            FROM exo_planets
        """)
        completeness = self.cursor.fetchone()
        stats["data_completeness"] = {
            "mass": completeness['mass_count'] / completeness['total'] * 100,
            "radius": completeness['radius_count'] / completeness['total'] * 100,
            "gravity": completeness['gravity_count'] / completeness['total'] * 100,
            "orbital_period": completeness['period_count'] / completeness['total'] * 100,
            "distance": completeness['distance_count'] / completeness['total'] * 100,
            "star_temperature": completeness['star_temp_count'] / completeness['total'] * 100
        }
        
        return stats

class ExoplanetDisplay:
    """Class for displaying exoplanet data"""
    
    @staticmethod
    def clear_screen():
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_title(title, color="cyan"):
        """Print a formatted title"""
        figlet = Figlet(font='slant')
        print(colored(figlet.renderText(title), color))
    
    @staticmethod
    def print_header(title, width=80, color="cyan"):
        """Print a formatted header"""
        print("\n" + "=" * width)
        print(colored(f" {title} ", color, attrs=["bold"]).center(width))
        print("=" * width + "\n")
    
    @staticmethod
    def print_subheader(title, width=80, color="green"):
        """Print a formatted subheader"""
        print("\n" + "-" * width)
        print(colored(f" {title} ", color, attrs=["bold"]).center(width))
        print("-" * width + "\n")
    
    @staticmethod
    def print_section(title, color="yellow"):
        """Print a section title"""
        print(colored(f"\n▶ {title}:", color, attrs=["bold"]))
    
    @staticmethod
    def print_subsection(title, color="blue"):
        """Print a subsection title"""
        print(colored(f"\n  • {title}:", color))
    
    @staticmethod
    def print_menu(options, prompt="Enter your choice: ", color="yellow"):
        """Print a menu and get user selection"""
        for key, value in options.items():
            print(f"  {key}. {value}")
        
        return input(colored(f"\n{prompt}", color))
    
    @staticmethod
    def print_loading(message="Loading", duration=1.5):
        """Print a loading animation"""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        start_time = time.time()
        i = 0
        
        while time.time() - start_time < duration:
            sys.stdout.write(f"\r{colored(chars[i % len(chars)], 'cyan')} {message}...")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        sys.stdout.write(f"\r{colored('✓', 'green')} {message} complete!      \n")
    
    @staticmethod
    def display_planet_card(planet):
        """Display a compact card view of a planet"""
        if not planet:
            print(colored("Planet data not available.", "yellow"))
            return
        
        width = 60
        print("┌" + "─" * width + "┐")
        
        name = planet.get('planet_name', 'Unknown Planet')
        print(f"│ {colored(name, 'cyan', attrs=['bold']):^{width}} │")
        print("├" + "─" * width + "┤")
        
        host = f"Orbiting: {planet.get('host_star', 'Unknown Star')}"
        print(f"│ {host:<{width}} │")
        
        discovered = f"Discovered: {planet.get('discovery_year', 'Unknown')} ({planet.get('discovery_method', 'Unknown method')})"
        print(f"│ {discovered:<{width}} │")
        
        distance = f"Distance: {planet.get('distance_value', 'Unknown')} {planet.get('distance_unit', 'light years')}"
        print(f"│ {distance:<{width}} │")
        
        planet_type = f"Type: {planet.get('planet_type', 'Unknown type')}"
        print(f"│ {planet_type:<{width}} │")
        
        mass = f"Mass: {planet.get('earth_mass_ratio', 'Unknown')} × Earth"
        print(f"│ {mass:<{width}} │")
        
        habitable = "Habitable Zone: Yes" if "habitable zone" in (planet.get('assessment') or "") else "Habitable Zone: No"
        print(f"│ {habitable:<{width}} │")
        
        print("└" + "─" * width + "┘")
    
    @staticmethod
    def display_planet_summary(planets, title="Exoplanets"):
        """Display a summary table of planets"""
        if not planets:
            print(colored("No planets found matching the criteria.", "yellow"))
            return
        
        # Select only the columns we want to display in the summary
        table_data = []
        for planet in planets:
            table_data.append([
                planet.get("planet_name", "Unknown"),
                planet.get("host_star", "Unknown"),
                planet.get("discovery_method", "Unknown"),
                planet.get("discovery_year", "Unknown"),
                planet.get("distance_value", "Unknown"),
                planet.get("planet_type", "Unknown"),
                "Yes" if "habitable zone" in (planet.get("assessment") or "") else "No"
            ])
        
        headers = [
            "Planet Name", "Host Star", "Discovery Method", 
            "Year", "Distance (ly)", "Type", "Habitable Zone"
        ]
        
        print(colored(f"\n{title} ({len(planets)} found):", "cyan", attrs=["bold"]))
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        
        # Show a random interesting fact about one of the planets
        if len(planets) > 0:
            random_planet = random.choice(planets)
            random_facts = [
                f"Did you know? {random_planet.get('planet_name')} was discovered using the {random_planet.get('discovery_method')} method.",
                f"Fun fact: {random_planet.get('planet_name')} is {random_planet.get('distance_value', 'Unknown')} light years away from Earth!",
                f"Interesting: {random_planet.get('planet_name')} orbits the star {random_planet.get('host_star', 'Unknown')}."
            ]
            if random_planet.get('earth_mass_ratio'):
                random_facts.append(f"Wow! {random_planet.get('planet_name')} has {random_planet.get('earth_mass_ratio'):.2f} times the mass of Earth.")
            if random_planet.get('orbital_period_days'):
                random_facts.append(f"Amazing: A year on {random_planet.get('planet_name')} lasts {random_planet.get('orbital_period_days'):.1f} Earth days!")
            
            print(colored(f"\n{random.choice(random_facts)}", "magenta", attrs=["bold"]))
    
    @staticmethod
    def display_planet_details(planet):
        """Display detailed information about a single planet with nested sections"""
        if not planet:
            print(colored("Planet not found.", "yellow"))
            return
        
        ExoplanetDisplay.clear_screen()
        
        # Use fancy title
        ExoplanetDisplay.print_title(planet['planet_name'])
        
        # Overview section
        ExoplanetDisplay.print_section("PLANETARY OVERVIEW")
        print(f"  Host Star:        {planet.get('host_star', 'Unknown')}")
        print(f"  Discovery Method: {planet.get('discovery_method', 'Unknown')}")
        print(f"  Discovery Year:   {planet.get('discovery_year', 'Unknown')}")
        print(f"  Planet Type:      {planet.get('planet_type', 'Unknown')}")
        
        # Create tabs for different categories of information
        tabs = {
            "1": "Location & Distance",
            "2": "Habitability Assessment",
            "3": "Physical Characteristics",
            "4": "Host Star Information",
            "5": "Layman Explanations",
            "B": "Back to Previous Menu"
        }
        
        while True:
            print("\n" + "─" * 80)
            print(colored("Select a category to explore:", "yellow", attrs=["bold"]))
            choice = ExoplanetDisplay.print_menu(tabs)
            
            if choice == "1":
                # Distance information
                ExoplanetDisplay.print_subheader("LOCATION & DISTANCE INFORMATION")
                if planet.get('distance_value'):
                    print(f"  Distance from Earth: {planet.get('distance_value', 'Unknown')} {planet.get('distance_unit', 'light years')}")
                    
                    # Add a scale comparison
                    if planet.get('distance_value'):
                        distance = planet.get('distance_value')
                        print("\n  Distance Perspective:")
                        print(f"    • Light travel time: {distance:.2f} years")
                        print(f"    • Voyager 1 travel time (@ 17 km/s): {distance * 17657:.0f} years")
                        print(f"    • Nearest star (Proxima Centauri): {distance / 4.246:.2f}x the distance")
                
                # Celestial coordinates (fictional for demo)
                print("\n  Celestial Coordinates:")
                print(f"    • Right Ascension: {random.randint(0, 23)}h {random.randint(0, 59)}m {random.randint(0, 59)}s")
                print(f"    • Declination: {random.choice(['+', '-'])}{random.randint(0, 89)}° {random.randint(0, 59)}' {random.randint(0, 59)}\"")
                print(f"    • Galactic Longitude: {random.randint(0, 359)}°")
                print(f"    • Galactic Latitude: {random.choice(['+', '-'])}{random.randint(0, 89)}°")
                
                input("\nPress Enter to continue...")
                
            elif choice == "2":
                # Habitability information
                ExoplanetDisplay.print_subheader("HABITABILITY ASSESSMENT")
                if planet.get('assessment'):
                    print(f"  Overall Assessment: {planet.get('assessment', 'Unknown')}")
                    print(f"  Habitable Zone Distance: {planet.get('habitable_zone_distance', 'Unknown')}")
                    print(f"  Inner Habitable Boundary: {planet.get('inner_habitable_boundary', 'Unknown')} AU")
                    print(f"  Outer Habitable Boundary: {planet.get('outer_habitable_boundary', 'Unknown')} AU")
                    print(f"  Actual Distance from Star: {planet.get('actual_distance', 'Unknown')} AU")
                    
                    # Additional fictional habitability factors
                    print("\n  Additional Habitability Factors:")
                    factors = [
                        ("Atmospheric Composition", random.choice(["Unknown", "Promising", "Challenging", "Unsuitable"])),
                        ("Surface Temperature", random.choice(["Unknown", "Extreme", "Moderate", "Varies by region"])),
                        ("Surface Water Potential", random.choice(["Unknown", "High", "Moderate", "Low", "None detected"])),
                        ("Magnetic Field", random.choice(["Unknown", "Strong", "Moderate", "Weak", "None detected"])),
                        ("Radiation Levels", random.choice(["Unknown", "Safe", "Moderate", "Dangerous"])),
                        ("Tectonic Activity", random.choice(["Unknown", "Active", "Moderate", "Minimal"]))
                    ]
                    
                    for factor, value in factors:
                        print(f"    • {factor}: {value}")
                    
                    # Habitability score (fictional)
                    score = random.randint(0, 100)
                    print(f"\n  Earth Similarity Index: {score}/100")
                    if score > 80:
                        print("    (Very similar to Earth)")
                    elif score > 60:
                        print("    (Moderately similar to Earth)")
                    elif score > 40:
                        print("    (Somewhat similar to Earth)")
                    else:
                        print("    (Not very similar to Earth)")
                else:
                    print("  Habitability information not available")
                
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                # Physical characteristics with nested sub-sections
                ExoplanetDisplay.print_subheader("PHYSICAL CHARACTERISTICS")
                
                # Mass subsection
                print(colored("\n  ▶ Mass Properties:", "blue"))
                print(f"    • Earth Mass Ratio: {planet.get('earth_mass_ratio', 'Unknown')} × Earth")
                if planet.get('earth_mass_ratio'):
                    mass = planet.get('earth_mass_ratio')
                    print(f"    • Jupiter Mass Ratio: {mass / 317.8:.4f} × Jupiter")
                    print(f"    • Solar Mass Ratio: {mass / 333000:.8f} × Sun")
                    print(f"    • Absolute Mass: {mass * 5.972e24:.2e} kg")
                
                # Size subsection
                print(colored("\n  ▶ Size Properties:", "blue"))
                print(f"    • Earth Radius Ratio: {planet.get('earth_radius_ratio', 'Unknown')} × Earth")
                if planet.get('earth_radius_ratio'):
                    radius = planet.get('earth_radius_ratio')
                    print(f"    • Jupiter Radius Ratio: {radius / 11.2:.4f} × Jupiter")
                    print(f"    • Absolute Radius: {radius * 6371:.0f} km")
                    print(f"    • Volume: {(4/3) * 3.14159 * (radius ** 3):.2f} × Earth")
                    print(f"    • Surface Area: {4 * 3.14159 * (radius ** 2):.2f} × Earth")
                
                # Gravity subsection
                print(colored("\n  ▶ Gravity Properties:", "blue"))
                print(f"    • Earth Gravity Ratio: {planet.get('earth_gravity_ratio', 'Unknown')} × Earth")
                if planet.get('earth_gravity_ratio'):
                    gravity = planet.get('earth_gravity_ratio')
                    print(f"    • Surface Gravity: {gravity * 9.8:.2f} m/s²")
                    print(f"    • Weight of 70kg Human: {70 * gravity:.1f} kg")
                
                # Orbital properties subsection (continued)
                print(colored("\n  ▶ Orbital Properties:", "blue"))
                print(f"    • Orbital Period: {planet.get('orbital_period_days', 'Unknown')} Earth days")
                if planet.get('orbital_period_days'):
                    period = planet.get('orbital_period_days')
                    print(f"    • Earth Years: {period / 365.25:.4f} years")
                    print(f"    • Orbital Velocity: {2 * 3.14159 * planet.get('actual_distance', 1) * 149597870.7 / (period * 86400):.2f} km/s")
                    
                    # Fictional additional orbit data
                    print(f"    • Eccentricity: {random.uniform(0.0, 0.3):.4f}")
                    print(f"    • Inclination: {random.uniform(0, 45):.2f}°")
                    print(f"    • Axial Tilt: {random.uniform(0, 90):.2f}°")
                
                # Atmospheric properties (fictional)
                print(colored("\n  ▶ Atmospheric Properties (Modeled):", "blue"))
                atmos_types = [
                    "Hydrogen/Helium dominated (Gas Giant)",
                    "Nitrogen/Oxygen mix (Earth-like)",
                    "Carbon Dioxide dominated (Venus-like)",
                    "Methane rich (Titan-like)",
                    "Thin/Negligible (Mars-like)",
                    "Unknown composition",
                    "Exotic metallic vapor composition"
                ]
                print(f"    • Composition Type: {random.choice(atmos_types)}")
                print(f"    • Atmospheric Pressure: {random.uniform(0, 100):.2f} Earth atmospheres")
                print(f"    • Cloud Coverage: {random.uniform(0, 100):.1f}%")
                print(f"    • Greenhouse Effect: {random.choice(['Strong', 'Moderate', 'Weak', 'Unknown'])}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "4":
                # Star information with nested details
                ExoplanetDisplay.print_subheader("HOST STAR INFORMATION")
                print(f"  Star Name: {planet.get('host_star', 'Unknown')}")
                print(f"  Star Type: {planet.get('star_type', 'Unknown')}")
                print(f"  Star Temperature: {planet.get('star_temperature', 'Unknown')} K")
                
                # Add more detailed star information
                if planet.get('star_temperature'):
                    temp = planet.get('star_temperature')
                    
                    # Star classification data
                    print("\n  Stellar Classification:")
                    if temp > 30000:
                        spectral_class = "O-type (Very hot blue star)"
                    elif temp > 10000:
                        spectral_class = "B-type (Hot blue-white star)"
                    elif temp > 7500:
                        spectral_class = "A-type (White star)"
                    elif temp > 6000:
                        spectral_class = "F-type (Yellow-white star)"
                    elif temp > 5200:
                        spectral_class = "G-type (Yellow star, like our Sun)"
                    elif temp > 3700:
                        spectral_class = "K-type (Orange star)"
                    else:
                        spectral_class = "M-type (Red dwarf star)"
                    
                    print(f"    • Spectral Class: {spectral_class}")
                    print(f"    • Color: {next(c for t, c in [(30000, 'Blue'), (10000, 'Blue-white'), (7500, 'White'), (6000, 'Yellow-white'), (5200, 'Yellow'), (3700, 'Orange'), (0, 'Red')] if temp > t)}")

                    
                    print(f"    • Comparison to Sun: {temp / 5778:.2f} × Sun's temperature")
                    
                    # Fictional additional star data
                    print("\n  Additional Star Properties (Estimated):")
                    # Estimate star radius based on temperature (very rough approximation)
                    if "giant" in (planet.get('star_type') or "").lower():
                        radius_factor = random.uniform(10, 100)
                    elif "dwarf" in (planet.get('star_type') or "").lower():
                        radius_factor = random.uniform(0.1, 0.8)
                    else:
                        radius_factor = (temp / 5778) ** 2
                    
                    print(f"    • Estimated Radius: {radius_factor:.2f} × Sun")
                    print(f"    • Estimated Mass: {radius_factor ** 0.8:.2f} × Sun")
                    print(f"    • Estimated Luminosity: {(radius_factor ** 2) * (temp / 5778) ** 4:.2e} × Sun")
                    print(f"    • Estimated Age: {random.uniform(0.1, 13):.1f} billion years")
                    print(f"    • Metallicity: {random.uniform(-2.5, 0.5):.2f} [Fe/H]")
                    
                    # Stellar system
                    system_types = ["Single star system", "Binary star system", "Triple star system", "Part of a cluster"]
                    print(f"    • System Type: {random.choice(system_types)}")
                    
                    # Star stability and activity
                    activity_levels = ["Very low", "Low", "Moderate", "High", "Very high", "Extreme"]
                    print(f"    • Stellar Activity: {random.choice(activity_levels)}")
                    print(f"    • Flare Frequency: {random.choice(activity_levels)}")
                else:
                    print("  Detailed star information not available")
                
                input("\nPress Enter to continue...")
                
            elif choice == "5":
                # Layman explanations section
                ExoplanetDisplay.print_subheader("LAYMAN'S GUIDE TO THIS PLANET")
                
                if planet.get('size_answer'):
                    print(colored("\n  ▶ Size:", "blue"))
                    print(textwrap.fill(planet.get('size_answer', ''), initial_indent="    ", 
                                       subsequent_indent="    ", width=76))
                
                if planet.get('mass_answer'):
                    print(colored("\n  ▶ Mass:", "blue"))
                    print(textwrap.fill(planet.get('mass_answer', ''), initial_indent="    ", 
                                       subsequent_indent="    ", width=76))
                
                if planet.get('gravity_answer'):
                    print(colored("\n  ▶ Gravity:", "blue"))
                    print(textwrap.fill(planet.get('gravity_answer', ''), initial_indent="    ", 
                                       subsequent_indent="    ", width=76))
                
                if planet.get('year_length_answer'):
                    print(colored("\n  ▶ Year Length:", "blue"))
                    print(textwrap.fill(planet.get('year_length_answer', ''), initial_indent="    ", 
                                       subsequent_indent="    ", width=76))
                
                if planet.get('star_type_answer'):
                    print(colored("\n  ▶ Star Type:", "blue"))
                    print(textwrap.fill(planet.get('star_type_answer', ''), initial_indent="    ", 
                                       subsequent_indent="    ", width=76))
                
                # Add a "what if you lived there" section (fictional)
                print(colored("\n  ▶ Life on this Planet:", "blue"))
                
                conditions = []
                
                # Determine likely conditions based on real data
                if planet.get('earth_mass_ratio') and planet.get('earth_mass_ratio') > 5:
                    conditions.append("The high gravity would make movement difficult. Your muscles and skeleton would need to be much stronger.")
                
                if planet.get('earth_mass_ratio') and planet.get('earth_mass_ratio') < 0.5:
                    conditions.append("The low gravity would make you feel very light. You could jump several times higher than on Earth.")
                
                if planet.get('orbital_period_days') and planet.get('orbital_period_days') < 100:
                    conditions.append("The years would be very short. Seasonal changes would happen rapidly, giving less time for agriculture.")
                
                if planet.get('orbital_period_days') and planet.get('orbital_period_days') > 1000:
                    conditions.append("The years would be extremely long. Each season might last longer than an entire Earth year.")
                
                if "habitable zone" not in (planet.get('assessment') or ""):
                    conditions.append("The temperature would likely be too extreme for Earth-like life without advanced technology.")
                
                if "gas giant" in (planet.get('planet_type') or "").lower():
                    conditions.append("There would be no solid surface to stand on. Any settlement would need to float in the upper atmosphere.")
                
                # Add some random conditions too
                random_conditions = [
                    "The day/night cycle would be significantly different from Earth.",
                    "Unique weather patterns would create challenges for settlement.",
                    "The different atmospheric composition would require breathing apparatus.",
                    "The radiation environment would necessitate special shielding.",
                    "The local stellar environment might offer spectacular skies with multiple visible stars.",
                    "Any liquid water might have different properties due to mineral content.",
                    "Local materials might enable new types of construction techniques.",
                    "Communication with Earth would be delayed due to the vast distance."
                ]
                
                # If we don't have enough real conditions, add some random ones
                while len(conditions) < 4:
                    condition = random.choice(random_conditions)
                    if condition not in conditions:
                        conditions.append(condition)
                
                # Print the conditions
                for condition in conditions[:4]:  # Limit to 4 conditions
                    print(f"    • {condition}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "B" or choice.lower() == "b":
                break
            else:
                print(colored("Invalid choice. Please try again.", "red"))
    
    @staticmethod
    def compare_planets(planets, comparison_type="basic"):
        """Display a comparison table between multiple planets with different comparison types"""
        if not planets or len(planets) < 2:
            print(colored("Need at least two planets to compare.", "yellow"))
            return
        
        ExoplanetDisplay.clear_screen()
        
        # Header
        ExoplanetDisplay.print_header(f"Comparison of {len(planets)} Exoplanets", width=100)
        
        # Comparison type options
        comparison_types = {
            "1": "Basic Properties",
            "2": "Physical Characteristics",
            "3": "Habitability Factors",
            "4": "Orbital Dynamics",
            "5": "Star Comparison",
            "6": "All Properties",
            "B": "Back to Previous Menu"
        }
        
        if comparison_type == "menu":
            print(colored("Select comparison type:", "cyan"))
            comparison_choice = ExoplanetDisplay.print_menu(comparison_types)
            
            if comparison_choice == "1":
                comparison_type = "basic"
            elif comparison_choice == "2":
                comparison_type = "physical"
            elif comparison_choice == "3":
                comparison_type = "habitability"
            elif comparison_choice == "4":
                comparison_type = "orbital"
            elif comparison_choice == "5":
                comparison_type = "star"
            elif comparison_choice == "6":
                comparison_type = "all"
            elif comparison_choice == "B" or comparison_choice.lower() == "b":
                return
            else:
                print(colored("Invalid choice. Using basic comparison.", "red"))
                comparison_type = "basic"
        
        # Build comparison table headers
        headers = ["Property"]
        for planet in planets:
            headers.append(planet.get("planet_name", "Unknown"))
        
        rows = []
        
        # Basic properties comparison
        if comparison_type in ["basic", "all"]:
            rows.append(["--- BASIC PROPERTIES ---", *["" for _ in range(len(planets))]])
            rows.append(["Host Star", *[p.get("host_star", "Unknown") for p in planets]])
            rows.append(["Discovery Method", *[p.get("discovery_method", "Unknown") for p in planets]])
            rows.append(["Discovery Year", *[p.get("discovery_year", "Unknown") for p in planets]])
            rows.append(["Distance (ly)", *[p.get("distance_value", "Unknown") for p in planets]])
            rows.append(["Planet Type", *[p.get("planet_type", "Unknown") for p in planets]])
        
        # Physical characteristics comparison
        if comparison_type in ["physical", "all"]:
            rows.append(["", *["" for _ in range(len(planets))]])
            rows.append(["--- PHYSICAL CHARACTERISTICS ---", *["" for _ in range(len(planets))]])
            rows.append(["Earth Mass Ratio", *[p.get("earth_mass_ratio", "Unknown") for p in planets]])
            rows.append(["Earth Radius Ratio", *[p.get("earth_radius_ratio", "Unknown") for p in planets]])
            rows.append(["Earth Gravity Ratio", *[p.get("earth_gravity_ratio", "Unknown") for p in planets]])
            
            # Derived physical properties (calculated if data available)
            densities = []
            for p in planets:
                if p.get("earth_mass_ratio") and p.get("earth_radius_ratio"):
                    density = p.get("earth_mass_ratio") / (p.get("earth_radius_ratio") ** 3)
                    densities.append(f"{density:.2f} × Earth")
                else:
                    densities.append("Unknown")
            rows.append(["Density (calculated)", *densities])
            
            volumes = []
            for p in planets:
                if p.get("earth_radius_ratio"):
                    volume = (4/3) * 3.14159 * (p.get("earth_radius_ratio") ** 3)
                    volumes.append(f"{volume:.2f} × Earth")
                else:
                    volumes.append("Unknown")
            rows.append(["Volume (calculated)", *volumes])
            
            surface_areas = []
            for p in planets:
                if p.get("earth_radius_ratio"):
                    area = 4 * 3.14159 * (p.get("earth_radius_ratio") ** 2)
                    surface_areas.append(f"{area:.2f} × Earth")
                else:
                    surface_areas.append("Unknown")
            rows.append(["Surface Area (calculated)", *surface_areas])
        
        # Habitability factors comparison
        if comparison_type in ["habitability", "all"]:
            rows.append(["", *["" for _ in range(len(planets))]])
            rows.append(["--- HABITABILITY FACTORS ---", *["" for _ in range(len(planets))]])
            rows.append(["In Habitable Zone", *["Yes" if "habitable zone" in (p.get("assessment") or "") else "No" for p in planets]])
            rows.append(["Habitability Assessment", *[p.get("assessment", "Unknown") for p in planets]])
            rows.append(["Habitable Zone Distance", *[p.get("habitable_zone_distance", "Unknown") for p in planets]])
            rows.append(["Inner HZ Boundary (AU)", *[p.get("inner_habitable_boundary", "Unknown") for p in planets]])
            rows.append(["Outer HZ Boundary (AU)", *[p.get("outer_habitable_boundary", "Unknown") for p in planets]])
            rows.append(["Actual Distance (AU)", *[p.get("actual_distance", "Unknown") for p in planets]])
            
            # Earth similarity calculation (simple formula based on available data)
            esi_scores = []
            for p in planets:
                score = 0
                factors = 0
                
                # Check if in habitable zone
                if "habitable zone" in (p.get("assessment") or ""):
                    score += 25
                    factors += 1
                
                # Check mass similarity to Earth
                if p.get("earth_mass_ratio"):
                    mass_factor = 25 * (1 - min(abs(math.log10(p.get("earth_mass_ratio"))), 2) / 2)
                    score += mass_factor
                    factors += 1
                
                # Check radius similarity to Earth
                if p.get("earth_radius_ratio"):
                    radius_factor = 25 * (1 - min(abs(p.get("earth_radius_ratio") - 1), 2) / 2)
                    score += radius_factor
                    factors += 1
                
                # Check gravity similarity to Earth
                if p.get("earth_gravity_ratio"):
                    gravity_factor = 25 * (1 - min(abs(p.get("earth_gravity_ratio") - 1), 2) / 2)
                    score += gravity_factor
                    factors += 1
                
                # Calculate final score
                if factors > 0:
                    final_score = score / factors * (factors / 4)  # Scale by completeness
                    esi_scores.append(f"{final_score:.1f}/100")
                else:
                    esi_scores.append("Unknown")
            
            rows.append(["Earth Similarity Index", *esi_scores])
        
        # Orbital dynamics comparison
        if comparison_type in ["orbital", "all"]:
            rows.append(["", *["" for _ in range(len(planets))]])
            rows.append(["--- ORBITAL DYNAMICS ---", *["" for _ in range(len(planets))]])
            rows.append(["Orbital Period (days)", *[p.get("orbital_period_days", "Unknown") for p in planets]])
            
            # Derived orbital properties
            orbital_velocities = []
            for p in planets:
                if p.get("orbital_period_days") and p.get("actual_distance"):
                    # v = 2πr/T
                    velocity = 2 * 3.14159 * p.get("actual_distance") * 149597870.7 / (p.get("orbital_period_days") * 86400)
                    orbital_velocities.append(f"{velocity:.2f} km/s")
                else:
                    orbital_velocities.append("Unknown")
            rows.append(["Orbital Velocity", *orbital_velocities])
            
            years_in_earth_years = []
            for p in planets:
                if p.get("orbital_period_days"):
                    years = p.get("orbital_period_days") / 365.25
                    years_in_earth_years.append(f"{years:.3f} Earth years")
                else:
                    years_in_earth_years.append("Unknown")
            rows.append(["Year Length", *years_in_earth_years])
        
        # Star comparison
        if comparison_type in ["star", "all"]:
            rows.append(["", *["" for _ in range(len(planets))]])
            rows.append(["--- HOST STAR PROPERTIES ---", *["" for _ in range(len(planets))]])
            rows.append(["Star Type", *[p.get("star_type", "Unknown") for p in planets]])
            rows.append(["Star Temperature (K)", *[p.get("star_temperature", "Unknown") for p in planets]])
            
            # Compare to our Sun
            sun_temp_ratio = []
            for p in planets:
                if p.get("star_temperature"):
                    ratio = p.get("star_temperature") / 5778
                    sun_temp_ratio.append(f"{ratio:.2f} × Sun")
                else:
                    sun_temp_ratio.append("Unknown")
            rows.append(["Temperature vs Sun", *sun_temp_ratio])
            
            # Star colors based on temperature
            star_colors = []
            for p in planets:
                if p.get("star_temperature"):
                    temp = p.get("star_temperature")
                    if temp > 30000:
                        star_colors.append("Blue")
                    elif temp > 10000:
                        star_colors.append("Blue-white")
                    elif temp > 7500:
                        star_colors.append("White")
                    elif temp > 6000:
                        star_colors.append("Yellow-white")
                    elif temp > 5200:
                        star_colors.append("Yellow")
                    elif temp > 3700:
                        star_colors.append("Orange")
                    else:
                        star_colors.append("Red")
                else:
                    star_colors.append("Unknown")
            rows.append(["Star Color", *star_colors])
        
        # Print the comparison table
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        
        # Add option to switch comparison type
        if comparison_type != "menu":
            print("\nOptions:")
            print("  C: Change comparison type")
            print("  B: Back to previous menu")
            
            option = input(colored("\nEnter your choice: ", "yellow")).upper()
            if option == "C":
                ExoplanetDisplay.compare_planets(planets, "menu")
        
        print("\n" + "="*100 + "\n")
    
    
    @staticmethod
    def generate_exoplanet_report(planets, report_title="Exoplanet Analysis Report", output_file=None):
        """Generate a comprehensive report on exoplanets with visualization and save to PDF"""
        ExoplanetDisplay.clear_screen()
        ExoplanetDisplay.print_header(f"Generating {report_title}", width=80)
        
        if not planets:
            print(colored("No planets available to generate report.", "yellow"))
            return
        
        # Create PDF with matplotlib
        with PdfPages(output_file or f"exoplanet_report_{int(time.time())}.pdf") as pdf:
            # Create title page
            plt.figure(figsize=(11, 8.5))
            plt.axis('off')
            plt.text(0.5, 0.6, report_title, fontsize=24, ha='center')
            plt.text(0.5, 0.5, f"Analysis of {len(planets)} Exoplanets", fontsize=18, ha='center')
            plt.text(0.5, 0.4, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", fontsize=14, ha='center')
            plt.text(0.5, 0.3, "Exoplanet Database Explorer", fontsize=16, ha='center')
            pdf.savefig()
            plt.close()
            
            # Summary statistics page
            plt.figure(figsize=(11, 8.5))
            plt.axis('off')
            plt.text(0.5, 0.95, "Summary Statistics", fontsize=20, ha='center')
            
            # Extract data for statistics
            planet_types = {}
            discovery_methods = {}
            discovery_years = []
            star_types = {}
            masses = []
            radii = []
            distances = []
            periods = []
            habitable_count = 0
            
            for planet in planets:
                # Count planet types
                planet_type = planet.get('planet_type')
                if planet_type:
                    planet_types[planet_type] = planet_types.get(planet_type, 0) + 1
                
                # Count discovery methods
                method = planet.get('discovery_method')
                if method:
                    discovery_methods[method] = discovery_methods.get(method, 0) + 1
                
                # Collect discovery years
                year = planet.get('discovery_year')
                if year:
                    discovery_years.append(year)
                
                # Count star types
                star_type = planet.get('star_type')
                if star_type:
                    star_types[star_type] = star_types.get(star_type, 0) + 1
                
                # Collect numerical data
                mass = planet.get('earth_mass_ratio')
                if mass:
                    masses.append(mass)
                
                radius = planet.get('earth_radius_ratio')
                if radius:
                    radii.append(radius)
                
                distance = planet.get('distance_value')
                if distance:
                    distances.append(distance)
                
                period = planet.get('orbital_period_days')
                if period:
                    periods.append(period)
                
                # Count habitable planets
                if "habitable zone" in (planet.get('assessment') or ""):
                    habitable_count += 1
            
            # Display summary statistics
            stats_text = [
                f"Total Planets: {len(planets)}",
                f"Habitable Zone Planets: {habitable_count} ({habitable_count/len(planets)*100:.1f}%)",
                f"Number of Planet Types: {len(planet_types)}",
                f"Number of Discovery Methods: {len(discovery_methods)}",
                f"Discovery Year Range: {min(discovery_years) if discovery_years else 'N/A'} - {max(discovery_years) if discovery_years else 'N/A'}",
                f"Number of Star Types: {len(star_types)}",
                f"Average Mass: {sum(masses)/len(masses) if masses else 'N/A':.2f} × Earth",
                f"Average Radius: {sum(radii)/len(radii) if radii else 'N/A':.2f} × Earth",
                f"Average Distance: {sum(distances)/len(distances) if distances else 'N/A':.2f} light years",
                f"Average Orbital Period: {sum(periods)/len(periods) if periods else 'N/A':.2f} days"
            ]
            
            for i, text in enumerate(stats_text):
                plt.text(0.1, 0.85 - i * 0.05, text, fontsize=12)
            
            pdf.savefig()
            plt.close()
            
            # Planet Types Distribution
            if planet_types:
                plt.figure(figsize=(11, 8.5))
                plt.subplot(111)
                
                labels = list(planet_types.keys())
                values = list(planet_types.values())
                colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
                
                # Filter to top 8 types for cleaner pie chart
                if len(labels) > 8:
                    top_indices = np.argsort(values)[-8:]
                    other_sum = sum(values[i] for i in range(len(values)) if i not in top_indices)
                    labels = [labels[i] for i in top_indices]
                    values = [values[i] for i in top_indices]
                    labels.append("Other")
                    values.append(other_sum)
                    colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
                
                plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
                plt.axis('equal')
                plt.title('Planet Types Distribution', fontsize=18)
                pdf.savefig()
                plt.close()
            
            # Discovery Methods Distribution
            if discovery_methods:
                plt.figure(figsize=(11, 8.5))
                plt.subplot(111)
                
                labels = list(discovery_methods.keys())
                values = list(discovery_methods.values())
                colors = plt.cm.plasma(np.linspace(0, 1, len(labels)))
                
                # Filter to top 8 methods for cleaner pie chart
                if len(labels) > 8:
                    top_indices = np.argsort(values)[-8:]
                    other_sum = sum(values[i] for i in range(len(values)) if i not in top_indices)
                    labels = [labels[i] for i in top_indices]
                    values = [values[i] for i in top_indices]
                    labels.append("Other")
                    values.append(other_sum)
                    colors = plt.cm.plasma(np.linspace(0, 1, len(labels)))
                
                plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
                plt.axis('equal')
                plt.title('Discovery Methods Distribution', fontsize=18)
                pdf.savefig()
                plt.close()
            
            # Discovery Timeline
            if discovery_years:
                plt.figure(figsize=(11, 8.5))
                plt.subplot(111)
                
                # Count discoveries per year
                year_counts = {}
                for year in discovery_years:
                    year_counts[year] = year_counts.get(year, 0) + 1
                
                years = sorted(year_counts.keys())
                counts = [year_counts[year] for year in years]
                
                plt.bar(years, counts, color='skyblue')
                plt.xlabel('Discovery Year', fontsize=14)
                plt.ylabel('Number of Planets Discovered', fontsize=14)
                plt.title('Exoplanet Discoveries Timeline', fontsize=18)
                plt.xticks(rotation=45)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                pdf.savefig()
                plt.close()
            
            # Mass vs. Radius Scatter Plot
            if masses and radii and len(masses) == len(radii):
                # Only use the planets that have both mass and radius
                valid_indices = [i for i in range(len(planets)) 
                               if planets[i].get('earth_mass_ratio') and planets[i].get('earth_radius_ratio')]
                
                valid_masses = [planets[i].get('earth_mass_ratio') for i in valid_indices]
                valid_radii = [planets[i].get('earth_radius_ratio') for i in valid_indices]
                
                if valid_masses and valid_radii:
                    plt.figure(figsize=(11, 8.5))
                    plt.subplot(111)
                    
                    # Define point colors based on planet habitability
                    colors = ['red' if "habitable zone" not in (planets[i].get('assessment') or "") 
                             else 'green' for i in valid_indices]
                    
                    plt.scatter(valid_masses, valid_radii, c=colors, alpha=0.7)
                    plt.xscale('log')
                    plt.yscale('log')
                    plt.xlabel('Mass (Earth = 1)', fontsize=14)
                    plt.ylabel('Radius (Earth = 1)', fontsize=14)
                    plt.title('Mass vs. Radius Relationship', fontsize=18)
                    plt.grid(True, alpha=0.3)
                    
                    # Add reference points
                    ref_objects = [
                        {"name": "Earth", "mass": 1, "radius": 1},
                        {"name": "Jupiter", "mass": 317.8, "radius": 11.2},
                        {"name": "Saturn", "mass": 95.2, "radius": 9.45},
                        {"name": "Neptune", "mass": 17.1, "radius": 3.88},
                        {"name": "Mars", "mass": 0.107, "radius": 0.532},
                        {"name": "Venus", "mass": 0.815, "radius": 0.949}
                    ]
                    
                    for obj in ref_objects:
                        plt.scatter(obj["mass"], obj["radius"], c='blue', marker='*', s=100)
                        plt.annotate(obj["name"], (obj["mass"], obj["radius"]), 
                                   xytext=(5, 5), textcoords='offset points')
                    
                    # Add legend for habitable vs non-habitable
                    from matplotlib.lines import Line2D
                    legend_elements = [
                        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Habitable Zone'),
                        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Non-Habitable Zone'),
                        Line2D([0], [0], marker='*', color='w', markerfacecolor='blue', markersize=10, label='Solar System Objects')
                    ]
                    plt.legend(handles=legend_elements, loc='upper left')
                    
                    pdf.savefig()
                    plt.close()
            
            # Distance Distribution Histogram
            if distances:
                plt.figure(figsize=(11, 8.5))
                plt.subplot(111)
                
                plt.hist(distances, bins=min(20, len(set(distances))), color='skyblue', edgecolor='black')
                plt.xlabel('Distance (Light Years)', fontsize=14)
                plt.ylabel('Number of Planets', fontsize=14)
                plt.title('Distance Distribution', fontsize=18)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                
                # Add median and mean lines
                median_dist = np.median(distances)
                mean_dist = np.mean(distances)
                plt.axvline(median_dist, color='red', linestyle='--', linewidth=2, label=f'Median: {median_dist:.2f} ly')
                plt.axvline(mean_dist, color='green', linestyle='--', linewidth=2, label=f'Mean: {mean_dist:.2f} ly')
                plt.legend()
                
                pdf.savefig()
                plt.close()
            
            # Orbital Period Distribution Histogram
            if periods:
                plt.figure(figsize=(11, 8.5))
                plt.subplot(111)
                
                # Log scale for better visualization of period distribution
                plt.hist(periods, bins=min(20, len(set(periods))), color='lightgreen', edgecolor='black')
                plt.xscale('log')
                plt.xlabel('Orbital Period (Days)', fontsize=14)
                plt.ylabel('Number of Planets', fontsize=14)
                plt.title('Orbital Period Distribution', fontsize=18)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                
                # Add Earth reference line
                plt.axvline(365.25, color='blue', linestyle='-', linewidth=2, label='Earth (365.25 days)')
                plt.legend()
                
                pdf.savefig()
                plt.close()
            
            # Habitable zone analysis page
            plt.figure(figsize=(11, 8.5))
            plt.axis('off')
            plt.text(0.5, 0.95, "Habitability Analysis", fontsize=20, ha='center')
            
            habitable_planets = [p for p in planets if "habitable zone" in (p.get('assessment') or "")]
            
            if habitable_planets:
                # Extract habitability data
                hab_types = {}
                hab_star_types = {}
                hab_distances = []
                hab_masses = []
                hab_radii = []
                
                for p in habitable_planets:
                    planet_type = p.get('planet_type')
                    if planet_type:
                        hab_types[planet_type] = hab_types.get(planet_type, 0) + 1
                    
                    star_type = p.get('star_type')
                    if star_type:
                        hab_star_types[star_type] = hab_star_types.get(star_type, 0) + 1
                    
                    if p.get('distance_value'):
                        hab_distances.append(p.get('distance_value'))
                    
                    if p.get('earth_mass_ratio'):
                        hab_masses.append(p.get('earth_mass_ratio'))
                    
                    if p.get('earth_radius_ratio'):
                        hab_radii.append(p.get('earth_radius_ratio'))
                
                # Display habitable zone statistics
                hab_stats_text = [
                    f"Total Habitable Zone Planets: {len(habitable_planets)}",
                    f"Percentage of Database: {len(habitable_planets)/len(planets)*100:.1f}%",
                    f"Most Common Planet Type: {max(hab_types.items(), key=lambda x: x[1])[0] if hab_types else 'N/A'}",
                    f"Most Common Star Type: {max(hab_star_types.items(), key=lambda x: x[1])[0] if hab_star_types else 'N/A'}",
                    f"Closest Habitable Planet: {min(hab_distances) if hab_distances else 'N/A'} light years",
                    f"Average Mass: {sum(hab_masses)/len(hab_masses) if hab_masses else 'N/A':.2f} × Earth",
                    f"Average Radius: {sum(hab_radii)/len(hab_radii) if hab_radii else 'N/A':.2f} × Earth",
                    f"Earth-like (0.5-2× Earth mass): {sum(1 for m in hab_masses if 0.5 <= m <= 2) if hab_masses else 0} planets"
                ]
                
                for i, text in enumerate(hab_stats_text):
                    plt.text(0.1, 0.85 - i * 0.05, text, fontsize=12)
                
                # List top 5 most Earth-like habitable planets
                earth_like = [p for p in habitable_planets if p.get('earth_mass_ratio') and 0.5 <= p.get('earth_mass_ratio') <= 2.0 
                              and p.get('earth_radius_ratio') and 0.8 <= p.get('earth_radius_ratio') <= 1.5]
                
                if earth_like:
                    plt.text(0.5, 0.45, "Most Earth-like Habitable Planets:", fontsize=14, ha='center')
                    
                    # Sort by Earth similarity
                    sorted_planets = sorted(earth_like, 
                                         key=lambda p: abs(p.get('earth_mass_ratio', 1) - 1) + abs(p.get('earth_radius_ratio', 1) - 1))
                    
                    for i, p in enumerate(sorted_planets[:5]):
                        similarity = 1 - (abs(p.get('earth_mass_ratio', 1) - 1) + abs(p.get('earth_radius_ratio', 1) - 1)) / 4
                        text = f"{i+1}. {p.get('planet_name')}: {similarity*100:.1f}% Earth similarity, {p.get('distance_value', 'Unknown')} light years"
                        plt.text(0.1, 0.4 - i * 0.05, text, fontsize=12)
            
            pdf.savefig()
            plt.close()
            
            # Report conclusion page
            plt.figure(figsize=(11, 8.5))
            plt.axis('off')
            plt.text(0.5, 0.6, "Report Summary", fontsize=24, ha='center')
            
            summary_points = [
                f"Analyzed {len(planets)} exoplanets from the database",
                f"Found {habitable_count} planets in the habitable zone",
                f"Identified {len(earth_like) if 'earth_like' in locals() else 0} Earth-like planets in habitable zones",
                f"Data spans discovery years from {min(discovery_years) if discovery_years else 'N/A'} to {max(discovery_years) if discovery_years else 'N/A'}",
                f"Most common discovery method: {max(discovery_methods.items(), key=lambda x: x[1])[0] if discovery_methods else 'N/A'}"
            ]
            
            for i, point in enumerate(summary_points):
                plt.text(0.5, 0.5 - i * 0.05, point, fontsize=14, ha='center')
            
            plt.text(0.5, 0.25, "Report generated by Exoplanet Database Explorer", fontsize=14, ha='center')
            plt.text(0.5, 0.2, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fontsize=12, ha='center')
            
            pdf.savefig()
            plt.close()
        
        print(colored(f"\nReport generated successfully and saved to: {output_file or f'exoplanet_report_{int(time.time())}.pdf'}", "green"))
        input("\nPress Enter to continue...")


class ExoplanetExplorer:
    """Main class for the Exoplanet Explorer application"""
    
    def __init__(self):
        """Initialize the explorer"""
        self.database = ExoplanetDatabase()
        self.display = ExoplanetDisplay()
        self.current_planets = []
    
    def display_welcome(self):
        """Display welcome screen"""
        ExoplanetDisplay.clear_screen()
        ExoplanetDisplay.print_title("Exoplanet Explorer")
        
        print(colored("\nWelcome to the Exoplanet Database Explorer!", "cyan", attrs=["bold"]))
        print("This program allows you to explore and analyze data on exoplanets - planets outside our solar system.")
        print("\nWith this tool, you can:")
        print("  • Browse and search the database of known exoplanets")
        print("  • View detailed information about specific planets")
        print("  • Compare different exoplanets side by side")
        print("  • Generate visualizations and reports")
        print("  • Explore statistics and trends in exoplanet discoveries")
        print("\nThe database contains information about planet properties, host stars, discovery methods,")
        print("habitability assessments, and much more.")
        
        input(colored("\nPress Enter to start exploring the cosmos...", "yellow"))
    
    def main_menu(self):
        """Display main menu and handle user choices"""
        while True:
            ExoplanetDisplay.clear_screen()
            ExoplanetDisplay.print_header("EXOPLANET EXPLORER - MAIN MENU", width=80)
            
            options = {
                "1": "Browse All Exoplanets",
                "2": "Search for Specific Planets",
                "3": "Explore Special Categories",
             
                "4": "Generate Reports",
                "5": "Random Planet Explorer",
                "Q": "Quit Program"
            }
            
            choice = ExoplanetDisplay.print_menu(options)
            
            if choice == "1":
                self.browse_planets()
            elif choice == "2":
                self.search_planets()
            elif choice == "3":
                self.explore_categories()
          
            elif choice == "4":
                self.generate_reports()
            elif choice == "5":
                self.random_planet()
            elif choice == "Q" or choice == "q":
                self.exit_program()
                break
            else:
                print(colored("Invalid choice. Please try again.", "red"))
                time.sleep(1)
    
    def browse_planets(self):
        """Browse all planets with pagination"""
        ExoplanetDisplay.clear_screen()
        ExoplanetDisplay.print_header("BROWSE EXOPLANETS", width=80)
        
        # Get total count
        all_planets = self.database.get_all_planets()
        total_count = len(all_planets)
        
        # Pagination settings
        page_size = 10
        total_pages = (total_count + page_size - 1) // page_size
        current_page = 1
        
        # Ordering options
        order_options = {
            "1": "Planet Name (A-Z)",
            "2": "Discovery Year (Oldest First)",
            "3": "Discovery Year (Newest First)",
            "4": "Distance (Closest First)",
            "5": "Distance (Furthest First)",
            "6": "Star Name (A-Z)",
            "7": "Planet Mass (Smallest First)",
            "8": "Planet Mass (Largest First)"
        }
        
        order_columns = {
            "1": "planet_name",
            "2": "discovery_year",
            "3": "discovery_year DESC",
            "4": "distance_value",
            "5": "distance_value DESC",
            "6": "host_star",
            "7": "earth_mass_ratio",
            "8": "earth_mass_ratio DESC"
        }
        
        # Default ordering
        current_order = "1"
        
        while True:
            ExoplanetDisplay.print_subheader(f"Browsing Page {current_page} of {total_pages}", width=80)
            
            # Fetch current page of planets with current ordering
            offset = (current_page - 1) * page_size
            planets = self.database.get_all_planets(
                limit=page_size, 
                offset=offset,
                order_by=order_columns[current_order]
            )
            
            # Display planets
            ExoplanetDisplay.display_planet_summary(planets, f"Exoplanets (Page {current_page}/{total_pages}, {total_count} total)")
            
            # Navigation options
            print("\nNavigation Options:")
            navigation = {
                "N": "Next Page",
                "P": "Previous Page",
                "G": "Go to Page...",
                "O": "Change Ordering",
                "V": "View Planet Details",
                "C": "Compare Selected Planets",
                "B": "Back to Main Menu"
            }
            
            if current_page >= total_pages:
                navigation.pop("N")
            if current_page <= 1:
                navigation.pop("P")
            
            choice = ExoplanetDisplay.print_menu(navigation)
            
            if choice == "N" and current_page < total_pages:
                current_page += 1
            elif choice == "P" and current_page > 1:
                current_page -= 1
            elif choice == "G":
                try:
                    page = int(input(colored("Enter page number: ", "yellow")))
                    if 1 <= page <= total_pages:
                        current_page = page
                    else:
                        print(colored(f"Please enter a page number between 1 and {total_pages}.", "red"))
                        time.sleep(1.5)
                except ValueError:
                    print(colored("Please enter a valid page number.", "red"))
                    time.sleep(1.5)
            elif choice == "O":
                print(colored("\nSelect ordering option:", "cyan"))
                order_choice = ExoplanetDisplay.print_menu(order_options)
                if order_choice in order_columns:
                    current_order = order_choice
                    # Reset to first page when changing order
                    current_page = 1
                else:
                    print(colored("Invalid ordering option. Keeping current order.", "red"))
                    time.sleep(1.5)
            elif choice == "V":
                planet_name = input(colored("Enter planet name to view details: ", "yellow"))
                planet = self.database.get_planet_by_name(planet_name)
                if planet:
                    self.current_planets = [planet]
                    ExoplanetDisplay.display_planet_details(planet)
                else:
                    print(colored(f"Planet '{planet_name}' not found.", "red"))
                    time.sleep(1.5)
            elif choice == "C":
                planet_names = input(colored("Enter planet names separated by commas: ", "yellow"))
                names_list = [name.strip() for name in planet_names.split(",")]
                
                planets_to_compare = []
                for name in names_list:
                    planet = self.database.get_planet_by_name(name)
                    if planet:
                        planets_to_compare.append(planet)
                    else:
                        print(colored(f"Planet '{name}' not found.", "red"))
                
                if len(planets_to_compare) >= 2:
                    self.current_planets = planets_to_compare
                    ExoplanetDisplay.compare_planets(planets_to_compare, "menu")
                else:
                    print(colored("Need at least two valid planets to compare.", "yellow"))
                    time.sleep(1.5)
            elif choice == "B":
                break
            else:
                print(colored("Invalid choice. Please try again.", "red"))
                time.sleep(1)
    
    def search_planets(self):
        """Search for specific planets"""
        ExoplanetDisplay.clear_screen()
        ExoplanetDisplay.print_header("SEARCH EXOPLANETS", width=80)
        
        # Search options menu
        search_options = {
            "1": "Search by Planet Name",
            "2": "Search by Host Star",
            "3": "Search by Discovery Method",
            "4": "Search by Discovery Year",
            "5": "Search by Planet Type",
            "6": "Search by Star Type",
            "7": "Search by Distance Range",
            "8": "Search by Mass Range",
            "9": "Search by Temperature Range",
            "B": "Back to Main Menu"
        }
        
        search_columns = {
            "1": "planet_name",
            "2": "host_star",
            "3": "discovery_method",
            "4": "discovery_year",
            "5": "planet_type",
            "6": "star_type"
        }
        
        while True:
            print(colored("Select search type:", "cyan"))
            choice = ExoplanetDisplay.print_menu(search_options)
            
            if choice in "123456":
                search_by = search_columns[choice]
                search_term = input(colored(f"Enter search term for {search_options[choice][10:]}: ", "yellow"))
                ExoplanetDisplay.print_loading("Searching")
                
                planets = self.database.search_planets(search_term, search_by)
                self.current_planets = planets
                
                ExoplanetDisplay.display_planet_summary(planets, f"Search Results for '{search_term}'")
                
                self.post_search_menu(planets)
                
            elif choice == "7":
                # Distance range search
                try:
                    min_distance = float(input(colored("Enter minimum distance (light years): ", "yellow")) or 0)
                    max_distance = float(input(colored("Enter maximum distance (light years): ", "yellow")) or 100000)
                    
                    ExoplanetDisplay.print_loading("Searching")
                    planets = self.database.get_planets_by_distance_range(min_distance, max_distance)
                    self.current_planets = planets
                    
                    ExoplanetDisplay.display_planet_summary(planets, f"Planets between {min_distance} and {max_distance} light years")
                    
                    self.post_search_menu(planets)
                    
                except ValueError:
                    print(colored("Please enter valid distance values.", "red"))
                    time.sleep(1.5)
                
            elif choice == "8":
                # Mass range search
                try:
                    min_mass = float(input(colored("Enter minimum mass (Earth masses): ", "yellow")) or 0)
                    max_mass = float(input(colored("Enter maximum mass (Earth masses): ", "yellow")) or 100000)
                    
                    ExoplanetDisplay.print_loading("Searching")
                    
                    # Since there's no direct method for this, we'll filter all planets
                    all_planets = self.database.get_all_planets()
                    planets = [p for p in all_planets if p.get('earth_mass_ratio') and 
                              min_mass <= p.get('earth_mass_ratio') <= max_mass]
                    
                    self.current_planets = planets
                    
                    ExoplanetDisplay.display_planet_summary(planets, f"Planets between {min_mass} and {max_mass} Earth masses")
                    
                    self.post_search_menu(planets)
                    
                except ValueError:
                    print(colored("Please enter valid mass values.", "red"))
                    time.sleep(1.5)
                
            elif choice == "9":
                # Star temperature range search
                try:
                    min_temp = float(input(colored("Enter minimum star temperature (K): ", "yellow")) or 0)
                    max_temp = float(input(colored("Enter maximum star temperature (K): ", "yellow")) or 100000)
                    
                    ExoplanetDisplay.print_loading("Searching")
                    planets = self.database.get_planets_by_star_temperature(min_temp, max_temp)
                    self.current_planets = planets
                    
                    ExoplanetDisplay.display_planet_summary(planets, f"Planets with star temp between {min_temp}K and {max_temp}K")
                    
                    self.post_search_menu(planets)
                    
                except ValueError:
                    print(colored("Please enter valid temperature values.", "red"))
                    time.sleep(1.5)
                
            elif choice == "B" or choice.lower() == "b":
                break
            else:
                print(colored("Invalid choice. Please try again.", "red"))
                time.sleep(1)
    
    def post_search_menu(self, planets):
        """Display options after a search result is shown"""
        if not planets:
            input(colored("\nNo results found. Press Enter to return to search menu...", "yellow"))
            return
        
        while True:
            print("\nOptions:")
            options = {
                "1": "View Planet Details",
                "2": "Compare Selected Planets",
                "3": "Generate Report for these Planets",
                "4": "New Search",
                "B": "Back to Search Menu"
            }
            
            choice = ExoplanetDisplay.print_menu(options)
            
            if choice == "1":
                planet_name = input(colored("Enter planet name to view details: ", "yellow"))
                planet = next((p for p in planets if p.get('planet_name') == planet_name), None)
                
                if planet:
                    ExoplanetDisplay.display_planet_details(planet)
                else:
                    print(colored(f"Planet '{planet_name}' not found in search results.", "red"))
                    time.sleep(1.5)
                
            elif choice == "2":
                if len(planets) < 2:
                    print(colored("Need at least two planets to compare.", "yellow"))
                    time.sleep(1.5)
                    continue
                
                planet_names = input(colored("Enter planet names separated by commas (or 'all' for all results): ", "yellow"))
                
                if planet_names.lower() == "all":
                    planets_to_compare = planets[:10]  # Limit to 10 for readability
                    if len(planets) > 10:
                        print(colored("Limiting comparison to first 10 planets for readability.", "yellow"))
                        time.sleep(1.5)
                else:
                    names_list = [name.strip() for name in planet_names.split(",")]
                    planets_to_compare = [p for p in planets if p.get('planet_name') in names_list]
                
                if len(planets_to_compare) >= 2:
                    ExoplanetDisplay.compare_planets(planets_to_compare, "menu")
                else:
                    print(colored("Need at least two valid planets to compare.", "yellow"))
                    time.sleep(1.5)
                
            elif choice == "3":
                report_title = input(colored("Enter report title (or press Enter for default): ", "yellow"))
                if not report_title:
                    report_title = "Exoplanet Search Results Analysis"
                
                output_file = input(colored("Enter output filename (or press Enter for default): ", "yellow"))
                if not output_file:
                    output_file = f"exoplanet_report_{int(time.time())}.pdf"
                elif not output_file.endswith('.pdf'):
                    output_file += '.pdf'
                
                ExoplanetDisplay.print_loading("Generating report")
                ExoplanetDisplay.generate_exoplanet_report(planets, report_title, output_file)
                
            elif choice == "4":
                break
                
            elif choice == "B" or choice.lower() == "b":
                break
            else:
                print(colored("Invalid choice. Please try again.", "red"))
                time.sleep(1)
    
    def explore_categories(self):
        """Explore special categories of exoplanets"""
        ExoplanetDisplay.clear_screen()
        ExoplanetDisplay.print_header("EXPLORE SPECIAL CATEGORIES", width=80)
        
        categories = {
            "1": "Planets in Habitable Zone",
            "2": "Earth-like Planets",
            "3": "Super-Earth Planets",
            "4": "Gas Giants",
            "5": "Nearby Planets (< 50 light years)",
            "6": "Recently Discovered Planets",
            "7": "Planets by Orbital Period",
            "8": "Browse Planet Categories",
            "B": "Back to Main Menu"
        }
        
        while True:
            print(colored("Select a category to explore:", "cyan"))
            choice = ExoplanetDisplay.print_menu(categories)
            
            if choice == "1":
                ExoplanetDisplay.print_loading("Finding habitable planets")
                planets = self.database.get_planets_in_habitable_zone()
                self.current_planets = planets
                ExoplanetDisplay.display_planet_summary(planets, "Planets in Habitable Zone")
                self.post_search_menu(planets)
                
            elif choice == "2":
                ExoplanetDisplay.print_loading("Finding Earth-like planets")
                planets = self.database.get_earthlike_planets()
                self.current_planets = planets
                ExoplanetDisplay.display_planet_summary(planets, "Earth-like Planets")
                self.post_search_menu(planets)
                
            elif choice == "3":
                ExoplanetDisplay.print_loading("Finding Super-Earth planets")
                planets = self.database.get_habitable_superearths()
                self.current_planets = planets
                ExoplanetDisplay.display_planet_summary(planets, "Habitable Super-Earth Planets")
                self.post_search_menu(planets)
                
            elif choice == "4":
                ExoplanetDisplay.print_loading("Finding gas giants")
                planets = self.database.get_gas_giants()
                self.current_planets = planets
                ExoplanetDisplay.display_planet_summary(planets, "Gas Giant Planets")
                self.post_search_menu(planets)
                
            elif choice == "5":
                max_distance = 50
                try:
                    user_max = input(colored(f"Enter maximum distance in light years (default: {max_distance}): ", "yellow"))
                    if user_max:
                        max_distance = float(user_max)
                except ValueError:
                    print(colored("Using default distance of 50 light years.", "yellow"))
                    time.sleep(1)
                
                ExoplanetDisplay.print_loading("Finding nearby planets")
                planets = self.database.get_nearby_planets(max_distance)
                self.current_planets = planets
                ExoplanetDisplay.display_planet_summary(planets, f"Nearby Planets (< {max_distance} light years)")
                self.post_search_menu(planets)
                
            elif choice == "6":
                years = 10
                try:
                    user_years = input(colored(f"Enter number of years to look back (default: {years}): ", "yellow"))
                    if user_years:
                        years = int(user_years)
                except ValueError:
                    print(colored(f"Using default of {years} years.", "yellow"))
                    time.sleep(1)
                
                ExoplanetDisplay.print_loading("Finding recent discoveries")
                planets = self.database.get_recently_discovered_planets(years)
                self.current_planets = planets
                ExoplanetDisplay.display_planet_summary(planets, f"Planets Discovered in the Last {years} Years")
                self.post_search_menu(planets)
                
            elif choice == "7":
                try:
                    min_days = float(input(colored("Enter minimum orbital period in days: ", "yellow")) or 0)
                    max_days = float(input(colored("Enter maximum orbital period in days: ", "yellow")) or 100000)
                    
                    ExoplanetDisplay.print_loading("Finding planets")
                    planets = self.database.get_planets_by_orbital_period(min_days, max_days)
                    self.current_planets = planets
                    ExoplanetDisplay.display_planet_summary(planets, f"Planets with orbital period between {min_days} and {max_days} days")
                    self.post_search_menu(planets)
                    
                except ValueError:
                    print(colored("Please enter valid orbital period values.", "red"))
                    time.sleep(1.5)
                    
            elif choice == "8":
                self.browse_categories()
                
            elif choice == "B" or choice.lower() == "b":
                break
            else:
                print(colored("Invalid choice. Please try again.", "red"))
                time.sleep(1)
    
    def browse_categories(self):
        """Browse detailed categories of planets"""
        ExoplanetDisplay.clear_screen()
        ExoplanetDisplay.print_header("BROWSE PLANET CATEGORIES", width=80)
        
        # Get categories from database
        categories = self.database.get_planet_categories()
        
        # Category options
        options = {
            "1": "Browse by Planet Type",
            "2": "Browse by Star Type",
            "3": "Browse by Discovery Method",
            "4": "Browse by Discovery Year Range",
            "B": "Back to Categories Menu"
        }
        
        while True:
            print(colored("Select a category to browse:", "cyan"))
            choice = ExoplanetDisplay.print_menu(options)
            
            if choice == "1":
                ExoplanetDisplay.print_subheader("PLANET TYPES", width=80)
                
                # Create menu of planet types
                type_menu = {}
                for i, planet_type in enumerate(categories['planet_types'], 1):
                    type_menu[str(i)] = planet_type
                type_menu["B"] = "Back"
                
                print(colored("Select a planet type to view:", "cyan"))
                type_choice = ExoplanetDisplay.print_menu(type_menu)
                
                if type_choice in type_menu and type_choice != "B":
                    selected_type = type_menu[type_choice]
                    ExoplanetDisplay.print_loading(f"Finding {selected_type} planets")
                    planets = self.database.get_planets_by_type(selected_type)
                    self.current_planets = planets
                    ExoplanetDisplay.display_planet_summary(planets, f"{selected_type} Planets")
                    self.post_search_menu(planets)
                elif type_choice.lower() != "b":
                    print(colored("Invalid choice. Please try again.", "red"))
                    time.sleep(1)
                    
            elif choice == "2":
                ExoplanetDisplay.print_subheader("STAR TYPES", width=80)
                
                # Create menu of star types
                type_menu = {}
                for i, star_type in enumerate(categories['star_types'], 1):
                    type_menu[str(i)] = star_type
                type_menu["B"] = "Back"
                
                print(colored("Select a star type to view planets for:", "cyan"))
                type_choice = ExoplanetDisplay.print_menu(type_menu)
                
                if type_choice in type_menu and type_choice != "B":
                    selected_type = type_menu[type_choice]
                    ExoplanetDisplay.print_loading(f"Finding planets orbiting {selected_type} stars")
                    planets = self.database.search_planets(selected_type, "star_type")
                    self.current_planets = planets
                    ExoplanetDisplay.display_planet_summary(planets, f"Planets Orbiting {selected_type} Stars")
                    self.post_search_menu(planets)
                elif type_choice.lower() != "b":
                    print(colored("Invalid choice. Please try again.", "red"))
                    time.sleep(1)
                    
            elif choice == "3":
                ExoplanetDisplay.print_subheader("DISCOVERY METHODS", width=80)
                
                # Create menu of discovery methods
                method_menu = {}
                for i, method in enumerate(categories['discovery_methods'], 1):
                    method_menu[str(i)] = method
                method_menu["B"] = "Back"
                
                print(colored("Select a discovery method to view planets for:", "cyan"))
                method_choice = ExoplanetDisplay.print_menu(method_menu)
                
                if method_choice in method_menu and method_choice != "B":
                    selected_method = method_menu[method_choice]
                    ExoplanetDisplay.print_loading(f"Finding planets discovered by {selected_method}")
                    planets = self.database.get_planets_by_discovery_method(selected_method)
                    self.current_planets = planets
                    ExoplanetDisplay.display_planet_summary(planets, f"Planets Discovered by {selected_method}")
                    self.post_search_menu(planets)
                elif method_choice.lower() != "b":
                    print(colored("Invalid choice. Please try again.", "red"))
                    time.sleep(1)
                    
            elif choice == "4":
                ExoplanetDisplay.print_subheader("DISCOVERY YEAR RANGE", width=80)
                
                min_year = categories['discovery_years']['min']
                max_year = categories['discovery_years']['max']
                
                print(f"Available years range from {min_year} to {max_year}")
                
                try:
                    start_year = int(input(colored("Enter start year: ", "yellow")) or min_year)
                    end_year = int(input(colored("Enter end year: ", "yellow")) or max_year)
                    
                    if start_year > end_year:
                        start_year, end_year = end_year, start_year
                    
                    ExoplanetDisplay.print_loading(f"Finding planets discovered between {start_year} and {end_year}")
                    planets = self.database.get_planets_by_year_range(start_year, end_year)
                    self.current_planets = planets
                    ExoplanetDisplay.display_planet_summary(planets, f"Planets Discovered Between {start_year} and {end_year}")
                    self.post_search_menu(planets)
                    
                except ValueError:
                    print(colored("Please enter valid years.", "red"))
                    time.sleep(1.5)
                    
            elif choice == "B" or choice.lower() == "b":
                break
            else:
                print(colored("Invalid choice. Please try again.", "red"))
                time.sleep(1)
    
    
       
    
    def generate_reports(self):
        """Generate comprehensive reports about exoplanets"""
        ExoplanetDisplay.clear_screen()
        ExoplanetDisplay.print_header("GENERATE EXOPLANET REPORTS", width=80)
        
        report_options = {
            "1": "Report on All Planets (Limited to 100 for performance)",
            "2": "Report on Habitable Zone Planets",
            "3": "Report on Earth-like Planets",
            "4": "Report on Nearby Planets",
            "5": "Custom Report (Based on Search)",
            "6": "Report on Current Selection",
            "B": "Back to Main Menu"
        }
        
        while True:
            print(colored("Select report type to generate:", "cyan"))
            choice = ExoplanetDisplay.print_menu(report_options)
            
            if choice == "1":
                
                 ExoplanetDisplay.print_loading("Gathering data")
    
   
                 print(colored("Enter limit (default: 100): ", "cyan"), end="")
                 user_input = input().strip()
    
                 if user_input.isdigit():
                     limit = int(user_input)
                 else:
                       print(colored("⚠️  Invalid input - using default limit of 100", "red"))
                       limit = 100
    
                 planets = self.database.get_all_planets(limit=limit)
                 report_title = "Comprehensive Exoplanet Analysis"
                 output_file = f"exoplanet_all_report_{int(time.time())}.pdf"
    
                 print(colored(f"✅ Processing {limit} planets...", "green"))
                 ExoplanetDisplay.generate_exoplanet_report(planets, report_title, output_file)
                
            elif choice == "2":
                ExoplanetDisplay.print_loading("Finding habitable planets")
                planets = self.database.get_planets_in_habitable_zone()
                report_title = "Habitable Zone Exoplanets Analysis"
                output_file = f"exoplanet_habitable_report_{int(time.time())}.pdf"
                ExoplanetDisplay.generate_exoplanet_report(planets, report_title, output_file)
                
            elif choice == "3":
                ExoplanetDisplay.print_loading("Finding Earth-like planets")
                planets = self.database.get_earthlike_planets()
                report_title = "Earth-like Exoplanets Analysis"
                output_file = f"exoplanet_earthlike_report_{int(time.time())}.pdf"
                ExoplanetDisplay.generate_exoplanet_report(planets, report_title, output_file)
                
            elif choice == "4":
                max_distance = 50
                try:
                    user_max = input(colored(f"Enter maximum distance in light years (default: {max_distance}): ", "yellow"))
                    if user_max:
                        max_distance = float(user_max)
                except ValueError:
                    print(colored("Using default distance of 50 light years.", "yellow"))
                    time.sleep(1)
                
                ExoplanetDisplay.print_loading("Finding nearby planets")
                planets = self.database.get_nearby_planets(max_distance)
                report_title = f"Nearby Exoplanets (< {max_distance} ly) Analysis"
                output_file = f"exoplanet_nearby_report_{int(time.time())}.pdf"
                ExoplanetDisplay.generate_exoplanet_report(planets, report_title, output_file)
                
            elif choice == "5":
                # First perform a search
                ExoplanetDisplay.clear_screen()
                ExoplanetDisplay.print_header("SEARCH FOR REPORT", width=80)
                
                # Use search functionality from search_planets method
                self.search_planets()
                
                # Check if we got any results
                if self.current_planets:
                    print(colored("\nGenerate report from these search results?", "cyan"))
                    confirm = input(colored("Enter Y to generate report, any other key to cancel: ", "yellow")).upper()
                    
                    if confirm == "Y":
                        report_title = input(colored("Enter report title: ", "yellow")) or "Custom Exoplanet Search Report"
                        output_file = input(colored("Enter output filename (or press Enter for default): ", "yellow"))
                        if not output_file:
                            output_file = f"exoplanet_custom_report_{int(time.time())}.pdf"
                        elif not output_file.endswith('.pdf'):
                            output_file += '.pdf'
                        
                        ExoplanetDisplay.print_loading("Generating report")
                        ExoplanetDisplay.generate_exoplanet_report(self.current_planets, report_title, output_file)
                
            elif choice == "6":
                if not self.current_planets:
                    print(colored("No planets currently selected. Please browse or search for planets first.", "yellow"))
                    time.sleep(1.5)
                else:
                    report_title = input(colored("Enter report title: ", "yellow")) or "Selected Exoplanets Report"
                    output_file = input(colored("Enter output filename (or press Enter for default): ", "yellow"))
                    if not output_file:
                        output_file = f"exoplanet_selection_report_{int(time.time())}.pdf"
                    elif not output_file.endswith('.pdf'):
                        output_file += '.pdf'
                    
                    ExoplanetDisplay.print_loading("Generating report")
                    ExoplanetDisplay.generate_exoplanet_report(self.current_planets, report_title, output_file)
                    
            elif choice == "B" or choice.lower() == "b":
                break
            else:
                print(colored("Invalid choice. Please try again.", "red"))
                time.sleep(1)
    
    def random_planet(self):
        """Explore a random planet from the database"""
        ExoplanetDisplay.clear_screen()
        ExoplanetDisplay.print_header("RANDOM PLANET EXPLORER", width=80)
        
        # Get random planet
        ExoplanetDisplay.print_loading("Finding a random planet")
        planet = self.database.get_random_planet()
        
        if planet:
            self.current_planets = [planet]
            
            # Display quick card view
            ExoplanetDisplay.display_planet_card(planet)
            
            # Options
            options = {
                "1": "View Detailed Information",
                "2": "Get Another Random Planet",
                "3": "Compare with Another Random Planet",
                "B": "Back to Main Menu"
            }
            
            while True:
                print(colored("\nWhat would you like to do with this planet?", "cyan"))
                choice = ExoplanetDisplay.print_menu(options)
                
                if choice == "1":
                    ExoplanetDisplay.display_planet_details(planet)
                    
                elif choice == "2":
                    ExoplanetDisplay.print_loading("Finding a new random planet")
                    planet = self.database.get_random_planet()
                    self.current_planets = [planet]
                    ExoplanetDisplay.display_planet_card(planet)
                    
                elif choice == "3":
                    ExoplanetDisplay.print_loading("Finding a second random planet")
                    second_planet = self.database.get_random_planet()
                    
                    # Ensure we don't get the same planet twice
                    while second_planet.get('planet_name') == planet.get('planet_name'):
                        second_planet = self.database.get_random_planet()
                        
                    self.current_planets = [planet, second_planet]
                    
                    # Display two planets for comparison
                    ExoplanetDisplay.compare_planets([planet, second_planet], "basic")
                    
                    # After comparison, ask if user wants to view details of either
                    print(colored("\nOptions:", "cyan"))
                    detail_options = {
                        "1": f"View details of {planet.get('planet_name')}",
                        "2": f"View details of {second_planet.get('planet_name')}",
                        "3": "Compare with different criteria",
                        "4": "Get two new random planets",
                        "B": "Back to random planet menu"
                    }
                    
                    detail_choice = ExoplanetDisplay.print_menu(detail_options)
                    
                    if detail_choice == "1":
                        ExoplanetDisplay.display_planet_details(planet)
                    elif detail_choice == "2":
                        ExoplanetDisplay.display_planet_details(second_planet)
                    elif detail_choice == "3":
                        ExoplanetDisplay.compare_planets([planet, second_planet], "menu")
                    elif detail_choice == "4":
                        ExoplanetDisplay.print_loading("Finding new random planets")
                        planet = self.database.get_random_planet()
                        second_planet = self.database.get_random_planet()
                        
                        # Ensure we don't get the same planet twice
                        while second_planet.get('planet_name') == planet.get('planet_name'):
                            second_planet = self.database.get_random_planet()
                            
                        self.current_planets = [planet, second_planet]
                        ExoplanetDisplay.compare_planets([planet, second_planet], "basic")
                    
                elif choice == "B" or choice.lower() == "b":
                    break
                else:
                    print(colored("Invalid choice. Please try again.", "red"))
                    time.sleep(1)
        else:
            print(colored("Could not retrieve a random planet. Database may be empty.", "red"))
            time.sleep(2)
    
    def exit_program(self):
        """Exit the program gracefully"""
        ExoplanetDisplay.clear_screen()
        print(colored("\nThank you for using the Exoplanet Explorer!", "cyan", attrs=["bold"]))
        print("Have a great day and keep exploring the cosmos!")
        time.sleep(1.5)


def setup_command_line():
    """Setup command line arguments parser"""
    parser = argparse.ArgumentParser(description='Exoplanet Database Explorer')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--user', default='root', help='Database user')
    parser.add_argument('--password', default='<password>', help='Database password')
    parser.add_argument('--database', default='exo', help='Database name')
    parser.add_argument('--quick', action='store_true', help='Skip welcome screen')
    
    return parser.parse_args()


def main():
    """Main entry point for the application"""
    # Parse command line arguments
    args = setup_command_line()
    
    try:
        # Initialize explorer with database connection
        explorer = ExoplanetExplorer()
        
        # Show welcome screen (unless --quick specified)
        if not args.quick:
            explorer.display_welcome()
        
        # Start main menu
        explorer.main_menu()
        
    except KeyboardInterrupt:
        print(colored("\n\nProgram terminated by user.", "yellow"))
    except Exception as e:
        print(colored(f"\n\nAn error occurred: {e}", "red"))
        print("Please check your database connection and try again.")
    finally:
        print("\nExiting Exoplanet Explorer. Goodbye!")


if __name__ == "__main__":
    main()
