# ERA5-Land Variable Reference

List of available ERA5-Land variables and their descriptions.

## 📋 Variable Name Mapping

ERA5-Land uses two types of variable names:
- **CDS API Name**: Variable name used when downloading
- **NetCDF Name**: Actual variable name in the file

This tool automatically handles variable name mapping - you only need to use CDS API names.

---

## 🌡️ Temperature Related

| CDS API Variable | NetCDF Name | Unit | Description |
|-----------------|-------------|------|-------------|
| `2m_temperature` | `t2m` | K | 2m temperature |
| `2m_dewpoint_temperature` | `d2m` | K | 2m dewpoint temperature |
| `skin_temperature` | `skt` | K | Skin temperature |
| `soil_temperature_level_1` | `stl1` | K | Soil temperature level 1 (0-7cm) |
| `soil_temperature_level_2` | `stl2` | K | Soil temperature level 2 (7-28cm) |
| `soil_temperature_level_3` | `stl3` | K | Soil temperature level 3 (28-100cm) |
| `soil_temperature_level_4` | `stl4` | K | Soil temperature level 4 (100-289cm) |

---

## ☀️ Radiation Related

| CDS API Variable | NetCDF Name | Unit | Description |
|-----------------|-------------|------|-------------|
| `surface_solar_radiation_downwards` | `ssrd` | J/m² | Surface solar radiation downwards |
| `surface_thermal_radiation_downwards` | `strd` | J/m² | Surface thermal radiation downwards |
| `surface_net_solar_radiation` | `ssr` | J/m² | Surface net solar radiation |
| `surface_net_thermal_radiation` | `str` | J/m² | Surface net thermal radiation |
| `surface_net_solar_radiation_clear_sky` | `ssrc` | J/m² | Clear-sky surface net solar radiation |
| `surface_net_thermal_radiation_clear_sky` | `strc` | J/m² | Clear-sky surface net thermal radiation |
| `total_sky_direct_solar_radiation_at_surface` | `fdir` | J/m² | Total sky direct solar radiation at surface |

---

## 💨 Wind Related

| CDS API Variable | NetCDF Name | Unit | Description |
|-----------------|-------------|------|-------------|
| `10m_u_component_of_wind` | `u10` | m/s | 10m U wind component (East-West) |
| `10m_v_component_of_wind` | `v10` | m/s | 10m V wind component (North-South) |

---

## 💧 Precipitation and Moisture Related

| CDS API Variable | NetCDF Name | Unit | Description |
|-----------------|-------------|------|-------------|
| `total_precipitation` | `tp` | m | Total precipitation |
| `snowfall` | `sf` | m | Snowfall (water equivalent) |
| `snow_depth` | `sd` | m | Snow depth |
| `snow_density` | `rsn` | kg/m³ | Snow density |
| `volumetric_soil_water_layer_1` | `swvl1` | m³/m³ | Volumetric soil water layer 1 |
| `volumetric_soil_water_layer_2` | `swvl2` | m³/m³ | Volumetric soil water layer 2 |
| `volumetric_soil_water_layer_3` | `swvl3` | m³/m³ | Volumetric soil water layer 3 |
| `volumetric_soil_water_layer_4` | `swvl4` | m³/m³ | Volumetric soil water layer 4 |

---

## 🌊 Runoff and Evaporation Related

| CDS API Variable | NetCDF Name | Unit | Description |
|-----------------|-------------|------|-------------|
| `surface_runoff` | `sro` | m | Surface runoff |
| `sub_surface_runoff` | `ssro` | m | Sub-surface runoff |
| `total_evaporation` | `e` | m | Total evaporation |
| `potential_evaporation` | `pev` | m | Potential evaporation |
| `evaporation_from_bare_soil` | `evabs` | m | Evaporation from bare soil |
| `evaporation_from_open_water_surfaces_excluding_lakes` | `evaow` | m | Evaporation from open water |
| `evaporation_from_vegetation_transpiration` | `evatrans` | m | Vegetation transpiration |
| `evaporation_from_the_top_of_canopy` | `evatc` | m | Evaporation from canopy |

---

## 🌿 Vegetation Related

| CDS API Variable | NetCDF Name | Unit | Description |
|-----------------|-------------|------|-------------|
| `leaf_area_index_high_vegetation` | `lai_hv` | m²/m² | Leaf area index (high vegetation) |
| `leaf_area_index_low_vegetation` | `lai_lv` | m²/m² | Leaf area index (low vegetation) |
| `high_vegetation_cover` | `cvh` | 0-1 | High vegetation cover |
| `low_vegetation_cover` | `cvl` | 0-1 | Low vegetation cover |

---

## 🌍 Surface Characteristics

| CDS API Variable | NetCDF Name | Unit | Description |
|-----------------|-------------|------|-------------|
| `surface_pressure` | `sp` | Pa | Surface pressure |
| `surface_albedo` | `fal` | 0-1 | Surface albedo |
| `land_sea_mask` | `lsm` | 0-1 | Land-sea mask |
| `orography` | `z` | m | Orography (elevation) |
| `soil_type` | `slt` | - | Soil type |

---

## 🔥 Heat Flux Related

| CDS API Variable | NetCDF Name | Unit | Description |
|-----------------|-------------|------|-------------|
| `surface_latent_heat_flux` | `slhf` | J/m² | Surface latent heat flux |
| `surface_sensible_heat_flux` | `sshf` | J/m² | Surface sensible heat flux |

---

## 📖 Usage Examples

### Example 1: Download Temperature and Precipitation

```python
from download_ERA5_Land import ERA5LandDownloader

downloader = ERA5LandDownloader()

files = downloader.download(
    variables=[
        '2m_temperature',
        'total_precipitation'
    ],
    start_date='2020-01-01',
    end_date='2020-01-31'
)
```

### Example 2: Download Radiation Data

```python
files = downloader.download(
    variables=[
        'surface_solar_radiation_downwards',
        'surface_thermal_radiation_downwards',
        'surface_net_solar_radiation'
    ],
    start_date='2020-01-01',
    end_date='2020-01-31'
)
```

### Example 3: Download Wind Data

```python
files = downloader.download(
    variables=[
        '10m_u_component_of_wind',
        '10m_v_component_of_wind'
    ],
    start_date='2020-01-01',
    end_date='2020-01-31'
)
```

### Example 4: Download Soil Data

```python
files = downloader.download(
    variables=[
        'soil_temperature_level_1',
        'soil_temperature_level_2',
        'volumetric_soil_water_layer_1',
        'volumetric_soil_water_layer_2'
    ],
    start_date='2020-01-01',
    end_date='2020-01-31'
)
```

---

## 🔧 Custom Variable Mapping

If you encounter variable name mismatch, add custom mapping:

```python
custom_mapping = {
    'your_cds_variable_name': 'actual_netcdf_variable_name'
}

downloader = ERA5LandDownloader(
    variable_mapping=custom_mapping
)
```

---

## 📚 More Information

For complete variable list and detailed descriptions, see:
- [ERA5-Land Official Documentation](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)
- [ERA5-Land Parameter List](https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation)

---

## 💡 Tips

1. **Unit Conversion**: 
   - Temperature unit is Kelvin (K), convert to Celsius: °C = K - 273.15
   - Precipitation and evaporation unit is meter (m), convert to mm: mm = m × 1000

2. **Accumulated Variables**: 
   - Radiation, precipitation, evaporation are accumulated values, need to calculate differences for hourly values

3. **Variable Combinations**:
   - Wind speed = √(u10² + v10²)
   - Wind direction = arctan2(v10, u10)

---

**Last Updated**: 2025-12-23

