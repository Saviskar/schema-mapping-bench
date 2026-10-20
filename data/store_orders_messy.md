# store_orders_messy.csv

Sales line items from four stores, September 2026. One row per product per transaction. 26 rows, 20 columns.

| Column | Meaning | Example | Blank rows |
|---|---|---|---|
| `txn_id` | Transaction (receipt) ID, repeated on every line of the same checkout. Format `T-YYMMDD-NNNN` | `T-260902-0003` | 0 |
| `line_no` | Line number within the transaction | `1`, `2`, `3` | 0 |
| `loc` | Name of the store where the sale happened | `Downtown` | 1 |
| `loc_cd` | Internal store code | `DT01` | 0 |
| `region` | Sales region the store belongs to | `Central` | 2 |
| `item_ref` | Store SKU of the item sold | `SKU-1001` | 1 |
| `vendor_part_no` | Supplier's part number for the item | `VP-4471-A` | 2 |
| `item_desc` | Short product name | `Wireless Mouse` | 1 |
| `pcs` | Units sold on this line | `4` | 1 |
| `pack_sz` | Units per case the item is stocked in (inventory, not the sale) | `12` | 0 |
| `qty_rtn` | Units later returned from this line. Blank means none | `1` | 19 |
| `amt_ea` | Price charged per unit, before discount | `19.99` | 2 |
| `cost_ea` | What the store pays the supplier per unit | `9.40` | 4 |
| `msrp` | Manufacturer's suggested retail price per unit | `24.99` | 5 |
| `line_amt` | Line total after discount, before tax | `75.96` | 0 |
| `adj_pct` | Discount on the transaction, in percent. Blank means not recorded | `10` | 9 |
| `tax_pct` | Store's sales tax rate, in percent | `8.875` | 1 |
| `doc_dt` | Date the sale happened | `2026-09-02` | 1 |
| `ship_dt` | Date the order shipped. Blank means taken in store | `2026-09-03` | 15 |
| `upd_ts` | When the record was last edited (UTC), not when the sale happened | `2026-09-07T05:00:00Z` | 2 |

## How the columns relate

- `line_amt = pcs × amt_ea × (1 − adj_pct / 100)`, rounded to 2 decimals. Tax and returns are not included.
- `adj_pct` and `tax_pct` are the same on every line of a transaction.
- `loc`, `loc_cd` and `region` always go together: Downtown/DT01/Central, Airport/AP02/East, Mall/ML03/West, Riverside/RS04/North.
- `cost_ea` < `amt_ea` ≤ `msrp` for every product.
- `pcs` has a blank, so pandas reads it as `float64` (`4.0`).
