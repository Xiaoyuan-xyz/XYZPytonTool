import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def classifying_data_scatter(x, y, jitter=0.6, s=4, c=None, *args, **kwargs):
    """
    Creates a scatter plot with jitter for categorical data.

    Parameters:
    ----------
    x : array-like
        The x-coordinates of the data points.
    y : array-like
        The y-coordinates of the data points.
    jitter : float, optional
        The amount of jitter to add to categorical data points to avoid overlap (default is 0.6).
    s : scalar or array-like, optional
        The size of the data points. If a single scalar is provided, all points will have the same size (default is 4).
    c : array-like or None, optional
        The color of the data points. If None, all points will have the same color (default is None).
    *args, **kwargs : additional keyword arguments
        Additional arguments passed to `plt.scatter` for further customization of the plot.

    Returns:
    -------
    None

    Notes:
    -----
    - Categorical variables in `x` or `y` are automatically converted to numeric codes, and jitter is added
      to reduce overlap.
    - If `c` is provided, a colorbar will be added to the plot.

    Example:
    --------
    >>> classifying_data_scatter(['A', 'B', 'A', 'C'], [1, 2, 1, 3])
    This will create a scatter plot with jittered x-coordinates for the categorical variable.
    """

    if type(s) in (int, float):
        s = np.full_like(x, s, dtype='float')
    df = pd.DataFrame({'x': x, 'y': y, 's': s, 'c': c if c is not None else np.zeros_like(x)})
    df.dropna(subset=['x', 'y'], inplace=True)
    x_labels, y_labels = None, None
    if not df['x'].dtypes.str.startswith('<i') and not df['x'].dtypes.str.startswith('<f'):
        df['x'], x_labels = pd.factorize(df['x'])
    if not df['y'].dtypes.str.startswith('<i') and not df['y'].dtypes.str.startswith('<f'):
        df['y'], y_labels = pd.factorize(df['y'])
    x_, y_ = df['x'].values, df['y'].values

    x_jitter = jitter * np.random.random(len(x_)) - jitter / 2 if df['x'].dtypes.str.startswith('<i') else 0
    y_jitter = jitter * np.random.random(len(y_)) - jitter / 2 if df['y'].dtypes.str.startswith('<i') else 0

    plt.scatter(x_ + x_jitter,
                y_ + y_jitter, s=df['s'], c=df['c'], *args, **kwargs)
    if x_labels is not None:
        plt.xticks(range(len(x_labels)), x_labels)
    if y_labels is not None:
        plt.yticks(range(len(y_labels)), y_labels)
    if c is not None and len(c) > 0 and type(c[0]) in (int, float):
        plt.colorbar()


if __name__ == '__main__':
    train = pd.read_csv(r'G:\Study\Work\work2\kaggle\kaggle\titanic\data/train.csv')
    # classifying_data_scatter([1, 1, 'p', 0, 's'], [2, 0, 4, 6, np.nan], alpha=0.5, s=4, c=[1, 2, 3, 4, 5])
    classifying_data_scatter(train['Sex'], train['Survived'], alpha=0.5, c=train['Age'], cmap='plasma')

    plt.show()
