import time, resource, os, sys

F = "big.xlsx"


def rss():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)


def step(name, fn):
    t0 = time.time()
    out = fn()
    print(f"{name}: {time.time()-t0:.1f}s peak_rss={rss()} MB -> {out}", flush=True)


def calamine_all():
    from python_calamine import CalamineWorkbook
    wb = CalamineWorkbook.from_path(F)
    sh = wb.sheet_names[0]
    rows = wb.get_sheet_by_name(sh).to_python(skip_empty_area=False)
    return f"sheet={sh} rows={len(rows)} cols={len(rows[0])}"


def duckdb_agg():
    import duckdb
    con = duckdb.connect()
    con.execute("INSTALL excel; LOAD excel;")
    q = con.execute(f"""
        SELECT region, count(*) n, round(sum(line_total),2) revenue
        FROM read_xlsx('{F}')
        GROUP BY 1 ORDER BY revenue DESC LIMIT 3
    """).fetchall()
    return q


def duckdb_to_parquet():
    import duckdb
    con = duckdb.connect()
    con.execute("INSTALL excel; LOAD excel;")
    t0 = time.time()
    con.execute(f"COPY (SELECT * FROM read_xlsx('{F}')) TO 'big.parquet' (FORMAT parquet, COMPRESSION zstd)")
    sz = os.path.getsize("big.parquet") / 1e6
    q = con.execute("SELECT region, count(*) n, round(sum(line_total),2) rev FROM 'big.parquet' GROUP BY 1 ORDER BY rev DESC LIMIT 3").fetchall()
    return f"parquet={sz:.1f} MB ({time.time()-t0:.1f}s incl. write), agg={q}"


def pandas_openpyxl():
    import pandas as pd
    df = pd.read_excel(F, sheet_name=0, engine="openpyxl")
    return f"shape={df.shape} revenue={round(df.line_total.sum(),2)}"


def pandas_calamine():
    import pandas as pd
    df = pd.read_excel(F, sheet_name=0, engine="calamine")
    return f"shape={df.shape} revenue={round(df.line_total.sum(),2)}"


which = sys.argv[1] if len(sys.argv) > 1 else "all"
steps = {
    "calamine": ("calamine full read", calamine_all),
    "duckdb": ("duckdb read_xlsx + GROUP BY", duckdb_agg),
    "parquet": ("duckdb xlsx->parquet + GROUP BY", duckdb_to_parquet),
    "pandas-openpyxl": ("pandas/openpyxl read_excel", pandas_openpyxl),
    "pandas-calamine": ("pandas/calamine read_excel", pandas_calamine),
}
for k, (name, fn) in steps.items():
    if which in ("all", k):
        if os.path.exists("./flag-" + k):
            print(f"{k}: already done", flush=True)
            continue
        try:
            step(name, fn)
        except Exception as e:
            print(f"{name}: FAILED {type(e).__name__}: {str(e)[:200]}", flush=True)
        open("./flag-" + k, "w").close()
print("ALL DONE", flush=True)
