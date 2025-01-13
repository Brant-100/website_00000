from fuzzywuzzy import process
import requests
import openai

openai.api_key = "your-openai-api-key"  # Replace with your OpenAI API key

def parse_doc_content(doc_content):
    """
    Parses the Google Doc content into a dictionary of questions and answers.
    """
    qa_pairs = {}
    lines = doc_content.split("\n")  # Split content by lines
    current_question = None

    for line in lines:
        line_lower = line.strip().lower()
        if "question:" in line_lower:  # Find lines containing "Question:"
            current_question = line.split(":", 1)[1].strip()
        elif "answer:" in line_lower and current_question:
            answer = line.split(":", 1)[1].strip()
            qa_pairs[current_question] = answer
            current_question = None  # Reset for the next Q&A pair
    return qa_pairs

def get_answer_from_doc(doc_content, user_query):
    """
    Finds the best match for the user query and retrieves the corresponding answer.
    Ensures the answer is only returned if the match is sufficiently close.
    """
    qa_pairs = parse_doc_content(doc_content)
    if not qa_pairs:
        return None  # No questions and answers found
    
    # Match the user query to the closest question
    questions = list(qa_pairs.keys())
    best_match = process.extractOne(user_query, questions)
    
    # If the match score is above the threshold (80%), return the answer
    if best_match and best_match[1] > 80:
        return qa_pairs[best_match[0]]  # Return the corresponding answer
    
    return None  # No relevant answer found in the document

def fallback_to_chatgpt(query, custom_prompt):
    """
    Queries ChatGPT with a custom prompt when no relevant answer is found in the Google Doc.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": custom_prompt},
                {"role": "user", "content": query}
            ]
        )
        return response['choices'][0]['message']['content']
    except openai.error.AuthenticationError:
        return "Error: Invalid OpenAI API key."
    except openai.error.RateLimitError:
        return "Error: Rate limit exceeded. Please try again later."
    except openai.error.APIError as e:
        return f"Error: API call failed - {e}"
    except Exception as e:
        return f"Error: {e}"

def chatbot_with_link(doc_link, query, custom_prompt):
    """
    Fetch content from the Google Doc, find the answer to the query, and use ChatGPT as a fallback only if needed.
    """
    try:
        # Extract document ID from the link
        doc_id = doc_link.split("/d/")[1].split("/")[0]
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
        
        # Fetch the document content
        response = requests.get(export_url)
        if response.status_code != 200:
            return "Error: Failed to fetch document."
        
        doc_content = response.text  # Get document content as plain text
        
        # Try to get an answer from the document
        answer = get_answer_from_doc(doc_content, query)
        
        if answer:
            # Return the answer in the desired format from the document
            return f"answer: {answer}", True  # Return True for document answer
        else:
            # Fallback to ChatGPT if no relevant answer is found in the document
            chatgpt_response = fallback_to_chatgpt(query, custom_prompt)
            return f"answer: {chatgpt_response}", False  # Return False for ChatGPT answer
    except Exception as e:
        return f"Error: {e}", False

# Main loop for handling multiple questions
if __name__ == "__main__":
    doc_link = "https://docs.google.com/document/d/12H7dNbrc7ZosAl_wGuouuznzKf7PugaJlIf96X58t1s/edit?tab=t.0"
    custom_chatgpt_prompt = "You are a helpful assistant who provides short and concise answers to any question. Only answer the user's question without extra context."
    
    print("Welcome to the chatbot! You can ask as many questions as you'd like.")
    while True:
        user_query = input("What can I help you with today? (Type 'exit' to quit) ")
        
        if user_query.lower() == "exit":
            print("Goodbye!")
            break
        
        # Get the response from the document or ChatGPT
        response, from_doc = chatbot_with_link(doc_link, user_query, custom_chatgpt_prompt)
        
        # Output the answer
        print(response)
        
        # Ask if the answer was helpful
        helpful = input("Was this answer helpful? (yes/no): ").strip().lower()
        
        if helpful == "yes":
            print("Thanks for using me! Have a great day!")
        elif helpful == "no":
            print("Sorry about that. Let me try answering again with ChatGPT.")
            # If not helpful, just use ChatGPT to answer
            chatgpt_response = fallback_to_chatgpt(user_query, custom_chatgpt_prompt)
            print(f"answer: {chatgpt_response}")
        else:
            print("Please respond with 'yes' or 'no'.")
