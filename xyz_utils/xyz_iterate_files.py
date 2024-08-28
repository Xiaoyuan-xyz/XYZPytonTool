import os
from collections.abc import Callable, Sequence

def file_suffix_criterion(types: str | Sequence[str]) -> Callable[[str], bool]:
    """
    Creates a criterion function that checks whether a file's suffix (extension) matches
    any of the specified types.

    Parameters:
    -----------
    types : str | Sequence[str]
        A single file suffix (e.g., ".txt") or a sequence of file suffixes (e.g., [".txt", ".jpg"]).
        The suffixes should include the leading dot ('.').

    Returns:
    --------
    Callable[[str], bool]
        A function that takes a file name as input and returns `True` if the file's suffix matches
        any of the specified types, otherwise `False`.

    Example:
    --------
    To create a function that checks if a file is a `.txt` or `.jpg` file:

    ```python
    criterion = file_suffix_criterion([".txt", ".jpg"])

    print(criterion("document.txt"))  # Output: True
    print(criterion("image.png"))     # Output: False
    ```

    This creates a criterion function that returns `True` for files with `.txt` or `.jpg` extensions
    and `False` for other files.
    """
    if isinstance(types, str):
        types = [types]

    def suffix_criterion(file: str) -> bool:
        return os.path.splitext(file)[1] in types

    return suffix_criterion



import os
from collections.abc import Callable, Sequence

def iterate_files(
    folder_path: str,
    callback: Callable[[str], None],
    criterion: str | Sequence[str] | Callable[[str], bool] | None = None
) -> None:
    """
    Recursively iterates over all files in a specified folder and applies a callback function 
    to each file that meets an optional criterion.

    Parameters:
    -----------
    folder_path : str
        The path to the folder where the file iteration will begin.

    callback : Callable[[str], None]
        A function that takes a file path as input and performs an operation on it.
        This function is called for each file that meets the criterion.

    criterion : str | Sequence[str] | Callable[[str], bool] | None, optional
        A filter to determine which files the callback function should be applied to.
        This can be:
        - A string representing a file extension (e.g., ".txt").
        - A sequence of strings representing multiple file extensions (e.g., [".txt", ".jpg"]).
        - A callable function that takes a file name as input and returns a boolean value.
        - If `None`, the callback function is applied to all files. (default is None)

    Raises:
    -------
    TypeError
        If `criterion` is neither a string, a sequence of strings, a callable, nor None.

    Example:
    --------
    To print the paths of all `.txt` files in a directory:

    ```python
    def print_file_path(file_path: str) -> None:
        print(file_path)

    iterate_files('/path/to/directory', print_file_path, '.txt')
    ```

    This will print the path of each `.txt` file in the specified directory and its subdirectories.
    """

    if isinstance(criterion, str) or isinstance(criterion, list):
        criterion = file_suffix_criterion(criterion)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if criterion is None or criterion(file):
                file_path = os.path.join(root, file)
                callback(file_path)
