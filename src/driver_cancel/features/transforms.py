import pandas as pd

def cap_categorias(s: pd.Series, k=30, other="Other"):
    if s.dtype == "O":
        top = s.value_counts().nlargest(k).index
        return s.where(s.isin(top), other)
    return s

def add_time_features(df: pd.DataFrame, date_col="Date", time_col="Time"):
    df = df.copy()
    dt_time = pd.to_datetime(df.get(time_col), errors="coerce")
    dt_date = pd.to_datetime(df.get(date_col), errors="coerce")
    df["hour"] = dt_time.dt.hour
    df["day_of_week"] = dt_date.dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype("int8")
    return df
