import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from data.data_functions import *
from langchain_ollama import ChatOllama
from agent.tools import crear_pdf_elementos

def run_agent(input, client_id,df):
    """
    Create a simple AI Agent that generates PDF reports using the three functions from Task 2 (src/data/data_functions.py).
    The agent should generate a PDF report only if valid data is available for the specified client_id and date range.
    Using the data and visualizations from Task 2, the report should be informative and detailed.

    The agent should return a dictionary containing the start and end dates, the client_id, and whether the report was successfully created.

    Parameters
    ----------
    df : pandas DataFrame
        DataFrame  of the data to be used for the agent.
    client_id : int
        Id of the client making the request.
    input : str
        String with the client input for creating the report.


    Returns
    -------
    variables_dict : dict
        Dictionary of the variables of the query.
            {
                "start_date": "YYYY-MM-DD",
                "end_date" : "YYYY-MM-DD",
                "client_id": int,
                "create_report" : bool
            }

    """
    prompt = input
    # Step 1: Set up the Ollama model with LangChain
    model = ChatOllama(model="llama3.2:1b", temperature=0)

    # Step 2: Define a prompt template to ensure clarity
    main_prompt = PromptTemplate(
        input_variables=["client_id", "text_prompt"],
        template="""
        You are a reporting assistant for client {client_id}. Extract the required dates from the following prompt
        Text prompt: "{text_prompt}"
        In a list format, provide the extracted dates in the following format: ["YYYY-MM-DD", "YYYY-MM-DD"] without the quotes. If no dates are found, provide an empty list.

        Examples:
            - Input: "Please provide data from 2023-01-01 to 2023-12-31."
            Output: ["2023-01-01", "2023-12-31"]

            - Input: "From July 15th, 2024, to August 20th, 2024, analyze the results."
            Output: ["2024-07-15", "2024-08-20"]
        Considerations:
        - If they ask you for a specific month, you must enter the first day of the month and the last day of the month.
        """,
    )

     
    r_fail  = {
            "start_date": None,
            "end_date": None,
            "client_id": client_id,
            "create_report": False
        }
    

    llm_chain = main_prompt | model
    
    max_attempts = 5
    attempts = 0
    found_dates = []

    while len(found_dates) < 2 and attempts < max_attempts:
        response = llm_chain.invoke({"client_id": client_id, "text_prompt": prompt})
        response_text = response.content

        date_pattern = r"\b\d{4}-\d{2}-\d{2}\b"
        found_dates = re.findall(date_pattern, response_text)
        
        attempts += 1
        
        # Si no se encontraron suficientes fechas, ajustar el prompt y reintentar
        if len(found_dates) < 2:
            print("No se encontraron suficientes fechas. Reintentando...")
            

    if len(found_dates) >= 2:
        start_date = found_dates[0]
        end_date = found_dates[1]
    else:
        return r_fail
    
    # if id_client is not in the data
    if client_id not in df["client_id"].unique():
        r_fail["start_date"] = start_date
        r_fail["end_date"] = end_date
        return r_fail

    ree = earnings_and_expenses(df, client_id,start_date, end_date)
    res = expenses_summary(df, client_id, start_date, end_date)
    rfs = cash_flow_summary(df, client_id, start_date, end_date)

    #nombre_pdf = f"report_{client_id}_{start_date}_{end_date}.pdf"
    nombre_pdf = "report.pdf"
    crear_pdf_elementos(rfs, res, ree, nombre_pdf)

    return {
        "start_date" : start_date,
        "end_date": end_date,
        "client_id": client_id,
        "create_report": True
    }



if __name__ == "__main__":
    ...
