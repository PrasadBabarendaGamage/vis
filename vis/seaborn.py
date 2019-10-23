import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib as mpl
import numpy as np
from six import string_types


def contour_plot(x, y, z, shade=False, legend=True, shade_lowest=True,
                 cbar=False, cbar_ax=None, cbar_kws=None, ax=None, **kwargs):

    """Plot a contour.

    Parameters
    ----------
    x : 1d array-like
        Input data.
    y: 1d array-like,
        Second input data.
    shade : bool, optional
        If True, shade in the area between contours
    legend : bool, optional
        If True, add a legend or label the axes when possible.
    shade_lowest : bool, optional
        If True, shade the lowest contour. Setting this to ``False`` can be
        useful when you want multiple contours on the same Axes.
    cbar : bool, optional
        If True and drawing a bivariate KDE plot, add a colorbar.
    cbar_ax : matplotlib axes, optional
        Existing axes to draw the colorbar onto, otherwise space is taken
        from the main axes.
    cbar_kws : dict, optional
        Keyword arguments for ``fig.colorbar()``.
    ax : matplotlib axes, optional
        Axes to plot on, otherwise uses current axes.
    kwargs : key, value pairings
        Other keyword arguments are passed to ``plt.plot()`` or
        ``plt.contour{f}``

    Returns
    -------
    ax : matplotlib Axes
        Axes with plot.

    Examples
    --------

    Plot a basic contour:

    .. plot::
        :context: close-figs

        >>> import numpy as np; np.random.seed(10)
        >>> import seaborn as sns; sns.set(color_codes=True)
        >>> import vis
        >>> x = np.arange(1, 10)
        >>> y = x.reshape(-1, 1)
        >>> z = x * y
        >>> ax = vis.contour_plot(x, y, z)

    Use an existing axis:

    .. plot::
        :context: close-figs

        >>> sns.set(style="darkgrid")
        >>> f, ax = plt.subplots(figsize=(8, 8))
        >>> ax.set_aspect("equal")
        >>> start, stop, n_values = -8, 8, 800
        >>> x_vals = np.linspace(start, stop, n_values)
        >>> y_vals = np.linspace(start, stop, n_values)
        >>> x, y = np.meshgrid(x_vals, y_vals)
        >>> z = np.sqrt(x**2 + y**2)
        >>> vis.contour_plot(x, y, z, ax=ax)

    Shade under the contour and use a different color:

    .. plot::
        :context: close-figs

        >>> ax = vis.contour_plot(x, shade=True, color="r")

    Use more contour levels and a different color palette:

    .. plot::
        :context: close-figs

        >>> ax = vis.contour_plot(x, y, z, n_levels=30, cmap="Purples_d")

    Specify contour level with a different color:

    .. plot::
        :context: close-figs

        >>> ax = vis.contour_plot(x, y, z, n_levels=[0.1, 0.2], color="r")

    Add a colorbar for the contours:

    .. plot::
        :context: close-figs

        >>> ax = vis.contour_plot(x, y, cbar=True)

    TODO extend functionality to plot text on contours:
    #https://stackoverflow.com/questions/33169093/how-to-label-a-seaborn-contour-plot


    """
    if ax is None:
        ax = plt.gca()

    if isinstance(x, list):
        x = np.asarray(x)
    if len(x) == 0:
        return ax
    x = x.astype(np.float64)

    if isinstance(y, list):
        y = np.asarray(y)
    y = y.astype(np.float64)
    if isinstance(z, list):
        z = np.asarray(z)
    z = z.astype(np.float64)

    ax = _contour_plot(
        x, y, z, shade, shade_lowest, legend, cbar, cbar_ax, cbar_kws, ax,
        **kwargs)

    return ax


def _contour_plot(x, y, z, filled, fill_lowest,
                       axlabel, cbar, cbar_ax, cbar_kws, ax, **kwargs):
    """Plot a contour."""
    # Plot the contours
    n_levels = kwargs.pop("n_levels", 10)

    scout, = ax.plot([], [])
    default_color = scout.get_color()
    scout.remove()

    colors = kwargs.pop("colors", None)
    if colors is None:
        color = kwargs.pop("color", default_color)
        cmap = kwargs.pop("cmap", None)
        if cmap is None:
            if filled:
                cmap = light_palette(color, as_cmap=True)
            else:
                cmap = dark_palette(color, as_cmap=True)
        if isinstance(cmap, string_types):
            if cmap.endswith("_d"):
                pal = ["#333333"]
                pal.extend(color_palette(cmap.replace("_d", "_r"), 2))
                cmap = blend_palette(pal, as_cmap=True)
            else:
                cmap = mpl.cm.get_cmap(cmap)
        kwargs["cmap"] = cmap
    else:
        kwargs["colors"] = colors

    label = kwargs.pop("label", None)

    contour_func = ax.contourf if filled else ax.contour
    cset = contour_func(x, y, z, n_levels, **kwargs)
    if filled and not fill_lowest:
        cset.collections[0].set_alpha(0)
    kwargs["n_levels"] = n_levels

    if cbar:
        cbar_kws = {} if cbar_kws is None else cbar_kws
        ax.figure.colorbar(cset, cbar_ax, ax, **cbar_kws)

    # Label the axes
    if hasattr(x, "name") and axlabel:
        ax.set_xlabel(x.name)
    if hasattr(y, "name") and axlabel:
        ax.set_ylabel(y.name)

    if label is not None:
        legend_color = cmap(.95) if color is None else color
        if filled:
            ax.fill_between([], [], color=legend_color, label=label)
        else:
            ax.plot([], [], color=legend_color, label=label)

    return ax
