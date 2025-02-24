import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

###############################################################################
# LOGGING SETUP
###############################################################################
logger = logging.getLogger(__name__ + "_plotting")
logger.setLevel(logging.DEBUG)  # Master log level: everything DEBUG+ is processed

# FORMATTERS
console_formatter = logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s - %(message)s")

# CONSOLE HANDLER (only shows INFO+ in console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# FILE HANDLER (writes DEBUG+ to file)
LOG_DIR = os.path.join(SCRIPT_DIR, "plotting_functions.log")
file_handler = logging.FileHandler(LOG_DIR, mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

# ADD HANDLERS TO LOGGER
logger.addHandler(console_handler)
logger.addHandler(file_handler)

###############################################################################
# PLOTTING_FUNCTIONS CLASS
###############################################################################
class Plotting_Functions:
    """
    A class to handle plotting and regression-related visualization needs
    (covering requirements #8 to #13).
    """

    def plot_histogram(
        self,
        df: pd.DataFrame,
        column: str,
        bins: int = 30,
        save_path: str = "histogram.png",
        title: str = "Histogram",
        xlabel: str = None,
        ylabel: str = "Frequency"
    ):
        """
        Generates and saves a figure for a histogram.

        WHAT IT IS:
            A way to visualize the distribution of data in a single column by
            counting the number of observations falling into discrete bins.

        WHAT IT'S GOOD FOR:
            - Quickly assessing the shape, central tendency, and spread of data.
            - Identifying skewness or outliers in large datasets.

        CAVEATS:
            - Bin size (the 'bins' parameter) can affect how the distribution looks.
            - Doesn't show the time order or correlation to other variables.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            column : str
                The column name for which to create the histogram.
            bins : int, default 30
                Number of bins in the histogram.
            save_path : str, default "histogram.png"
                File path where the histogram plot will be saved.
            title : str, default "Histogram"
                Plot title.
            xlabel : str, optional
                Label for the x-axis. If None, defaults to the column name.
            ylabel : str, default "Frequency"
                Label for the y-axis.

        RETURNS:
            None. The figure is saved to 'save_path'.
        """
        logger.debug("Starting plot_histogram for column '%s' with %d bins", column, bins)
        data = df[column].dropna()

        plt.figure(figsize=(8, 6))
        plt.hist(data, bins=bins, alpha=0.7, edgecolor='black')
        plt.title(title)
        plt.xlabel(xlabel if xlabel else column)
        plt.ylabel(ylabel)
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Histogram saved to '%s' for column '%s'.", save_path, column)

    def plot_scatter(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        save_path: str = "scatter.png",
        title: str = "Scatter Plot",
        xlabel: str = None,
        ylabel: str = None,
        regression_type: str = None
    ):
        """
        Generates and saves a figure for a scatter plot, optionally overlaying a regression curve.

        WHAT IT IS:
            A plot of data points in two dimensions (x vs. y).

        WHAT IT'S GOOD FOR:
            - Visualizing relationships or correlations between two numeric variables.
            - Spotting trends or clustering, especially when combined with regression lines.

        CAVEATS:
            - Large datasets might require strategies to reduce overplotting (e.g., transparency).
            - Scatter alone doesn't provide a measure of confidence or complexity of relationships.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            x_col : str
                The column name for the x-axis.
            y_col : str
                The column name for the y-axis.
            save_path : str, default "scatter.png"
                File path where the scatter plot will be saved.
            title : str, default "Scatter Plot"
                Plot title.
            xlabel : str, optional
                Label for the x-axis. If None, defaults to x_col.
            ylabel : str, optional
                Label for the y-axis. If None, defaults to y_col.
            regression_type : str, optional
                If provided, must be one of {"linear", "quadratic", "log"}.
                Adds a best-fit line/curve to the scatter plot and prints regression parameters.

        RETURNS:
            None. The figure is saved to 'save_path'.
        """
        logger.debug("Starting plot_scatter with x_col='%s', y_col='%s', regression='%s'",
                     x_col, y_col, regression_type)

        x_data = df[x_col].dropna().values
        y_data = df[y_col].dropna().values

        plt.figure(figsize=(8, 6))
        plt.scatter(x_data, y_data, alpha=0.7, edgecolor='black')
        plt.title(title)
        plt.xlabel(xlabel if xlabel else x_col)
        plt.ylabel(ylabel if ylabel else y_col)

        if regression_type is not None:
            if regression_type.lower() in ["linear", "quadratic", "log"]:
                fit_params = self.compute_regression_parameters(x_data, y_data, regression_type.lower())
                x_sorted = np.sort(x_data)

                if regression_type.lower() == "linear":
                    slope, intercept = fit_params["params"]
                    y_fit = slope * x_sorted + intercept
                elif regression_type.lower() == "quadratic":
                    a, b, c = fit_params["params"]
                    y_fit = a * x_sorted**2 + b * x_sorted + c
                elif regression_type.lower() == "log":
                    x_sorted_positive = x_sorted[x_sorted > 0]
                    if len(x_sorted_positive) == 0:
                        print("Cannot plot log regression because all x-values are <= 0.")
                        y_fit = None
                    else:
                        slope, intercept = fit_params["params"]
                        y_fit = intercept + slope * np.log(x_sorted_positive)
                        x_sorted = x_sorted_positive

                if y_fit is not None:
                    plt.plot(x_sorted, y_fit, color='red', label=f"{regression_type.capitalize()} Fit")
                    plt.legend()
            else:
                print("Invalid regression_type. Choose 'linear', 'quadratic', or 'log'.")

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Scatter plot saved to '%s' (x_col='%s', y_col='%s').", save_path, x_col, y_col)

    def plot_pie_chart(
        self,
        df: pd.DataFrame,
        column: str,
        save_path: str = "pie_chart.png",
        title: str = "Pie Chart",
        labels: list = None
    ):
        """
        Generates and saves a figure for a pie chart.

        WHAT IT IS:
            A circular graph where each "slice" represents a proportion of the whole.

        WHAT IT'S GOOD FOR:
            - Visualizing relative proportions of categories (e.g., percentages).

        CAVEATS:
            - Not ideal for comparing exact values or subtle differences.
            - Quickly becomes cluttered if there are many categories.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            column : str
                The column name (typically categorical or grouped numeric values).
            save_path : str, default "pie_chart.png"
                File path where the pie chart will be saved.
            title : str, default "Pie Chart"
                Plot title.
            labels : list, optional
                Custom labels for the pie slices. If None, uses unique values in the column
                or tries to interpret the column’s index if numeric.

        RETURNS:
            None. The figure is saved to 'save_path'.
        """
        logger.debug("Starting plot_pie_chart for column '%s'", column)
        data = df[column].dropna()

        # If column is numeric with many unique values, user might want to group them first
        # or pass in a pre-aggregated Series. For simplicity, let's assume it is categorical or aggregated.
        if pd.api.types.is_numeric_dtype(data):
            counts = data.value_counts()
            labels_for_pie = labels if labels else counts.index.tolist()
            values_for_pie = counts.values
        else:
            counts = data.value_counts()
            labels_for_pie = labels if labels else counts.index.tolist()
            values_for_pie = counts.values

        plt.figure(figsize=(8, 6))
        plt.title(title)
        plt.pie(values_for_pie, labels=labels_for_pie, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Pie chart saved to '%s' for column '%s'.", save_path, column)

    def plot_bar_chart(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        save_path: str = "bar_chart.png",
        title: str = "Bar Chart",
        xlabel: str = None,
        ylabel: str = None
    ):
        """
        Generates and saves a figure for a bar chart.

        WHAT IT IS:
            A chart representing data with rectangular bars proportional to the values.

        WHAT IT'S GOOD FOR:
            - Comparing discrete categories or groups side by side.
            - Seeing the magnitude of categories or subgroups at a glance.

        CAVEATS:
            - Works best with grouped or aggregated data (e.g., sums, means per category).
            - Too many categories can make the chart hard to read.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            x_col : str
                The column name for x-axis categories.
            y_col : str
                The column name for bar height.
            save_path : str, default "bar_chart.png"
                File path where the bar chart will be saved.
            title : str, default "Bar Chart"
                Plot title.
            xlabel : str, optional
                Label for the x-axis. If None, defaults to x_col.
            ylabel : str, optional
                Label for the y-axis. If None, defaults to y_col.

        RETURNS:
            None. The figure is saved to 'save_path'.
        """
        logger.debug("Starting plot_bar_chart with x_col='%s', y_col='%s'", x_col, y_col)
        x_data = df[x_col].astype(str)  # Ensure string categories
        y_data = df[y_col].values

        plt.figure(figsize=(8, 6))
        plt.bar(x_data, y_data, alpha=0.7, edgecolor='black')
        plt.title(title)
        plt.xlabel(xlabel if xlabel else x_col)
        plt.ylabel(ylabel if ylabel else y_col)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        logger.info("Bar chart saved to '%s' (x_col='%s', y_col='%s').", save_path, x_col, y_col)

    def compute_regression_parameters(
        self,
        x: np.ndarray,
        y: np.ndarray,
        regression_type: str = "linear"
    ) -> dict:
        """
        Generates and prints parameters for 1st-order, 2nd-order, or log regression of data.

        WHAT IT IS:
            A helper function that fits the user-specified regression model to (x, y) data
            and prints out the resulting parameters.

        WHAT IT'S GOOD FOR:
            - Understanding linear or polynomial relationships between variables.
            - Determining if a log relationship (y vs. ln(x)) might be a better fit.

        CAVEATS:
            - Not a robust stats or diagnostics approach (e.g., R^2 not provided here).
            - For log regression, x must be strictly positive.

        PARAMETERS:
            x : np.ndarray
                1D array of x-values.
            y : np.ndarray
                1D array of y-values.
            regression_type : str, default "linear"
                One of {"linear", "quadratic", "log"}.

        RETURNS:
            A dictionary:
                {
                    "type": <regression_type>,
                    "params": tuple_of_parameters
                }

            Where 'params' can be (slope, intercept) for linear/log, or (a, b, c) for quadratic.
        """
        logger.debug("Computing %s regression parameters for x, y arrays of size %d, %d",
                     regression_type, len(x), len(y))

        valid_idx = ~np.isnan(x) & ~np.isnan(y)
        x = x[valid_idx]
        y = y[valid_idx]

        if regression_type == "linear":
            slope, intercept = np.polyfit(x, y, 1)
            print(f"Linear Regression: y = {slope:.4f}x + {intercept:.4f}")
            logger.info("Linear regression parameters: slope=%.4f, intercept=%.4f", slope, intercept)
            return {"type": "linear", "params": (slope, intercept)}

        elif regression_type == "quadratic":
            a, b, c = np.polyfit(x, y, 2)
            print(f"Quadratic Regression: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}")
            logger.info("Quadratic regression parameters: a=%.4f, b=%.4f, c=%.4f", a, b, c)
            return {"type": "quadratic", "params": (a, b, c)}

        elif regression_type == "log":
            x_positive_idx = x > 0
            if not np.any(x_positive_idx):
                print("All x values are non-positive. Cannot perform log regression.")
                logger.warning("Cannot perform log regression. All x values <= 0.")
                return {"type": "log", "params": None}
            x_log = np.log(x[x_positive_idx])
            y_log = y[x_positive_idx]
            slope, intercept = np.polyfit(x_log, y_log, 1)
            print(f"Log Regression: y = {intercept:.4f} + {slope:.4f} ln(x)")
            logger.info("Log regression parameters: slope=%.4f, intercept=%.4f", slope, intercept)
            return {"type": "log", "params": (slope, intercept)}

        else:
            logger.error("Invalid regression_type specified: %s", regression_type)
            raise ValueError("Invalid regression_type. Choose from {'linear', 'quadratic', 'log'}.")
        
    def plot_fft_spectrum(
        self,
        fft_results: dict,
        columns: list = None,
        save_path: str = "fft_spectrum.png",
        title: str = "FFT Spectrum",
        xlabel: str = "Frequency (Hz)",
        ylabel: str = "Amplitude"
    ):
        """
        Plots frequency-domain data from an FFT analysis, as returned by analyze_fft.

        WHAT IT IS:
            A line plot of the frequency bins (x-axis) versus the FFT magnitude or amplitude (y-axis).

        WHAT IT'S GOOD FOR:
            - Visualizing the frequency components of signals processed by analyze_fft.
            - Comparing multiple signals in the same frequency domain plot.

        CAVEATS:
            - If columns have drastically different amplitude scales, consider plotting them separately
            or using a log scale (plt.yscale('log')).
            - This function assumes fft_results is a dict where each key is a column name
            and the value is (freq, fft_magnitude). Example:
                fft_results["Voltage"] => (freq_array, magnitude_array)
            - If your signals are non-stationary or have time-dependent frequency content,
            consider an STFT or wavelet transform and a different plot function.

        PARAMETERS:
            fft_results : dict
                Dictionary returned by analyze_fft. Example structure:
                    {
                    "ColumnName1": (freq_array, fft_magnitude_array),
                    "ColumnName2": (freq_array, fft_magnitude_array),
                    ...
                    }
            columns : list, optional
                A list of columns (keys in fft_results) to plot. If None, plots all keys.
            save_path : str, default "fft_spectrum.png"
                File path where the FFT spectrum plot will be saved.
            title : str, default "FFT Spectrum"
                Plot title.
            xlabel : str, default "Frequency (Hz)"
                Label for the x-axis.
            ylabel : str, default "Amplitude"
                Label for the y-axis.

        RETURNS:
            None. The figure is saved to 'save_path'.
        """
        import matplotlib.pyplot as plt
        
        # If columns not specified, plot all columns in fft_results
        if columns is None:
            columns = list(fft_results.keys())

        plt.figure(figsize=(8, 6))

        for col in columns:
            logger.debug(f'Starting a FFT of columns {columns}')
            if col not in fft_results:
                logger.debug(f"Warning: '{col}' not found in fft_results. Skipping.")
                continue

            freq, magnitude = fft_results[col]
            # Plot magnitude vs frequency
            plt.plot(freq, magnitude, label=col)

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"FFT spectrum plot saved to '{save_path}'.")

