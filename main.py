import os
import requests
from scholarly import scholarly
from PyPDF2 import PdfReader

import datetime

import datetime
from scholarly import scholarly


def scrape_paper_metadata(authors_list, domain="marshall.usc.edu", output_file="authorAndPapers.txt"):
    """
    Scrape metadata for papers authored by a list of authors.
    Collect metadata from all verified authors without stopping at the first match.
    Only include papers from the last 10 years and save results to a text file.
    """
    metadata = []
    current_year = datetime.datetime.now().year
    recent_years_limit = current_year - 10  # Define the 10-year window

    with open(output_file, "w", encoding="utf-8") as f:
        for author_name in authors_list:
            print(f"Searching for author: {author_name}")
            f.write(f"Author: {author_name}\n")
            f.write("=" * 40 + "\n")

            search_results = scholarly.search_author(author_name)
            found_verified = False  # Track if a verified author is found

            # Iterate through all search results for this name
            for result in search_results:
                print("Checking result...")
                email_domain = result.get("email_domain", "")
                if domain in email_domain:  # Verify authors at USC
                    found_verified = True
                    print(f"Verified author found: {result['name']} ({email_domain})")
                    f.write(f"Verified Author: {result['name']} ({email_domain})\n")
                    scholarly.fill(result)
                    counterPaper = 0

                    for paper in result.get("publications", []):
                        try:
                            print(f"Processing paper #{counterPaper} for {result['name']}...")

                            # Pre-check for publication year before filling the paper
                            pub_year = paper.get("bib", {}).get("pub_year", "N/A")
                            if pub_year.isdigit() and int(pub_year) >= recent_years_limit:
                                scholarly.fill(paper)  # Only fill if the year is valid

                                metadata_entry = {
                                    "title": paper.get("bib", {}).get("title", "Unknown Title"),
                                    "authors": result["name"],
                                    "year": pub_year,
                                    "doi": paper.get("bib", {}).get("doi", None),
                                    "url": paper.get("pub_url", None)
                                }
                                metadata.append(metadata_entry)

                                # Write to the output file
                                f.write(f"Title: {metadata_entry['title']}\n")
                                f.write(f"Year: {metadata_entry['year']}\n")
                                f.write(f"DOI: {metadata_entry['doi']}\n")
                                f.write(f"URL: {metadata_entry['url']}\n")
                                f.write("-" * 40 + "\n")


                            else:
                                print(f"Skipping paper with invalid or old year: {pub_year}")
                                f.write(f"Skipping paper with invalid or old year: {pub_year}\n")
                        except Exception as e:
                            print(f"Error processing paper: {e}")
                            f.write(f"Error processing paper #{counterPaper}: {e}\n")

                    counterPaper += 1

            if not found_verified:
                print(f"No verified author found for: {author_name}")
                f.write(f"No verified author found for: {author_name}\n")
            f.write("\n")

    return metadata


def fetch_and_download_pdfs(metadata, output_folder="papers"):
    """
    Use metadata to locate and download PDFs.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for paper in metadata:
        title = paper.get("title", "Unknown Title").replace(" ", "_").replace("/", "_")
        url = paper.get("url", "")
        doi = paper.get("doi", "")
        file_name = os.path.join(output_folder, f"{title}.pdf")

        if os.path.exists(file_name):
            print(f"PDF already downloaded: {title}")
            continue

        # Attempt to download directly via URL
        if url and url.endswith(".pdf"):
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(file_name, "wb") as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            f.write(chunk)
                    print(f"Downloaded: {title}")
                else:
                    print(f"Failed to download from URL: {url}")
            except Exception as e:
                print(f"Error downloading {title} from URL: {e}")

        # Placeholder for DOI-based search
        elif doi:
            print(f"TODO: Add logic to fetch using DOI: {doi}")
        else:
            print(f"No download source available for: {title}")

def save_metadata_to_txt(metadata, output_file="papers_metadata.txt"):
    """
    Save metadata to a text file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Full List of Papers:\n\n")
        for paper in metadata:
            f.write(f"Title: {paper.get('title', 'Unknown Title')}\n")
            f.write(f"Authors: {paper.get('authors', 'Unknown Authors')}\n")
            f.write(f"Year: {paper.get('year', 'Unknown Year')}\n")
            f.write(f"Access Link: {paper.get('url', 'No URL Available')}\n\n")
    print(f"Metadata saved to {output_file}")

def extract_text_from_pdf(file_name):
    """
    Extract text from a PDF file using PyPDF2.
    """
    try:
        reader = PdfReader(file_name)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def screen_pdfs_for_acknowledgment(input_folder, lab_name):
    """
    Extract text from PDFs and search for acknowledgments.
    """
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(input_folder, file_name)
            try:
                text = extract_text_from_pdf(file_path)
                if text:
                    if lab_name.lower() in text.lower():
                        print(f"Acknowledgment found in: {file_name}")
                    else:
                        print(f"No acknowledgment in: {file_name}")
            except Exception as e:
                print(f"Error processing {file_name}: {e}")

def main():
    authors_list =  [
    "Thomas Gerald Cummings",
    "Nathanael Fast",
    "Eric Anicich",
    "Zachariah Berry",
    "Peter J. Carnevale",
    "Daniel Fehder",
    "Peer C. Fiss",
    "Sarah Townsend",
    "Cheryl Jan Wakslak",
    "Scott Wiltermuth",
    "Peter H. Kim",
    "Kyle J. Mayer",
    "Florenta Teodoridis",
    "Shon R. Hiatt",
    "Melody H. Chang",
    "Geoffrey Garrett",
    "Nan Jia",
    "Paul S. Adler",
    "Nandini Rajagopalan"
]

    lab_name = "University of Southern California"

    # Step 1: Scrape metadata
    metadata = scrape_paper_metadata(authors_list)

    # Step 2: Save metadata to a text file
    save_metadata_to_txt(metadata, output_file="papers_metadata.txt")

    # Step 3: Download PDFs
    fetch_and_download_pdfs(metadata, output_folder="papers")

    # Step 4: Screen for acknowledgments
    screen_pdfs_for_acknowledgment(input_folder="papers", lab_name=lab_name)

if __name__ == "__main__":
    main()
