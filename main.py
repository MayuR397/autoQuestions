import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

def extract_mcq_data(filename):
    with open(filename, 'r') as file:
        content = file.read()

    questions = re.split(r'\n\d+\.\s', content)[1:]

    extracted_questions = []
    for q in questions:
        question_match = re.search(r'^.*?(?=\n[A-D]\))', q, re.DOTALL | re.MULTILINE)
        question_text = question_match.group().strip() if question_match else "No question found"
        options_matches = re.findall(r'^[A-D]\) (.*?)(?=\n[A-D]\)|\nAnswer:)', q, re.DOTALL | re.MULTILINE)
        options = options_matches + ["No option found"] * (4 - len(options_matches))
        answer_match = re.search(r'Answer: ([A-D])', q)
        answer = answer_match.group(1) if answer_match else "No answer found"
        extracted_questions.append((question_text, *options, answer))

    return extracted_questions

def create_quiz(questions, email, password, tags, topic, question_type,content_type):
    # service = Service(r'C:\Users\Mayur\Downloads\Compressed\chromedriver_win32\chromedriver.exe')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get('https://assess-admin.masaischool.com/auth/sign-in')

    wait = WebDriverWait(driver, 10)

    email_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="Email"]')))
    email_input.send_keys(email)

    password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="Password"]')))
    password_input.send_keys(password)

    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
    login_button.click()

    # Wait for the select element to be present and select the desired option
    try:
        select_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'chakra-select')))
        select = Select(select_element)
        select.select_by_visible_text('Masai LMS')
    except TimeoutException as e:
        print(f"Timeout while waiting for the select element: {e}")
        driver.quit()
        return

    # Handle alert if present
    try:
        alert = wait.until(EC.alert_is_present())
        alert.accept()
    except NoAlertPresentException:
        pass

    driver.get('https://assess-admin.masaischool.com/questions/create')

    for question, option_a, option_b, option_c, option_d, correct_answer in questions:
        # Example usage of clicking a specific button in a dropdown
        click_specific_button_in_dropdown(driver, '//button[@id="menu-button-:rh:"]', question_type)
        select_dropdown_option(driver, 'react-select-3-input', 'react-select-3-listbox', tags)
        click_specific_button_in_dropdown(driver, '//button[@id="menu-button-:r17:"]', content_type)

        # Add question
        question_input = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/main/div/div/div/div[3]/div[4]/div/div[2]/textarea")))
        question_input.clear()
        question_input.send_keys(question)

        # Add options
        option_a_input = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/main/div/div/div/div[3]/div[5]/div[1]/div[1]/div[2]/div/div/input")))
        option_a_input.clear()
        option_a_input.send_keys(option_a)

        option_b_input = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/main/div/div/div/div[3]/div[5]/div[1]/div[2]/div[2]/div/div/input")))
        option_b_input.clear()
        option_b_input.send_keys(option_b)

        option_c_input = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/main/div/div/div/div[3]/div[5]/div[1]/div[3]/div[2]/div/div/input")))
        option_c_input.clear()
        option_c_input.send_keys(option_c)

        option_d_input = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/main/div/div/div/div[3]/div[5]/div[1]/div[4]/div[2]/div/div/input")))
        option_d_input.clear()
        option_d_input.send_keys(option_d)

        # Select the correct radio button based on the provided XPath
        select_correct_radio_button(driver, correct_answer)


        #Click on create button
        try:
            # Find and click the "Create" button
            create_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]")))
            create_button.click()
            print("Clicked the 'Create' button.")
        except TimeoutException as e:
            print(f"Timeout while waiting for the 'Create' button: {e}")

    # Keep the browser open until the user manually closes it
    input("Press Enter to close the browser...")
    driver.quit()

def click_specific_button_in_dropdown(driver, button_xpath, button_text):
    dropdown_button = driver.find_element(By.XPATH, button_xpath)
    dropdown_button.click()
    wait = WebDriverWait(driver, 10)
    specific_button = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'chakra-menu__menu-list')]//button[normalize-space(text())='{button_text}']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", specific_button)
    driver.execute_script("arguments[0].click();", specific_button)

def select_dropdown_option(driver, input_id, dropdown_id, keyword):
    input_element = driver.find_element(By.ID, input_id)
    input_element.click()
    input_element.send_keys(keyword)
    wait = WebDriverWait(driver, 10)
    option_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='{dropdown_id}']//div[text()='{keyword}']")))
    option_element.click()
    driver.find_element(By.TAG_NAME, 'body').click()

def select_correct_radio_button(driver, correct_answer):
    xpaths = {
        'A': '/html/body/div[1]/div/div[1]/main/div/div/div/div[3]/div[5]/div[1]/div[1]/div[1]/div/div/label/input',
        'B': '/html/body/div[1]/div/div[1]/main/div/div/div/div[3]/div[5]/div[1]/div[2]/div[1]/div/div/label/input',
        'C': '/html/body/div[1]/div/div[1]/main/div/div/div/div[3]/div[5]/div[1]/div[3]/div[1]/div/div/label/input',
        'D': '/html/body/div[1]/div/div[1]/main/div/div/div/div[3]/div[5]/div[1]/div[4]/div[1]/div/div/label/input'
    }
    xpath = xpaths.get(correct_answer.upper())
    if xpath:
        radio_button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView(true);", radio_button)
        driver.execute_script("arguments[0].click();", radio_button)
    else:
        raise ValueError(f"Invalid correct answer: {correct_answer}")

# Streamlit UI
st.title("Quiz Creator")

email = st.text_input("Email", value="mayur.khachane@masaischool.com")
password = st.text_input("Password", type="password", value="mayur.khachane@masaischool.com213")
question_type = st.selectbox("Type", ['Integer', 'Fill in the blank', 'Multiple choice single choice', 'Multiple choice multiple choice'])
tags = st.selectbox("Tag", ['Frontend->JS', 'NodeJS->NodeJS Basics', 'React->React Basics', 'Java->Revision'])
content_type = st.selectbox("Content-Type", ['Html', 'AdvancedEditor', 'Text', 'Markdown'])
questions_file = st.file_uploader("Questions File", type=["txt"])
topic = st.text_input("Topic")

if st.button("Start"):
    if not email or not password:
        st.warning("Please enter both email and password.")
    elif not questions_file:
        st.warning("Please select a questions file.")
    else:
        # Save the file temporarily
        with open("temp_questions_file.txt", "wb") as f:
            f.write(questions_file.read())
        
        questions = extract_mcq_data("temp_questions_file.txt")
        create_quiz(questions, email, password, tags, topic, question_type, content_type)
        st.success("Quiz creation started.")

