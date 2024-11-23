import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# Define character-specific configurations
characters = {
    "MockBot": {
        "color": "#1e3a8a",
        "avatar": "images/mockbot.jpg",  # Ensure the image is present in a folder named 'images'
        "greeting": "Hello, I am MockBot. Let's begin!",
    },
    "Professor Snape": {
        "color": "#4b0082",
        "avatar": "images/snape.png",
        "greeting": "Ah, another student daring to test their knowledge...",
    },
    "Tony Stark": {
        "color": "#b22222",
        "avatar": "images/iron-man.jpg",
        "greeting": "Hey there! Genius, billionaire, playboy, philanthropist here. Let's see what you've got!",
    },
    "Jitu Bhaiya": {
        "color": "#228b22",
        "avatar": "images/jitubhaiya.jpg",
        "greeting": "Beta, let's check how much you've studied. Dhyan se!",
    },
}

# Function to dynamically generate questions using Google Generative AI
def generate_questions(domain, num_questions):
    try:
        # Create a prompt to generate questions
        prompt = (
            f"Generate {num_questions} multiple-choice quiz questions on the topic of {domain}. "
            "Each question should have 4 options and clearly indicate the correct answer."
        )
        
        # Configure the Generative AI API
        genai.configure(api_key="AIzaSyBUXmEqXWEL35t-_TGu5cRaCocL2hfhgUI")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Extract and parse the response into structured quiz data
        questions_text = response.candidates[0].content.parts[0].text
        questions = parse_questions(questions_text)

        return questions
    except Exception as e:
        st.warning(f"Error generating questions: {e}. Falling back to default questions.")
        # Fallback to static questions
        return [
            {"question": f"Static Question {i+1}", "options": ["A", "B", "C", "D"], "answer": "A"}
            for i in range(num_questions)
        ]

# Function to parse questions from AI response
def parse_questions(questions_text):
    questions = []
    for block in questions_text.split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue
        question = lines[0]
        options = lines[1:-1]
        answer_line = lines[-1]
        if "Answer:" in answer_line:
            answer = answer_line.split("Answer:")[-1].strip()
        else:
            answer = options[0]  # Default to first option if missing
        questions.append({
            "question": question,
            "options": options,
            "answer": answer,
        })
    return questions

# Initialize session state
if "bot_name" not in st.session_state:
    st.session_state.bot_name = "MockBot"
    st.session_state.character = characters["MockBot"]
    st.session_state.quiz_started = False
    st.session_state.questions = []
    st.session_state.score = 0

# UI Setup
st.title("Personality Quiz Bot")
character = st.session_state.character

# Display Character Card
st.markdown(
    f"<div style='background-color: {character['color']}; padding: 10px; border-radius: 5px;'>"
    f"<h2 style='color: white;'>{st.session_state.bot_name}</h2>"
    f"<p style='color: white;'>{character['greeting']}</p>"
    f"</div>",
    unsafe_allow_html=True,
)
st.image(character["avatar"], width=200)

# Quiz Setup
if not st.session_state.quiz_started:
    st.subheader("Setup Your Quiz")
    num_questions = st.slider("Number of Questions", 1, 10, 5)
    domain = st.selectbox("Choose a Domain", ["General Knowledge", "Science", "Technology"])
    selected_character = st.radio(
        "Choose Your Quiz Master", list(characters.keys())
    )

    if st.button("Start Quiz"):
        with st.spinner("Generating your questions..."):
            st.session_state.bot_name = selected_character
            st.session_state.character = characters[selected_character]
            st.session_state.quiz_started = True
            st.session_state.questions = generate_questions(domain, num_questions)
            st.session_state.score = 0
            if not st.session_state.questions:
                st.error("Failed to generate questions. Please try again.")
                st.session_state.quiz_started = False
else:
    st.subheader("Quiz Time!")
    questions = st.session_state.questions

    # Progress through the questions
    for i, question_data in enumerate(questions):
        with st.form(key=f"form_{i}"):
            question = question_data.get("question", "Question text unavailable.")
            options = question_data.get("options", [])
            correct_answer = question_data.get("answer", "")

            st.write(f"Q{i + 1}: {question}")
            user_answer = st.radio("Choose your answer", options, key=f"answer_{i}")
            submit = st.form_submit_button("Submit")

            if submit:
                if user_answer == correct_answer:
                    st.session_state.score += 1
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect! The correct answer was: {correct_answer}")
                break  # Prevent answering multiple questions simultaneously

    # Finish the quiz
    if st.button("Finish Quiz"):
        score = st.session_state.score
        total = len(questions)

        st.balloons()
        st.success(f"You scored {score}/{total}!")

        # Reset to default state
        st.session_state.bot_name = "MockBot"
        st.session_state.character = characters["MockBot"]
        st.session_state.quiz_started = False
        st.session_state.questions = []
        st.session_state.score = 0
        #st.experimental_rerun()
