import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid

import datapi
import datapi.legacy_api_client
import pytest

from asli import ASL_REGION
from asli.data import (
    get_era5_monthly,
    get_land_sea_mask,
    _get_request_area,
    _cli_data_common_args,
    _get_cli_lsm_args,
    _cli_get_era5_monthly,
)


@pytest.mark.parametrize(
    "area,border,expected",
    [
        (None, None, None),
        (
            ASL_REGION,
            10,
            {
                "north": ASL_REGION["north"] + 10,
                "south": ASL_REGION["south"] - 10,
                "east": ASL_REGION["east"] + 10,
                "west": ASL_REGION["west"] - 10,
            },
        ),
        (ASL_REGION, None, ASL_REGION),
    ],
)
def test_get_request_area(area, border, expected):
    assert _get_request_area(area, border) == expected


class TestCDSDownloader(unittest.TestCase):
    """Test class for tests implementing cdsapi.Client"""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        """
        Write a dummy CDS API key file if needed.
        Tests don't actually call the API, but the cdsapi package expects this file to exist.
        """

        cls.cdsapirc_path = Path(Path.home(), ".cdsapirc")
        if not os.path.exists(cls.cdsapirc_path):
            cls.created_temp_cdsapirc_file = True
            with open(cls.cdsapirc_path, "w") as f:
                f.writelines(
                    [
                        "\n",
                        "url: https://cds-beta.climate.copernicus.eu/api\n",
                        f"key: {str(uuid.uuid4())}\n",
                        "\n",
                    ]
                )
        else:
            cls.created_temp_cdsapirc_file = False

    @classmethod
    def tearDownClass(cls):
        """Remove the .cdsapirc file if it was created by these tests."""
        if cls.created_temp_cdsapirc_file:
            os.remove(cls.cdsapirc_path)

    def test_get_land_sea_mask(self):
        data_dir = self.tmp_dir.name
        area = ASL_REGION
        border = 10

        request_params = {
            "format": "netcdf",
            "product_type": "monthly_averaged_reanalysis",
            "variable": "land_sea_mask",
            "year": "2023",
            "month": "12",
            "time": "00:00",
        }

        request_area = _get_request_area(area, border)

        request_params.update(
            {
                "area": [
                    request_area["north"],
                    request_area["west"],
                    request_area["south"],
                    request_area["east"],
                ]
            }
        )

        with patch.object(datapi.legacy_api_client.LegacyApiClient, "retrieve", return_value=None) as mock_method:
            get_land_sea_mask(
                data_dir=str(data_dir), area=area, border=border
            )

        mock_method.assert_called_with(
            "reanalysis-era5-single-levels-monthly-means", request_params, Path(data_dir, "era5_lsm.nc")
        )

    def test_get_era5_monthly(self):
        data_dir = self.tmp_dir.name
        start_year = 2006
        end_year = 2010
        area = ASL_REGION
        border = 10

        request_params = {
            "format": "netcdf",
            "product_type": "monthly_averaged_reanalysis",
            "variable": ["mean_sea_level_pressure"],
            "year": list(map(str, list(range(start_year, end_year + 1, 1)))),
            "month": [
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "12",
            ],
            "time": "00:00",
        }

        request_area = _get_request_area(area, border)

        request_params.update(
            {
                "area": [
                    request_area["north"],
                    request_area["west"],
                    request_area["south"],
                    request_area["east"],
                ]
            }
        )

        output_filename = f"ERA5/monthly/era5_mean_sea_level_pressure_monthly_{start_year}-{end_year}.nc"
        output_path = Path(data_dir, output_filename)

        with patch.object(datapi.legacy_api_client.LegacyApiClient, "retrieve", return_value=None) as mock_method:
            get_era5_monthly(
                data_dir=data_dir,
                start_year=start_year,
                end_year=end_year,
                area=area,
                border=border,
            )

        mock_method.assert_called_with(
            "reanalysis-era5-single-levels-monthly-means", request_params, output_path
        )


def test_get_cli_lsm_args():
    # test -e flag
    with patch("sys.argv", ["_", "-e"]):
        args = _get_cli_lsm_args()

        assert args.e is True
        assert args.area_dict is None

    # test area and border parsing
    test_border = 7.0
    with patch(
        "sys.argv", ["_", "--area", "1", "2", "3", "4", "--border", str(test_border)]
    ):
        args = _get_cli_lsm_args()

        assert args.area_dict == {"north": 1, "west": 2, "south": 3, "east": 4}
        assert args.border == test_border

    # test that -e overrides --area
    with patch("sys.argv", ["_", "--area", "1", "2", "3", "4", "-e"]):
        args = _get_cli_lsm_args()

        assert args.e is True
        assert args.area_dict is None
