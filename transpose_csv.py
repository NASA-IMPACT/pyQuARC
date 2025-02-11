import csv
import sys

def transpose_csv(input_file: str, output_file: str):
    """
    Reads a CSV file, transposes its content (rows → columns), 
    and writes it to a new CSV file.
    """
    try:
        # Read the CSV file
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = list(csv.reader(infile))  # Convert to list for processing
        
        if not reader:
            print("Error: The input CSV file is empty.")
            return

        # Handle inconsistent row lengths by padding shorter rows
        max_cols = max(len(row) for row in reader)  # Find the longest row
        padded_reader = [row + [''] * (max_cols - len(row)) for row in reader]  # Pad shorter rows
        
        # Transpose the data (swap rows and columns)
        transposed_data = list(map(list, zip(*padded_reader)))  # Convert tuples to lists

        # Write the transposed data to a new CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(transposed_data)

        print(f"✅ Transposed data has been saved to '{output_file}'.")

    except FileNotFoundError:
        print(f"❌ Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

# Run the function if executed as a script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 transpose_csv.py <input_file> <output_file>")
    else:
        transpose_csv(sys.argv[1], sys.argv[2])


