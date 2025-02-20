import os
from pathlib import Path
import tempfile
import unittest

import pandas as pd
import pytest
import xarray as xr

import asli

class TestASLICalculator(unittest.TestCase):

    def setUp(self):
        self.data_dir = str(Path("tests", "fixtures"))
        self.lsm_file = "test_lsm.nc"
        self.msl_file = "test_era5_msl.nc"
        self.temp_filename = tempfile.NamedTemporaryFile(delete=False).name

    def tearDown(self):
        os.remove(self.temp_filename)

    def test_calculate(self):

        a = asli.ASLICalculator(
            data_dir=self.data_dir,
            mask_filename=self.lsm_file,
            msl_pattern=self.msl_file,
        )
        a.read_data()

        assert a.land_sea_mask is not None
        assert a.raw_msl_data is not None

        assert isinstance(a.masked_msl_data, xr.DataArray)
        assert isinstance(a.sliced_msl, xr.DataArray)
        assert isinstance(a.sliced_masked_msl, xr.DataArray)

        assert a.asl_df == None

        a.calculate()
        assert isinstance(a.asl_df, pd.DataFrame)
        assert a.asl_df.shape == (11, 7)

        a.to_csv(self.temp_filename)

        # test plotting behaviour for calculated dataframe
        a.plot_region_all()
        a.plot_region_year(2024)

        # should raise warning if a.asl_df already present and force option is false
        with pytest.warns(UserWarning):
            a.import_from_csv(filename=self.temp_filename)

    def test_import_csv(self):

        a = asli.ASLICalculator(
            data_dir=self.data_dir,
            mask_filename=self.lsm_file,
            msl_pattern=self.msl_file,
        )
        a.read_data()

        a.import_from_csv(filename=Path("test_csv.csv"))
        assert isinstance(a.asl_df, pd.DataFrame)
        assert a.asl_df.shape == (11, 7)

        # test plotting behaviour for imported data
        a.plot_region_all()
        a.plot_region_year(2024)
