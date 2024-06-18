### Running the Application

1. **Setup Steps:**

   - **Step 1:** Clone the repository containing the application code. or Unzip the files
   - **Step 2:** Ensure you have Python installed on your system (Python 3.6 or higher is recommended).
   - **Step 3:** Install required Python packages using `pip`:
     ```bash
     pip install openai python-dotenv
     ```
   - **Step 4:** Obtain an OpenAI API key and store it in a `.env` file in the root directory of the project:
     ```plaintext
     OPENAI_API_KEY=your-api-key-here
     ```

2. **Running the Application:**

   - **Step 1:** Navigate to the directory where the `app.py` file is located.
   - **Step 2:** Run the script using Python:
     ```bash
     python app.py
     ```

3. **Expected Output:**

   - The script will load a sample Jupyter notebook (`Sample1.ipynb`) located in the `notebook/` directory.
   - It will generate variations of each cell in the notebook using the OpenAI GPT-4 model.
   - The varied notebook will be saved as `varied/notebook.json`.
   - Confirmation messages will be printed indicating where variations were saved.

