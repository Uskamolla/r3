import sys

import traceback
from typing import Optional, cast

class ResearchAnalystException(Exception):
    # A custom error class used throughout this project.
    # When something goes wrong, instead of a generic Python error,
    # this tells you: which file crashed, which line, and what the message was.

    def __init__(self, error_message, error_details: Optional[object] = None):
        # Convert whatever error_message is into a plain string
        if isinstance(error_message, BaseException):
            norm_msg = str(error_message)
        else:
            norm_msg = str(error_message)

        # Figure out WHERE the crash happened by reading the traceback.
        # You can pass: nothing (uses current crash), the sys module, or an Exception object.
        exc_type = exc_value = exc_tb = None
        if error_details is None:
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_details, "exc_info"):  # e.g., sys
                exc_info_obj = cast(sys, error_details)
                exc_type, exc_value, exc_tb = exc_info_obj.exc_info()
            elif isinstance(error_details, BaseException):
                exc_type, exc_value, exc_tb = type(error_details), error_details, error_details.__traceback__
            else:
                exc_type, exc_value, exc_tb = sys.exc_info()

        # Walk through all the frames in the traceback to find the deepest one
        # (the deepest frame = the exact line where the actual crash happened)
        last_tb = exc_tb
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next

        self.file_name = last_tb.tb_frame.f_code.co_filename if last_tb else "<unknown>"
        self.lineno = last_tb.tb_lineno if last_tb else -1
        self.error_message = norm_msg

        # Build the full traceback string so you can see the complete error chain
        if exc_type and exc_tb:
            self.traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        else:
            self.traceback_str = ""

        super().__init__(self.__str__())

    def __str__(self):
        # What gets printed when this exception is raised or logged
        # Format: "Error in [file.py] at line [42] | Message: something failed"
        base = f"Error in [{self.file_name}] at line [{self.lineno}] | Message: {self.error_message}"
        if self.traceback_str:
            return f"{base}\nTraceback:\n{self.traceback_str}"
        return base

    def __repr__(self):
        return f"ResearchAnalystException(file={self.file_name!r}, line={self.lineno}, message={self.error_message!r})"