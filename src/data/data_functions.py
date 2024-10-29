import pandas as pd
from matplotlib import pyplot as plt
import os,json

folder_file = os.path.dirname(__file__)

fig_folder = os.path.join(folder_file, "..", "..", "reports", "figures")

if not os.path.exists(fig_folder):
    os.makedirs(fig_folder)

mcc_codes_path = os.path.join(folder_file, "..", "..", "data", "raw", "mcc_codes.json")
mcc_codes = json.load(open(mcc_codes_path))

def earnings_and_expenses(
    df: pd.DataFrame, client_id: int, start_date: str, end_date: str
) -> pd.DataFrame:
    """
    For the period defined in between start_date and end_date (both included), get the client data available and return
    a pandas DataFrame with the Earnings and Expenses total amount for the period range and user given.The expected columns are:
        - Earnings
        - Expenses
    The DataFrame should have the columns in this order ['Earnings','Expenses']. Round the amounts to 2 decimals.

    Create a Bar Plot with the Earnings and Expenses absolute values and save it as "reports/figures/earnings_and_expenses.png" .

    Parameters
    ----------
    df : pandas DataFrame
       DataFrame of the data to be used for the agent.
    client_id : int
        Id of the client.
    start_date : str
        Start date for the date period. In the format "YYYY-MM-DD".
    end_date : str
        End date for the date period. In the format "YYYY-MM-DD".


    Returns
    -------
    Pandas Dataframe with the earnings and expenses rounded to 2 decimals.

    """

    # if df
    if  df["date"].dtype != "datetime64[ns]":
        df["date"] = pd.to_datetime(df["date"])
    if df["amount"].dtype != "float64":
        df["amount"] = df["amount"].apply(lambda x: x.replace("$", "").replace(",", "")).astype(float)

    # verify if the client_id exists
    if client_id not in df["client_id"].unique():
        return pd.DataFrame({"Earnings": [0], "Expenses": [0]})

    # verify if the date range is correct
    if start_date > end_date:
        raise ValueError("Start date must be before end date")
    

    df_selected = df[(df["client_id"] == client_id) & (df["date"] >= start_date) & (df["date"] <= end_date)]
    Earnings = df_selected[df_selected["amount"] > 0]["amount"].sum()
    Expenses = df_selected[df_selected["amount"] < 0]["amount"].sum()

    fig, ax = plt.subplots()
    ax.bar(["Earnings", "Expenses"], [Earnings, -Expenses])
    plt.grid()
    plt.title("client_id: {} from {} to {}".format(client_id, start_date, end_date))
    # tick to dollars
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))

    plt.savefig(os.path.join(fig_folder, "earnings_and_expenses.png"))
    
    return pd.DataFrame({"Earnings": [round(Earnings, 2)], "Expenses": [round(Expenses, 2)]})



def expenses_summary(
    df: pd.DataFrame, client_id: int, start_date: str, end_date: str
) -> pd.DataFrame:
    """
    For the period defined in between start_date and end_date (both included), get the client data available and return
    a Pandas Data Frame with the Expenses by merchant category. The expected columns are:
        - Expenses Type --> (merchant category names)
        - Total Amount
        - Average
        - Max
        - Min
        - Num. Transactions
    The DataFrame should be sorted alphabeticaly by Expenses Type and values have to be rounded to 2 decimals. Return the dataframe with the columns in the given order.
    The merchant category names can be found in data/raw/mcc_codes.json .

    Create a Bar Plot with the data in absolute values and save it as "reports/figures/expenses_summary.png" .

    Parameters
    ----------
    df : pandas DataFrame
       DataFrame  of the data to be used for the agent.
    client_id : int
        Id of the client.
    start_date : str
        Start date for the date period. In the format "YYYY-MM-DD".
    end_date : str
        End date for the date period. In the format "YYYY-MM-DD".


    Returns
    -------
    Pandas Dataframe with the Expenses by merchant category.

    """

    # if df
    if  df["date"].dtype != "datetime64[ns]":
        df["date"] = pd.to_datetime(df["date"])
    if df["amount"].dtype != "float64":
        df["amount"] = df["amount"].apply(lambda x: x.replace("$", "").replace(",", "")).astype(float)


    df_selected = df[(df["client_id"] == client_id) & \
                     (df["date"] >= start_date) & \
                     (df["date"] <= end_date) & \
                     (df["amount"] < 0)]

    mcc_des = df_selected["mcc"].apply(lambda x: mcc_codes[str(x)])
    df_selected = df_selected.copy()
    df_selected["mcc_des"] = mcc_des

    df_selected = df_selected.groupby("mcc_des").agg(
        Total_Amount = ("amount", "sum"),
        Average = ("amount", "mean"),
        Max = ("amount", "max"),
        Min = ("amount", "min"),
        Num_Transactions = ("amount", "count")
    ).reset_index()

    df_selected = df_selected.round(2)
    df_selected = df_selected.sort_values("mcc_des")

    

    fig = plt.figure()
    plt.bar(df_selected["mcc_des"], -df_selected["Total_Amount"])
    plt.xticks(rotation=90)
    plt.ylabel("Total Amount")
    plt.title("Expenses by Merchant Category")
    # yaxis label in dollars
    plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))
    
    plt.savefig(os.path.join(fig_folder, "expenses_summary.png"))

    return pd.DataFrame(
        {
            "Expenses Type"         : df_selected["mcc_des"],
            "Total Amount"          : -df_selected["Total_Amount"], # Negative values
            "Average"               : -df_selected["Average"], # Negative values
            "Max"                   : -df_selected["Max"], # Negative values
            "Min"                   : -df_selected["Min"], # Negative values
            "Num. Transactions"     : df_selected["Num_Transactions"]
        }
    )



def cash_flow_summary(
    df: pd.DataFrame, client_id: int, start_date: str, end_date: str
) -> pd.DataFrame:
    """
    For the period defined by start_date and end_date (both inclusive), retrieve the available client data and return a Pandas DataFrame containing cash flow information.

    If the period exceeds 60 days, group the data by month, using the end of each month for the date. If the period is 60 days or shorter, group the data by week.

        The expected columns are:
            - Date --> the date for the period. YYYY-MM if period larger than 60 days, YYYY-MM-DD otherwise.
            - Inflows --> the sum of the earnings (positive amounts)
            - Outflows --> the sum of the expenses (absolute values of the negative amounts)
            - Net Cash Flow --> Inflows - Outflows
            - % Savings --> Percentage of Net Cash Flow / Inflows

        The DataFrame should be sorted by ascending date and values rounded to 2 decimals. The columns should be in the given order.

        Parameters
        ----------
        df : pandas DataFrame
           DataFrame  of the data to be used for the agent.
        client_id : int
            Id of the client.
        start_date : str
            Start date for the date period. In the format "YYYY-MM-DD".
        end_date : str
            End date for the date period. In the format "YYYY-MM-DD".


        Returns
        -------
        Pandas Dataframe with the cash flow summary.
    """
    if  df["date"].dtype != "datetime64[ns]":
        df["date"] = pd.to_datetime(df["date"])
    if df["amount"].dtype != "float64":
        df["amount"] = df["amount"].apply(lambda x: x.replace("$", "").replace(",", "")).astype(float)
        
    # Convert start and end dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    delta_days = (end_date - start_date).days

    # Set the period format based on the number of days
    order_by = "ME" if delta_days > 60 else "W"
    # Convert 'date' column to datetime if not already

    # Filter for the client ID and date range
    df = df[(df["client_id"] == client_id) & (df["date"] >= start_date) & (df["date"] <= end_date)]
    
    # group by the month 
    df = df.groupby(pd.Grouper(key="date", freq=order_by)).agg(
        Inflows=("amount", lambda x: x[x > 0].sum()),
        Outflows=("amount", lambda x: -x[x < 0].sum()),
    ).reset_index()

    # Calculate the Net Cash Flow
    df["Net Cash Flow"] = df["Inflows"] - df["Outflows"]
    df["% Savings"] = df["Net Cash Flow"] / df["Inflows"] *100

    # name
    df["Date"] = df["date"]
    # Drop the date column
    df = df.drop(columns="date")
    # order the columns
    df = df[["Date", "Inflows", "Outflows", "Net Cash Flow", "% Savings"]]
    # order the rows
    df = df.sort_values(by="Date", ascending=True)

    # 2 decimal places
    df = df.round(2)

    # date format string "YYYY-MM-DD"
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")  if order_by == "W" else df["Date"].dt.strftime("%Y-%m")
    return df


if __name__ == "__main__":
    ...
