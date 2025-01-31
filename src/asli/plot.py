"""Helper functions for plotting ASLI data"""

import cartopy.crs as ccrs
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from .params import ASL_REGION


def draw_regional_box(region, transform=None):
    """
    Draw box around a region on a map
    region is a dictionary with west,east,south,north
    """

    if transform is None:
        transform = ccrs.PlateCarree()

    plt.plot(
        [region["west"], region["west"]],
        [region["south"], region["north"]],
        "k-",
        transform=transform,
        linewidth=1,
    )
    plt.plot(
        [region["east"], region["east"]],
        [region["south"], region["north"]],
        "k-",
        transform=transform,
        linewidth=1,
    )

    for i in range(int(region["west"]), int(region["east"])):
        plt.plot(
            [i, i + 1],
            [region["south"], region["south"]],
            "k-",
            transform=transform,
            linewidth=1,
        )
        plt.plot(
            [i, i + 1],
            [region["north"], region["north"]],
            "k-",
            transform=transform,
            linewidth=1,
        )


def plot_lows(
    da: xr.DataArray,
    df: pd.DataFrame,
    cmap: str = "Reds",
    border: int = 10,
    regionbox: dict = ASL_REGION,
    coastlines: bool = False,
    point_color: str = "k",
    point_cmap: str = "gray",
) -> plt.figure:
    """Plot monthly pressure contour plots with points marked as crosses.

    Args:
        da (xr.DataArray): DataArray containing monthly pressure fields. Expects time field named `valid_time`.
        df (pd.DataFrame): DataFrame containing monthly coordinates, takes one or more point per month.
        cmap (str, optional): matplotlib-valid colormap string for contour plots. Defaults to "Reds".
        border (int, optional): border around each plot. Defaults to 10.
        regionbox (dict, optional): plot a black box around region. Defaults to asli.params.ASL_REGION.
        coastlines (bool, optional): show coastlines. Defaults to False.
        point_color (str, optional): used when one point per month, colour of marker, must be matplotlib-valid color string. Defaults to "k".
        point_cmap (str, optional): used when multiple points per month. must be matplotlib-valid colormap. Defaults to "gray".

    Returns:
        plt.figure: matplotlib.pyplot.figure object
    """
    fig = plt.figure(figsize=(20, 15))

    for i in range(da.shape[0]):
        da_2D = da.isel(valid_time=i)

        da_2D = da_2D.sel(
            latitude=slice(regionbox["north"] + border, regionbox["south"] - border),
            longitude=slice(regionbox["west"] - border, regionbox["east"] + border),
        )

        ax = plt.subplot(
            3,
            4,
            i + 1,
            projection=ccrs.Stereographic(
                central_longitude=0.0, central_latitude=-90.0
            ),
        )

        if regionbox:
            ax.set_extent(
                [
                    regionbox["west"] - border,
                    regionbox["east"] + border,
                    regionbox["south"] - border,
                    regionbox["north"] + border,
                ],
                ccrs.PlateCarree(),
            )

        da_2D.plot.contourf(
            "longitude",
            "latitude",
            cmap=cmap,
            transform=ccrs.PlateCarree(),
            add_colorbar=False,
            levels=np.linspace(np.nanmin(da_2D.values), np.nanmax(da_2D.values), 20),
        )

        if coastlines:
            ax.coastlines(resolution="110m")


        ## mark ASL
        time = pd.to_datetime(da_2D.valid_time.values)
        time_str = time.strftime('%Y-%m-%d')
        ax.set_title(time_str)
        df2 = df[df["time"] == time_str]
        df2.reset_index(inplace=True)
        num_points = len(df2)
        if num_points > 1:
            # for more than one point, color them in sequence using a colormap
            point_colormap = matplotlib.colormaps[point_cmap].resampled(num_points)
            point_color_list = point_colormap(np.linspace(0, 1, num_points))
        else:
            # for a single point, use single color
            point_color_list = [point_color]
        for i in range(num_points):
            ax.plot(df2["lon"][i], df2["lat"][i], color=point_color_list[i], marker="x", transform=ccrs.PlateCarree())

        if regionbox:
            draw_regional_box(regionbox)

    return fig
