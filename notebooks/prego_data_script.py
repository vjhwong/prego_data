#!/usr/bin/env python

import pandas as pd
import PyPDF2
import os
import argparse


def extract_text_from_pdf(pdf_path: str) -> list[tuple[int, str]]:
    """Extract text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        list[tuple[int, str]]: List of tuples where the first element is the page number and the second element is the text on that page.
    """
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        return {f"Page {i}": page.extract_text() for i, page in enumerate(reader.pages)}


def get_month(first_page: str) -> str:
    """Get the month from the first page of the PDF.

    Args:
        first_page (str): Text from the first page of the PDF.

    Returns:
        str: The month in the format "January", "February", etc.
    """
    month_names = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December",
    }
    date_range = first_page.split("\n")[2]
    month = date_range.split("-")[1]
    return month_names[month]


def clean_sales_data(second_page: str) -> str:
    """Clean the sales data from the second page of the PDF.

    Args:
        second_page (str): Text from the second page of the PDF.

    Returns:
        str: Cleaned sales data.
    """
    second_page = second_page.replace("Försäljning efter produkt\n", "")
    second_page = second_page.replace(
        "Namn Sålt Returnerat Exklusive moms Inklusive moms",
        "Namn Sålt Returnerat Exklusive-moms Inklusive-moms",
    )
    second_page = second_page.replace("PANINI, ", "PANINI,")
    second_page = second_page.replace("KAFFE, ", "KAFFE,")
    second_page = second_page.replace("TRIUMF, ", "TRIUMF,")
    second_page = second_page.replace("SÖTA, ", "SÖTA,")
    second_page = second_page.replace("\xa0", "")
    rows = second_page.split("\n")
    sales_data = [row.split(" ") for row in rows]
    sales_data[0].remove("Returnerat")
    return sales_data


def join_product_names(sales_data: list[list[str]]) -> list[list[str]]:
    """Join product names that have been split into multiple elements.

    Args:
        sales_data (list[list[str]]): Sales data.

    Returns:
        list[list[str]]: Sales data with product names joined.
    """
    processed_data = [sales_data[0]]
    for item in sales_data[1:]:
        new_item = []
        name = ""
        i = 0
        while i < len(item):
            if item[i].isdigit():
                break
            name += item[i] + " "
            i += 1
        new_item.append(name.strip())
        new_item.extend(item[i:])
        processed_data.append(new_item)
    return processed_data[:-3]


def convert_to_dataframe(sales_data: list[list[str]], month: str) -> pd.DataFrame:
    """Convert sales data to a DataFrame.

    Args:
        sales_data (list[list[str]]): Sales data.
        month (str): The month in the format "January", "February", etc.

    Returns:
        pd.DataFrame: Sales data as a DataFrame.
    """
    df = pd.DataFrame(sales_data[1:], columns=sales_data[0])
    df["Month"] = month
    return df


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(
        description="Extract data from a PDF file and save it to a CSV file."
    )
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("--output", "-o", help="Path to the output file")
    args = parser.parse_args()

    # Main functionality
    print("Input file:", args.input_file)
    if args.output:
        print("Output file:", args.output)
    else:
        print("Output file not specified")

    pdf = extract_text_from_pdf(args.input_file)
    month = get_month(pdf["Page 0"])
    sales_data = clean_sales_data(pdf["Page 1"])
    sales_data = join_product_names(sales_data)
    df = convert_to_dataframe(sales_data, month)
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"Data saved to {args.output}")
    else:
        print(df)


if __name__ == "__main__":
    main()



