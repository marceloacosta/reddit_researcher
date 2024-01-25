# Reddit researcher

## Overview

This project involves a complex setup integrating multiple APIs and libraries to perform web scraping, data analysis, and content generation. The main focus is on using Reddit data to generate reports and blog posts about specific subjects, along with sourcing and critiquing information. 

Key components include:
- `praw`: Python Reddit API Wrapper for scraping Reddit data.
- `langchain`: Tools for chaining language models and utilities.
- `crewai`: For defining agents and tasks.
- `dotenv`: To manage environment variables.
- `io`: For input/output operations.

## Requirements

To run this project, you need to install the following Python libraries:
- `praw`
- `langchain`
- `crewai`
- `python-dotenv`

You can install these packages using pip:

```bash
pip install praw langchain crewai python-dotenv
```

## Setting Up the `.env` File

This project requires setting up an environment file (`.env`) to securely store API keys and other sensitive information. Here's how to set it up:

1. **Create a `.env` file** in your project directory.

2. **Add the following variables** to your `.env` file:

   ```
   SERPER_API_KEY=your_google_serper_api_key
   OPENAI_API_KEY=your_openai_api_key
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT=your_reddit_user_agent
   SUB_REDDIT=specific_subreddit_to_scrape
   SUBJECT=topic_of_interest
   ```

3. Replace `your_*` with your actual API keys and configurations.

   - **SERPER_API_KEY**: Your API key for Google SERPer. Obtain it from [serper.dev](https://serper.dev/).
   - **OPENAI_API_KEY**: Your OpenAI API key.
   - **REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT**: Credentials for using the Reddit API via `praw`. Get these by registering your application on Reddit.
   - **SUB_REDDIT**: The specific subreddit you want to scrape.
   - **SUBJECT**: The topic or subject of interest for content generation.

4. **Save the `.env` file**.

## Usage

After setting up the `.env` file and installing the required packages, you can run the script. The script will:
1. Scrape content from the specified subreddit.
2. Use various agents and tasks for researching, writing, sourcing, and critiquing content.
3. Produce a final output which includes detailed reports and blog posts about the specified subject.

## Notes
- Make sure your Reddit API usage complies with Reddit's terms and guidelines.
- Ensure the `.env` file is included in your `.gitignore` to prevent sensitive data from being pushed to version control systems. 

## Contribution

Contributions are welcome. Please open an issue or submit a pull request with your suggestions or improvements.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). See the LICENSE file for more details.

---

For any additional questions or clarifications, please open an issue in the project's repository.

---

