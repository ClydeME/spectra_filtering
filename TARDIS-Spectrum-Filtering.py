import faulthandler
faulthandler.enable()


import os
import xml.etree.ElementTree as et
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import requests
import yaml
from astropy import units as u
from IPython.display import Image, display
from tardis import run_tardis

# Run the TARDIS Simulation
sim = run_tardis("../../tardis_example.yml",
                 virtual_packet_logging=True,
                 show_convergence_plots=False,
                 export_convergence_plots=False,
                 log_level="ERROR")

# Extract and Plot the Spectrum
spectrum = sim.spectrum_solver.spectrum_real_packets
spectrum_virtual = sim.spectrum_solver.spectrum_virtual_packets
spectrum_integrated = sim.spectrum_solver.spectrum_integrated

plt.figure()
plt.plot(spectrum.wavelength, spectrum.luminosity_density_lambda)
plt.plot(spectrum.wavelength, spectrum_virtual.luminosity_density_lambda)
plt.plot(spectrum.wavelength, spectrum_integrated.luminosity_density_lambda)
plt.xlabel("Wavelength (Angstrom)")
plt.ylabel("Luminosity Density (erg/s/Angstrom)")
plt.xlim(500, 12000)
plt.title("Unfiltered TARDIS Example Model Spectrum")

# Function to get Filter URL from TARDIS config file
def get_url_from_config(config_file_path):
    
    with open(config_file_path, 'r') as f:
        config = yaml.safe_load(f)
        telescope = config['filter']['Telescope_Name']
        instrument = config['filter']['Instrument']
        filter_id = config['filter']['Filter_ID']


    name = f"{telescope}/{instrument}.{filter_id}"
    safe_name = name.replace('/', '.')
    url = f"https://svo2.cab.inta-csic.es/theory/fps/fps.php?ID={name}"

    return url, safe_name

# Function to download the filter file
def download_filter(url, filename):
    req = requests.get(url, timeout = 10)

    with open((f'Filters/{filename}.xml'), 'wb') as f:
            
        # Chunking to avoid large memory consumption
        for chunk in req.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
        
        return filename
    
# Function to check if the filter file is valid
def check_filter(filter_name):
    
    root = et.parse(f"Filters/{filter_name}.xml")
    
    info = root.find('INFO')
    check = info.get('value')

    if check == 'ERROR':
        return False
    else:
        return True
    
# Main Execution

# Get URL and Filter Name from config file
url_and_name = get_url_from_config('filter_config.yml')
DownloadUrl = url_and_name[0]
FilterName = url_and_name[1]

# Download the filter file
chosen_filter = download_filter(DownloadUrl, FilterName)

# Check if the filter URL is valid. If not, remove the file and raise an error.
if check_filter(FilterName) == True:
    print("Filter URL is valid. Proceeding with filtering process.")
elif check_filter(FilterName) == False:
    print("Filter URL is not valid. Removing invalid filter file.")
    os.remove(f'Filters/{FilterName}.xml')
    raise ValueError("Invalid Filter URL. The filter file has been removed.")

# Function to get wavelength and transmission values from filter file
def get_filter(filter_name):
    
    # Parse XML File from Filters Directory 
    root = et.parse(f"Filters/{filter_name}.xml")
    
    # Get wavelength and transmission values in one array (Will be in aleternating order)
    all_vals = np.array([float(x.text) for x in root.findall('.//TD')])

    # Separate wavelength and transmission values
    wl = all_vals[0::2] * u.AA
    tr = all_vals[1::2]
    return wl, tr

# Function to interpolate filter to match TARDIS Spectrum
def interp_filter(spectrum_to_filter, filter_name):
    #Interpolate filter transmission values to match TARDIS Spectrum
    return np.interp(spectrum_to_filter, get_filter(filter_name)[0], get_filter(filter_name)[1])

def plot_filter(spectrum, chosen_filter):
    
    # Interpolate filter transmission values to match TARDIS Spectrum
    prepared_filter = interp_filter(spectrum.wavelength, chosen_filter)
    
    # Plot the filter transmission curve
    plt.figure()
    plt.plot(spectrum.wavelength, prepared_filter)
    plt.title("Filter Transmission Curve")
    plt.xlabel("Wavelength (Angstrom)")
    plt.ylabel("Transmission")
    plt.xlim(500, 12000)


def plot_filtered_spectrum(spectrum, spectrum_virtual, spectrum_integrated, chosen_filter):
    # Interpolate filter transmission values to match TARDIS Spectrum
    prepared_filter = interp_filter(spectrum.wavelength, chosen_filter)

    # Plot the filtered spectra
    plt.figure()
    plt.plot(spectrum.wavelength, spectrum.luminosity_density_lambda * prepared_filter)
    plt.plot(spectrum.wavelength, spectrum_virtual.luminosity_density_lambda * prepared_filter)
    plt.plot(spectrum.wavelength, spectrum_integrated.luminosity_density_lambda * prepared_filter)
    plt.xlabel("Wavelength (Angstrom)")
    plt.ylabel("Luminosity Density (erg/s/Angstrom)")
    plt.xlim(500, 12000)
    plt.title("Filtered TARDIS Example Model Spectrum")
    plt.show()

plot_filter(spectrum, chosen_filter)
plot_filtered_spectrum(spectrum, spectrum_virtual, spectrum_integrated, chosen_filter)