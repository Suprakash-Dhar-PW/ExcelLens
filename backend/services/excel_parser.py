import pandas as pd
import io
import math
import logging
import json
from datetime import datetime

logger = logging.getLogger('excel_parser')

def fuzzy_match_column(columns, candidates):
    """Returns the first column name that matches any of the candidates (exact match first, then substring)."""
    cols_lower = {str(c).lower().strip(): c for c in columns if pd.notna(c)}
    
    # Try exact matches first
    for cand in candidates:
        cand_lower = cand.lower().strip()
        for cl in cols_lower:
            if cand_lower == cl:
                return cols_lower[cl]
                
    # Fallback to substring matches
    for cand in candidates:
        cand_lower = cand.lower().strip()
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
            df = pd.read_csv(io.BytesIO(file_content), header=None)
            df_dict = {"Summary Overall": df} # Default fallback for csv
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            return records_dict
    else:
        try:
            df_dict = pd.read_excel(io.BytesIO(file_content), sheet_name=None, header=None)
        except Exception as e:
            logger.error(f"Failed to read Excel: {e}")
            return records_dict
        
    if not df_dict:
        logger.warning("Uploaded file contained no sheets or data.")
        return records_dict
        
    def safe_float(val):
        if isinstance(val, pd.Series):
            val = val.iloc[0]
        try:
            v = float(val)
            return 0.0 if math.isnan(v) else v
        except:
            return 0.0

    def safe_int(val):
        if isinstance(val, pd.Series):
            val = val.iloc[0]
        try:
            v = int(val)
            return 0 if math.isnan(v) else v
        except:
            return 0

    def safe_str(val):
        if isinstance(val, pd.Series):
            val = val.iloc[0]
        if pd.isna(val):
            return None
        return str(val).strip()

    def safe_date(val):
        if isinstance(val, pd.Series):
            val = val.iloc[0]
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

    for sheet_name, raw_df in df_dict.items():
        if raw_df.empty:
            logger.warning(f"Sheet '{sheet_name}' is empty.")
            continue
            
        sheet_lower = sheet_name.lower().strip()
        
        # Header Detection Fix
        # Search first 20 rows. Choose the row with the highest number of non-empty cells.
        best_row_idx = 0
        max_non_empty = 0
        
        for i in range(min(20, len(raw_df))):
            non_empty_count = raw_df.iloc[i].count()
            if non_empty_count > max_non_empty:
                max_non_empty = non_empty_count
                best_row_idx = i
                
        if max_non_empty > 0:
            df = raw_df.copy()
            df.columns = df.iloc[best_row_idx]
            df = df.iloc[best_row_idx + 1:].reset_index(drop=True)
            # Remove any empty column names (NaN or None)
            df = df.loc[:, df.columns.notna()]
            # Ensure columns are strings
            df.columns = [str(c).strip() for c in df.columns]
        else:
            df = raw_df.copy()

        cols = list(df.columns)
        
        # Strict Sheet Mapping
        branch = "None"
        if any(x in sheet_lower for x in ["dod", "dod achieved", "yakeen dod", "achieved data"]):
            branch = "Daily Performance"
        elif any(x in sheet_lower for x in ["offering tracking-mtd", "offering tracking-ytd", "offering", "program", "course"]):
            branch = "Offering Performance"
        elif any(x in sheet_lower for x in ["top batches", "batch tracking", "batch performance"]):
            branch = "Batch Performance"
        elif any(x in sheet_lower for x in ["leader", "manager", "team"]):
            branch = "Leader Performance"
        elif any(x in sheet_lower for x in ["category", "categories", "top categories", "bottom categories"]):
            branch = "Category Performance"
        elif sheet_lower in ["summary", "executive summary", "summary-ac", "summary-overall", "summary-test series"]:
            branch = "Executive Summary"
            
        count = 0
        leader_count = 0 # Track separately if extracted in another branch
        
        # 1. Daily Performance (DOD View)
        if branch == "Daily Performance":
            date_col = fuzzy_match_column(cols, ['converted_date', 'date', 'day', 'time'])
            coll_col = fuzzy_match_column(cols, ['collection_fy27', 'achieved', 'revenue', 'actual', 'collection', 'amount', 'value'])
            
            if date_col:
                for _, row in df.iterrows():
                    d = safe_date(row[date_col])
                    c = safe_float(row[coll_col]) if coll_col else 0.0
                    t = 0.0 # Force target to 0 as requested for DOD
                    if d:
                        records_dict["daily_performances"].append({
                            "date": d,
                            "collection": c,
                            "target": t
                        })
                        count += 1
                logger.info(f"DOD rows inserted: {count}")

        # 2. Offering Performance
        elif branch == "Offering Performance":
            off_col = fuzzy_match_column(cols, ['category', 'offering', 'product', 'service', 'name', 'program', 'course'])
            rev_col = fuzzy_match_column(cols, ['achieved mtd', 'achieved ytd', 'achieved', 'revenue', 'collection', 'value', 'actual', 'amount'])
            period = 'YTD' if 'ytd' in sheet_lower else 'MTD'
            
            if off_col and rev_col:
                for _, row in df.iterrows():
                    o = safe_str(row[off_col])
                    r = safe_float(row[rev_col])
                    if o and str(o).lower() != 'nan':
                        records_dict["offering_performances"].append({
                            "offering": o,
                            "revenue": r,
                            "period": period
                        })
                        count += 1

        # 3. Batch Performance
        elif branch == "Batch Performance":
            b_col = fuzzy_match_column(cols, ['batch name', 'batch'])
            rev_col = fuzzy_match_column(cols, ['achieved mtd', 'achieved ytd', 'achieved', 'revenue', 'collection', 'actual', 'amount'])
            
            if b_col:
                for _, row in df.iterrows():
                    b = safe_str(row[b_col])
                    r = safe_float(row[rev_col]) if rev_col else 0.0
                    e = 0 # Not required in fix logic, keeping 0
                    if b and str(b).lower() != 'nan':
                        records_dict["batch_performances"].append({
                            "batch_name": b,
                            "revenue": r,
                            "enrollments": e
                        })
                        count += 1
                        
        # 4. Leader Performance (Dedicated Sheet)
        elif branch == "Leader Performance":
            l_col = fuzzy_match_column(cols, ['leader', 'name', 'manager', 'performer', 'team'])
            rev_col = fuzzy_match_column(cols, ['achieved mtd', 'achieved ytd', 'achieved', 'revenue', 'collection', 'actual', 'amount'])
            tgt_col = fuzzy_match_column(cols, ['target', 'quota', 'goal'])
            
            if l_col:
                for _, row in df.iterrows():
                    l = safe_str(row[l_col])
                    r = safe_float(row[rev_col]) if rev_col else 0.0
                    t = safe_float(row[tgt_col]) if tgt_col else 0.0
                    if l and str(l).lower() != 'nan':
                        records_dict["leader_performances"].append({
                            "leader_name": l,
                            "revenue": r,
                            "target": t
                        })
                        count += 1

        # 5. Category Performance
        elif branch == "Category Performance":
            cat_col = fuzzy_match_column(cols, ['category', 'name'])
            rev_col = fuzzy_match_column(cols, ['achieved mtd', 'achieved ytd', 'achieved', 'revenue', 'collection', 'value', 'actual', 'amount'])
            rank_type = 'top' if 'top' in sheet_lower else 'bottom' if 'bottom' in sheet_lower else 'unranked'
            
            if cat_col and rev_col:
                for _, row in df.iterrows():
                    c = safe_str(row[cat_col])
                    r = safe_float(row[rev_col])
                    if c and str(c).lower() != 'nan':
                        records_dict["category_performances"].append({
                            "category": c,
                            "revenue": r,
                            "rank_type": rank_type
                        })
                        count += 1

        # 6. Executive Summary (Also extracts Leader Performance)
        elif branch == "Executive Summary":
            target_metrics = ['revenue', 'target', 'collection', 'order', 'achievement', 'kpi', 'metric']
            wide_cols = [c for c in cols if any(m in str(c).lower() for m in target_metrics)]
            
            # Extract standard generic summary if available
            if len(wide_cols) >= 2 and len(df) > 0:
                row = df.iloc[0]
                for c in wide_cols:
                    val = safe_float(row[c])
                    records_dict["executive_summaries"].append({
                        "metric_name": str(c),
                        "value": val
                    })
                    count += 1
            else:
                metric_col = fuzzy_match_column(cols, ['metric', 'kpi', 'name']) or (cols[0] if len(cols) > 0 else None)
                val_col = fuzzy_match_column(cols, ['value', 'amount', 'total', 'revenue', 'collection', 'actual', 'target', 'metric'])
                if not val_col and len(cols) > 1:
                    val_col = cols[1]
                
                if val_col and metric_col:
                    for _, row in df.iterrows():
                        metric = safe_str(row[metric_col])
                        val = safe_float(row[val_col])
                        if metric and str(metric).lower() != 'nan':
                            records_dict["executive_summaries"].append({
                                "metric_name": metric,
                                "value": val
                            })
                            count += 1

            # NEW: Extract KPIs explicitly from the "Total" row
            l_col = fuzzy_match_column(cols, ['leader', 'name', 'manager', 'performer', 'team'])
            if l_col:
                total_row = None
                for _, row in df.iterrows():
                    lname = str(row[l_col]).lower()
                    if 'total' in lname:
                        total_row = row
                        break
                
                if total_row is not None:
                    for c in cols:
                        c_lower = str(c).lower()
                        if any(m in c_lower for m in ['achieved', 'bizfin aop', 'target', 'projected']):
                            val = safe_float(total_row[c])
                            records_dict["executive_summaries"].append({
                                "metric_name": str(c),
                                "value": val
                            })
                            count += 1

            # ALSO Extract Leader Performance from Summary Sheets
            l_col = fuzzy_match_column(cols, ['leader', 'name', 'manager', 'performer', 'team'])
            rev_col = fuzzy_match_column(cols, ['achieved mtd', 'achieved ytd', 'achieved', 'revenue', 'collection', 'actual', 'amount'])
            tgt_col = fuzzy_match_column(cols, ['target', 'quota', 'goal'])
            
            if l_col and rev_col:
                for _, row in df.iterrows():
                    l = safe_str(row[l_col])
                    r = safe_float(row[rev_col])
                    t = safe_float(row[tgt_col]) if tgt_col else 0.0
                    # Skip rows where leader is just a generic string like "Total" or is empty
                    if l and str(l).lower() not in ['nan', 'total', 'grand total', 'summary']:
                        records_dict["leader_performances"].append({
                            "leader_name": l,
                            "revenue": r,
                            "target": t
                        })
                        leader_count += 1

        # Parser debug logging as requested
        logger.info({
            "sheet": sheet_name,
            "detected_type": branch,
            "rows": len(df),
            "columns": list(df.columns),
            "records_created": count,
            "leader_records_created_from_summary": leader_count
        })

    logger.info("Final Extracted Counts:\n" + json.dumps({
        "executive_summaries": len(records_dict["executive_summaries"]),
        "daily_performances": len(records_dict["daily_performances"]),
        "category_performances": len(records_dict["category_performances"]),
        "offering_performances": len(records_dict["offering_performances"]),
        "batch_performances": len(records_dict["batch_performances"]),
        "leader_performances": len(records_dict["leader_performances"])
    }, indent=4))
        
    return records_dict
