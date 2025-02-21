# import os

# # Directory containing the files
# input_directory = 'routes'  # Replace with your directory path
# output_file = 'combined_errors.log'  # Output file name

# # Define the keyword to search for
# keyword = 'info'

# # Open the output file in write mode
# with open(output_file, 'w') as outfile:
#     # Loop through all files in the directory
#     for filename in os.listdir(input_directory):
#         # Construct the full file path
#         file_path = os.path.join(input_directory, filename)
        
#         # Check if it's a file (not a directory)
#         if os.path.isfile(file_path):
#             print(f"Processing file: {filename}")
            
#             # Open and read the file
#             with open(file_path, 'r') as infile:
#                 # Read each line in the file
#                 for line in infile:
#                     # Check if the keyword is in the line
#                     if keyword in line:
#                         # Write the line to the output file
#                         outfile.write(line)

# print(f"All '{keyword}' messages have been written to {output_file}")