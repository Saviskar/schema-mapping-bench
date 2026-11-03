# Dirty datasets: answer key

Ground truth for the 10 CSVs in the parent folder. Every injected problem is listed cell by cell in `issue_log.csv`; this page summarises it.

**Blind testing:** the file names describe the main problems. If the model under test can see file names, rename the files (e.g. `dataset_01.csv`) first. Keep this `_answer_key` folder away from the model.

## How to read issue_log.csv

| column | meaning |
|---|---|
| file | dataset file name |
| row | 1-based DATA row (first row under the header row(s) = 1, i.e. pandas index + 1). `HEADER` = the column name itself, `ALL` = the whole column (pattern or rule), `FILE` = whole-file finding |
| col_index | 1-based column position (`*` = whole row / not one column) |
| column | header text as it appears in the file (two-row headers joined with ` / `) |
| issue_id / issue | which of the 19 Quartz Bad Data Guide problems it is |
| dirty_value | exactly what is in the cell |
| expected_clean_value | what a correct cleaner should produce; blank = should become null/unknown |
| note | why it is wrong, plus the true value when the clean value has to be null |

Regenerate or tweak: `cd _generator && python3 run_all.py && python3 verify.py` (seeded, so output is identical; verify.py re-checks every cell-level entry against the CSVs).

## Coverage: logged findings per issue and file

| # | Issue | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Values are missing | 52 | 97 | 40 | 11 | 21 | 102 | 22 | 42 | 130 | 69 |
| 2 | Zeros replace missing values | 2 | 33 | 566 | 12 | 5 | 104 | 30 | 13 |  | 39 |
| 3 | Data are missing you know should be there |  |  | 3 |  |  |  |  | 2 |  | 1 |
| 4 | Rows or values are duplicated | 26 | 22 | 15 | 2 | 12 | 8 | 6 | 14 | 180 | 2 |
| 5 | Spelling is inconsistent | 492 | 541 | 32 | 4 | 151 | 314 | 179 | 910 | 16 | 21 |
| 6 | Name order is inconsistent | 77 |  | 20 |  |  | 153 | 83 |  | 7 |  |
| 7 | Date formats are inconsistent | 61 | 639 | 11 |  | 60 | 539 | 270 | 5 | 1 | 190 |
| 8 | Units are not specified | 30 | 314 | 3 | 92 | 28 | 107 | 12 | 1 | 2 | 2 |
| 9 | Categories are badly chosen | 106 | 41 |  | 50 | 45 | 324 | 52 | 622 | 7 | 6 |
| 10 | Field names are ambiguous | 3 | 14 | 1 |  | 15 | 27 | 19 | 13 |  |  |
| 11 | Provenance is not documented | 1 |  |  | 2 |  | 1 |  |  |  |  |
| 12 | Suspicious values are present | 14 | 10 | 13 | 5 | 13 | 7 | 8 | 65 | 50 | 13 |
| 13 | Data are too coarse |  |  |  | 4 |  |  |  | 384 | 1 |  |
| 14 | Totals differ from published aggregates |  |  |  | 30 |  |  | 13 |  | 130 |  |
| 15 | Spreadsheet has 65536 rows |  |  |  |  |  |  |  |  | 1 |  |
| 16 | Spreadsheet has 255 columns |  |  |  |  |  |  |  |  |  | 1 |
| 17 | Spreadsheet has dates in 1900, 1904, 1969, or 1970 | 9 | 20 | 6 |  | 15 | 47 | 22 | 8 | 50 |  |
| 18 | Text has been converted to numbers | 99 |  |  |  | 203 | 431 | 60 | 893 | 2 | 44 |
| 19 | Numbers have been stored as text |  | 522 |  | 49 | 93 | 251 | 256 | 6 | 1 | 6 |

Files 02, 05, 06, 07 and 08 have deliberately cryptic/confusing column names; the other 5 have messy but readable headers.

## 01. Supplier / vendor master

`01_supplier_master__duplicates_spelling_name_order.csv`

- Data rows: **145**. 1 header row, UTF-8, comma-delimited.
- Logged findings: 972 across 13 of the 19 issue types.
- 120 real suppliers; 16 re-entered from another system with a new ID and misspelled name; 9 exact duplicate rows.
- Some ID values are text-to-number damaged (leading zeros dropped), so 100231 and 0000100231 are the same supplier.

**What each column really is**

| header in file | true meaning |
|---|---|
| `supplier_id` | supplier ID (3 schemes, see provenance) |
| `Supplier Name` | company name |
| `Contact Person ` | contact person name |
| `Phone/Mobile` | phone |
| `e-mail` | email |
| `City/Town` | city |
| `country` | country |
| `Postal Code` | postal code |
| `VAT No.` | VAT registration no |
| `Pmt Terms` | payment terms |
| `Category` | supplier category |
| `Onboarded On` | onboarding date |
| `Active?` | active flag |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 52 | e-mail: `(blank)` → `(blank)` (missing (true value: sales@bluelinedairy.lk))<br>Phone/Mobile: `TBD` → `(blank)` (missing (true value: 0729060268))<br>Onboarded On: `none` → `(blank)` (missing (true value: 2016-06-16))<br>e-mail: `NIL` → `(blank)` (missing (true value: accounts@deltaplastics.lk))<br>Contact Person : `null` → `(blank)` (missing (true value: Nadeesha Perera))<br>City/Town: `NULL` → `(blank)` (missing (true value: Kandy)) |
| 2 | Zeros replace missing values | 2 | VAT No.: `0` → `(blank)` (0 used for unknown VAT (true value: 115485498-7000)) |
| 4 | Rows or values are duplicated | 26 | same supplier as row 8, re-entered from another system (different ID + spelling)<br>exact duplicate of row 54<br>same supplier as row 125, re-entered from another system (different ID + spelling)<br>same supplier as row 7, re-entered from another system (different ID + spelling)<br>VAT No.: `n/a` → `132507043-7000` (VAT no copied from another supplier (Southern Packaging Enterprises)) |
| 5 | Spelling is inconsistent | 492 | e-mail: `accounts[at]rainbowlogisti.…` → `accounts@rainbowlogisti.lk` (obfuscated @)<br>country: `IN` → `India` (ISO code instead of name)<br>Pmt Terms: `NT14` → `Net 14` (ERP payment-term code)<br>Category: `LG` → `Logistics` (undocumented category code)<br>Contact Person : `asanka wijesinghe` → `Asanka Wijesinghe` (lower-cased name)<br>VAT No.: `1922731327000` → `192273132-7000` (VAT no without '-' separator) |
| 6 | Name order is inconsistent | 77 | Contact Person : `Eng. Tharindu Jayasinghe` → `Tharindu Jayasinghe` (honorific prefix)<br>Contact Person : `de Silva Lakshmi` → `Lakshmi de Silva` (Last First (no comma))<br>Contact Person : `W.S. Wickramasinghe` → `Shanika Wickramasinghe` (Sri Lankan initials format: first name not recoverable)<br>Contact Person : `S. Wickramasinghe` → `Shanika Wickramasinghe` (initial + surname: first name not recoverable)<br>Contact Person : `Arjun K. Weerasinghe` → `Arjun Weerasinghe` (middle initial added)<br>Contact Person : `Ranasinghe, Imran` → `Imran Ranasinghe` (Last, First) |
| 7 | Date formats are inconsistent | 61 | Onboarded On: (Onboarded On mixes ISO, DD/MM/YYYY and M/D/YYYY: 03/04/2021 and 3/4/2021 mean different days)<br>Onboarded On: `27/05/2022` → `2022-05-27` (DD/MM/YYYY)<br>Onboarded On: `5/9/2022` → `2022-05-09` (M/D/YYYY (US) (ambiguous))<br>Onboarded On: `6/26/2020` → `2020-06-26` (M/D/YYYY (US))<br>Onboarded On: `07/06/2023` → `2023-06-07` (DD/MM/YYYY (ambiguous)) |
| 8 | Units are not specified | 30 | `Pmt Terms` = some rows give payment-term days as a bare number<br>Pmt Terms: `14` → `Net 14` (number of days with no unit) |
| 9 | Categories are badly chosen | 106 | Active?: `X` → `No` (SAP-style deletion flag: blank = active, X = blocked (inverted meanin…)<br>Pmt Terms: `Cash` → `Immediate` (payment method mixed into payment-terms field)<br>e-mail: `accounts@deltasteel.lk; acc…` → `accounts@deltasteel.lk` (two emails in one field)<br>Category: `Other` → `Services` (catch-all category hides the real one)<br>Active?: `On Hold` → `(blank)` (status value mixed into a yes/no field)<br>Category: `Pakaging` → `Packaging` (category label inconsistent / overlapping) |
| 10 | Field names are ambiguous | 3 | `supplier_id` = one column holds three different ID schemes (10-digit zero-padded / SUP-#### / 4-digit)<br>`Contact Person ` = trailing space in header 'Contact Person '<br>`Active?` = 'Active?' mixes Yes/No, Y/N, TRUE/FALSE, 1/0, statuses and SAP-style X(=blocked)/blank(=active) |
| 11 | Provenance is not documented | 1 | No source column or metadata, but rows were merged from 3 systems: (A) 10-digit zero-padded IDs, ISO dates, NTxx terms, ISO country codes, category codes, X/blank flag; (B) SUP-#### IDs, DD/MM/YYYY, Yes/No; (C) 4-digit … |
| 12 | Suspicious values are present | 14 | e-mail: `a@a.com` → `(blank)` (placeholder email)<br>Postal Code: `99999` → `00300` (placeholder postal code)<br>Postal Code: `00000` → `(blank)` (UAE has no postal codes; 00000 is a placeholder)<br>Onboarded On: `2033-03-11` → `(blank)` (onboarding date in the future)<br>e-mail: `accounts@islandrubber,lk` → `accounts@islandrubber.lk` (invalid email (comma typo))<br>Phone/Mobile: `555-3485` → `(blank)` (fake/placeholder phone number) |
| 17 | Spreadsheet has dates in 1900, 1904, 1969, or 1970 | 9 | Onboarded On: `00/01/1900` → `(blank)` (spreadsheet/unix epoch placeholder (true date: 2016-01-22)) |
| 18 | Text has been converted to numbers | 99 | supplier_id: `100231` → `0000100231` (leading zeros stripped by spreadsheet)<br>Phone/Mobile: `728560726` → `0728560726` (leading 0 dropped by spreadsheet)<br>Phone/Mobile: `9.47427E+10` → `0742672261` (scientific notation: digits lost, unrecoverable)<br>VAT No.: `1.44727E+12` → `144727411-7000` (scientific notation: digits lost, unrecoverable)<br>Postal Code: `300` → `00300` (leading zeros stripped by spreadsheet) |

## 02. Shipment tracking log (CONFUSING HEADERS)

`02_CONFUSING_HEADERS_shipment_tracking__legacy_field_codes_mixed_dates_unitless_weights.csv`

- Data rows: **422**. 1 header row, UTF-8, two headers have trailing spaces. Rows sorted by real ship date.
- Logged findings: 2,253 across 11 of the 19 issue types.
- 400 shipments + 12 stale status rows (same SHKEY, older status) + 10 exact duplicate scans.
- Decoding: SHQTY carries kg/lbs text on some rows (weight), SHSIZ looks like LxWxH, SHMTR matches lane distances (Kandy 115, Jaffna 396).
- Units of SHQTY/SHSIZ/SHMTR depend on SHVND (carrier), so the carrier spelling mess also breaks unit recovery.

**What each column really is**

| header in file | true meaning |
|---|---|
| `SHKEY` | shipment ID |
| `SHREF` | sales-order reference (SHREF could be any reference) |
| `SHLOC1` | origin hub |
| `SHLOC2  ` | destination city (header has trailing spaces) |
| `SHVND` | carrier / courier (legacy 'vendor' field) |
| `SHDT1` | ship date |
| `SHDT2` | estimated arrival date |
| `SHDT3` | actual delivery timestamp, local +05:30 (blank or epoch placeholder when not delivered) |
| `SHQTY` | MISLEADING: gross WEIGHT kept in a legacy 'quantity' field (kg, but lb for FedEx and grams for small Island Couriers parcels) |
| `SHSIZ` | parcel dimensions LxWxH (cm, but inches for FedEx and mm for Island Couriers) |
| `SHMTR` | MISLEADING: lane distance in km (miles for FedEx), not metres |
| `SHVAL` | MISLEADING: FREIGHT COST (LKR domestic, USD international), not the goods value |
| `SHSTS ` | shipment status (header has a trailing space) |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 97 | SHSIZ: `(blank)` → `(blank)` (missing (true value: 69x47x29))<br>SHSIZ: `null` → `(blank)` (missing (true value: 78x54x37))<br>SHVND: `none` → `(blank)` (missing (true value: Island Couriers))<br>SHQTY: `' '` → `(blank)` (missing (true value: 11.84))<br>SHDT2: `TBC` → `(blank)` (missing (true value: 2024-01-10))<br>SHREF: `-` → `(blank)` (missing (true value: SO-24-89875)) |
| 2 | Zeros replace missing values | 33 | SHMTR: `0` → `115` (0 used for unknown distance)<br>SHDT3: `0` → `(blank)` (0 used for no delivery date (In Transit)) |
| 4 | Rows or values are duplicated | 22 | older status row for the same shipment as row 16; keep the latest<br>exact duplicate of row 43<br>older status row for the same shipment as row 100; keep the latest<br>older status row for the same shipment as row 116; keep the latest |
| 5 | Spelling is inconsistent | 541 | SHLOC1: `Col DC` → `Colombo DC` (origin spelled differently)<br>SHSTS : `delivered` → `Delivered` (status label inconsistent / overlapping)<br>SHLOC2  : `Trinco` → `Trincomalee` (destination spelled differently)<br>SHVND: `Isl. Couriers` → `Island Couriers` (carrier spelled differently)<br>SHKEY: `shp-24-000190` → `SHP-24-000190` (lower-case ID)<br>SHSIZ: `49*31*21 cm` → `49x31x21` (different separator + 'cm') |
| 7 | Date formats are inconsistent | 639 | SHDT1: (SHDT1 / SHDT2 (ship date / ETA) mix 12 formats incl. Excel serials, unix seconds and US vs EU day/month order)<br>SHDT1: `02.01.2024` → `2024-01-02` (DD.MM.YYYY (ambiguous day/month))<br>SHDT2: `03/01/2024` → `2024-01-03` (DD/MM/YYYY (ambiguous day/month))<br>SHDT3: `2024-01-05T05:30:00Z` → `2024-01-05 11:00` (UTC ISO timestamp (local time is +05:30))<br>SHDT2: `Thu 04 Jan 2024` → `2024-01-04` (weekday + D Mon YYYY)<br>SHDT1: `1704240000` → `2024-01-03` (unix epoch seconds) |
| 8 | Units are not specified | 314 | `SHQTY` = no unit: mostly kg, but FedEx rows are lb, small Island Couriers parcels are grams<br>`SHSIZ` = no unit: cm, but FedEx = inches, Island Couriers = mm<br>`SHMTR` = no unit: km, but FedEx rows are miles<br>`SHVAL` = no currency: domestic rows LKR, international rows USD<br>SHSIZ: `770x750x490` → `77x75x49` (millimetres, unit not stated)<br>SHQTY: `1100` → `1.10` (grams, unit not stated) |
| 9 | Categories are badly chosen | 41 | SHSTS : `Completed` → `Delivered` (status label inconsistent / overlapping) |
| 10 | Field names are ambiguous | 14 | `SHKEY` = shipment ID<br>`SHREF` = sales-order reference (SHREF could be any reference)<br>`SHLOC1` = origin hub<br>`SHLOC2  ` = destination city (header has trailing spaces) |
| 12 | Suspicious values are present | 10 | SHVAL: `999999.99` → `(blank)` (implausible freight cost)<br>SHDT3: `2024-01-29 10:00` → `(blank)` (delivered before it was shipped)<br>SHQTY: `0` → `(blank)` (impossible weight) |
| 17 | Spreadsheet has dates in 1900, 1904, 1969, or 1970 | 20 | SHDT3: (SHDT3 (delivery timestamp) holds 1900/1904/1969/1970 epoch placeholders for undelivered shipments)<br>SHDT3: `1900-01-00` → `(blank)` (epoch placeholder for a shipment that is In Transit) |
| 19 | Numbers have been stored as text | 522 | SHVAL: `490/-` → `LKR 490.00` ('/-' suffix)<br>SHVAL: `560,00` → `LKR 560.00` (European format (decimal comma))<br>SHQTY: `0.9kg` → `0.87` (unit text glued to number)<br>SHMTR: `115 km` → `115` (number stored with 'km')<br>SHVAL: `470.00` → `LKR 470.00` (thousands separator)<br>SHVAL: `LKR2690` → `LKR 2690.00` (currency code glued to number) |

## 03. Warehouse stock - daily snapshots (Q3 2024)

`03_warehouse_stock_daily__zeros_for_missing_gaps_suspicious_values.csv`

- Data rows: **3,986**. 1 header row, UTF-8. One row per date x warehouse x SKU.
- Logged findings: 710 across 11 of the 19 issue types.
- Expected 3 x 15 x 92 = 4,140 rows; gaps + duplicate 2024-08-31 COL-01 snapshot give a different count.
- On Hand(t) = On Hand(t-1) + Inbound(t) - Outbound(t) holds on clean rows, which exposes the zeros and sentinels.

**What each column really is**

| header in file | true meaning |
|---|---|
| `snapshot_date` | snapshot date |
| `WH` | warehouse code |
| `SKU` | SKU |
| `Item Description` | item description |
| `On Hand` | closing stock on hand |
| `Inbound` | quantity received that day |
| `Outbound` | quantity issued that day |
| `Reorder Lvl` | reorder level |
| `last_counted` | timestamp of last physical count |
| `Counted By` | who did the last count |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 40 | Counted By: `?` → `(blank)` (missing)<br>Item Description: `NA` → `(blank)` (missing) |
| 2 | Zeros replace missing values | 566 | Reorder Lvl: `0` → `(blank)` (reorder level never configured at KDY-02: 0 should be null (420 rows))<br>GAL-03 Sundays: On Hand/Inbound/Outbound all 0 although stock was there the day before and after<br>On Hand: `0` → `(blank)` (Sunday WMS sync failed at GAL-03: 0 written instead of null (true val…)<br>Inbound: `0` → `(blank)` (Sunday WMS sync failed at GAL-03: 0 written instead of null (true val…)<br>Outbound: `0` → `(blank)` (Sunday WMS sync failed at GAL-03: 0 written instead of null (true val…)<br>Inbound: `0` → `(blank)` (movement feed outage: 0 written instead of null (true value 0)) |
| 3 | Data are missing you know should be there | 3 | KDY-02 has no rows at all for 2024-08-12 .. 2024-08-18 (whole week missing)<br>No warehouse has rows for 2024-09-15<br>SKU-1013 at GAL-03 vanishes after 2024-09-10 although it still had stock |
| 4 | Rows or values are duplicated | 15 | same snapshot loaded twice: duplicate of row 2641<br>same snapshot loaded twice: duplicate of row 2643<br>same snapshot loaded twice: duplicate of row 2645<br>same snapshot loaded twice: duplicate of row 2647 |
| 5 | Spelling is inconsistent | 32 | Item Description: `COCONUT OIL 1LTR` → `Coconut Oil 1L` (KDY-02 spells the item differently (83 rows))<br>Item Description: `WHITE SUGAR 1KG` → `White Sugar 1kg` (KDY-02 spells the item differently (84 rows))<br>Item Description: `RED LENTILS 1KG` → `Red Lentils (Dhal) 1kg` (KDY-02 spells the item differently (83 rows))<br>Item Description: `BASMATI RICE 5KG` → `Basmati Rice 5kg` (KDY-02 spells the item differently (84 rows)) |
| 6 | Name order is inconsistent | 20 | Counted By: `Dr. Nimal Perera` → `Nimal Perera` (honorific prefix (92 rows))<br>Counted By: `Perera, Nimal` → `Nimal Perera` (Last, First (184 rows))<br>Counted By: `Nimal A. Perera` → `Nimal Perera` (middle initial added (91 rows))<br>Counted By: `N. Perera` → `Nimal Perera` (initial + surname: first name not recoverable (92 rows)) |
| 7 | Date formats are inconsistent | 11 | snapshot_date: (snapshot_date: COL-01 = ISO, KDY-02 = DD-Mon-YY, GAL-03 = ISO in Jul-Aug then DD/MM/YYYY in Sep, plus stray formats)<br>snapshot_date: `45481` → `2024-07-08` (stray serial date format)<br>snapshot_date: `20240726` → `2024-07-26` (stray compact date format)<br>snapshot_date: `August 01, 2024` → `2024-08-01` (stray long date format) |
| 8 | Units are not specified | 3 | `On Hand` = no unit: units/packs, except SKU-1004 at COL-01 = kg (others count 5kg bags) and SKU-1009 at COL-01 = cartons of 24<br>`Inbound` = same unit problem as On Hand<br>`Outbound` = same unit problem as On Hand |
| 10 | Field names are ambiguous | 1 | `Reorder Lvl` = abbreviated 'Reorder Lvl'; same unit problem as On Hand |
| 12 | Suspicious values are present | 13 | On Hand: `-1` → `237` (integer-limit / sentinel value)<br>Outbound: `4294967295` → `16` (uint32 max sentinel) |
| 17 | Spreadsheet has dates in 1900, 1904, 1969, or 1970 | 6 | last_counted: `1970-01-01 05:30:00` → `(blank)` (never counted: unix epoch 0 shown in Sri Lanka time (+05:30) (273 rows))<br>last_counted: `1900-01-00 00:00` → `(blank)` (spreadsheet epoch placeholder) |

## 04. Regional sales summary FY2024 (finance pivot export)

`04_regional_sales_summary__totals_mismatch_coarse_bad_categories.csv`

- Data rows: **61**. 1 header row, UTF-8. Data rows are mixed with subtotal rows, a grand total, a published-figure row and a footnote.
- Logged findings: 261 across 11 of the 19 issue types.
- True unit is LKR million. Northern/Eastern blocks are LKR thousands, Export block is USD thousands at LKR 300/USD.
- True FY2024 revenue (= the published row) is 3,194.5 LKR mn.

**What each column really is**

| header in file | true meaning |
|---|---|
| `Region` | region (badly chosen, overlapping) |
| `Category` | product category |
| `Q1` | Q1 revenue |
| `Q2` | Q2 revenue |
| `Q3` | Q3 revenue |
| `Q4` | Q4 revenue |
| `FY Total` | full-year revenue |
| `YoY %` | year-on-year growth |
| `Notes` | analyst notes |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 11 | Region: `(blank)` → `Western` (merged-cell export: region only on first row of block (fill down))<br>Q4: `(blank)` → `23.9` (not reported yet) |
| 2 | Zeros replace missing values | 12 | Q1: `0` → `(blank)` (online sales not integrated until Q3: 0 means no data)<br>Q2: `0` → `(blank)` (online sales not integrated until Q3: 0 means no data)<br>Q1: `0` → `(blank)` (no data before Q3)<br>Q2: `0` → `(blank)` (no data before Q3) |
| 4 | Rows or values are duplicated | 2 | exact duplicate of row 16<br>One category row in the Kandy block is duplicated. |
| 5 | Spelling is inconsistent | 4 | Region: `CP` → `Central` (region spelled differently) |
| 8 | Units are not specified | 92 | `Q1` = no unit or currency anywhere in the header (mostly LKR mn; Northern/Eastern LKR 000; Export USD 000)<br>`YoY %` = 'YoY %' holds percents, fractions, signed numbers and spreadsheet errors<br>YoY %: `+13` → `12.8` (percent sign missing)<br>YoY %: `0.07` → `6.8` (fraction, not percent)<br>Q1: `19,500` → `19.5` (LKR '000 (not mn) with thousands separator)<br>Q2: `17,900` → `17.9` (LKR '000 (not mn) with thousands separator) |
| 9 | Categories are badly chosen | 50 | Region list mixes provinces, cities inside provinces (Colombo, Kandy), a channel (Online), a market (Export) and a catch-all.<br>Category: `Accessories/Other` → `Accessories/Other` (two things in one category)<br>Region: `Colombo` → `Colombo` (city that is part of Western (double counted))<br>Category: `Mobile Phones` → `Mobile Phones` (sub-category of Electronics listed as a peer)<br>Category: `Misc` → `Misc` (catch-all category)<br>Region: `Kandy` → `Kandy` (city that is part of Central (double counted)) |
| 11 | Provenance is not documented | 2 | `Notes` = free-text notes are the only provenance (prelim, per Dinesh's sheet, v3 FINAL (2)...)<br>No source system, extraction date, currency, unit or definition of revenue (gross/net, VAT) documented. |
| 12 | Suspicious values are present | 5 | YoY %: `#DIV/0!` → `(blank)` (spreadsheet error: no prior-year base) |
| 13 | Data are too coarse | 4 | Only quarter x region x category; YoY rounded to whole %, \|YoY\|<1 suppressed; cannot answer monthly/store/SKU questions.<br>YoY %: `<1%` → `-1.0` (suppressed / too coarse) |
| 14 | Totals differ from published aggregates | 30 | Published FY total 3,194.5 (LKR mn) vs Grand Total row 4,203.3: Colombo and Kandy are double counted, three subtotals are wrong (Southern omits its last row, Central +12.5 manual adj in Q1, Eastern adds its first row tw…<br>FY Total: `472.6` → `491.1` (FY Total != Q1+Q2+Q3+Q4 (stale value, LKR mn 472.6 vs 491.1))<br>Q1: `149.1` → `136.6` (subtotal != sum of its rows (149.1 vs 136.6 LKR mn))<br>FY Total: `620.1` → `607.6` (subtotal != sum of its rows)<br>Q2: `90.1` → `95.6` (subtotal != sum of its rows (90.1 vs 95.6 LKR mn))<br>Q3: `84.3` → `90.5` (subtotal != sum of its rows (84.3 vs 90.5 LKR mn)) |
| 19 | Numbers have been stored as text | 49 | Q1: `19,500` → `19.5` (LKR '000 (not mn) with thousands separator)<br>Q2: `17,900` → `17.9` (LKR '000 (not mn) with thousands separator)<br>Q3: `18,800` → `18.8` (LKR '000 (not mn) with thousands separator)<br>Q4: `24,200` → `24.2` (LKR '000 (not mn) with thousands separator)<br>FY Total: `80,400` → `80.4` (LKR '000 (not mn) with thousands separator)<br>Q1: `38,900` → `38.9` (; LKR '000 (not mn) with thousands separator) |

## 05. Product catalog / item master (CONFUSING HEADERS)

`05_CONFUSING_HEADERS_product_catalog__opaque_attribute_ids_excel_mangled_codes.csv`

- Data rows: **146**. 1 header row, UTF-8 (one brand is mojibake on purpose).
- Logged findings: 661 across 12 of the 19 issue types.
- Decoding: on clean rows ATTR_410_B is 55-75% of ATTR_410 (cost vs price); ATTR_117 is 13 digits starting 479 (Sri Lanka GS1); ATTR_621 looks like 0902.30 (HS chapter.heading).
- Good file for AI categorisation: real category is recoverable from ATTR_102@en_LK (name) even when ATTR_118 is junk.
- 6 products are listed twice under a new SKU; 5 rows are exact duplicates.

**What each column really is**

| header in file | true meaning |
|---|---|
| `ATTR_101` | SKU / item code (some mangled into dates or scientific notation) |
| `ATTR_117` | EAN-13 barcode |
| `ATTR_102@en_LK` | product name (English, Sri Lanka locale) |
| `ATTR_230` | brand |
| `ATTR_118` | category |
| `ATTR_118_1` | sub-category |
| `ATTR_305` | pack size |
| `ATTR_410` | selling price, LKR |
| `ATTR_410_B` | MISLEADING: unit COST in LKR, though the code looks like a second price list 'B' |
| `ATTR_512` | launch date |
| `ATTR_620` | supplier code (same 3 ID schemes as file 01) |
| `ATTR_621` | customs HS tariff code (next to the supplier code; both look like codes) |
| `ATTR_306` | size variant: clothing size, shoe size or pipe diameter |
| `ATTR_900` | lifecycle status |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 21 | ATTR_117: `(blank)` → `(blank)` (missing (true value: 4791560126168))<br>ATTR_118_1: `?` → `(blank)` (missing (true value: Paper))<br>ATTR_118_1: `(blank)` → `(blank)` (missing (true value: Lighting))<br>ATTR_117: `TBA` → `(blank)` (missing (true value: 4790421217533))<br>ATTR_118: `-` → `(blank)` (missing (true value: Dairy))<br>ATTR_118_1: `none` → `(blank)` (missing (true value: Spices)) |
| 2 | Zeros replace missing values | 5 | ATTR_410_B: `0` → `(blank)` (cost unknown, 0 entered (true 451.81) -> fake 100% margin) |
| 4 | Rows or values are duplicated | 12 | exact duplicate of row 60<br>same product as row 32 listed again under a new SKU<br>same product as row 17 listed again under a new SKU<br>same product as row 71 listed again under a new SKU<br>ATTR_117: `4797989732546` → `4798157620252` (barcode copied from a different product) |
| 5 | Spelling is inconsistent | 151 | ATTR_900: `active` → `Active` (status spelled differently)<br>ATTR_230: `HOMESHINE` → `HomeShine` (brand spelled differently)<br>ATTR_305: `10 ROLLS` → `10 rolls` (same size written differently)<br>ATTR_102@en_LK: `ceyfresh  chilli flakes 250g` → `Ceyfresh Chilli Flakes 250g` (spelled differently)<br>ATTR_118: `Drinks` → `Beverages` (synonym / overlapping category)<br>ATTR_102@en_LK: `HomeShine  Steel  Water Bot…` → `HomeShine Steel Water Bottl…` (extra spaces) |
| 7 | Date formats are inconsistent | 60 | ATTR_512: `42880` → `2017-05-25` (serial)<br>ATTR_512: `19/02/2024` → `2024-02-19` (dmy)<br>ATTR_512: `October 05, 2018` → `2018-10-05` (long)<br>ATTR_512: `20161114` → `2016-11-14` (compact)<br>ATTR_512: `17-Jan-2021` → `2021-01-17` (d-mon-y)<br>ATTR_512: `04/26/2020` → `2020-04-26` (mdy) |
| 8 | Units are not specified | 28 | `ATTR_305` = pack size unit sometimes missing<br>`ATTR_410` = no currency (LKR)<br>ATTR_305: `18` → `18W` (unit stripped (g? ml? kg?))<br>ATTR_306: `8` → `8` (shoe size system not stated (UK/US/EU?)) |
| 9 | Categories are badly chosen | 45 | ATTR_118_1: `Grocery` → `Spices` (sub-category just repeats a category)<br>ATTR_900: `Out of Stock` → `(blank)` (availability/flag mixed into lifecycle status)<br>ATTR_118: `New Arrivals` → `Home` (promotion/attribute used as category)<br>ATTR_118: `Uncategorized` → `Personal Care` (catch-all category) |
| 10 | Field names are ambiguous | 15 | `ATTR_101` = SKU / item code (some mangled into dates or scientific notation)<br>`ATTR_117` = EAN-13 barcode<br>`ATTR_102@en_LK` = product name (English, Sri Lanka locale)<br>`ATTR_230` = brand |
| 12 | Suspicious values are present | 13 | ATTR_410: `99999` → `2220.00` (implausible price)<br>ATTR_117: `9999999999999` → `4798072244007` (placeholder barcode)<br>ATTR_410_B: `#REF!` → `588.22` (spreadsheet error exported as value) |
| 17 | Spreadsheet has dates in 1900, 1904, 1969, or 1970 | 15 | ATTR_512: `1900-01-01` → `(blank)` (epoch placeholder (true 2024-05-03)) |
| 18 | Text has been converted to numbers | 203 | Codes that were opened in Excel: ATTR_101 SKU (lost zeros, dates like 3-Dec, 1.00E+10), ATTR_117 barcode (4.79123E+12), ATTR_621 HS code (902.3), ATTR_306 size (2-Jan)<br>ATTR_621: `904.12` → `0904.12` (HS code read as a number: leading/trailing zeros lost)<br>ATTR_101: `15-Mar` → `MAR15` (spreadsheet turned the code into a date)<br>ATTR_117: `4.79776E+12` → `4797756299807` (scientific notation: last digits lost, unrecoverable)<br>ATTR_620: `100336` → `0000100336` (leading zeros stripped)<br>ATTR_101: `2.00E+12` → `2E12` (spreadsheet read the code as scientific notation) |
| 19 | Numbers have been stored as text | 93 | ATTR_410: `0.4k` → `419.99` ('k' suffix, precision lost)<br>ATTR_410: `780,00` → `780.00` (European format (decimal comma))<br>ATTR_410: `0.03L` → `3080.00` (in lakhs (x100,000), precision lost)<br>ATTR_410: `Rs 800/=` → `800.00` (Sri Lankan '/=' suffix)<br>ATTR_410: ` 120.00 ` → `120.00` (padded with spaces)<br>ATTR_410: `Rs. 149.99` → `149.99` (currency prefix) |

## 06. ERP purchase-order lines (CONFUSING HEADERS)

`06_CONFUSING_HEADERS_erp_po_lines__cryptic_misleading_columns.csv`

- Data rows: **285**. UTF-8 WITH BOM. 1 header row, one header has an embedded newline (quoted). 26 columns.
- Logged findings: 2,415 across 14 of the 19 issue types.
- Decoding checks that work on clean rows: Price = ප්‍රමාණය x Amount x (1 - discount); Value (USD) = 0.18 x Price for LKR lines;
- DT <= தேதி; Date_ is blank/epoch exactly when Recv Qty = 0 and STAT is A/X.

**What each column really is**

| header in file | true meaning |
|---|---|
| `Unnamed: 0` | leftover pandas index (0-based, with gaps where rows were filtered) - meaningless |
| `DOC` | purchase order number |
| `ITM` | PO line item number (10, 20, 30 ...) |
| `LIFNR` | vendor/supplier ID (SAP LIFNR, 10-digit zero padded; zeros often stripped) |
| `Vendor` | MISLEADING: the BUYER (purchasing officer) who raised the PO, not the vendor |
| `Name` | vendor company name |
| `MAT` | material code |
| `Description` | material description |
| `ප්‍රමාණය` | order quantity (header is Sinhala for 'quantity/amount') |
| `UoM` | unit of measure of the quantity |
| `Price` | MISLEADING: net LINE TOTAL = qty x unit price x (1 - discount), not a unit price |
| `Amount` | MISLEADING: UNIT PRICE, not a total amount |
| `Value (USD)` | MISLEADING: VAT amount in the line currency (18% of line total for LKR lines, 0 for USD imports) - not USD |
| `CUR` | currency of Price/Amount/Value |
| `DT` | PO creation date |
| `தேதி` | requested delivery date (header is Tamil for 'date') |
| `Date_` | actual goods-receipt date |
| `Recv\nQty` | quantity received so far |
| `WERKS` | receiving plant (1000 Colombo, 1100 Biyagama, 2000 Kandy) |
| `STAT` | line status: A=open, B=partially received, C=closed, X=cancelled (plus free-text variants) |
| `(empty)` | payment terms (column has NO header) |
| `2` | line discount % (header '2' is a stray value) |
| `x` | urgent/expedite flag |
| `REF` | vendor's invoice number for the receipt |
| `REF.1` | purchase requisition number |
| `Column1` | free-text remarks (Power Query default column name) |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 102 | UoM: `nan` → `(blank)` (missing (true value: EA))<br>CUR: `(blank)` → `(blank)` (missing (true value: LKR))<br>2: `(blank)` → `0` (blank = 0?)<br>CUR: `--` → `(blank)` (missing (true value: USD))<br>UoM: `unknown` → `(blank)` (missing (true value: KG))<br>UoM: `(blank)` → `(blank)` (missing (true value: ROL)) |
| 2 | Zeros replace missing values | 104 | Recv\nQty: `0` → `(blank)` (nothing received yet/cancelled: 0 instead of null) |
| 4 | Rows or values are duplicated | 8 | same PO line (DOC+ITM) as row 38: only the index column differs<br>same PO line (DOC+ITM) as row 58: only the index column differs<br>same PO line (DOC+ITM) as row 73: only the index column differs<br>same PO line (DOC+ITM) as row 135: only the index column differs |
| 5 | Spelling is inconsistent | 314 | UoM: `ea` → `EA` (unit of measure spelled differently)<br>STAT: `CLSD` → `C` (status code mixed with words/numbers)<br>(blank header, col 21): `45 days` → `Net 45` (payment terms written differently)<br>CUR: `LKR ` → `LKR` (currency code spelled differently)<br>Name: `CEYLON PACKAGING INDUSTRIES` → `Ceylon Packaging Industries` (vendor name spelled differently)<br>Vendor: `janani selvaraj` → `Janani Selvaraj` (lower-cased name) |
| 6 | Name order is inconsistent | 153 | Vendor: `SELVARAJ Janani` → `Janani Selvaraj` (SURNAME First)<br>Vendor: `Selvaraj, Janani` → `Janani Selvaraj` (Last, First)<br>Vendor: `J. Selvaraj` → `Janani Selvaraj` (initial + surname: first name not recoverable)<br>Vendor: `Prof. Imran Marikar` → `Imran Marikar` (honorific prefix)<br>Vendor: `Jayasinghe R.` → `Ruwan Jayasinghe` (surname + initial: first name not recoverable)<br>Vendor: `K.J. Selvaraj` → `Janani Selvaraj` (Sri Lankan initials format: first name not recoverable) |
| 7 | Date formats are inconsistent | 539 | DT: `19.06.2024` → `2024-06-19` (dot)<br>தேதி: `06/30/2024` → `2024-06-30` (mdy)<br>Date_: `02-Jul-24` → `2024-07-02` (d-mon-yy)<br>தேதி: `20240719` → `2024-07-19` (compact)<br>DT: `19/06/2024` → `2024-06-19` (dmy)<br>தேதி: `45475` → `2024-07-02` (serial) |
| 8 | Units are not specified | 107 | Value (USD): ('Value (USD)' is VAT in the line currency (mostly LKR); quantities switch between KG and MT)<br>2: `0.05` → `5` (fraction vs percent)<br>ප්‍රමාණය: `1` → `1000` (quantity in metric tonnes on this line (UoM=MT), kg elsewhere)<br>(blank header, col 21): `30` → `Net 30` (payment terms written differently) |
| 9 | Categories are badly chosen | 324 | x: `yes` → `Y` (flag encoded inconsistently)<br>STAT: `DEL` → `X` (status code mixed with words/numbers) |
| 10 | Field names are ambiguous | 27 | `Unnamed: 0` = leftover pandas index (0-based, with gaps where rows were filtered) - meaningless<br>`DOC` = purchase order number<br>`ITM` = PO line item number (10, 20, 30 ...)<br>`LIFNR` = vendor/supplier ID (SAP LIFNR, 10-digit zero padded; zeros often stripped) |
| 11 | Provenance is not documented | 1 | File passed through SAP (LIFNR/WERKS names), pandas ('Unnamed: 0' index, 10.0 floats, '.1' suffix on REF.1) and Power Query ('Column1'), plus Sinhala/Tamil headers from a localised template. No source, extract date or f… |
| 12 | Suspicious values are present | 7 | Amount: `0.01` → `4779.01` (placeholder unit price)<br>Price: `-98518.23` → `98518.23` (negative line total on a normal PO line)<br>ප්‍රමාණය: `99999` → `10` (placeholder quantity) |
| 17 | Spreadsheet has dates in 1900, 1904, 1969, or 1970 | 47 | Date_: `1970-01-01` → `(blank)` (epoch placeholder: nothing received) |
| 18 | Text has been converted to numbers | 431 | LIFNR: `100042` → `0000100042` (leading zeros stripped)<br>WERKS: `1100.0` → `1100` (int became float (pandas NaN artefact))<br>REF.1: `3.01412E+11` → `301412147089` (scientific notation: PR digits lost)<br>ITM: `10.0` → `10` (int became float (pandas NaN artefact))<br>REF: `3.47425E+11` → `347425393974` (scientific notation: invoice no digits lost)<br>DOC: `4.50001E+09` → `4500012046` (scientific notation: PO digits lost (recoverable only via other lines…) |
| 19 | Numbers have been stored as text | 251 | Price: `4,500.00` → `4500.00` (thousands separator)<br>2: `0%` → `0` (percent sign stored as text)<br>Amount: `Rs. 248,730.00` → `248730.00` (currency prefix)<br>Price: ` 49782.38 ` → `49782.38` (padded with spaces)<br>Price: `Rs. 2,341,714.90` → `2341714.90` (currency prefix) |

## 07. Delivery-driver roster + September payroll (CONFUSING HEADERS)

`07_CONFUSING_HEADERS_driver_roster_payroll__two_row_header_duplicate_names.csv`

- Data rows: **127**. UTF-8. TWO header rows (group row + sub-label row). Last row is a TOTAL row.
- Logged findings: 1,032 across 14 of the 19 issue types.
- On clean rows: Total = Basic + Allow. + OT(amount); OT(amount) = OT(hours) x Basic/240 x 1.5.
- Dt columns are DOB, join date, licence expiry in that order: DOB years 1965-2000, joins 2010-2024, expiries 2024-2032.

**What each column really is**

| header in file | true meaning |
|---|---|
| `#` | row number from the original sheet (gaps where rows were deleted) - not an ID |
| `Driver / Name` | driver full name, in inconsistent order |
| `Name` | same driver's 'name with initials' (Sri Lankan official format) |
| `Code` | employee code (DRV-####) |
| `Contact / Tel` | driver's own mobile |
| `Tel` | EMERGENCY contact number (same header as driver mobile) |
| `Pay (Sep) / Basic` | basic monthly salary, LKR |
| `Allow.` | fuel + meal allowance, LKR |
| `OT` | overtime HOURS |
| `OT` | overtime AMOUNT, LKR (same header as hours) |
| `Total` | gross pay = Basic + Allow. + OT amount |
| `Dates / Dt` | date of BIRTH |
| `Dt` | date JOINED |
| `Dt` | driving-licence EXPIRY date |
| `Vehicle / No` | assigned vehicle registration number |
| `Type` | vehicle type |
| `Status / Type` | employment type (same header as vehicle type) |
| `?` | currently active? (header is just "?") |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 22 | Dt: `(blank)` → `(blank)` (missing (true value: 2027-09-18))<br>Tel: `N/A` → `(blank)` (missing (true value: 0707872841))<br>Tel: `(blank)` → `(blank)` (missing (true value: 0722875570))<br>Tel: `-` → `(blank)` (missing (true value: 0750233671))<br>Dates / Dt: `-` → `(blank)` (missing (true value: 1999-09-09))<br>Tel: `N/A` → `(blank)` (missing (true value: 0718537566)) |
| 2 | Zeros replace missing values | 30 | Allow.: `0` → `10500.00` (Kandy allowance sheet never merged: 0 instead of missing) |
| 4 | Rows or values are duplicated | 6 | exact duplicate of row 71<br>same driver as row 122 (copy-pasted again, code written differently)<br>same driver as row 27 (copy-pasted again, code written differently)<br>same driver as row 120 (copy-pasted again, code written differently) |
| 5 | Spelling is inconsistent | 179 | Driver / Name: `thilini kanagaratnam` → `Thilini Kanagaratnam` (lower-cased name)<br>?: `Yes` → `Y` (flag encoded differently)<br>Status / Type: `PERMANENT` → `Permanent` (overlapping / inconsistent employment type)<br>Code: `1003` → `DRV-1003` (prefix dropped)<br>Code: `D1008` → `DRV-1008` (different prefix)<br>Type: `M/C` → `Motorcycle` (overlapping / inconsistent vehicle type) |
| 6 | Name order is inconsistent | 83 | Driver / Name: `Ismail M.` → `Malini Ismail` (surname + initial: first name not recoverable)<br>Driver / Name: `N.P.P. Ismail` → `Priyanka Ismail` (Sri Lankan initials format: first name not recoverable)<br>Driver / Name: `Thilini K. Mendis` → `Thilini Mendis` (middle initial added)<br>Name: `Karunaratne S.H.N.` → `S.H.N. Karunaratne` (surname before initials)<br>Driver / Name: `Herath, Gayan` → `Gayan Herath` (Last, First)<br>Driver / Name: `Prof. Suresh Jayasinghe` → `Suresh Jayasinghe` (honorific prefix) |
| 7 | Date formats are inconsistent | 270 | Dates / Dt: `25079` → `1968-08-29` (serial)<br>Dt: `05/11/2020` → `2020-05-11` (mdy)<br>Dates / Dt: `10/09/1966` → `1966-09-10` (dmy)<br>Dt: `27/09/2023` → `2023-09-27` (dmy)<br>Dt: `April 22, 2024` → `2024-04-22` (long)<br>Dates / Dt: `26/1/93` → `1993-01-26` (d/m/yy (2-digit year: century ambiguous)) |
| 8 | Units are not specified | 12 | Pay (Sep) / OT: (OT appears twice: first = hours, second = LKR amount; Basic sometimes in thousands)<br>Pay (Sep) / Basic: `87.5` → `87500.00` (in thousands (85 = 85,000)) |
| 9 | Categories are badly chosen | 52 | Type: `Canter` → `Small lorry` (overlapping / inconsistent vehicle type)<br>Status / Type: `Contract/Casual` → `Contract` (overlapping / inconsistent employment type)<br>?: `On leave` → `N` (status mixed into flag) |
| 10 | Field names are ambiguous | 19 | ` \|\| #` = row number from the original sheet (gaps where rows were deleted) - not an ID<br>`Driver \|\| Name` = driver full name, in inconsistent order<br>` \|\| Name` = same driver's 'name with initials' (Sri Lankan official format)<br>` \|\| Code` = employee code (DRV-####) |
| 12 | Suspicious values are present | 8 | Tel: `072-3491671` → `0748977534` (emergency contact = driver's own number)<br>OT: `999` → `8` (744 = every hour of a 31-day month / 999 placeholder)<br>Dt: `2027-09-12` → `(blank)` (joining date in the future) |
| 14 | Totals differ from published aggregates | 13 | Total: `94062.50` → `101562.50` (gross != Basic + Allow. + OT (stale/partial))<br>Pay (Sep) / Basic: `4428300.00` → `9352500.00` (SUM() skipped cells stored as text and counted duplicate rows)<br>Allow.: `489500.00` → `900500.00` (SUM() skipped cells stored as text and counted duplicate rows)<br>OT: `539593.75` → `1195687.50` (SUM() skipped cells stored as text and counted duplicate rows)<br>Total: `6944656.25` → `11448687.50` (SUM() skipped cells stored as text and counted duplicate rows) |
| 17 | Spreadsheet has dates in 1900, 1904, 1969, or 1970 | 22 | Dt: `00/01/1900` → `(blank)` (epoch placeholder (true 2029-05-26))<br>Dates / Dt: `1/1/1970` → `(blank)` (epoch placeholder (true 1979-01-26)) |
| 18 | Text has been converted to numbers | 60 | Tel: `753059145` → `0753059145` (leading 0 dropped)<br>Vehicle / No: `Dec-24` → `12-2024` (old-style plate read as a month-year date)<br>Contact / Tel: `714376691` → `0714376691` (leading 0 dropped)<br>Contact / Tel: `9.47651E+10` → `0765067179` (scientific notation: digits lost) |
| 19 | Numbers have been stored as text | 256 | Pay (Sep) / Basic: `Rs 85,000/=` → `85000.00` (Sri Lankan '/=' suffix)<br>Total: `Rs 97,750/=` → `97750.00` (Sri Lankan '/=' suffix)<br>Pay (Sep) / Basic: `82,500.00` → `82500.00` (thousands separator)<br>Allow.: `7,500.00` → `7500.00` (thousands separator)<br>OT: `18.6k` → `18562.50` ('k' suffix, precision lost)<br>OT: `Rs. 6,562.50` → `6562.50` (currency prefix) |

## 08. Cold-chain sensor log (CONFUSING HEADERS)

`08_CONFUSING_HEADERS_coldchain_sensor_log__cryptic_columns_sentinel_values.csv`

- Data rows: **1,759**. 1 header row, UTF-8 (degree signs in some cells).
- Logged findings: 2,978 across 14 of the 19 issue types.
- 5 loggers x 4 days x 15-min = 1,920 expected slots. Fridge set-point 2-8 deg C (35.6-46.4 deg F for TL-0045).
- Trap: one-letter headers invite "t = temperature"; t is the timestamp and v1 is the temperature.

**What each column really is**

| header in file | true meaning |
|---|---|
| `id` | per-device reading sequence number (NOT unique; TL-0044 restarts at 1 after a reboot) |
| `dev` | logger/device ID, written several ways |
| `t` | reading TIMESTAMP (not temperature!): format and timezone differ per device |
| `v1` | air temperature: deg C, except TL-0045 which reports deg F |
| `v2` | relative humidity: %, except TL-0043 which reports a 0-1 fraction |
| `v3` | battery: volts, except TL-0046 which reports millivolts |
| `s` | cellular signal: RSSI dBm (negative), except TL-0045 which reports modem CSQ 0-31 (99 = unknown) |
| `f` | status bitmask: bit0 = door open, bit1 = temperature alarm; written as int, hex or words |
| `loc` | GPS position 'lat,lon' in ONE field (sometimes swapped, DMS, rounded or 0,0) |
| `ref` | shipment reference (same scheme as file 02 SHKEY) |
| `fw` | firmware version (1.10 got turned into 1.1) |
| `z` | second probe: product core temperature in deg C, only on dual-probe loggers TL-0042 and TL-0046 |
| `Unnamed: 12` | empty spill-over column; 'ALM' typed in by an operator on some excursion rows |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 42 | loc: `--` → `(blank)` (missing (true value: 6.8983,79.8733))<br>loc: `-` → `(blank)` (missing (true value: 6.9781,79.9695))<br>loc: `null` → `(blank)` (missing (true value: 6.9805,79.9743))<br>loc: `?` → `(blank)` (missing (true value: 6.9926,80.0005))<br>loc: `(blank)` → `(blank)` (missing (true value: 6.7177,79.9484))<br>loc: `(blank)` → `(blank)` (missing (true value: 7.6015,79.9021)) |
| 2 | Zeros replace missing values | 13 | s: `0` → `(blank)` (0 = no signal reading (real values are negative dBm))<br>v3: `0` → `(blank)` (0 = battery not read) |
| 3 | Data are missing you know should be there | 2 | TL-0043: no readings 2024-05-11 02:00-07:45 UTC (24 x 15-min slots), then 8 earlier readings are re-sent<br>TL-0046 stops at 2024-05-12 14:00 UTC (battery died; v3 trends down beforehand); ~1% random single readings dropped |
| 4 | Rows or values are duplicated | 14 | exact duplicate of row 200<br>exact duplicate of row 405<br>exact duplicate of row 556<br>re-sent after the TL-0043 modem outage: duplicate of row 479 |
| 5 | Spelling is inconsistent | 910 | fw: `v2.0.1` → `2.0.1` ('v' prefix)<br>dev: `tl42` → `TL-0042` (device ID written differently)<br>loc: `6°53'42.8"N 79°52'28.6"E` → `6.8952,79.8746` (degrees-minutes-seconds text)<br>loc: `79.8834,6.8715` → `6.8715,79.8834` (lat/lon swapped) |
| 7 | Date formats are inconsistent | 5 | t: (rows from TL-0042: t is ISO 8601 UTC (canonical))<br>t: (rows from TL-0043: t is local Sri Lanka time (+05:30) without offset)<br>t: (rows from TL-0044: t is DD/MM/YYYY HH:MM local time (+05:30))<br>t: (rows from TL-0045: t is unix epoch SECONDS) |
| 8 | Units are not specified | 1 | v1: (TL-0045 v1 in deg F; TL-0043 v2 as fraction; TL-0046 v3 in mV; TL-0045 s in CSQ units - nothing in the file says so) |
| 9 | Categories are badly chosen | 622 | f: `0x00` → `0` (hex instead of int)<br>f: `OK` → `0` (word instead of bitmask) |
| 10 | Field names are ambiguous | 13 | `id` = per-device reading sequence number (NOT unique; TL-0044 restarts at 1 after a reboot)<br>`dev` = logger/device ID, written several ways<br>`t` = reading TIMESTAMP (not temperature!): format and timezone differ per device<br>`v1` = air temperature: deg C, except TL-0045 which reports deg F |
| 12 | Suspicious values are present | 65 | v2: `255` → `(blank)` (uint8 max = read error)<br>loc: `0,0` → `(blank)` ('null island' 0,0 = no GPS fix)<br>v1: `-127.0` → `(blank)` (DS18B20 "sensor disconnected" sentinel)<br>v1: `85.0` → `(blank)` (DS18B20 power-on-reset value, not a real reading)<br>v1: `-3276.8` → `(blank)` (int16/10 overflow)<br>s: `99` → `(blank)` (modem CSQ 99 = 'not known') |
| 13 | Data are too coarse | 384 | loc: `7.3,80.6` → `7.2909,80.6337` (rounded to 0.1 deg (~11 km)) |
| 17 | Spreadsheet has dates in 1900, 1904, 1969, or 1970 | 8 | t: `01/01/1970 00:00` → `2024-05-12T09:30:00Z` (clock reset to unix epoch after reboot (true time recoverable from se…) |
| 18 | Text has been converted to numbers | 893 | fw: `1.1` → `1.10` (1.10 read as a number)<br>ref: `493` → `SHP-24-000493` (numeric part only, zeros lost) |
| 19 | Numbers have been stored as text | 6 | v1: `4,7` → `4.7` (temperature stored as text) |

## 09. POS transaction lines - truncated at 65,536 rows

`09_pos_transactions__truncated_at_65536_rows_excel97_limit.csv`

- Data rows: **65,535**. 1 header row + 65,535 data rows, UTF-8.
- Logged findings: 578 across 14 of the 19 issue types.
- The single most important finding is truncation: row count = old Excel limit and the period is incomplete.

**What each column really is**

| header in file | true meaning |
|---|---|
| `fiscal_period` | fiscal period label |
| `txn_id` | transaction ID (store-date-seq) |
| `line` | line i of n (mangled into a date) |
| `txn_datetime` | transaction time |
| `store` | store code |
| `cashier` | cashier |
| `sku` | SKU |
| `qty` | quantity |
| `unit_price` | unit price LKR |
| `discount` | discount |
| `line_total` | line total LKR |
| `payment_method` | payment method |
| `customer_phone` | loyalty customer mobile |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 130 | cashier: `unknown` → `(blank)` (missing) |
| 4 | Rows or values are duplicated | 180 | double-posted line: duplicate of row 310<br>double-posted line: duplicate of row 720<br>double-posted line: duplicate of row 813<br>double-posted line: duplicate of row 1690 |
| 5 | Spelling is inconsistent | 16 | store: `Colombo 03` → `COL03` (store name instead of / besides code (2266 rows))<br>payment_method: `LankaQR` → `QR` (payment label overlaps / inconsistent (1184 rows))<br>store: `Kollupitiya` → `COL03` (store name instead of / besides code (942 rows))<br>payment_method: `CASH` → `Cash` (payment label overlaps / inconsistent (3709 rows)) |
| 6 | Name order is inconsistent | 7 | cashier: `Samarasinghe Priyanka` → `Priyanka Samarasinghe` (Last First (no comma) (3577 rows))<br>cashier: `R.M.H.P. de Silva` → `Priyanka de Silva` (Sri Lankan initials format: first name not recoverable (3770 rows))<br>cashier: `WIJESINGHE Ravi` → `Ravi Wijesinghe` (SURNAME First (3572 rows))<br>cashier: `Mendis, Kumaran` → `Kumaran Mendis` (Last, First (3478 rows)) |
| 7 | Date formats are inconsistent | 1 | txn_datetime: (Excel rewrote timestamps as US M/D/YYYY H:MM (seconds lost); 2/1/2024 is 1 Feb, not 2 Jan) |
| 8 | Units are not specified | 2 | discount: (discount is an LKR amount everywhere except GAL01, where it is a '10%' string)<br>qty: (VEG-* SKUs are sold by weight: qty is kg there, units elsewhere) |
| 9 | Categories are badly chosen | 7 | payment_method: `Credit Card` → `Card` (payment label overlaps / inconsistent (1201 rows))<br>payment_method: `Debit` → `Card` (payment label overlaps / inconsistent (1139 rows))<br>payment_method: `Master` → `Card` (payment label overlaps / inconsistent (1188 rows))<br>payment_method: `Card/Cash` → `Card` (payment label overlaps / inconsistent (1092 rows)) |
| 12 | Suspicious values are present | 50 | qty: `-1` → `1` (implausible quantity)<br>customer_phone: `123456789` → `(blank)` (placeholder phone) |
| 13 | Data are too coarse | 1 | txn_datetime: (txn_datetime only has minute resolution (Excel dropped the seconds): lines and transactions within the same minute cannot be ordered) |
| 14 | Totals differ from published aggregates | 130 | line_total: `3820.00` → `3720.00` (line_total != qty x unit_price - discount) |
| 15 | Spreadsheet has 65536 rows | 1 | Exactly 65,536 rows incl. header (Excel 97-2003 sheet limit). Data stops at 2024-01-30 15:44 in the middle of GAL01-20240130-0101 (line 1 of 4) although fiscal_period says 2024-Q1 (should run to 2024-03-31). Ask for the… |
| 17 | Spreadsheet has dates in 1900, 1904, 1969, or 1970 | 50 | txn_datetime: `1/1/1970 5:34` → `2024-01-17 09:04` (terminal clock reset: unix epoch in local time) |
| 18 | Text has been converted to numbers | 2 | line: (Excel turned 'line i/n' into a date: '3-Feb' means line 2 of 3 (day = lines in txn, month = line no.))<br>customer_phone: (customer_phone lost its leading 0 everywhere (771234567 = 0771234567)) |
| 19 | Numbers have been stored as text | 1 | unit_price: (KDY01 rows store unit_price as text with 'Rs.' prefix) |

## 10. Store x day sales matrix - truncated at 255 columns

`10_store_daily_sales_wide__truncated_at_255_columns_numbers_app.csv`

- Data rows: **39**. 1 header row, UTF-8, 255 columns.
- Logged findings: 394 across 12 of the 19 issue types.
- Month header formats: Jan = ISO; Feb = D-Mon-YY; Mar = Excel serial number; Apr = MM/DD/YYYY (US); May = DD/MM/YYYY; Jun = Mon D, no year; Jul = DD.MM. no year; Aug = D/M no year; Sep = YYYYMMDD.

**What each column really is**

| header in file | true meaning |
|---|---|
| `Store Code` | store code (4-digit, zeros often stripped) |
| `Store Name` | store name |
| `Region` | region (badly chosen) |
| `<252 date headers>` | daily net sales for that date; header format changes each month (see notes) |

**Problems planted**

| # | issue | count | examples (`dirty` → expected) or finding |
|---|---|---|---|
| 1 | Values are missing | 69 | 2024-01-03: `CLOSED` → `(blank)` (missing / text in numeric column)<br>2024-01-16: `(blank)` → `(blank)` (missing / text in numeric column)<br>45352: `(blank)` → `(blank)` (missing / text in numeric column)<br>16/8: `CLOSED` → `(blank)` (missing / text in numeric column)<br>23/05/2024: `#N/A` → `(blank)` (spreadsheet lookup error)<br>24/8: `(blank)` → `(blank)` (missing / text in numeric column) |
| 2 | Zeros replace missing values | 39 | 21/05/2024: `0` → `(blank)` (POS sync failed for every store this day: 0 instead of missing (true …) |
| 3 | Data are missing you know should be there | 1 | No column for 2024-06-30 (a whole day missing between Jun 29 and Jul 1). |
| 4 | Rows or values are duplicated | 2 | same store as row 2, listed again with a differently formatted code<br>2024-03-10 appears twice (columns 73 and 74, both with header 45361), values differ slightly. |
| 5 | Spelling is inconsistent | 21 | Region: `WP` → `Western` (region spelled differently)<br>Store Name: `STORE - COLOMBO 03 2` → `Store - Colombo 03 2` (store name written differently) |
| 7 | Date formats are inconsistent | 190 | `1-Feb-24` = date header in D-Mon-YY format = 2024-02-01<br>`2-Feb-24` = date header in D-Mon-YY format = 2024-02-02<br>`3-Feb-24` = date header in D-Mon-YY format = 2024-02-03<br>`4-Feb-24` = date header in D-Mon-YY format = 2024-02-04 |
| 8 | Units are not specified | 2 | this store reports LKR '000, every other store reports LKR<br>No currency/unit anywhere; most stores LKR, some LKR thousands. |
| 9 | Categories are badly chosen | 6 | Region: `Online` → `Western` (channel/ownership used as region)<br>Region: `Metro` → `Western` (city/zone used as region) |
| 12 | Suspicious values are present | 13 | 2024-01-28: `9999999` → `(blank)` (sentinel / impossible value (true 232200))<br>45381: `-1` → `(blank)` (sentinel / impossible value (true 863200))<br>04/21/2024: `9999999` → `(blank)` (sentinel / impossible value (true 481400))<br>18/05/2024: `9999999` → `(blank)` (sentinel / impossible value (true 1251900))<br>45365: `-1` → `(blank)` (sentinel / impossible value (true 283400))<br>Jun 5: `-1` → `(blank)` (sentinel / impossible value (true 161300)) |
| 16 | Spreadsheet has 255 columns | 1 | Exactly 255 columns (Apple Numbers limit). Daily columns stop at 2024-09-08 although the sheet is a 2024 store x day matrix; Q4 and any total column were cut off. |
| 18 | Text has been converted to numbers | 44 | `45352` = date header in Excel serial number format = 2024-03-01<br>`45353` = date header in Excel serial number format = 2024-03-02<br>`45354` = date header in Excel serial number format = 2024-03-03<br>`45355` = date header in Excel serial number format = 2024-03-04<br>Store Code: `38` → `0038` (leading zeros stripped) |
| 19 | Numbers have been stored as text | 6 | values stored as text (thousands separators or Rs prefix)<br>values stored as text (thousands separators or Rs prefix)<br>values stored as text (thousands separators or Rs prefix)<br>values stored as text (thousands separators or Rs prefix) |

