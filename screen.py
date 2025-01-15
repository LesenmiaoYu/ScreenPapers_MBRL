import openai
import csv

# Set your OpenAI API key
openai.api_key = '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'


# Read papers from a metadata file
def read_papers(file_path):
    papers = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            paper = {}
            for line in file:
                line = line.strip()
                if line.startswith("Title:"):
                    if paper:  # Save the previous paper
                        papers.append(paper)
                        paper = {}
                    paper["Title"] = line.replace("Title: ", "")
                elif line.startswith("Authors:"):
                    paper["Authors"] = line.replace("Authors: ", "")
                elif line.startswith("Year:"):
                    paper["Year"] = line.replace("Year: ", "")
            if paper:  # Add the last paper
                papers.append(paper)
    except Exception as e:
        print(f"Error reading file: {e}")
    return papers


# Query OpenAI for each paper
def query_paper(paper):
    try:
        prompt = (
            f"For the work titled '{paper['Title']}' "
            f"by {paper['Authors']}, is it affiliated with USC? Give me either true or false, go based on your intuition if you need. ONLY return T/F"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )

        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"


# Main script
def main():
    input_file = 'papers_metadata.txt'
    output_file = 'paper_screening_results.csv'

    # Read papers from the metadata file
    papers = read_papers(input_file)

    if not papers:
        print("No papers found in the metadata file.")
        return

    # Process each paper and save results
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Authors", "Year", "Response"])

        for paper in papers:
            response = query_paper(paper)
            writer.writerow([paper["Title"], paper["Authors"], paper["Year"], response])
            print(f"Processed: {paper['Title']} - Response: {response}")

    print(f"Screening results saved to {output_file}")


if __name__ == "__main__":
    main()