import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
        data = df[column].dropna()
        plt.figure(figsize=(8, 6))
        plt.hist(data, bins=bins, alpha=0.7, edgecolor='black')
        plt.title(title)
        plt.xlabel(xlabel if xlabel else column)
        plt.ylabel(ylabel)
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

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
        x_data = df[x_col].dropna().values
        y_data = df[y_col].dropna().values

        plt.figure(figsize=(8, 6))
        plt.scatter(x_data, y_data, alpha=0.7, edgecolor='black')
        plt.title(title)
        plt.xlabel(xlabel if xlabel else x_col)
        plt.ylabel(ylabel if ylabel else y_col)

        if regression_type is not None:
            if regression_type.lower() in ["linear", "quadratic", "log"]:
                # Compute regression parameters and the fitted curve
                fit_params = self.compute_regression_parameters(x_data, y_data, regression_type.lower())

                # Plot the fitted curve
                x_sorted = np.sort(x_data)
                if regression_type.lower() == "linear":
                    slope, intercept = fit_params["params"]
                    y_fit = slope * x_sorted + intercept
                elif regression_type.lower() == "quadratic":
                    a, b, c = fit_params["params"]
                    y_fit = a * x_sorted**2 + b * x_sorted + c
                elif regression_type.lower() == "log":
                    # log fit => y = a + b*ln(x), so we must handle x>0
                    x_sorted_positive = x_sorted[x_sorted > 0]
                    if len(x_sorted_positive) == 0:
                        print("Cannot plot log regression because all x-values are <= 0.")
                        y_fit = None
                    else:
                        slope, intercept = fit_params["params"]
                        y_fit = intercept + slope * np.log(x_sorted_positive)
                        # Switch to that subset for plotting
                        x_sorted = x_sorted_positive
                if y_fit is not None:
                    plt.plot(x_sorted, y_fit, color='red', label=f"{regression_type.capitalize()} Fit")
                    plt.legend()
            else:
                print("Invalid regression_type. Choose 'linear', 'quadratic', or 'log'.")

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

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
        data = df[column].dropna()
        
        # If column is numeric with many unique values, user might want to group them first
        # or pass in a pre-aggregated Series. For simplicity, let's assume it is categorical or aggregated.
        if pd.api.types.is_numeric_dtype(data):
            # Convert numeric data to a value counts approach (e.g., each value is a category).
            counts = data.value_counts()
            labels_for_pie = labels if labels else counts.index.tolist()
            values_for_pie = counts.values
        else:
            # For categorical data, get value counts
            counts = data.value_counts()
            labels_for_pie = labels if labels else counts.index.tolist()
            values_for_pie = counts.values
        
        plt.figure(figsize=(8, 6))
        plt.title(title)
        plt.pie(values_for_pie, labels=labels_for_pie, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

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
        # If data is not aggregated, consider grouping. For this simple example, we assume
        # y_col is already aggregated or that each x_col entry has a single y_col value.
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
        # Ensure no NaNs (keep indices consistent)
        valid_idx = ~np.isnan(x) & ~np.isnan(y)
        x = x[valid_idx]
        y = y[valid_idx]

        if regression_type == "linear":
            # y = mx + b
            slope, intercept = np.polyfit(x, y, 1)
            print(f"Linear Regression: y = {slope:.4f}x + {intercept:.4f}")
            return {"type": "linear", "params": (slope, intercept)}

        elif regression_type == "quadratic":
            # y = ax^2 + bx + c
            a, b, c = np.polyfit(x, y, 2)
            print(f"Quadratic Regression: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}")
            return {"type": "quadratic", "params": (a, b, c)}

        elif regression_type == "log":
            # y = a + b ln(x)
            # => y vs ln(x): slope = b, intercept = a
            x_positive_idx = x > 0
            if not np.any(x_positive_idx):
                print("All x values are non-positive. Cannot perform log regression.")
                return {"type": "log", "params": None}
            x_log = np.log(x[x_positive_idx])
            y_log = y[x_positive_idx]
            slope, intercept = np.polyfit(x_log, y_log, 1)
            print(f"Log Regression: y = {intercept:.4f} + {slope:.4f} ln(x)")
            return {"type": "log", "params": (slope, intercept)}

        else:
            raise ValueError("Invalid regression_type. Choose from {'linear', 'quadratic', 'log'}.")
