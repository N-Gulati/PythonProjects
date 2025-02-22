from typing import Union, List, Optional
import pandas as pd

class Import_Functions:
    """
    A class that encapsulates various data-import functions.
    """

    def import_csv(
        self,
        file_path: str,
        delimiter: str = ",",
        header: Union[str, int] = "infer",
        usecols: Optional[List[str]] = None,
        parse_dates: Optional[List[str]] = None,
        encoding: Optional[str] = None,
        na_values: Optional[Union[List[str], str]] = None
    ) -> pd.DataFrame:
        """
        Imports a CSV file and returns a pandas DataFrame.

        :param file_path: Path to the CSV file.
        :param delimiter: Delimiter used in the CSV file (default is ',').
        :param header: Row number to use as column names, or 'infer' 
                       if the first row contains column names (default is 'infer').
        :param usecols: List of column names to parse from the CSV file (default is None).
        :param parse_dates: List of column names to parse as dates (default is None).
        :param encoding: Encoding of the CSV file (default is None, which uses system default).
        :param na_values: Additional strings to recognize as NaN (default is None).
        :return: Pandas DataFrame containing the data from the CSV.
        """
        try:
            df = pd.read_csv(
                file_path,
                sep=delimiter,
                header=header,
                usecols=usecols,
                parse_dates=parse_dates,
                encoding=encoding,
                na_values=na_values
            )
            return df
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except pd.errors.EmptyDataError as e:
            print(f"No data: {e}")
        except Exception as e:
            print(f"An error occurred while importing the CSV: {e}")
        return pd.DataFrame()

    def import_excel(
        self,
        file_path: str,
        sheet_name: Union[str, int] = 0,
        usecols: Optional[List[str]] = None,
        header: Union[int, None] = 0,
        parse_dates: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Imports an Excel file (.xlsx or .xls) into a pandas DataFrame.

        :param file_path: Path to the Excel file.
        :param sheet_name: Name or index of the sheet to read (default is 0).
        :param usecols: List of columns to read (default is None, reads all).
        :param header: Row number to use as the column names (default is 0).
        :param parse_dates: List of column names to parse as dates (default is None).
        :return: Pandas DataFrame containing the data from the Excel sheet.
        """
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                usecols=usecols,
                header=header,
                parse_dates=parse_dates
            )
            return df
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except pd.errors.EmptyDataError as e:
            print(f"No data in the Excel file: {e}")
        except Exception as e:
            print(f"An error occurred while importing the Excel file: {e}")
        return pd.DataFrame()

    def import_json(
        self,
        file_path: str,
        orient: Optional[str] = None,
        convert_dates: bool = False,
    ) -> pd.DataFrame:
        """
        Imports data from a JSON file into a pandas DataFrame.

        :param file_path: Path to the JSON file.
        :param orient: Indication of expected JSON string format 
                       ('split', 'records', 'index', 'columns', 'values', 'table').
        :param convert_dates: Whether to attempt parsing date strings (default is False).
        :return: Pandas DataFrame containing the data from the JSON file.
        """
        try:
            df = pd.read_json(
                file_path,
                orient=orient,
                convert_dates=convert_dates
            )
            return df
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except ValueError as e:
            print(f"Value error with JSON file: {e}")
        except Exception as e:
            print(f"An error occurred while importing the JSON file: {e}")
        return pd.DataFrame()

    def import_text(
        self,
        file_path: str,
        delimiter: Optional[str] = None,
        header: bool = False
    ) -> pd.DataFrame:
        """
        Imports data from a text file line by line and converts it to a pandas DataFrame.

        :param file_path: Path to the text file.
        :param delimiter: A character or string to split each line on (default None,
                          which means no splitting—each line is one column).
        :param header: If True, interprets the first non-empty line as the column names.
        :return: Pandas DataFrame.
        """
        try:
            lines = []
            with open(file_path, "r") as file:
                for line in file:
                    clean_line = line.strip()
                    # Skip empty lines
                    if not clean_line:
                        continue

                    if delimiter:
                        row = clean_line.split(delimiter)
                    else:
                        # Store the entire line as a single column
                        row = [clean_line]

                    lines.append(row)

            if not lines:
                # No data read
                print("No valid lines found in the text file.")
                return pd.DataFrame()

            if header:
                # Use first row as column names
                columns = lines[0]
                data = lines[1:]
                df = pd.DataFrame(data, columns=columns)
            else:
                df = pd.DataFrame(lines)

            return df
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except Exception as e:
            print(f"An error occurred while importing the text file: {e}")

        return pd.DataFrame()
