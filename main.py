import streamlit as st
from helpers.youtube_utils import extract_video_id_from_url, get_transcript_text
from helpers.quiz_maker_ai import quiz_creator_ai
from helpers.quiz_utils import get_randomized_options, string_to_list

st.set_page_config(
    page_title="QuizYouTube",
    page_icon="https://scontent.fmnl9-4.fna.fbcdn.net/v/t39.30808-6/434936376_122102643554262820_4654967845999879789_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=5f2048&_nc_eui2=AeEOnls-8YBejVDWEf9fHiLVfNpEX6x4HSl82kRfrHgdKZD6aWhyJkTdWys4-Gcn4LW0x5YQL3Yp1L1I8iWCVuJr&_nc_ohc=halbCDH6ousQ7kNvgEPUZYH&_nc_ht=scontent.fmnl9-4.fna&oh=00_AYDiXALhV3-OxpMR09WYI-H7hpk_CwEI2VJP-lpSCzcFTw&oe=66646C97",
    layout="wide"
)

#hide_streamlit_style = """
#
##MainMenu {visibility: hidden;}
#footer {visibility: hidden;}
#header {visibility: hidden;}
#
#"""

# Set the background image aesthetic
st.markdown(f"""
            <style>
            .stApp {{background-image: url("https://images.unsplash.com/photo-1516557070061-c3d1653fa646?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2070&q=80"); 
                     background-attachment: fixed;
                     background-size: cover}}
            </style>
         """, unsafe_allow_html=True)

st.title(":red[QuizYouTube] - AI :brain:")

st.write("""
Finished a YouTube video and curious about your understanding? Welcome to **QuizYouTube**! by [Linuztx](https://github.com/linuztx)

**How it works:**
 Paste the URL of a YouTube video with English captions.

QuizYouTube will generate questions based on the video's content, turning your watching experience into an interactive quiz. Test your knowledge now!
""")

with st.form("user_input"):
    YOUTUBE_URL = st.text_input("Enter the YouTube video link: ", placeholder="https://youtu.be/bcYwiwsDfGE?si=qQ0nvkmKkzHJom2y")
    submitted = st.form_submit_button("Craft my quiz!")

if submitted or ("quiz_data_list" in st.session_state):
    if not YOUTUBE_URL:
        st.info("Please provide a valid YouTube video link. Head over to [YouTube](https://www.youtube.com/) to fetch one.")
        st.stop()

    with st.spinner("Crafting your quiz... 😎"):
        if submitted:
            video_id = extract_video_id_from_url(YOUTUBE_URL)
            video_transcription = get_transcript_text(video_id)
            quiz_data_str = quiz_creator_ai(video_transcription)
            st.session_state.quiz_data_list = string_to_list(quiz_data_str)

            if 'user_answers' not in st.session_state:
                st.session_state.user_answers = [None for _ in st.session_state.quiz_data_list]
            if 'correct_answers' not in st.session_state:
                st.session_state.correct_answers = []
            if 'randomized_options' not in st.session_state:
                st.session_state.randomized_options = []

            for q in st.session_state.quiz_data_list:
                options, correct_answer = get_randomized_options(q[1:])
                st.session_state.randomized_options.append(options)
                st.session_state.correct_answers.append(correct_answer)

        with st.form(key='quiz_form'):
            st.subheader(":brain: Quiz Time: Test Your Knowledge!")
            for i, q in enumerate(st.session_state.quiz_data_list):
                options = st.session_state.randomized_options[i]
                default_index = st.session_state.user_answers[i] if st.session_state.user_answers[i] is not None else 0
                response = st.radio(q[0], options, index=default_index)
                user_choice_index = options.index(response)
                st.session_state.user_answers[i] = user_choice_index

            results_submitted = st.form_submit_button(label='Unveil My Score')

            if results_submitted:
                score = sum([ua == st.session_state.randomized_options[i].index(ca) for i, (ua, ca) in enumerate(zip(st.session_state.user_answers, st.session_state.correct_answers))])
                st.success(f"Your score: {score}/{len(st.session_state.quiz_data_list)}")

                if score == len(st.session_state.quiz_data_list):
                    st.balloons()
                else:
                    incorrect_count = len(st.session_state.quiz_data_list) - score
                    if incorrect_count == 1:
                        st.warning(f"Almost perfect! You got 1 question wrong. Let's review it:")
                    else:
                        st.warning(f"Almost there! You got {incorrect_count} questions wrong. Let's review them:")

                for i, (ua, ca, q, ro) in enumerate(zip(st.session_state.user_answers, st.session_state.correct_answers, st.session_state.quiz_data_list, st.session_state.randomized_options)):
                    with st.expander(f"Question {i + 1}"):
                        if ro[ua] != ca:
                            st.info(f"Question: {q[0]}")
                            st.error(f"Your answer: {ro[ua]}")
                            st.success(f"Correct answer: {ca}")

        # Add a refresh button to reset the session state
        if st.button("Refresh"):
            st.session_state.clear()
            st.rerun()
