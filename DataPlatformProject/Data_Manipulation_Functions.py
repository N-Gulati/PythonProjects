import pandas as pd

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
        """
        if not isinstance(columns, list):
            raise ValueError("columns must be a list of column names.")

        if inplace:
            df_out = df
        else:
            df_out = df.copy()

        for col in columns:
            if col not in df_out.columns:
                raise ValueError(f"Column '{col}' does not exist in the DataFrame.")

            if new_column_name and len(columns) == 1:
                # Single column => place the result in the new column
                df_out[new_column_name] = df_out[col].apply(transform_func)
            else:
                # Overwrite the column
                df_out[col] = df_out[col].apply(transform_func)

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
        try:
            df.to_csv(file_path, index=index, encoding=encoding)
            print(f"Data successfully exported to CSV at '{file_path}'.")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")

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
        try:
            df.to_excel(file_path, sheet_name=sheet_name, index=index)
            print(f"Data successfully exported to Excel at '{file_path}'.")
        except Exception as e:
            print(f"Error exporting to Excel: {e}")

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
        try:
            # Use to_csv under the hood, but specify a custom delimiter
            df.to_csv(file_path, sep=delimiter, index=False, header=header)
            print(f"Data successfully exported to text file at '{file_path}'.")
        except Exception as e:
            print(f"Error exporting to text file: {e}")

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
        try:
            df.to_json(file_path, orient=orient, date_format=date_format)
            print(f"Data successfully exported to JSON at '{file_path}'.")
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
