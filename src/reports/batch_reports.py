from pathlib import Path
import shutil
import pandas as pd

from src.reports.tearsheet import build_tearsheet

#Paths

PROJECT_ROOT =Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEARSHEET_DIR = PROJECT_ROOT / "reports" / "tearsheets"
SKIPPED_FILE = OUTPUT_DIR / "skipped_tearsheets.csv"

#Main

def generation_batch_tearsheets():

    TEARSHEET_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    companies = pd.read_csv(DATA_DIR / "companies_clean.csv")
    financial = pd.read_csv(DATA_DIR / "financial_ratios_clean.csv")
    skipped = []
    generated = []

    #Number of uniwue years available for each company

    year_counts = (financial.groupby("company_id")["year"].nunique())

    print("=" * 60)
    print("DAY 34 - BATCH TEARSHEET GENERATION")
    print("=" * 60)

    print(f"Total companies: {len(companies)}")
    print()

    for _, company in companies.iterrows():

        company_id = company["id"]
        company_name = company["company_name"]

        years = int(year_counts.get(company_id, 0))

        print(
            f"{company_id:<15} "
            f"{company_name[:35]:<35} "
            f"Years: {years}"
        )

        #Skip companies with fewer than 3 years

        if years < 3:

            skipped.append({
                "company_id": company_id,
                "company_name": company_name,
                "years_available": years,
                "reason": "Fewer than 3 years of data"
            })

            print("    -> SKIPPED")

            continue

        #Generate Tearsheet
         
        try:

            build_tearsheet(company_id)

            source_file = OUTPUT_DIR / f"{company_id}_tearsheet.pdf"
            destination_file = (
                TEARSHEET_DIR / f"{company_id}_tearsheet.pdf"
            )

            if source_file.exists():

                shutil.copy2(
                    source_file,
                    destination_file
                )

                generated.append(company_id)

                print("    -> GENERATED")

            else:

                skipped.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "years_available": years,
                    "reason": "Tearsheets PDF was not created"
                })

                print("    -> FAILED: PDF was not found")

        except Exception as e:

            skipped.append({
                "company_id": company_id,
                "company_name": company_name,
                "years_available": years,
                "reason": f"Generation error {str(e)}"
            })

            print("    -> FAILED: {e}")

    #Saved Skipped Companies

    skipped_df = pd.DataFrame(skipped)

    skipped_df.to_csv(
        SKIPPED_FILE,
        index=False
    )

    #Summary

    print("=" * 60)
    print("BATCH GENERATION COMPLETE")
    print("=" * 60)

    print(f"Total companies : {len(companies)}")
    print(f"Generated       : {len(generated)}")
    print(f"Skipped         : {len(skipped)}")

    print()
    print(f"Tearsheets saved to:")
    print(TEARSHEET_DIR)

    print()
    print(f"Skipped log:")
    print(SKIPPED_FILE)

if __name__ == "__main__":
    generation_batch_tearsheets()
          