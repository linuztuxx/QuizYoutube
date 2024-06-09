import streamlit as st
import requests


def quiz_creator_ai(prompt):
    template = f"""
    You are a helpful assistant programmed to generate questions based on any text provided. For every chunk of text you receive, you're tasked with designing 5 distinct questions. Each of these questions will be accompanied by 3 possible answers: one correct answer and two incorrect ones. 

    For clarity and ease of processing, structure your response in a way that emulates a Python list of lists. 

    Your output should be shaped as follows:

    1. An outer list that contains 10 inner lists.
    2. Each inner list represents a set of question and answers, and contains exactly 4 strings in this order:
    - The generated question.
    - The correct answer.
    - The first incorrect answer.
    - The second incorrect answer.

    Your output should mirror this structure:
    [
        ["Generated Question 1", "Correct Answer 1", "Incorrect Answer 1.1", "Incorrect Answer 1.2"],
        ["Generated Question 2", "Correct Answer 2", "Incorrect Answer 2.1", "Incorrect Answer 2.2"],
        ...
    ]

    It is crucial that you adhere to this format as it's optimized for further Python processing.

    """

    try:
        endpoint = st.secrets["AI_ENDPOINT"]
        res = requests.post(endpoint, json={
            "model": "Qwen/Qwen1.5-72B-Chat",
            "max_tokens": 1000,
            "temperature": 0.5,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": [
                "<|im_end|>",
                "<|im_start|>"
            ],
            "messages": [
                {
                    "content": template,
                    "role": "system"
                },
                {
                    "content": prompt,
                    "role": "user"
                }
            ]
        }, headers={
            "Authorization": st.secrets["AI_API_KEY"]
        })
        response = res.json()
        print(response['choices'][0]['message']['content'])
        return response['choices'][0]['message']['content']
    
    except Exception as e:
        if "AuthenticationError" in str(e):
            st.error("Something went wrong please try again later...")
            st.stop()
        else:
            st.error("An error occured check the log files for more information.")
            st.stop()