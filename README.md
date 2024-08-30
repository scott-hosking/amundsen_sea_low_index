# Amundsen Sea Low Index (ASLI)

![GitHub License](https://img.shields.io/github/license/davidwilby/amundsen-sea-low-index)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdavidwilby%2Famundsen-sea-low-index%2Fpackaging%2Fpyproject.toml)
![tests](https://github.com/davidwilby/amundsen-sea-low-index/actions/workflows/tests.yml/badge.svg)

![ASL image](asl.jpg) 

The Amundsen Seas Low (ASL) is a highly dynamic and mobile climatological low pressure system located in the Pacific sector of the Southern Ocean. In this sector, variability in sea-level pressure is greater than anywhere in the Southern Hemisphere, making it challenging to isolate local fluctuations in the ASL from larger-scale shifts in atmospheric pressure. The position and strength of the ASL are crucial for understanding regional change over West Antarctica. 

This repository contains a python package (`asli`) which implements the ASL calculation methods described in [Hosking *et al.* (2016)](http://dx.doi.org/10.1002/2015GL067143), as well as notebooks illustrating its usage.

More information can be found [here](https://scotthosking.com/asl_index)

If using the `asli` package please cite both this repository (see "Cite this repository" at the top right on GitHub), as well as the original paper, e.g.

> Hosking, J. S., A. Orr, T. J. Bracegirdle, and J. Turner (2016), Future circulation changes off West Antarctica: Sensitivity of the Amundsen Sea Low to projected anthropogenic forcing, Geophys. Res. Lett., 43, 367–376, doi:10.1002/2015GL067143. 

> Hosking, J. S., & Wilby, D. asli [Computer software]. https://github.com/scotthosking/amundsen-sea-low-index

## Usage

### Installation

We advise installing this package and its dependencies in a python virtual environment using a tool such as [venv](https://docs.python.org/3/library/venv.html) or [conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-python) (other virtual environment managers are available).

Install the package from GitHub using pip: `pip install git+https://github.com/scotthosking/amundsen-sea-low-index`

### Downloading data
Command-line utilities are provided as a convenient way to download the datasets required for this analysis.

+ `asli_data_lsm` downloads land-sea mask ERA5 data.
+ `asli_data_era5` downloads certain variables from ERA5, by default `mean_sea_level_pressure`.

The `--help` flags can be used to find out more information, e.g.

```sh
asli_data_lsm --help
```

Alternatively, using the python interface:

```py
from asli.data import get_land_sea_mask, get_era5_monthly

help(get_land_sea_mask)
...

help(get_era5_monthly)
...
```

### Running calculations
A command-line utility is also provided for performing the basic calculations, with a similar help flag:

```sh
asli_calc --help
```

Alternatively, using the python interface, import the package and create an instance of the `ASLICalculator` class, initialising with the locations of the land-sea mask and mean sea level pressure data:

```py
import asli
a = asli.ASLICalculator(data_dir="./data/", 
                   mask_filename="era5_lsm.nc",
                   msl_pattern="ERA5/monthly/era5_mean_sea_level_pressure_monthly_1988.nc"
                   )


then read in the data and perform the calculation:

```py
a.read_mask_data()
a.read_msl_data()
a.calculate()
```

#### Working with Zarr and Object Storage
The `asli` package also supports Zarr data import from s3 storage through the python interface. The method remains the same, but you will need to install the [s3] optional dependencies.

```sh
pip install git+https://github.com/scotthosking/amundsen-sea-low-index[s3]
```

Additionally you will need to provide the location of your s3 config file, to the `ASLICalculator` class:

```py
from pathlib import Path

a = asli.ASLICalculator(data_dir="s3://asli", 
                   mask_filename="zarr-lsm",
                   msl_pattern="zarr-msl",
                   s3_config_dir = Path.home(), # Default location
                   s3_config_filename = ".s3cfg" # Default location
                   )
```

Below is an example of an s3 config file, `~/.s3cfg`. This example is adapted from the [JASMIN documentation on using object storage](https://help.jasmin.ac.uk/docs/short-term-project-storage/using-the-jasmin-object-store/#using-s3cmd). Other object store providers can be used, but the config at a minimum should contain the `[default]` header and provide `access key`, `host_base`, `host_bucket` and `secret_key`. 

```txt
[default]
access_key = <access key>
host_base = my-os-tenancy-o.s3-ext.jc.rl.ac.uk
host_bucket = my-os-tenancy-o.s3-ext.jc.rl.ac.uk
secret_key = <secret key>
use_https = True
signature_v2 = False
```

### Outputting data as a csv file and plotting
Once the calculations are done, we can write out the dataframe to a csv file, providing the filename:

```py
a.to_csv('asl.csv')
```

Basic plots of the pressure fields and lows can be made using the `plot_region_all()` and `plot_region_year()` methods.

```py
a.plot_region_all()
```

### Getting help
Most of the package has docstrings in the source code, so try running `help()` on any of the functions, classes or their methods, e.g. `help(asli.ASLICalculator)`.


## Contributing
We welcome contributions and improvements to this package!

Please submit bug reports and feature requests as issues [on the GitHub repo](https://github.com/scotthosking/amundsen-sea-low-index/issues/new).

### Development tips

When making changes to the source code (including to the docs):

1. Fork this repository on GitHub,
1. Clone the package to your computer: `git clone https://github.com/<your-username>/amundsen-sea-low-index`
1. Inside a virtual environment, install the package as an editable pip install, including the optional development dependencies: `pip install -e amundsen-sea-low-index[tests,docs,dev,s3]` (where `amundsen-sea-low-index` is the relative path to the cloned repository),
1. Make your changes and run the tests using pytest: `pytest` and/or test the docs build using `jupyter-book build docs/`
1. Commit and push your changes to GitHub and open a pull request.
