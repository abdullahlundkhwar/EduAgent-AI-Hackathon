
import streamlit as st
from google import genai
import time


# ==============================
# Gemini API
# ==============================

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)


# ==============================
# Retry Function
# ==============================

def generate_with_retry(prompt, max_retries=3):

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            return response.text

        except Exception as e:

            if "503" in str(e) or "UNAVAILABLE" in str(e):

                time.sleep(5)

            else:
                raise e

    raise Exception(
        "Gemini is still unavailable after several attempts."
    )


# ==============================
# Planning Agent
# ==============================

def planning_agent(
    subject,
    grade,
    topic,
    duration,
    difficulty
):

    prompt = f"""
You are the Planning Agent of EduAgent AI,
a multi-agent teaching assistant for teachers.

Create a structured lesson plan using the information below.

Subject: {subject}
Grade: {grade}
Topic: {topic}
Class Duration: {duration} minutes
Difficulty Level: {difficulty}

Create:

1. Three clear learning objectives
2. A short introduction to the topic
3. A lesson sequence with time allocation
4. Teaching/learning activities
5. A suitable classroom activity
6. A short conclusion
7. Materials/resources required

Make the lesson appropriate for the specified grade.
Use simple, clear language.
Focus on accurate educational content.

Return the answer with clear headings.
"""

    return generate_with_retry(prompt)


# ==============================
# Content Agent
# ==============================

def content_agent(
    subject,
    grade,
    topic,
    lesson_plan
):

    prompt = f"""
You are the Content Agent of EduAgent AI.

Your job is to create high-quality teaching content
based on the lesson plan prepared by the Planning Agent.

Teacher information:
Subject: {subject}
Grade: {grade}
Topic: {topic}

Lesson plan from Planning Agent:
{lesson_plan}

Create:

1. A clear explanation of the topic
2. Important concepts and definitions
3. Important formulas, if applicable
4. One or two simple real-life examples
5. A worked example suitable for the students
6. A classroom activity
7. Three questions the teacher can ask students

Requirements:
- Keep the content appropriate for the specified grade.
- Use simple language.
- For Physics, make sure formulas and scientific concepts are accurate.
- Do not introduce advanced concepts unnecessarily.
- Organize the answer with clear headings.
"""

    return generate_with_retry(prompt)


# ==============================
# Assessment Agent
# ==============================

def assessment_agent(
    subject,
    grade,
    topic,
    content
):

    prompt = f"""
You are the Assessment Agent of EduAgent AI.

Create assessments based on the teaching content.

Subject: {subject}
Grade: {grade}
Topic: {topic}

Teaching content:
{content}

Create:

1. Five multiple-choice questions (MCQs)
   - Give 4 options for each question
   - Clearly identify the correct answer

2. Three short-answer questions
   - Suitable for the specified grade
   - Include a brief answer/key point for each

3. Two homework questions
   - One basic question
   - One application-based question

Requirements:
- Questions must be based on the provided content.
- Keep the difficulty appropriate for the grade.
- Avoid ambiguous questions.
- Make sure the answers are scientifically accurate.
- Use clear formatting and headings.
"""

    return generate_with_retry(prompt)


# ==============================
# Review Agent
# ==============================

def review_agent(
    subject,
    grade,
    topic,
    lesson_plan,
    content,
    assessment
):

    prompt = f"""
You are the Review Agent of EduAgent AI.

Review the complete teaching package.

Subject: {subject}
Grade: {grade}
Topic: {topic}

LESSON PLAN:
{lesson_plan}

TEACHING CONTENT:
{content}

ASSESSMENT:
{assessment}

Review for:

1. Scientific accuracy
2. Grade appropriateness
3. Alignment between learning objectives and content
4. Alignment between content and assessment
5. Clarity and readability
6. Correct formulas and calculations
7. Quality of MCQs and answers
8. Suitable difficulty level

Provide:

A. Overall quality rating out of 10

B. Problems or issues found

C. Specific corrections needed

D. Final recommendations for the teacher

If everything is correct, clearly say:
"No major issues found."

Keep the review concise and useful.
"""

    return generate_with_retry(prompt)


# ==============================
# Complete Multi-Agent Pipeline
# ==============================

def generate_teaching_package(
    subject,
    grade,
    topic,
    duration,
    difficulty
):

    lesson_plan = planning_agent(
        subject,
        grade,
        topic,
        duration,
        difficulty
    )

    content = content_agent(
        subject,
        grade,
        topic,
        lesson_plan
    )

    assessment = assessment_agent(
        subject,
        grade,
        topic,
        content
    )

    review = review_agent(
        subject,
        grade,
        topic,
        lesson_plan,
        content,
        assessment
    )

    return {
        "lesson_plan": lesson_plan,
        "content": content,
        "assessment": assessment,
        "review": review
    }


# ==============================
# Streamlit Interface
# ==============================

st.set_page_config(
    page_title="EduAgent AI",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 EduAgent AI")
st.subheader("Multi-Agent Teaching Assistant")

st.write(
    "Generate a complete teaching package using "
    "four specialized AI agents."
)


# Teacher Inputs
# Using a form + explicit keys makes the text fields stable and editable
# and sends all teacher inputs together when Generate is pressed.

with st.form("teaching_package_form"):

    subject = st.text_input(
        "Subject",
        value="Physics",
        key="subject_input",
        placeholder="e.g. Physics"
    )

    grade = st.text_input(
        "Grade",
        value="Grade 9",
        key="grade_input",
        placeholder="e.g. Grade 9"
    )

    topic = st.text_input(
        "Topic",
        value="Ohm's Law",
        key="topic_input",
        placeholder="e.g. Ohm's Law"
    )

    duration = st.number_input(
        "Class Duration (minutes)",
        min_value=10,
        max_value=180,
        value=40,
        step=5,
        key="duration_input"
    )

    difficulty = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1,
        key="difficulty_input"
    )

    submitted = st.form_submit_button(
        "🚀 Generate Teaching Package",
        type="primary"
    )


# Generate Button

if submitted:

    with st.spinner(
        "EduAgent AI is preparing your teaching package..."
    ):

        package = generate_teaching_package(
            subject,
            grade,
            topic,
            duration,
            difficulty
        )

    st.success(
        "Teaching package generated successfully!"
    )

    st.header("📚 Lesson Plan")
    st.markdown(package["lesson_plan"])

    st.header("🧠 Teaching Content")
    st.markdown(package["content"])

    st.header("📝 Assessment")
    st.markdown(package["assessment"])

    st.header("🔍 Review")
    st.markdown(package["review"])
