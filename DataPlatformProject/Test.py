# main.py

from Config_Manager import Config_Manager
from Import_Functions import Import_Functions
from Analysis_Functions import Analysis_Functions
from Data_Manipulation_Functions import Data_Manipulation_Functions
from Plotting_Functions import Plotting_Functions
import os
# ... etc.

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "Results")

def main():

    os.chdir(SCRIPT_DIR)

    config = Config_Manager("Test_config.yaml")
    importer = Import_Functions()
    analyzer = Analysis_Functions()
    manipulator = Data_Manipulation_Functions()
    plotter = Plotting_Functions()

    df_csv = importer.import_csv("synthetic_data.csv")

    print(df_csv.head())

    stats_df = analyzer.descriptive_statistics(df_csv, ['Voltage'])
    sampling_rate = config.get('analysis_functions.analyze_fft.sampling_rate')
    fft_results = analyzer.analyze_fft(df_csv, ['Voltage'], sampling_rate)

    plotter.plot_fft_spectrum(fft_results, save_path=os.path.join(OUT_DIR, 'Voltage_FFT.png'))

    # manipulator.export_csv(stats_df, os.path.join(OUT_DIR, 'Stats.csv'))

if __name__ == "__main__":
    main()
