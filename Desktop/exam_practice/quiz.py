import google.generativeai as genai
from dotenv import load_dotenv
import os
import ast
import streamlit as st

load_dotenv()
key = os.getenv("KEY")


genai.configure(api_key=key)



st.title("📝 AI Quiz Generator")


# Initialize all session state variables
if "quiz_ready" not in st.session_state:
    st.session_state.quiz_ready = False
if "lists" not in st.session_state:
    st.session_state.lists = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "i" not in st.session_state:
    st.session_state.i = 0
if "answer" not in st.session_state:
    st.session_state.answer = None



topic = st.text_input("Enter a topic for the quiz:")
filename = f"data/{topic}.txt"


if st.button("Generate Quiz"):
    st.spinner("Generating quiz...")
  
    # Step 1: Try loading quiz from file
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            raw_output = f.read().strip()

    else:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Generate a quiz with 15 questions about {topic}. Each question should have 4 options (A, B, C, D) and indicate the correct option number (1 for A, 2 for B, etc.). Format the output as a list of lists, where each inner list contains the question, four options, and the correct option number.")
        raw_output = response.text.strip()

        # Remove markdown-style code fences if they exist
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1]  # keep inside the fences
            # sometimes it starts with "python\n", so remove that too
            raw_output = raw_output.replace("python\n", "").replace("python", "").strip()

        # Remove "quiz =" if Gemini included it
        if raw_output.startswith("quiz ="):
            raw_output = raw_output.split("=", 1)[1].strip()


        print(raw_output)

        with open(f"data/{topic}.txt", "w", encoding="utf-8") as file:
            file.write(raw_output)
    
    st.session_state.lists = ast.literal_eval(raw_output) 
    st.session_state.quiz_ready = True   
    st.session_state.score = 0            
    st.session_state.i = 0
    st.rerun() 


if st.session_state.quiz_ready == True:
    lists = st.session_state.lists
            
        
    i = st.session_state.i


    if i < len(lists):
        q = lists[i]
        st.subheader(f"Question {i+1}: {q[0]}")

        chosen = st.radio(
                "Choose:",
                [("1. " + q[1], 1), ("2. " + q[2], 2), ("3. " + q[3], 3), ("4. " + q[4], 4)],
                format_func=lambda x: x[0],
                horizontal=True,
                key=f"choice_{i}",
                index=None
            )

        if st.button(f"Submit Q{i+1}", key=f"submit_{i}"):
                if chosen is not None:
                    option = chosen[1]  # get the number
                    if option == q[5]:
                        st.session_state.answer = "correct"
                        st.session_state.score += 1
                    else:
                        st.session_state.answer = "wrong"
                

                st.rerun()
                # Show next button
        if "answer" in st.session_state:
            
            if st.session_state.answer == "correct":
                st.success("✅ Correct!")
            elif st.session_state.answer == "wrong":
                st.error(f"❌ Wrong! Correct answer: option {q[5]}")

            if st.button("Next Question", key=f"next_{i}"):
                st.session_state.i += 1
                del st.session_state.answer
                st.rerun()
                    
    else:
        st.success(f"🎉 Quiz finished! Final Score: {st.session_state.score}/{len(lists)}")