# ERA5-Land 变量参考

ERA5-Land 可用变量列表及其说明。

## 📋 变量名映射

ERA5-Land 使用两种变量名：
- **CDS API 名称**: 下载时使用的变量名
- **NetCDF 名称**: 文件中实际的变量名

本工具会自动处理变量名映射，您只需使用 CDS API 名称即可。

---

## 🌡️ 温度相关

| CDS API 变量名 | NetCDF 名称 | 单位 | 说明 |
|---------------|------------|------|------|
| `2m_temperature` | `t2m` | K | 2米高度温度 |
| `2m_dewpoint_temperature` | `d2m` | K | 2米高度露点温度 |
| `skin_temperature` | `skt` | K | 地表皮肤温度 |
| `soil_temperature_level_1` | `stl1` | K | 土壤温度第1层 (0-7cm) |
| `soil_temperature_level_2` | `stl2` | K | 土壤温度第2层 (7-28cm) |
| `soil_temperature_level_3` | `stl3` | K | 土壤温度第3层 (28-100cm) |
| `soil_temperature_level_4` | `stl4` | K | 土壤温度第4层 (100-289cm) |

---

## ☀️ 辐射相关

| CDS API 变量名 | NetCDF 名称 | 单位 | 说明 |
|---------------|------------|------|------|
| `surface_solar_radiation_downwards` | `ssrd` | J/m² | 地表向下短波辐射 |
| `surface_thermal_radiation_downwards` | `strd` | J/m² | 地表向下长波辐射 |
| `surface_net_solar_radiation` | `ssr` | J/m² | 地表净短波辐射 |
| `surface_net_thermal_radiation` | `str` | J/m² | 地表净长波辐射 |
| `surface_net_solar_radiation_clear_sky` | `ssrc` | J/m² | 晴空地表净短波辐射 |
| `surface_net_thermal_radiation_clear_sky` | `strc` | J/m² | 晴空地表净长波辐射 |
| `total_sky_direct_solar_radiation_at_surface` | `fdir` | J/m² | 地表直接太阳辐射 |

---

## 💨 风速相关

| CDS API 变量名 | NetCDF 名称 | 单位 | 说明 |
|---------------|------------|------|------|
| `10m_u_component_of_wind` | `u10` | m/s | 10米高度U风速（东西方向） |
| `10m_v_component_of_wind` | `v10` | m/s | 10米高度V风速（南北方向） |

---

## 💧 降水和水分相关

| CDS API 变量名 | NetCDF 名称 | 单位 | 说明 |
|---------------|------------|------|------|
| `total_precipitation` | `tp` | m | 总降水量 |
| `snowfall` | `sf` | m | 降雪量（水当量） |
| `snow_depth` | `sd` | m | 积雪深度 |
| `snow_density` | `rsn` | kg/m³ | 积雪密度 |
| `volumetric_soil_water_layer_1` | `swvl1` | m³/m³ | 土壤含水量第1层 |
| `volumetric_soil_water_layer_2` | `swvl2` | m³/m³ | 土壤含水量第2层 |
| `volumetric_soil_water_layer_3` | `swvl3` | m³/m³ | 土壤含水量第3层 |
| `volumetric_soil_water_layer_4` | `swvl4` | m³/m³ | 土壤含水量第4层 |

---

## 🌊 径流和蒸发相关

| CDS API 变量名 | NetCDF 名称 | 单位 | 说明 |
|---------------|------------|------|------|
| `surface_runoff` | `sro` | m | 地表径流 |
| `sub_surface_runoff` | `ssro` | m | 地下径流 |
| `total_evaporation` | `e` | m | 总蒸发量 |
| `potential_evaporation` | `pev` | m | 潜在蒸发量 |
| `evaporation_from_bare_soil` | `evabs` | m | 裸土蒸发 |
| `evaporation_from_open_water_surfaces_excluding_lakes` | `evaow` | m | 开放水面蒸发 |
| `evaporation_from_vegetation_transpiration` | `evatrans` | m | 植被蒸腾 |
| `evaporation_from_the_top_of_canopy` | `evatc` | m | 冠层蒸发 |

---

## 🌿 植被相关

| CDS API 变量名 | NetCDF 名称 | 单位 | 说明 |
|---------------|------------|------|------|
| `leaf_area_index_high_vegetation` | `lai_hv` | m²/m² | 高植被叶面积指数 |
| `leaf_area_index_low_vegetation` | `lai_lv` | m²/m² | 低植被叶面积指数 |
| `high_vegetation_cover` | `cvh` | 0-1 | 高植被覆盖度 |
| `low_vegetation_cover` | `cvl` | 0-1 | 低植被覆盖度 |

---

## 🌍 地表特征

| CDS API 变量名 | NetCDF 名称 | 单位 | 说明 |
|---------------|------------|------|------|
| `surface_pressure` | `sp` | Pa | 地表气压 |
| `surface_albedo` | `fal` | 0-1 | 地表反照率 |
| `land_sea_mask` | `lsm` | 0-1 | 陆海掩膜 |
| `orography` | `z` | m | 地形高度 |
| `soil_type` | `slt` | - | 土壤类型 |

---

## 🔥 热通量相关

| CDS API 变量名 | NetCDF 名称 | 单位 | 说明 |
|---------------|------------|------|------|
| `surface_latent_heat_flux` | `slhf` | J/m² | 地表潜热通量 |
| `surface_sensible_heat_flux` | `sshf` | J/m² | 地表感热通量 |

---

## 📖 使用示例

### 示例1: 下载温度和降水

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

### 示例2: 下载辐射数据

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

### 示例3: 下载风速数据

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

### 示例4: 下载土壤数据

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

## 🔧 自定义变量名映射

如果遇到变量名不匹配的问题，可以添加自定义映射：

```python
custom_mapping = {
    'your_cds_variable_name': 'actual_netcdf_variable_name'
}

downloader = ERA5LandDownloader(
    variable_mapping=custom_mapping
)
```

---

## 📚 更多信息

完整的变量列表和详细说明请参考：
- [ERA5-Land 官方文档](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)
- [ERA5-Land 参数列表](https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation)

---

## 💡 提示

1. **单位转换**: 
   - 温度单位为开尔文(K)，转换为摄氏度: °C = K - 273.15
   - 降水和蒸发单位为米(m)，转换为毫米: mm = m × 1000

2. **累积变量**: 
   - 辐射、降水、蒸发等为累积值，需要计算差值得到小时值

3. **变量组合**:
   - 风速大小 = √(u10² + v10²)
   - 风向 = arctan2(v10, u10)

---

**更新日期**: 2025-12-23

