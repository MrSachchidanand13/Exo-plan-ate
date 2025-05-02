import pymysql
import json

# Function to connect to MySQL and create the database/table
def setup_database():
    try:
        # Connect to MySQL server (default connection without selecting a database)
        connection = pymysql.connect(
            host="localhost",  # Replace with your MySQL host
            user="root",       # Replace with your MySQL username
            password="<password>",  # Replace with your MySQL password
            cursorclass=pymysql.cursors.DictCursor  # Optional: Use dictionary-style cursors
        )
        cursor = connection.cursor()

        # Create the 'exo' database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS exo;")
        cursor.execute("USE exo;")

        # Drop the 'exo_planets' table if it exists
        cursor.execute("DROP TABLE IF EXISTS exo_planets;")

        # Create the 'exo_planets' table with all fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exo_planets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                planet_name VARCHAR(255) NOT NULL,
                host_star VARCHAR(255),
                discovery_method VARCHAR(255),
                discovery_year INT,
                distance_value FLOAT,
                distance_unit VARCHAR(50),
                habitable_zone_distance FLOAT,
                inner_habitable_boundary FLOAT,
                outer_habitable_boundary FLOAT,
                actual_distance FLOAT,
                assessment TEXT,
                planet_type TEXT,
                earth_mass_ratio FLOAT,
                earth_radius_ratio FLOAT,
                earth_gravity_ratio FLOAT,
                orbital_period_days FLOAT,
                star_temperature FLOAT,
                star_type TEXT,
                size_answer TEXT,
                mass_answer TEXT,
                gravity_answer TEXT,
                year_length_answer TEXT,
                star_type_answer TEXT
            );
        """)

        print("Database and table created successfully.")
        return connection, cursor

    except pymysql.Error as err:
        print(f"Error setting up database: {err}")
        return None, None

# Function to insert data into the 'exo_planets' table
def insert_data(cursor, connection, planets):
    for i, planet in enumerate(planets):
        print(f"\nProcessing planet {i + 1}: {planet.get('planet_name')}")

        # Parse layman_explanation for detailed data
        layman = planet.get("layman_explanation", {})
        distance = layman.get("distance", {})
        habitability = layman.get("habitability", {})
        planet_type = layman.get("planet_type", {})
        size = layman.get("size", {})
        mass = layman.get("mass", {})
        gravity = layman.get("gravity", {})
        year_length = layman.get("year_length", {})
        star_type = layman.get("star_type", {})

        # Debug extracted data
        print("Extracted data:")
        print(f"  planet_name: {planet.get('planet_name')}")
        print(f"  host_star: {planet.get('host_star')}")
        print(f"  discovery_method: {planet.get('discovery_method')}")
        print(f"  discovery_year: {planet.get('discovery_year')}")
        print(f"  distance_value: {distance.get('value')}")
        print(f"  habitable_zone_distance: {habitability.get('habitable_zone_distance')}")
        print(f"  earth_mass_ratio: {mass.get('earth_mass_ratio')}")
        print(f"  orbital_period_days: {year_length.get('orbital_period_days')}")
        print(f"  star_temperature: {star_type.get('star_temperature')}")

        # Insert all data into the 'exo_planets' table
        try:
            cursor.execute("""
                INSERT INTO exo_planets (
                    planet_name, host_star, discovery_method, discovery_year,
                    distance_value, distance_unit, habitable_zone_distance,
                    inner_habitable_boundary, outer_habitable_boundary, actual_distance,
                    assessment, planet_type, earth_mass_ratio, earth_radius_ratio,
                    earth_gravity_ratio, orbital_period_days, star_temperature,
                    star_type, size_answer, mass_answer, gravity_answer,
                    year_length_answer, star_type_answer
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                planet.get("planet_name"),
                planet.get("host_star"),
                planet.get("discovery_method"),
                planet.get("discovery_year"),
                distance.get("value"),
                distance.get("unit"),
                habitability.get("habitable_zone_distance"),
                habitability.get("inner_habitable_boundary"),
                habitability.get("outer_habitable_boundary"),
                habitability.get("actual_distance"),
                habitability.get("assessment"),
                planet_type.get("type"),
                mass.get("earth_mass_ratio"),
                size.get("earth_radius_ratio"),
                gravity.get("earth_gravity_ratio"),
                year_length.get("orbital_period_days"),
                star_type.get("star_temperature"),
                star_type.get("star_type"),
                size.get("answer"),
                mass.get("answer"),
                gravity.get("answer"),
                year_length.get("answer"),
                star_type.get("answer")
            ))
        except pymysql.Error as err:
            print(f"Error inserting data for planet {planet.get('planet_name')}: {err}")

    # Commit changes to the database
    connection.commit()
    print("Data insertion completed.")

# Main function to read JSON file and populate the database
def main():
    # Path to your JSON file
    json_file_path = "exoplanet_explanations.json"  # Replace with your JSON file path

    # Read the JSON file
    try:
        with open(json_file_path, "r") as file:
            planets = json.load(file)
            print(f"Loaded {len(planets)} planets from JSON file.")
            if len(planets) == 0:
                print("JSON file is empty or contains no data.")
                return
            print("First planet data:", planets[0])  # Print the first planet's data for debugging
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    # Setup the database and get connection/cursor
    connection, cursor = setup_database()

    if connection and cursor:
        # Insert data into the database
        insert_data(cursor, connection, planets)

        # Close the connection
        cursor.close()
        connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
