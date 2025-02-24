import logging
from typing import Union, List, Optional
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

################################################################################
# LOGGING SETUP
################################################################################
logger = logging.getLogger(__name__ + "_manipulation")
logger.setLevel(logging.DEBUG)  # Master log level

# FORMATTERS
console_formatter = logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s - %(message)s")

# CONSOLE HANDLER (INFO+ on console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# FILE HANDLER (DEBUG+ to file)
LOG_DIR = os.path.join(SCRIPT_DIR, "data_manipulation.log")
file_handler = logging.FileHandler(LOG_DIR, mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

# ADD HANDLERS
logger.addHandler(console_handler)
logger.addHandler(file_handler)

################################################################################
# DATA_MANIPULATION_FUNCTIONS CLASS
################################################################################

class Data_Manipulation_Functions:
    """
    A class for data manipulation (Requirement #6) and exporting (Requirement #14).
    Includes:
      - Arbitrary data transform method(s).
      - Exporting data as text, CSV, Excel, and JSON.
    """

    def transform_data(
        self,
        df: pd.DataFrame,
        columns: list,
        transform_func,
        new_column_name: str = None,
        inplace: bool = False
    ) -> pd.DataFrame:
        """
        Applies a user-defined transformation function to specified columns in a DataFrame.

        WHAT IT IS:
            A generic function that lets you apply an arbitrary operation to each data point
            or entire Series of the chosen columns.

        WHAT IT'S GOOD FOR:
            - Converting voltage to current (I = V / R).
            - Normalizing/scaling data, applying log transforms, etc.
            - Quickly prototyping domain-specific calculations on your dataset.

        CAVEATS:
            - Your transform function must be compatible with the data type in the chosen columns.
            - If new_column_name is provided but multiple columns are selected, the same transform 
              is stored in the single new column (not typical). 
            - If large DataFrames are used, be mindful of performance.

        PARAMETERS:
            df : pd.DataFrame
                The original DataFrame containing your data.
            columns : list
                The columns you want to transform.
            transform_func : callable
                The function or lambda to be applied.
            new_column_name : str, optional
                If provided, the transformed values are assigned to this new column 
                (for single-column transforms).
            inplace : bool, default False
                If True, modifies df directly. Otherwise returns a copy.

        RETURNS:
            A pd.DataFrame (modified in place if inplace=True, or a copy otherwise).
        
        Enhanced Logging:
            - Logs debug info about which columns are being transformed.
            - Logs info about successful transformations or any exceptions.
        """
        logger.debug("Starting transform_data on columns: %s", columns)

        if not isinstance(columns, list):
            logger.error("`columns` must be a list. Received: %s", type(columns).__name__)
            raise ValueError("columns must be a list of column names.")

        # Decide whether to work on a copy or modify in place
        if inplace:
            df_out = df
        else:
            df_out = df.copy()

        for col in columns:
            if col not in df_out.columns:
                logger.error("Column '%s' does not exist in the DataFrame.", col)
                raise ValueError(f"Column '{col}' does not exist in the DataFrame.")
            try:
                if new_column_name and len(columns) == 1:
                    # Single column => place the result in the new column
                    logger.debug("Applying transform_func to column '%s'; results in '%s'.", col, new_column_name)
                    df_out[new_column_name] = df_out[col].apply(transform_func)
                else:
                    logger.debug("Applying transform_func in place to column '%s'.", col)
                    df_out[col] = df_out[col].apply(transform_func)
            except Exception as e:
                logger.exception("Error while transforming column '%s'.", col)
                raise e

        logger.info("Data transformation complete on columns: %s", columns)
        return df_out
    
    def export_csv(
        self,
        df: pd.DataFrame,
        file_path: str,
        index: bool = False,
        encoding: str = "utf-8"
    ):
        """
        Exports the DataFrame to a CSV file.

        WHAT IT IS:
            Saves the data to a comma-separated-values file, a plain-text format widely used for data interchange.

        WHAT IT'S GOOD FOR:
            - Quick, lightweight exporting of tabular data.
            - Easy interoperability with spreadsheets and other data-analysis tools.

        CAVEATS:
            - Does not preserve types as explicitly as binary formats.
            - Large CSVs may be slow to handle and large on disk.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame to export.
            file_path : str
                The path (including file name) where the CSV will be saved.
            index : bool, default False
                Whether to write the DataFrame index as a column in the output file.
            encoding : str, default "utf-8"
                Encoding for the output file.

        RETURNS:
            None. The DataFrame is written to the specified file path.
        """
        logger.debug("Attempting to export DataFrame to CSV: %s", file_path)
        try:
            df.to_csv(file_path, index=index, encoding=encoding)
            logger.info("Data successfully exported to CSV at '%s'.", file_path)
        except Exception as e:
            logger.exception("Error exporting to CSV: %s", file_path)

    def export_excel(
        self,
        df: pd.DataFrame,
        file_path: str,
        sheet_name: str = "Sheet1",
        index: bool = False
    ):
        """
        Exports the DataFrame to an Excel file.

        WHAT IT IS:
            Saves data in a native spreadsheet format (.xlsx), preserving tabular structure,
            columns, and (optionally) data types.

        WHAT IT'S GOOD FOR:
            - Interoperability with Excel for further analysis or sharing.
            - Maintaining multiple sheets in a single file if needed (e.g., using ExcelWriter).

        CAVEATS:
            - Requires the openpyxl or xlsxwriter libraries installed for .xlsx files.
            - Excel files can be larger in size than CSVs, and saving can be slower.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame to export.
            file_path : str
                The path (including file name) where the Excel file will be saved (e.g., "data.xlsx").
            sheet_name : str, default "Sheet1"
                The name of the sheet within the workbook.
            index : bool, default False
                Whether to write the DataFrame index as a column.

        RETURNS:
            None. The DataFrame is written to the specified file path.
        """
        logger.debug("Attempting to export DataFrame to Excel: %s (sheet: %s)", file_path, sheet_name)
        try:
            df.to_excel(file_path, sheet_name=sheet_name, index=index)
            logger.info("Data successfully exported to Excel at '%s' (sheet: %s).", file_path, sheet_name)
        except Exception as e:
            logger.exception("Error exporting to Excel: %s", file_path)

    def export_text(
        self,
        df: pd.DataFrame,
        file_path: str,
        delimiter: str = "\t",
        header: bool = True
    ):
        """
        Exports the DataFrame to a text file.

        WHAT IT IS:
            Writes tabular data to a plain text file, typically using a specified delimiter.

        WHAT IT'S GOOD FOR:
            - Sharing data in a very human-readable or simple format.
            - Easy to parse with custom scripts if CSV or Excel are not desired.

        CAVEATS:
            - No built-in type preservation (all data becomes text).
            - Potentially large file sizes for big datasets.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame to export.
            file_path : str
                The path (including file name) where the text file will be saved.
            delimiter : str, default "\t"
                Delimiter used between columns.
            header : bool, default True
                Whether to include column names in the first row.

        RETURNS:
            None. Writes the DataFrame to the specified text file.
        """
        logger.debug("Attempting to export DataFrame to text: %s (delimiter='%s')", file_path, delimiter)
        try:
            df.to_csv(file_path, sep=delimiter, index=False, header=header)
            logger.info("Data successfully exported to text file at '%s'.", file_path)
        except Exception as e:
            logger.exception("Error exporting to text file: %s", file_path)

    def export_json(
        self,
        df: pd.DataFrame,
        file_path: str,
        orient: str = "records",
        date_format: str = "iso"
    ):
        """
        Exports the DataFrame to a JSON file.

        WHAT IT IS:
            Saves data in a JavaScript Object Notation (JSON) format.

        WHAT IT'S GOOD FOR:
            - Interoperability with web services and modern APIs.
            - Flexible structure for nested or hierarchical data.

        CAVEATS:
            - Not as compact as binary formats for large data.
            - JSON structure can become confusing if you pick an orient that doesn’t suit your use case.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame to export.
            file_path : str
                The path (including file name) where the JSON will be saved.
            orient : str, default "records"
                The format of the JSON (e.g., "split", "records", "index", "columns", "values").
            date_format : str, default "iso"
                How to format datetime objects (e.g., "epoch", "iso", "iso8601").

        RETURNS:
            None. Writes the DataFrame to the specified JSON file.
        """
        logger.debug("Attempting to export DataFrame to JSON: %s (orient='%s')", file_path, orient)
        try:
            df.to_json(file_path, orient=orient, date_format=date_format)
            logger.info("Data successfully exported to JSON at '%s'.", file_path)
        except Exception as e:
            logger.exception("Error exporting to JSON: %s", file_path)
