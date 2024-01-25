import praw
import time
import os
from langchain.tools import tool
from crewai import Agent, Task, Process, Crew
from langchain.agents import Tool
from langchain.agents import load_tools
from dotenv import load_dotenv, find_dotenv
import io

# Load environment variables
_ = load_dotenv(find_dotenv())


from langchain_community.utilities import GoogleSerperAPIWrapper

# to get your api key for free, visit and signup: https://serper.dev/
os.environ["SERPER_API_KEY"] = os.getenv('SERPER_API_KEY')

search = GoogleSerperAPIWrapper()

search_tool = Tool(
    name="Scrape google searches",
    func=search.run,
    description="useful for when you need to ask the agent to search the internet",
)



# To load Human in the loop
human_tools = load_tools(["human"])

# To Load GPT-4
api = os.environ.get("OPENAI_API_KEY")
sub_reddit = os.getenv('SUB_REDDIT', 'default_subreddit')
subject = os.getenv('SUBJECT', 'default_subject')



class BrowserTool:
    @tool("Scrape reddit content")
    def scrape_reddit(max_comments_per_post=3):
        """Useful to scrape a reddit content"""
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT'),
        )
        subreddit = reddit.subreddit(sub_reddit)
        scraped_data = []

        for post in subreddit.hot(limit=7):
            post_data = {"title": post.title, "url": post.url, "comments": []}

            try:
                post.comments.replace_more(limit=0)  # Load top-level comments only
                comments = post.comments.list()
                if max_comments_per_post is not None:
                    comments = comments[:5]

                for comment in comments:
                    post_data["comments"].append(comment.body)

                scraped_data.append(post_data)

            except praw.exceptions.APIException as e:
                print(f"API Exception: {e}")
                time.sleep(60)  # Sleep for 1 minute before retrying

        return scraped_data


"""
- define agents that are going to research latest {subject} tools and write a blog about it 
- explorer will use access to internet and reactjs subreddit to get all the latest news
- writer will write drafts 
- critique will provide feedback and make sure that the blog text is engaging and easy to understand
"""

explorer = Agent(
    role="Senior Researcher",
    goal=f"Find and explore the most exciting projects and companies on {sub_reddit} subreddit in 2024",
    backstory=f"""You are and Expert strategist that knows how to spot emerging trends and companies in {subject}. 
    You're great at finding interesting, exciting projects on {sub_reddit} subreddit. You turned scraped data into detailed reports with names
    of most exciting projects an companies in the {subject} world. ONLY use scraped data from {sub_reddit} subreddit for the report.
    Once you find a relevant tool or product, perform a web search and remember the most relevant web result for it.
    """,
    verbose=True,
    allow_delegation=False,
    tools=[BrowserTool().scrape_reddit],
   
    
)

writer = Agent(
    role="Senior Technical Writer",
    goal=f"Write engaging and interesting blog post about latest {subject} projects using simple, layman vocabulary",
    backstory=f"""You are an Expert Writer on technical innovation, especially in the field of {subject}. You know how to write in 
    engaging, interesting but simple, straightforward and concise. You know how to present complicated technical terms to general audience in a 
    fun way by using layman words.ONLY use scraped data from {sub_reddit} subreddit for the blog.""",
    verbose=True,
    allow_delegation=True,
)

sourcerer = Agent(
    role="Senior Researcher",
    goal=f"Find and explore the most relevant link sources for any tools, products or projects as requested",
    backstory=f"""You are and Expert researcher. When given any subject you will search internet and find the most relevant web pages that can be cited as sources for that subject.
    Your output is a verified URL that can be used as a trustworthy link for getting more information on the subject.
    """,
    verbose=True,
    allow_delegation=False,
    tools=[search_tool] + human_tools,
   
    
)
    

critic = Agent(
    role="Expert Writing Critic",
    goal="Provide feedback and criticize blog post drafts. Make sure that the tone and writing style is compelling, simple and concise",
    backstory="""You are an Expert at providing feedback to the technical writers. You can tell when a blog text isn't concise,
    simple or engaging enough. You know how to provide helpful feedback that can improve any text. You know how to make sure that text 
    stays technical and insightful by using layman terms.
    """,
    verbose=True,
    allow_delegation=True,
    
)

task_report = Task(
    description=f"""Use and summarize scraped data from subreddit LocalLLama to make a detailed report on the latest rising projects in {subject}. Use ONLY 
    scraped data from {sub_reddit} to generate the report. Your final answer MUST be a full analysis report, text only, ignore any code or anything that 
    isn't text. The report has to have bullet points and with 5-10 exciting new {subject} projects and tools. Write names of every tool and project. 
    Each bullet point MUST contain 3 sentences that refer to one specific {subject} company, product, library or anything you found on subreddit {sub_reddit}.  
    """,
    agent=explorer,
)

task_blog = Task(
    description=f"""Write a blog article with text only and with a short but impactful headline and at least 10 paragraphs. Blog should start with a short introduction and then summarize 
    the report on latest {subject} tools found on {sub_reddit} subreddit. Style and tone should be compelling and concise, fun, technical but also use layman words for the general public. Name specific new, exciting projects, apps and companies in {subject} world. Finish with a short concluding paragraph. Don't write "**Paragraph [number of the paragraph]:**", instead start the new paragraph in a new line. Write names of projects and tools in BOLD.
    ONLY include information from {sub_reddit}. Do not include links to Reddit.
    For your Outputs use the following markdown format:
    ```
    ##Intro
    -Introduction to article
    ## [Title of post]
    - Interesting facts
    - Own thoughts on how it connects to the overall theme of the newsletter
    ## [Title of second post]
    - Interesting facts
    - Own thoughts on how it connects to the overall theme of the newsletter
    ##Conclusion and Call to action
    -Conclusion and call to action
    ```
    """,
    agent=writer,
)

task_find_sources = Task(
    description=f"""Read the article provided by {task_blog} and for each product, project, tool or news search on the web and find a relevant source URL.
    ONLY include links to projects/tools/research papers that were obtained in the web search. ONLY include information related to the provided text. Do not include links to Reddit.
   Add the source links to the title of the post in this way:

   ## [Title of post](link to project, product or tool as obtained in web search)
   ## [Title of second post](link to project, product or tool as obtained in web search)
   and so in all titles
    
    """,
    agent=sourcerer,
)

task_critique = Task(
    description="""The Output MUST have the following markdown format:
   ```
    ##Intro
    -Introduction to article
    ## [Title of post](link to project, product or tool as obtained in web search)
    - Interesting facts
    - Own thoughts on how it connects to the overall theme of the newsletter
    ## [Title of second post](link to project, product or tool as obtained in web search)
    - Interesting facts
    - Own thoughts on how it connects to the overall theme of the newsletter
    ##Conclusion and Call to action
    -Conclusion and call to action
    ```
    Check links to see that they are real, correspond to the subject they should, and not hallucinations.
    Make sure that it does and if it doesn't, rewrite it accordingly. Either way, output the complete text in its final form.
    """,
    agent=critic,
)

# instantiate crew of agents
crew = Crew(
    agents=[explorer, writer, sourcerer, critic],
    tasks=[task_report, task_blog, task_find_sources, task_critique],
    verbose=2,
    process=Process.sequential,  # Sequential process will have tasks executed one after the other and the outcome of the previous one is passed as extra content into this next.
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)