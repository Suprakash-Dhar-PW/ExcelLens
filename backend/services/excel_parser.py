import pandas as pd
import io
import math
import logging
import json
from datetime import datetime

logger = logging.getLogger('excel_parser')

def fuzzy_match_column(columns, candidates):
    """Returns the first column name that matches any of the candidates (case-insensitive substring)."""
    cols_lower = {str(c).lower(): c for c in columns if pd.notna(c)}
    for cand in candidates:
        for cl in cols_lower:
            if cand in cl:
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
        if isinstance(val, (int, float)):
            try:
                if val > 30000:
                    return pd.to_datetime(val, unit='D', origin='1899-12-30').to_pydatetime()
            except:
                pass
        if isinstance(val, str):
            try:
                from dateutil import parser
                return parser.parse(val, fuzzy=True)
            except:
                pass
        return None

    for sheet_name, df in df_dict.items():
        if df.empty:
            logger.warning(f"Sheet '{sheet_name}' is empty.")
            continue
            
        sheet_lower = sheet_name.lower()
        cols = list(df.columns)
        
        branch = "None"
        matched_cols = {}
        count = 0
        
        logger.info("==================================================")
        logger.info(f"SHEET NAME: {sheet_name}")
        logger.info(f"ROWS: {len(df)}")
        logger.info(f"COLUMNS: {cols}")
        
        # 1. Executive Summary
        if any(x in sheet_lower for x in ['summary', 'overall', 'generic', 'vertical', 'last year', 'ac']):
            branch = "Executive Summary"
            metric_col = cols[0]
            val_col = fuzzy_match_column(cols, ['value', 'amount', 'total', 'revenue', 'collection', 'actual', 'target', 'metric'])
            if not val_col and len(cols) > 1:
                val_col = cols[1]
                
            matched_cols['Metric Column'] = metric_col
            matched_cols['Value Column'] = val_col
            
            if val_col:
                for _, row in df.iterrows():
                    metric = safe_str(row[metric_col])
                    val = safe_float(row[val_col])
                    if metric:
                        records_dict["executive_summaries"].append({
                            "metric_name": metric,
                            "value": val
                        })
                        count += 1

        # 2. Daily Performance (DOD View)
        elif any(x in sheet_lower for x in ['dod', 'daily', 'trend', 'achieved']):
            branch = "Daily Performance"
            date_col = fuzzy_match_column(cols, ['date', 'day', 'time'])
            coll_col = fuzzy_match_column(cols, ['collection', 'achieved', 'revenue', 'actual', 'amount', 'value'])
            tgt_col = fuzzy_match_column(cols, ['target', 'quota', 'goal'])
            
            matched_cols['Date Column'] = date_col
            matched_cols['Collection Column'] = coll_col
            matched_cols['Target Column'] = tgt_col
            
            if date_col:
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

        # 3. Category Performance (Top / Bottom Categories)
        elif 'category' in sheet_lower or 'categories' in sheet_lower:
            branch = "Category Performance"
            cat_col = fuzzy_match_column(cols, ['category', 'name'])
            rev_col = fuzzy_match_column(cols, ['revenue', 'collection', 'value', 'actual', 'amount'])
            rank_type = 'top' if 'top' in sheet_lower else 'bottom' if 'bottom' in sheet_lower else 'unranked'
            
            matched_cols['Category Column'] = cat_col
            matched_cols['Revenue Column'] = rev_col
            matched_cols['Rank Type'] = rank_type
            
            if cat_col and rev_col:
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

        # 4. Offering Performance (MTD / YTD)
        elif any(x in sheet_lower for x in ['offering', 'program', 'product', 'course']):
            branch = "Offering Performance"
            off_col = fuzzy_match_column(cols, ['offering', 'product', 'service', 'name', 'program', 'course'])
            rev_col = fuzzy_match_column(cols, ['revenue', 'collection', 'value', 'actual', 'amount'])
            period = 'YTD' if 'ytd' in sheet_lower else 'MTD'
            
            matched_cols['Offering Column'] = off_col
            matched_cols['Revenue Column'] = rev_col
            matched_cols['Period'] = period
            
            if off_col and rev_col:
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

        # 5. Batch Performance (Top Batches)
        elif 'batch' in sheet_lower:
            branch = "Batch Performance"
            b_col = fuzzy_match_column(cols, ['batch', 'name'])
            rev_col = fuzzy_match_column(cols, ['revenue', 'collection', 'actual', 'amount'])
            enr_col = fuzzy_match_column(cols, ['enroll', 'student', 'count'])
            
            matched_cols['Batch Column'] = b_col
            matched_cols['Revenue Column'] = rev_col
            matched_cols['Enrollments Column'] = enr_col
            
            if b_col:
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
                        
        # 6. Leader Performance
        elif any(x in sheet_lower for x in ['leader', 'manager', 'performer', 'team']):
            branch = "Leader Performance"
            l_col = fuzzy_match_column(cols, ['leader', 'name', 'manager', 'performer', 'team'])
            rev_col = fuzzy_match_column(cols, ['revenue', 'achieved', 'collection', 'actual', 'amount'])
            tgt_col = fuzzy_match_column(cols, ['target', 'quota', 'goal'])
            
            matched_cols['Leader Column'] = l_col
            matched_cols['Revenue Column'] = rev_col
            matched_cols['Target Column'] = tgt_col
            
            if l_col:
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

        logger.info(f"BRANCH: {branch}")
        for k, v in matched_cols.items():
            logger.info(f"{k}: {v}")
        logger.info(f"Extracted Rows: {count}")
        logger.info("==================================================")

    logger.info("Final Extracted Counts:\n" + json.dumps({
        "executive_summaries": len(records_dict["executive_summaries"]),
        "daily_performances": len(records_dict["daily_performances"]),
        "category_performances": len(records_dict["category_performances"]),
        "offering_performances": len(records_dict["offering_performances"]),
        "batch_performances": len(records_dict["batch_performances"]),
        "leader_performances": len(records_dict["leader_performances"])
    }, indent=4))
        
    return records_dict

