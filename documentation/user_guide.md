# CCI SurveyHUB — User Guide

Step-by-step instructions for CCI staff to use the CCI SurveyHUB application.

---

## 1. Logging In

1. Open your browser and go to `http://127.0.0.1:5000` (or your deployed URL)
2. You will see the login screen
3. Enter your **email** and **password**
4. Click **Login**
5. If the credentials are correct, you will be redirected to the Dashboard
6. If you see "Invalid email or password", check your credentials and try again

**Default test credentials:**

| Email | Password | Role |
|-------|----------|------|
| jean.dupont@cci.fr | admin123 | Admin |
| marie.curie@cci.fr | user123 | User |

> To log out, click the **Logout** link in the bottom-left sidebar.

---

## 2. Creating a Survey

1. Click **Surveys** in the left sidebar
2. Click the **Create Survey** button at the top right
3. A new draft survey is created and you are redirected to the **Survey Builder**
4. In the **Survey Settings** panel (left sidebar):
   - Fill in the **Title** (required)
   - Optionally fill in **Description**, **Objective**, and **Target Audience**
   - Leave the **Status** as "Draft" until you are ready to publish
   - Click **Save Settings**

### Adding Blocks

1. Scroll to the bottom of the builder page
2. Type a title for your block (e.g., "Company Information")
3. Click **Add Block**
4. The new block appears in the builder

### Adding Questions

1. Under the desired block, type your question text in the "Add a question..." field
2. Click **Add Question**
3. The question appears as a multiple-choice question

### Adding Choices

1. Under the desired question, type an answer option in the "Add a choice..." field
2. Click the **+** button
3. Repeat for each answer option

> The first block is expanded by default. Click a block header to collapse or expand it.

---

## 3. Previewing a Survey

1. In the Survey Builder, click the **Preview** button in the top bar
2. A read-only preview of the survey opens in a new tab
3. Verify that all blocks, questions, and choices appear correctly
4. Close the preview tab when done

---

## 4. Publishing a Survey

1. In the Survey Builder, click the **Publish** button in the top bar
2. Confirm the publish action in the dialog
3. The survey status changes to "Published"
4. A **public link** appears in the top bar (e.g., `http://127.0.0.1:5000/survey/a3f9bc12de`)
5. Click the **copy icon** next to the link to copy it to your clipboard

> Once published, respondents can access the survey via the public link without logging in.

---

## 5. Setting a Password on a Public Survey

1. In the Survey Builder, locate the **Response Password** field in the Survey Settings panel
2. Enter a password (e.g., `CCI2025`)
3. Click **Save Settings**
4. Now when a respondent opens the public link, they will see a password entry screen
5. Share the password with your intended respondents separately

> To remove the password protection, clear the password field and save. The form will be publicly accessible again.

---

## 6. Sharing the Survey with Respondents

1. Copy the public link from the Survey Builder top bar
2. Share it via email, messaging, or any channel
3. If a password is set, share the password separately
4. Respondents will:
   - Open the link in their browser
   - Enter the password (if set)
   - Fill in their company information (name, SIRET, email, phone)
   - Answer the survey questions
   - Click **Submit Response**

---

## 7. Viewing Results and Charts

1. Click **Surveys** in the left sidebar
2. Find the survey you want to view
3. Click the **chart icon** (bar chart) next to the survey
4. The Results page shows:
   - **Summary cards**: Total Responses, Complete Responses, Completion Rate
   - **Per-question charts**: Bar charts showing answer distribution
   - **Data tables**: Choice, Count, and Percentage for each question

> Charts use Chart.js and are automatically generated from the collected responses.

---

## 8. Resolving Anomalies

1. Click **Anomalies** in the left sidebar
2. You will see a list of data quality issues detected during form submissions
3. Use the **Status** filter to show Open or Resolved anomalies
4. Use the **Issue Type** filter to filter by: Invalid Format, Missing Value, or Duplicate
5. For each anomaly, review the company name, field, and issue
6. Click **Resolve** to mark an anomaly as resolved

**Common issue types:**

| Issue | Description |
|-------|-------------|
| Invalid Format | Email, SIRET, or phone number format is incorrect |
| Missing Value | A required field was left empty |
| Duplicate | A SIRET number already exists in the system |

---

## 9. Exporting Data

### Export Survey Responses (CSV or Excel)

1. Click **Surveys** in the left sidebar
2. Click the **chart icon** next to the survey to open the Results page
3. Click **Export CSV** or **Export Excel** in the top-right corner
4. The file will download automatically

**Columns included:**
- Company Name, SIRET, Email, Phone
- Submitted At, Status
- One column per question with the selected choice

> Excel exports have bold headers and auto-filters enabled, making them ready for Power BI import.

### Export Anomalies Report

1. Click **Exports** in the left sidebar
2. Click **Export Anomalies CSV**
3. The file will download automatically

**Columns included:**
- Company Name, Field, Issue Type, Status
- Detected At, Resolved At, Resolved By

---

## 10. Using the AI Assistant

1. Click the **blue chat icon** in the bottom-right corner of any internal page
2. The AI Assistant panel opens
3. Type your question about CCI SurveyHUB in the input field
4. Press **Enter** or click **Send**
5. The assistant responds with step-by-step guidance

**Example questions:**
- "How do I create a survey?"
- "How do I publish a survey?"
- "How do I export data to Excel?"
- "How do I set a password on a survey?"
- "How do I resolve an anomaly?"

> The AI Assistant only answers questions about using CCI SurveyHUB. If you ask something unrelated, it will politely redirect you.

---

## Quick Reference

| Action | Where |
|--------|-------|
| Create a survey | Surveys → Create Survey |
| Add questions | Survey Builder → Add Question |
| Preview survey | Survey Builder → Preview |
| Publish survey | Survey Builder → Publish |
| Set password | Survey Builder → Response Password field |
| View results | Surveys → Chart icon |
| Export CSV/Excel | Results page → Export buttons |
| View anomalies | Sidebar → Anomalies |
| Export anomalies | Sidebar → Exports → Export Anomalies CSV |
| AI Assistant | Blue chat icon (bottom-right) |
| Logout | Sidebar → Logout |
