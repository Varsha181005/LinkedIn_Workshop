import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os

# --- Configuration for Certificate ---
CERTIFICATE_TEMPLATE_PATH = "certificate_template.png" # Make sure this path is correct
FONT_PATH = "" # Optional: Path to your desired font (e.g., "GreatVibes-Regular.ttf"). Leave empty to try Arial/default.

# --- CRITICAL ADJUSTMENTS FOR YOUR 2000x1414px IMAGE ---
# **YOU MUST FINE-TUNE THESE BY TRIAL AND ERROR AFTER TESTING**
# These values are based on your 2000x1414px image dimensions and your template's layout.
FONT_SIZE_NAME = 80 # Adjusted: This is a realistic size for a name on a 1414px high image.
FONT_SIZE_TEXT = 40 # Adjusted: A good size for supporting text.
NAME_Y_POS = 650 # Adjusted Y-coordinate to place the name below "This certificate is presented to".
TEXT_Y_POS = 800 # Example Y-coordinate for other dynamic text if you add it later (e.g., seminar details).
# --- END CRITICAL ADJUSTMENTS ---

COLOR_NAME = (0, 0, 0) # Black color for the name (RGB)
COLOR_TEXT = (50, 50, 50) # Dark grey for other text

# --- Scoring Logic ---
def calculate_linkedin_score(answers):
    score = 0
    if answers['q1'] == 'Yes': score += 5
    if answers['q2'] == 'Yes': score += 5
    if answers['q3'] == 'Yes': score += 5
    if answers['q4'] == 'Yes, detailed': score += 10
    elif answers['q4'] == 'Yes, brief': score += 5
    if answers['q5'] == 'Yes': score += 5

    if answers['q6'] == 'Yes, detailed': score += 10
    elif answers['q6'] == 'Yes, brief': score += 5
    if answers['q7'] == 'Yes, 5+ skills': score += 5
    elif answers['q7'] == 'Yes, 1-4 skills': score += 2
    if answers['q8'] == 'Yes, 5+ endorsements': score += 5
    elif answers['q8'] == 'Yes, 1-4 endorsements': score += 2
    if answers['q9'] == 'Yes, 3+ items': score += 5
    elif answers['q9'] == 'Yes, 1-2 items': score += 2
    if answers['q10'] == 'Yes, 1+ recommendation': score += 5

    if answers['q11'] == '500+': score += 10
    elif answers['q11'] == '100-499': score += 5
    elif answers['q11'] == '1-99': score += 2
    if answers['q12'] == 'Yes, regularly': score += 5
    elif answers['q12'] == 'Sometimes': score += 2
    if answers['q13'] == 'Yes, regularly': score += 5
    elif answers['q13'] == 'Sometimes': score += 2
    if answers['q14'] == 'Yes, 5+ entities': score += 5
    elif answers['q14'] == 'Yes, 1-4 entities': score += 2

    if answers['q15'] == 'Yes, regularly': score += 5
    elif answers['q15'] == 'Yes, occasionally': score += 2
    if answers['q16'] == 'Yes, regularly': score += 5
    elif answers['q16'] == 'Sometimes': score += 2
    if answers['q17'] == 'Yes': score += 5
    return score

def get_score_tier(score):
    if 0 <= score <= 30:
        return "Beginner/Limited Usage: Time to explore LinkedIn's potential!"
    elif 31 <= score <= 60:
        return "Developing User: You're on the right track! Let's optimize your profile."
    elif 61 <= score <= 80:
        return "Proficient User: Great start! Leverage advanced features for more opportunities."
    elif 81 <= score <= 100:
        return "LinkedIn Master: You're an inspiration! Keep networking and growing."
    else:
        return "Score out of range."

# --- Certificate Generation Function ---
def generate_certificate_image(name):
    try:
        img = Image.open(CERTIFICATE_TEMPLATE_PATH).convert("RGB")
        draw = ImageDraw.Draw(img)
        width, height = img.size

        name_font = None
        text_font = None

        if FONT_PATH and os.path.exists(FONT_PATH):
            try:
                name_font = ImageFont.truetype(FONT_PATH, FONT_SIZE_NAME)
                text_font = ImageFont.truetype(FONT_PATH, FONT_SIZE_TEXT)
            except IOError:
                st.warning(f"Error loading custom font from {FONT_PATH}. Trying Arial. Make sure the font file is valid.")
        elif FONT_PATH:
             st.warning(f"Custom font not found at {FONT_PATH}. Trying Arial.")

        if name_font is None:
            try:
                name_font = ImageFont.truetype("arial.ttf", FONT_SIZE_NAME)
                text_font = ImageFont.truetype("arial.ttf", FONT_SIZE_TEXT)
            except IOError:
                st.warning("Arial font not found. Falling back to Pillow's basic default font (which may not scale well).")
                name_font = ImageFont.load_default()
                text_font = ImageFont.load_default()

        if hasattr(name_font, 'getbbox'):
            bbox = draw.textbbox((0, 0), name, font=name_font)
            text_width_name = bbox[2] - bbox[0]
            text_height_name = bbox[3] - bbox[1]
        else:
            text_width_name, text_height_name = draw.textsize(name, font=name_font)

        name_x_pos = (width - text_width_name) / 2
        draw.text((name_x_pos, NAME_Y_POS), name, font=name_font, fill=COLOR_NAME)

        seminar_text = "" # Currently empty; text will not be printed from this variable.
        topic_text = "" # Currently empty; text will not be printed from this variable.

        if seminar_text:
            if hasattr(text_font, 'getbbox'):
                bbox = draw.textbbox((0, 0), seminar_text, font=text_font)
                text_width_seminar = bbox[2] - bbox[0]
                text_height_seminar = bbox[3] - bbox[1]
            else:
                text_width_seminar, text_height_seminar = draw.textsize(seminar_text, font=text_font)

            seminar_x_pos = (width - text_width_seminar) / 2
            draw.text((seminar_x_pos, TEXT_Y_POS), seminar_text, font=text_font, fill=COLOR_TEXT)

        if topic_text:
            if hasattr(text_font, 'getbbox'):
                bbox = draw.textbbox((0, 0), topic_text, font=text_font)
                text_width_topic = bbox[2] - bbox[0]
                text_height_topic = bbox[3] - bbox[1]
            else:
                text_width_topic, text_height_topic = draw.textsize(topic_text, font=text_font)

            topic_x_pos = (width - text_width_topic) / 2
            y_pos_topic = TEXT_Y_POS + (text_height_seminar + 10 if seminar_text else 0)
            draw.text((topic_x_pos, y_pos_topic), topic_text, font=text_font, fill=COLOR_TEXT)

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr.seek(0)
        return img_byte_arr

    except FileNotFoundError:
        st.error(f"Certificate template image not found at: {CERTIFICATE_TEMPLATE_PATH}. Please make sure it's in the correct directory.")
        return None
    except Exception as e:
        st.error(f"An error occurred during image processing: {e}")
        st.exception(e)
        return None

# --- Streamlit App ---
st.set_page_config(page_title="LinkedIn Seminar Tool", layout="centered")

st.title("🎓 LinkedIn Seminar: Assessment & Certificate")
st.markdown("This tool will help you assess your current LinkedIn usage and generate a certificate of completion for the seminar.")

# --- Questionnaire Section ---
st.header("1. LinkedIn Usage Self-Assessment")
st.markdown("Please answer the following questions to determine your LinkedIn proficiency score.")

with st.form("linkedin_questionnaire_form"):
    answers = {}
    st.subheader("Section 1: Profile Completeness")
    answers['q1'] = st.radio("1. Do you have a LinkedIn profile?", ('Yes', 'No'), key='q1')
    answers['q2'] = st.radio("2. Is your profile picture professional and clear?", ('Yes', 'No'), key='q2')
    answers['q3'] = st.radio("3. Do you have a compelling headline that goes beyond \"Student\"?", ('Yes', 'No'), key='q3')
    answers['q4'] = st.radio("4. Have you written a comprehensive \"About\" section that highlights your skills, interests, and career aspirations?", ('Yes, detailed', 'Yes, brief', 'No'), key='q4')
    answers['q5'] = st.radio("5. Have you listed your education, including your current university/college and expected graduation date?", ('Yes', 'No'), key='q5')

    st.subheader("Section 2: Experience & Skills")
    answers['q6'] = st.radio("6. Have you added relevant work experience (internships, part-time jobs, volunteer work) with descriptions of your responsibilities and achievements?", ('Yes, detailed', 'Yes, brief', 'No'), key='q6')
    answers['q7'] = st.radio("7. Have you added relevant skills to your profile?", ('Yes, 5+ skills', 'Yes, 1-4 skills', 'No'), key='q7')
    answers['q8'] = st.radio("8. Have you received any skill endorsements from others?", ('Yes, 5+ endorsements', 'Yes, 1-4 endorsements', 'No'), key='q8')
    answers['q9'] = st.radio("9. Have you added any projects, certifications, or awards to your profile?", ('Yes, 3+ items', 'Yes, 1-2 items', 'No'), key='q9')
    answers['q10'] = st.radio("10. Have you requested any recommendations from professors, supervisors, or mentors?", ('Yes, 1+ recommendation', 'No'), key='q10')

    st.subheader("Section 3: Networking & Engagement")
    answers['q11'] = st.radio("11. How many connections do you have on LinkedIn?", ('500+', '100-499', '1-99', '0'), key='q11')
    answers['q12'] = st.radio("12. Do you actively connect with people in your field of interest, alumni, or recruiters?", ('Yes, regularly', 'Sometimes', 'No'), key='q12')
    answers['q13'] = st.radio("13. Do you engage with posts (like, comment, share) from others in your network or industry?", ('Yes, regularly', 'Sometimes', 'No'), key='q13')
    answers['q14'] = st.radio("14. Do you follow companies, influencers, or industry-specific hashtags?", ('Yes, 5+ entities', 'Yes, 1-4 entities', 'No'), key='q14')

    st.subheader("Section 4: Content Creation & Job Search")
    answers['q15'] = st.radio("15. Have you posted original content (articles, posts, videos) on LinkedIn?", ('Yes, regularly', 'Yes, occasionally', 'No'), key='q15')
    answers['q16'] = st.radio("16. Do you use LinkedIn's job search features (e.g., applying for jobs, saving job alerts)?", ('Yes, regularly', 'Sometimes', 'No'), key='q16')
    answers['q17'] = st.radio("17. Have you set your \"Open to Work\" status or similar features to signal your job search?", ('Yes', 'No'), key='q17')

    submitted = st.form_submit_button("Calculate My LinkedIn Score")

    if submitted:
        score = calculate_linkedin_score(answers)
        st.session_state['linkedin_score'] = score
        st.session_state['score_calculated'] = True
        st.success(f"Your LinkedIn Score: {score} / 100")
        st.info(f"**Your LinkedIn Proficiency Level:** {get_score_tier(score)}")

# --- Certificate Generation Section ---
st.header("2. Generate Your Seminar Certificate")
st.markdown("Once you've completed the assessment, enter your name below to generate your certificate.")

student_name_for_certificate = st.text_input("Enter your Full Name for the Certificate:", key='certificate_name_input')

if st.button("Generate Certificate"):
    if not student_name_for_certificate.strip():
        st.warning("Please enter your name to generate the certificate.")
    else:
        if st.session_state.get('score_calculated', False):
            st.info(f"Generating certificate for: **{student_name_for_certificate}**...")
            certificate_image_buffer = generate_certificate_image(student_name_for_certificate)

            if certificate_image_buffer:
                st.download_button(
                    label="Click Here to Download Your Certificate (JPG)",
                    data=certificate_image_buffer,
                    file_name=f"{student_name_for_certificate}_LinkedIn_Seminar_Certificate.jpg",
                    mime="image/jpeg",
                    key='download_certificate_button'
                )
                st.success("Your certificate is ready for download!")
                st.balloons()
            else:
                st.error("Could not generate certificate. Please check the template path and your name input.")
        else:
            st.warning("Please complete the LinkedIn Usage Self-Assessment first before generating your certificate.")

st.markdown("---")
st.subheader("Instructions for Setting Up Your Streamlit App:")
st.markdown("""
1.  **Save the code:** Save the Python code above as `app.py`.
2.  **Prepare your certificate template image:** Create a PNG or JPG image (e.g., `certificate_template.png` or `certificate_template.jpg`) with your certificate design, leaving blank space for the name and seminar details. **Place this image in the same directory as `app.py`.**
3.  **Optional: Add a custom font:** Download a `.ttf` font file (e.g., `GreatVibes-Regular.ttf`) from a reliable source (like [Google Fonts](https://fonts.google.com/)). **Place it in the same directory as this script.** Update `FONT_PATH` in the code if your font file has a different name. **Strongly recommended for best appearance.** If `FONT_PATH` is left empty, it will try to use "arial.ttf" and then Pillow's default.
4.  **Crucially, adjust `FONT_SIZE_NAME`, `FONT_SIZE_TEXT`, `NAME_Y_POS`, and `TEXT_Y_POS`:**
    * Open your `certificate_template.png` (or `.jpg`) in an image editor and confirm its **pixel dimensions (2000 x 1414 in your case)**.
    * **Through trial and error**, using the recommended starting values above (`FONT_SIZE_NAME = 150`, `NAME_Y_POS = 460`), adjust them slightly until the text appears exactly where and how you want it on your template.
5.  **Install Libraries:** If you haven't already, open your terminal or command prompt and run:
    ```bash
    pip install streamlit Pillow
    ```
6.  **Run the Streamlit app:** In your terminal, navigate to the directory where you saved `app.py`, and run:
    ```bash
    streamlit run app.py
    ```
7.  **Access and Use:** Your browser will automatically open to the Streamlit application (usually `http://localhost:8501`). Users can then complete the questionnaire and generate their certificates.
""")

st.info("Remember to **carefully adjust** the `FONT_SIZE_NAME`, `FONT_SIZE_TEXT`, `NAME_Y_POS`, and `TEXT_Y_POS` variables to match your specific certificate template's design and resolution. Experimentation is key to getting the text to display correctly.")