"""
NASA Exoplanet Data Processor

This script reads a NASA CSV file containing exoplanet data,
processes it to create a human-friendly dataset, and stores
the results in a MySQL database.
"""

import pandas as pd
import pymysql
import numpy as np
import os
from tqdm import tqdm  # For progress bar

# Constants for Earth values and habitable zone calculations
EARTH_RADIUS = 1.0  # in Earth radii
EARTH_MASS = 1.0  # in Earth masses
PARSEC_TO_LIGHT_YEAR = 3.26  # 1 parsec = 3.26 light-years

# Habitable zone parameters (simplified)
# These are approximate values for the habitable zone based on star temperature
# Values in Kelvin
TEMP_RANGES = {
    'too_hot': 7000,  # Above this, likely too hot
    'too_cold': 3500,  # Below this, likely too cold
}

def create_database_connection():
    """
    Create a connection to the MySQL database.
    Returns the connection and cursor objects.
    """
    try:
        # Replace these with your actual database connection details
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Sachchidanand@12',
            database='exoplanet_db'
        )
        cursor = connection.cursor()
        print("Database connection successful")
        return connection, cursor
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None, None

def create_table(cursor):
    """
    Create the simplified_planet_data table if it doesn't exist.
    """
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS simplified_planet_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            planet_name VARCHAR(255),
            radius_earth_units FLOAT,
            mass_earth_units FLOAT,
            distance_light_years FLOAT,
            habitable VARCHAR(3),
            discovery_method VARCHAR(255),
            UNIQUE (planet_name)
        );
        """
        cursor.execute(create_table_query)
        print("Table created or already exists")
    except Exception as e:
        print(f"Error creating table: {e}")

def parallax_to_light_years(plx):
    """
    Convert parallax (in milliarcseconds) to light-years.
    
    Formula: distance_in_parsecs = 1000 / plx
    Then convert parsecs to light-years: parsecs * 3.26
    """
    if pd.isna(plx) or plx <= 0:
        return np.nan
    
    # Convert from milliarcseconds to parsecs, then to light-years
    try:
        parsecs = 1000 / plx
        light_years = parsecs * PARSEC_TO_LIGHT_YEAR
        return light_years
    except:
        return np.nan

def is_habitable(star_temp, semi_major_axis, star_radius):
    """
    Determine if a planet is in the habitable zone based on star temperature 
    and distance from the star.
    
    This is a simplified model. Real habitability depends on many more factors.
    """
    try:
        # If we don't have the necessary data, return "N/A"
        if pd.isna(star_temp) or pd.isna(semi_major_axis):
            return "N/A"
        
        # Very simple habitability check based on star temperature
        if star_temp > TEMP_RANGES['too_hot']:
            return "No"  # Star too hot
        elif star_temp < TEMP_RANGES['too_cold']:
            return "No"  # Star too cold
        
        # For stars in the right temperature range, check if the planet is at
        # a reasonable distance (simplified calculation)
        
        # If we have the star's radius, use it for a more accurate estimate
        if not pd.isna(star_radius) and star_radius > 0:
            # Very simplified habitable zone calculation
            # For a Sun-like star, habitable zone is roughly 0.9-1.4 AU
            # Scale based on star temperature compared to Sun (~5700K)
            temp_factor = (star_temp / 5700.0) ** 2
            inner_bound = 0.9 * temp_factor
            outer_bound = 1.4 * temp_factor
            
            if inner_bound <= semi_major_axis <= outer_bound:
                return "Yes"
            else:
                return "No"
        
        # If we don't have star radius, use a very simplified check
        # that planets between 0.7-1.5 AU from a suitable temperature star might be habitable
        elif 0.7 <= semi_major_axis <= 1.5:
            return "Yes"
        else:
            return "No"
            
    except Exception as e:
        print(f"Error in habitability calculation: {e}")
        return "N/A"

def process_planet_data(csv_file_path):
    """
    Process the NASA exoplanet data from a CSV file.
    Returns a simplified DataFrame with calculated values.
    """
    try:
        print(f"Reading CSV file: {csv_file_path}")
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        print(f"Total planets in dataset: {len(df)}")
        
        # Display the column names to help with debugging
        print("Columns in the dataset:")
        print(df.columns.tolist())
        
        # Create a new DataFrame for simplified data
        simplified_df = pd.DataFrame()
        
        # Extract planet names (assuming 'pl_name' is the planet name column)
        # Adjust column names based on actual CSV structure
        planet_name_col = 'pl_name' if 'pl_name' in df.columns else None
        radius_col = 'pl_rade' if 'pl_rade' in df.columns else None  # Planet radius in Earth radii
        mass_col = 'pl_bmasse' if 'pl_bmasse' in df.columns else None  # Planet mass in Earth masses
        parallax_col = 'st_plx' if 'st_plx' in df.columns else None  # Parallax in milliarcseconds
        star_temp_col = 'st_teff' if 'st_teff' in df.columns else None  # Star effective temperature
        semi_major_col = 'pl_orbsmax' if 'pl_orbsmax' in df.columns else None  # Semi-major axis in AU
        discovery_method_col = 'pl_discmethod' if 'pl_discmethod' in df.columns else None
        star_radius_col = 'st_rad' if 'st_rad' in df.columns else None  # Star radius in solar radii
        
        # Check if all required columns are present
        if not planet_name_col:
            print("Error: Planet name column not found")
            return None
        
        # Copy the planet names
        simplified_df['planet_name'] = df[planet_name_col]
        
        # Calculate radius in Earth units (if available)
        if radius_col:
            simplified_df['radius_earth_units'] = df[radius_col]
        else:
            simplified_df['radius_earth_units'] = np.nan
            print("Warning: Planet radius column not found")
        
        # Calculate mass in Earth units (if available)
        if mass_col:
            simplified_df['mass_earth_units'] = df[mass_col]
        else:
            simplified_df['mass_earth_units'] = np.nan
            print("Warning: Planet mass column not found")
        
        # Calculate distance in light-years (if parallax is available)
        if parallax_col:
            simplified_df['distance_light_years'] = df[parallax_col].apply(parallax_to_light_years)
        else:
            simplified_df['distance_light_years'] = np.nan
            print("Warning: Parallax column not found")
        
        # Determine if the planet is in the habitable zone
        if star_temp_col and semi_major_col:
            print("Calculating habitability...")
            # Apply the habitability calculation to each row
            simplified_df['habitable'] = df.apply(
                lambda row: is_habitable(
                    row[star_temp_col] if not pd.isna(row[star_temp_col]) else np.nan,
                    row[semi_major_col] if not pd.isna(row[semi_major_col]) else np.nan,
                    row[star_radius_col] if star_radius_col and not pd.isna(row[star_radius_col]) else np.nan
                ),
                axis=1
            )
        else:
            simplified_df['habitable'] = "N/A"
            print("Warning: Star temperature or semi-major axis columns not found")
        
        # Copy the discovery method
        if discovery_method_col:
            simplified_df['discovery_method'] = df[discovery_method_col]
        else:
            simplified_df['discovery_method'] = "Unknown"
            print("Warning: Discovery method column not found")
        
        return simplified_df
    
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def insert_data_into_database(connection, cursor, df):
    """
    Insert the processed data into the MySQL database.
    """
    try:
        print("Inserting data into the database...")
        # Use a progress bar to show insertion progress
        for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            # Prepare the INSERT query
            insert_query = """
            INSERT IGNORE INTO simplified_planet_data 
            (planet_name, radius_earth_units, mass_earth_units, 
             distance_light_years, habitable, discovery_method)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Replace NaN values with None for database insertion
            values = (
                row['planet_name'],
                row['radius_earth_units'] if not pd.isna(row['radius_earth_units']) else None,
                row['mass_earth_units'] if not pd.isna(row['mass_earth_units']) else None,
                row['distance_light_years'] if not pd.isna(row['distance_light_years']) else None,
                row['habitable'],
                row['discovery_method']
            )
            
            # Execute the query
            cursor.execute(insert_query, values)
        
        # Commit the changes
        connection.commit()
        print(f"Successfully inserted {df.shape[0]} records into the database")
    
    except Exception as e:
        print(f"Error inserting data: {e}")
        connection.rollback()

def main():
    """
    Main function to run the entire process.
    """
    try:
        # File path of the CSV file
        csv_file_path = './data.csv'  # Update with your file path
        
        # Process the data
        simplified_df = process_planet_data(csv_file_path)
        
        if simplified_df is not None:
            # Create a connection to the database
            connection, cursor = create_database_connection()
            
            if connection and cursor:
                # Create the table if it doesn't exist
                create_table(cursor)
                
                # Insert the data into the database
                insert_data_into_database(connection, cursor, simplified_df)
                
                # Close the database connection
                connection.close()
                print("Database connection closed")
            
            # Save the simplified data to a CSV file as a backup
            simplified_df.to_csv('simplified_exoplanet_data.csv', index=False)
            print("Simplified data saved to 'simplified_exoplanet_data.csv'")
            
            # Display summary information
            print("\nSummary:")
            print(f"Total planets processed: {len(simplified_df)}")
            habitable_count = len(simplified_df[simplified_df['habitable'] == 'Yes'])
            print(f"Potentially habitable planets: {habitable_count}")
            print(f"Unknown habitability: {len(simplified_df[simplified_df['habitable'] == 'N/A'])}")
            
            # Display methods of discovery
            print("\nDiscovery methods distribution:")
            method_counts = simplified_df['discovery_method'].value_counts()
            for method, count in method_counts.items():
                print(f"  {method}: {count}")
    
    except Exception as e:
        print(f"An error occurred in the main function: {e}")

if __name__ == "__main__":
    main()