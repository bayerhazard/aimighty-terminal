import duckdb, time, os, resource, sys

ROWS = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
OUT = sys.argv[2] if len(sys.argv) > 2 else "big.xlsx"

con = duckdb.connect()
con.execute("INSTALL excel; LOAD excel;")
t0 = time.time()
con.execute(f"""
COPY (
  SELECT
    i                                                    AS id,
    (i % 5000)                                           AS customer_id,
    'Region ' || (i % 24)                                AS region,
    'Product ' || (i % 240)                              AS product,
    'SKU-' || lpad((i % 9999)::VARCHAR, 5, '0')          AS sku,
    (i % 97) + 1                                         AS quantity,
    round(((i * 37) % 100000) / 100.0, 2)                AS unit_price,
    round((((i * 37) % 100000) / 100.0) * ((i % 97) + 1), 2) AS line_total,
    (DATE '2024-01-01' + ((i % 730)::INTEGER * INTERVAL 1 DAY)) AS order_date,
    'Supplier ' || (i % 96)                              AS supplier,
    'WH-' || lpad((i % 12)::VARCHAR, 2, '0')             AS warehouse,
    (['EUR','USD','GBP','CHF'])[1 + (i % 4)]             AS currency,
    (['new','processing','shipped','invoiced','paid','cancelled'])[1 + (i % 6)] AS status,
    round((i % 15) / 100.0, 2)                           AS discount_rate,
    round((((i * 37) % 100000) / 100.0) * 0.19, 2)       AS vat_amount,
    ('Note for row ' || i || ' — follow-up required, contact the regional account manager before the next quarterly review')  AS comment,
    ('https://erp.example.internal/orders/' || i)        AS order_url,
    ((i % 2) = 0)                                        AS is_priority
  FROM range({ROWS}) t(i)
) TO '{OUT}' (FORMAT xlsx, HEADER true)
""")
size = os.path.getsize(OUT)
print(f"rows={ROWS} file={size/1e6:.1f} MB write={time.time()-t0:.1f}s")
print("peak_rss_mb", round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024, 1))
