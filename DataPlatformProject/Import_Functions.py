import logging
from typing import Union, List, Optional
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

################################################################################
# LOGGING SETUP
################################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Master log level (everything DEBUG+ is processed)

# FORMATTERS
console_formatter = logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s - %(message)s")

# HANDLERS
# 1) Console Handler (only INFO+ messages will appear in console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# 2) File Handler (all DEBUG+ messages will be written to the file)
LOG_FILE = os.path.join(SCRIPT_DIR,"import_functions.log")
file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

# ADD BOTH HANDLERS TO LOGGER
logger.addHandler(console_handler)
logger.addHandler(file_handler)

################################################################################
# IMPORT_FUNCTIONS CLASS
################################################################################
class Import_Functions:
    """
    A class that encapsulates various data-import functions with enhanced logging
    to both console and file.
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
        logger.debug("Attempting to import CSV from: %s", file_path)
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
            logger.info("CSV import successful: '%s' (%d rows).", file_path, len(df))
            return df
        except FileNotFoundError as e:
            logger.error("File not found: '%s'. Exception: %s", file_path, e)
        except pd.errors.EmptyDataError as e:
            logger.warning("No data found in CSV: '%s'. Exception: %s", file_path, e)
        except Exception as e:
            logger.exception("Unexpected error importing CSV from '%s'.", file_path)

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
        logger.debug("Attempting to import Excel from: %s (sheet: %s)", file_path, sheet_name)
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                usecols=usecols,
                header=header,
                parse_dates=parse_dates
            )
            logger.info("Excel import successful: '%s' (sheet: %s) (%d rows).", file_path, sheet_name, len(df))
            return df
        except FileNotFoundError as e:
            logger.error("File not found: '%s'. Exception: %s", file_path, e)
        except pd.errors.EmptyDataError as e:
            logger.warning("No data found in Excel file: '%s'. Exception: %s", file_path, e)
        except Exception as e:
            logger.exception("Unexpected error importing Excel from '%s'.", file_path)

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
        logger.debug("Attempting to import JSON from: %s", file_path)
        try:
            df = pd.read_json(file_path, orient=orient, convert_dates=convert_dates)
            logger.info("JSON import successful: '%s' (%d rows).", file_path, len(df))
            return df
        except FileNotFoundError as e:
            logger.error("File not found: '%s'. Exception: %s", file_path, e)
        except ValueError as e:
            logger.warning("Value error with JSON file: '%s'. Exception: %s", file_path, e)
        except Exception as e:
            logger.exception("Unexpected error importing JSON from '%s'.", file_path)

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
        logger.debug("Attempting to import Text from: %s", file_path)
        lines = []
        try:
            with open(file_path, "r") as file:
                for line in file:
                    clean_line = line.strip()
                    if not clean_line:
                        continue
                    if delimiter:
                        row = clean_line.split(delimiter)
                    else:
                        row = [clean_line]
                    lines.append(row)

            if not lines:
                logger.warning("No valid lines found in the text file: '%s'.", file_path)
                return pd.DataFrame()

            if header:
                columns = lines[0]
                data = lines[1:]
                df = pd.DataFrame(data, columns=columns)
            else:
                df = pd.DataFrame(lines)

            logger.info("Text import successful: '%s' (%d rows).", file_path, len(df))
            return df
        except FileNotFoundError as e:
            logger.error("File not found: '%s'. Exception: %s", file_path, e)
        except Exception as e:
            logger.exception("Unexpected error importing text from '%s'.", file_path)

        return pd.DataFrame()
