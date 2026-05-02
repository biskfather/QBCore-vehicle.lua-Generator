import os

# QBCore Vehicle Config Generator
#
# INSTRUCTIONS:
# 1. When running the script, you will be prompted to enter the path 
#    to your vehicle pack folder (e.g., 'resources/[vehicles]/mypack').
# 2. The script will now search inside each subfolder for 'handling.meta'.
# 3. The official spawn code is extracted from the <handlingName> tag in the meta file.
# 4. You will be prompted to enter default values for the batch (price, category, brand, type).
# 5. The final Lua code is saved to 'new_vehicles.lua' in the same directory as this script.

# Default shop name for general vehicles. Change this if needed.
DEFAULT_SHOP = 'pdm' 

def extract_model_from_handling_meta(file_path):
    """
    Reads handling.meta and extracts the spawn code (handlingName).
    Uses simple string parsing for maximum compatibility.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Look for the common <handlingName> tag
            start_tag = '<handlingName>'
            end_tag = '</handlingName>'
            
            # Simple string search
            if start_tag in content and end_tag in content:
                start_index = content.find(start_tag) + len(start_tag)
                end_index = content.find(end_tag, start_index)
                
                if start_index < end_index:
                    model_name = content[start_index:end_index].strip()
                    return model_name
    except Exception as e:
        print(f"Warning: Could not read or parse {file_path}. Error: {e}")
        return None
    return None


def scan_directory_for_models(directory):
    """
    Scans the given directory and returns a list of tuples: 
    (spawn_code, folder_name).
    """
    model_data = []
    
    # Check if the directory exists
    if not os.path.isdir(directory):
        print(f"Error: Directory not found at '{directory}'")
        return None

    # Get all immediate subdirectories
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            folder_name = item # Used for display name basis
            
            # 1. Check for handling.meta directly in the folder
            meta_path = os.path.join(item_path, 'handling.meta')
            if not os.path.exists(meta_path):
                # 2. Check for handling.meta in a common 'data' subfolder
                meta_path = os.path.join(item_path, 'data', 'handling.meta')

            spawn_code = None
            if os.path.exists(meta_path):
                spawn_code = extract_model_from_handling_meta(meta_path)
                
            if spawn_code and spawn_code.strip() != "":
                # Store the extracted spawn code and the original folder name (for display name generation)
                model_data.append((spawn_code, folder_name))
            else:
                print(f"Warning: Could not find handling.meta or extract spawn code for '{folder_name}'. Skipping.")

    return model_data

def generate_lua_config(models_data, category, price, prefix="", brand="", type=""):
    """
    Generates the Lua table structure for QBCore vehicles using the extracted model data
    in the new array format: { model=..., name=..., brand=..., price=..., etc. }
    """
    lua_output = "local vehicles = {\n"

    for spawn_code, folder_name in models_data:
        # The key in the vehicles table MUST be the spawn code (lowercase)
        model = spawn_code.lower().strip() 
        
        # Create a display name based on the folder name (more readable than spawn code)
        display_name = f"{prefix} {folder_name.replace('_', ' ').title()}".strip()
        display_name = display_name.replace("'", "\\'") # Escape single quotes in name
        safe_brand = brand.replace("'", "\\'") # Escape single quotes in brand

        # NEW ARRAY-BASED FORMAT
        entry = "    {\n"
        entry += f"        model = '{model}',\n"
        entry += f"        name = '{display_name}',\n"
        entry += f"        brand = '{safe_brand}',\n"
        entry += f"        price = {price},\n"
        entry += f"        category = '{category}',\n"
        entry += f"        type = '{type}',\n"
        entry += f"        shop = '{DEFAULT_SHOP}'\n"
        entry += "    },\n"
        
        lua_output += entry

    lua_output += "}\n\n"
    lua_output += "return vehicles"
    return lua_output

if __name__ == "__main__":
    
    # 1. Get the directory path from the user
    print("--- QBCore Vehicle Config Generator (Handling.meta Lookup) ---")
    folder_path = input("Enter the path to the vehicle pack folder (e.g., C:\\FiveM\\resources\\vehicles\\mycars): ").strip()
    print(f"Searching directory: {folder_path}") # Log the entered path for debugging

    model_list = scan_directory_for_models(folder_path)
    
    if not model_list:
        # IMPROVED EXIT MESSAGE FOR DEBUGGING
        print("\n❌ FAILED: No valid vehicle model folders found.")
        print("Please check the following:")
        print("1. The path you entered is correct and exists.")
        print("2. The folder contains subfolders (one for each vehicle, e.g., 'car_a', 'car_b').")
        print("3. Each vehicle subfolder contains a 'handling.meta' file (or one in a 'data' subfolder).")
        print("Exiting.")
    else:
        print(f"\nFound {len(model_list)} valid vehicle models with handling data.")
        
        # 2. Get default configuration values (UPDATED for new QBCore format)
        default_price = input("Enter the default price for ALL these vehicles (e.g., 50000): ").strip()
        default_category = input("Enter the default category (e.g., 'sports', 'coupes', 'emergency'): ").strip()
        display_prefix = input("Enter a display name prefix (e.g., 'Custom' or leave blank): ").strip()
        
        # NEW REQUIRED FIELDS
        default_brand = input("Enter the default brand (e.g., 'Custom Motors'): ").strip()
        default_type = input("Enter the default vehicle type (e.g., 'automobile', 'motorcycle'): ").strip()
        
        try:
            default_price = int(default_price)
        except ValueError:
            print("Invalid price entered. Defaulting price to 10000.")
            default_price = 10000
        
        # 3. Generate the Lua config
        generated_lua = generate_lua_config(
            models_data=model_list,
            category=default_category,
            price=default_price,
            prefix=display_prefix,
            brand=default_brand,
            type=default_type
        )
        
        # --- WRITE OUTPUT TO FILE ---
        output_filename = 'new_vehicles.lua'
        # Get the absolute path to show the user exactly where the file is being saved
        output_filepath = os.path.abspath(output_filename) 
        
        try:
            with open(output_filename, 'w') as f:
                f.write(generated_lua)
            
            print(f"\n✅ SUCCESS: Generated configuration for {len(model_list)} vehicles.")
            print(f"The Lua code has been saved to: {output_filepath}") # <-- Display the absolute path
            print("\n(You can now copy the content of 'new_vehicles.lua' into your server's qb-core/shared/vehicles.lua file.)")

        except Exception as e:
            print(f"\n❌ ERROR: Failed to write to file '{output_filename}'.")
            print(f"Please check your folder permissions. Error details: {e}")
            print("\n--- BEGIN Console Output (Fallback) ---")
            print(generated_lua)
            print("--- END Console Output (Fallback) ---")

    # FIX: Pause execution so the window doesn't close immediately if double-clicked
    input("\nPress Enter to exit...")
