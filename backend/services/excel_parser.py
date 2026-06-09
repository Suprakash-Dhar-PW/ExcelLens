import pandas as pd
import io
import math
import logging
from datetime import datetime

logger = logging.getLogger('excel_parser')

def fuzzy_match_column(columns, candidates):
    """Returns the first column name that matches any of the candidates (case-insensitive substring)."""
    cols_lower = {str(c).lower(): c for c in columns if pd.notna(c)}
    for cand in candidates:
        cand_lower = cand.lower()
        for cl in cols_lower:
            if cand_lower in cl:
                return cols_lower[cl]
    return None

def parse_excel_file(file_content: bytes, filename: str) -> dict:
    """
    Parses an uploaded excel or csv file, extracts sheet-specific data,
    and returns a dictionary of lists corresponding to the new models.
    """
    records_dict = {
        "executive_summaries": [],
        "daily_performances": [],
        "category_performances": [],
        "offering_performances": [],
        "batch_performances": [],
        "leader_performances": []
    }
    
    if filename.lower().endswith('.csv'):
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            df_dict = {"Summary Overall": df} # Default fallback for csv
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            return records_dict
    else:
        try:
            df_dict = pd.read_excel(io.BytesIO(file_content), sheet_name=None)
        except Exception as e:
            logger.error(f"Failed to read Excel: {e}")
            return records_dict
        
    if not df_dict:
        logger.warning("Uploaded file contained no sheets or data.")
        return records_dict
        
    def safe_float(val):
        try:
            v = float(val)
            return 0.0 if math.isnan(v) else v
        except:
            return 0.0

    def safe_int(val):
        try:
            v = int(val)
            return 0 if math.isnan(v) else v
        except:
            return 0

    def safe_str(val):
        if pd.isna(val):
            return None
        return str(val).strip()

    def safe_date(val):
        if pd.isna(val):
            return None
        if isinstance(val, pd.Timestamp):
            return val.to_pydatetime()
        if isinstance(val, str):
            try:
                from dateutil import parser
                return parser.parse(val)
            except:
                pass
        return None

    for sheet_name, df in df_dict.items():
        if df.empty:
            logger.warning(f"Sheet '{sheet_name}' is empty.")
            continue
            
        sheet_lower = sheet_name.lower()
        cols = list(df.columns)
        logger.info(f"Processing sheet '{sheet_name}' with {len(df)} rows. Columns: {cols}")
        
        # 1. Executive Summary
        if 'summary' in sheet_lower or 'overall' in sheet_lower:
            metric_col = cols[0]
            val_col = fuzzy_match_column(cols, ['value', 'amount', 'total', 'revenue', 'collection', 'actual', 'target', 'metric'])
            if not val_col and len(cols) > 1:
                val_col = cols[1]
                
            logger.info(f"Executive Summary mapping - Metric: '{metric_col}', Value: '{val_col}'")
            
            if val_col:
                count = 0
                for _, row in df.iterrows():
                    metric = safe_str(row[metric_col])
                    val = safe_float(row[val_col])
                    if metric:
                        records_dict["executive_summaries"].append({
                            "metric_name": metric,
                            "value": val
                        })
                        count += 1
                logger.info(f"Extracted {count} rows for executive_summaries from sheet '{sheet_name}'")

        # 2. Daily Performance (DOD View)
        elif 'dod' in sheet_lower or 'daily' in sheet_lower:
            date_col = fuzzy_match_column(cols, ['date', 'day'])
            coll_col = fuzzy_match_column(cols, ['collection', 'achieved', 'revenue', 'actual'])
            tgt_col = fuzzy_match_column(cols, ['target', 'quota'])
            
            logger.info(f"Daily Performance mapping - Date: '{date_col}', Collection: '{coll_col}', Target: '{tgt_col}'")
            
            if date_col:
                count = 0
                for _, row in df.iterrows():
                    d = safe_date(row[date_col])
                    c = safe_float(row[coll_col]) if coll_col else 0.0
                    t = safe_float(row[tgt_col]) if tgt_col else 0.0
                    if d:
                        records_dict["daily_performances"].append({
                            "date": d,
                            "collection": c,
                            "target": t
                        })
                        count += 1
                logger.info(f"Extracted {count} rows for daily_performances from sheet '{sheet_name}'")

        # 3. Category Performance (Top / Bottom Categories)
        elif 'categor' in sheet_lower:
            cat_col = fuzzy_match_column(cols, ['category', 'name'])
            rev_col = fuzzy_match_column(cols, ['revenue', 'collection', 'value', 'actual'])
            rank_type = 'top' if 'top' in sheet_lower else 'bottom' if 'bottom' in sheet_lower else 'unranked'
            
            logger.info(f"Category Performance mapping - Category: '{cat_col}', Revenue: '{rev_col}', RankType: '{rank_type}'")
            
            if cat_col and rev_col:
                count = 0
                for _, row in df.iterrows():
                    c = safe_str(row[cat_col])
                    r = safe_float(row[rev_col])
                    if c:
                        records_dict["category_performances"].append({
                            "category": c,
                            "revenue": r,
                            "rank_type": rank_type
                        })
                        count += 1
                logger.info(f"Extracted {count} rows for category_performances from sheet '{sheet_name}'")

        # 4. Offering Performance (MTD / YTD)
        elif 'offering' in sheet_lower:
            off_col = fuzzy_match_column(cols, ['offering', 'product', 'service', 'name'])
            rev_col = fuzzy_match_column(cols, ['revenue', 'collection', 'value', 'actual'])
            period = 'YTD' if 'ytd' in sheet_lower else 'MTD'
            
            logger.info(f"Offering Performance mapping - Offering: '{off_col}', Revenue: '{rev_col}', Period: '{period}'")
            
            if off_col and rev_col:
                count = 0
                for _, row in df.iterrows():
                    o = safe_str(row[off_col])
                    r = safe_float(row[rev_col])
                    if o:
                        records_dict["offering_performances"].append({
                            "offering": o,
                            "revenue": r,
                            "period": period
                        })
                        count += 1
                logger.info(f"Extracted {count} rows for offering_performances from sheet '{sheet_name}'")

        # 5. Batch Performance (Top Batches)
        elif 'batch' in sheet_lower:
            b_col = fuzzy_match_column(cols, ['batch', 'name'])
            rev_col = fuzzy_match_column(cols, ['revenue', 'collection', 'actual'])
            enr_col = fuzzy_match_column(cols, ['enroll', 'student', 'count'])
            
            logger.info(f"Batch Performance mapping - Batch: '{b_col}', Revenue: '{rev_col}', Enrollments: '{enr_col}'")
            
            if b_col:
                count = 0
                for _, row in df.iterrows():
                    b = safe_str(row[b_col])
                    r = safe_float(row[rev_col]) if rev_col else 0.0
                    e = safe_int(row[enr_col]) if enr_col else 0
                    if b:
                        records_dict["batch_performances"].append({
                            "batch_name": b,
                            "revenue": r,
                            "enrollments": e
                        })
                        count += 1
                logger.info(f"Extracted {count} rows for batch_performances from sheet '{sheet_name}'")
                        
        # 6. Leader Performance
        elif 'leader' in sheet_lower or 'manager' in sheet_lower:
            l_col = fuzzy_match_column(cols, ['leader', 'name', 'manager'])
            rev_col = fuzzy_match_column(cols, ['revenue', 'achieved', 'collection', 'actual'])
            tgt_col = fuzzy_match_column(cols, ['target', 'quota'])
            
            logger.info(f"Leader Performance mapping - Leader: '{l_col}', Revenue: '{rev_col}', Target: '{tgt_col}'")
            
            if l_col:
                count = 0
                for _, row in df.iterrows():
                    l = safe_str(row[l_col])
                    r = safe_float(row[rev_col]) if rev_col else 0.0
                    t = safe_float(row[tgt_col]) if tgt_col else 0.0
                    if l:
                        records_dict["leader_performances"].append({
                            "leader_name": l,
                            "revenue": r,
                            "target": t
                        })
                        count += 1
                logger.info(f"Extracted {count} rows for leader_performances from sheet '{sheet_name}'")

    for k, v in records_dict.items():
        logger.info(f"Total extracted for {k}: {len(v)}")
        
    return records_dict

