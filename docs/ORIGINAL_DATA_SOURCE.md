# Original Dataset Documentation: Vietnam CPI (2002-2024)

## 1. Source & Metadata
- **Source:** General Statistics Office (GSO) of Vietnam.
- **Data Type:** Consumer Price Index (CPI) - Month-over-Month change.
- **Original Filename:** `data/Long_cleaned.csv`
- **Timeframe:** January 2002 - December 2024.
- **Geography:** Vietnam (National).

## 2. Original Structure (Wide Format)
The original data was provided in a "Wide" matrix format commonly used for official statistical reporting:
- **Rows:** Each row represents a specific Year and a specific Commodity Category.
- **Columns:**
    - `Năm` (Year): 2002 to 2024.
    - `Nhóm hàng` (Commodity Category): 11 main groups + sub-categories + Gold/USD.
    - `1` through `12`: Columns representing the 12 months of the year.

## 3. Key Categories (Vietnamese)
The dataset includes the official GSO baskets:
1. **Chỉ số giá tiêu dùng:** Total CPI (General Index).
2. **Hàng ăn và dịch vụ ăn uống:** Food and catering services.
3. **Đồ uống và thuốc lá:** Beverages and tobacco.
4. **May mặc, mũ nón, giày dép:** Garments, hats, and footwear.
5. **Nhà ở và vật liệu xây dựng:** Housing and construction materials.
6. **Thiết bị và đồ dùng gia đình:** Household appliances and goods.
7. **Thuốc và dịch vụ y tế:** Medicine and healthcare services.
8. **Giao thông:** Transport.
9. **Bưu chính viễn thông:** Post and telecommunications.
10. **Giáo dục:** Education.
11. **Văn hóa, giải trí và du lịch:** Culture, entertainment, and tourism.
12. **Hàng hóa và dịch vụ khác:** Other goods and services.
13. **Chỉ số giá vàng:** Gold price index.
14. **Chỉ số đô la Mỹ:** US Dollar index.

## 4. Value Meaning
- **Base Value:** 100.00.
- **Meaning:** Values represent the price level relative to the previous month.
- **Example:** A value of `102.50` in February 2008 for "Food" means food prices increased by **2.5%** compared to January 2008.
- **Data Quality:** Missing or unavailable data was marked with `..` in the raw file (handled as NaN during processing).

## 5. Limitations
In its original wide format, the dataset only contained **462 rows**, which did not meet the homework requirement of 2000+ rows. This necessitated the "Melt" transformation to a Long format (4,464 rows).
