from fastapi import HTTPException
from src.blogs import service as blog_service
from sqlalchemy.orm import Session
from smolagents import ToolCallingAgent, LiteLLMModel, ManagedAgent, CodeAgent
from .smoltools.jinaai import scrape_page_with_jina_ai, search_facts_with_jina_ai
from dotenv import load_dotenv
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    LiteLLMModel,
    ManagedAgent,
    DuckDuckGoSearchTool,
)
import logging
import os

load_dotenv()

# Initialize the AI model and agent
model = LiteLLMModel(model_id="gpt-4o-mini")

research_agent = ToolCallingAgent(
    tools=[scrape_page_with_jina_ai, search_facts_with_jina_ai, DuckDuckGoSearchTool()],
    model=model,
    max_steps=10,
)

managed_research_agent = ManagedAgent(
    agent=research_agent,
    name="super_researcher",
    description="Researches topics thoroughly using web searches and content scraping. Provide the research topic as input.",
)

# Research Checker Agent
research_checker_agent = ToolCallingAgent(
    tools=[],
    model=model
)

managed_research_checker_agent = ManagedAgent(
    agent=research_checker_agent,
    name="research_checker",
    description="Checks the research for relevance to the original task request. If the research is not relevant, it will ask for more research.",
)

# Writer Agent
writer_agent = ToolCallingAgent(
    tools=[],
    model=model
)

managed_writer_agent = ManagedAgent(
    agent=writer_agent,
    name="writer",
    description="Writes blog posts based on the checkedresearch. Provide the research findings and desired tone/style.",
)

# Copy Editor Agent
copy_editor_agent = ToolCallingAgent(
    tools=[],
    model=model
)

managed_copy_editor = ManagedAgent(
    agent=copy_editor_agent,
    name="editor",
    description="Reviews and polishes the blog post based on the research and original task request. Order the final blog post and any lists in a way that is most engaging to someone working in AI. Provides the final, edited version in markdown.",
)

# Initialize the Blog Writing Manager (similar to your original code)
blog_manager = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[],  # We will need to make sure these are passed correctly in your setup
    additional_authorized_imports=["re"]
)

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def generate_blog_content_and_save(topic: str, db: Session, blog_id: int) -> str:
    try:
        # Log the start of content generation
        logger.info(f"Starting blog generation for topic: {topic}")
        
        # Use the AI model to generate the blog content
        result = blog_manager.run(f"""Create a blog post about: {topic}
        1. Research the topic thoroughly, focus on specific products and sources
        2. Write an engaging blog post, not just a list
        3. Edit and polish the content
        """)

        # Check if the result is empty or invalid
        if not result or len(result.strip()) == 0:
            raise ValueError("AI generated content is empty or invalid.")

        # Log successful content generation
        logger.info(f"Successfully generated content for topic: {topic}")

        # Update the content and status of the blog in the database
        blog_service.update_blog(db, blog_id, result)
        
        return result

    except ValueError as ve:
        # Log the specific issue if content is empty or invalid
        logger.error(f"Failed to generate valid content for topic '{topic}': {ve}")
        raise HTTPException(status_code=500, detail=f"AI generated invalid content: {ve}")
    
    except Exception as e:
        # Log general errors
        logger.error(f"Error generating blog content for topic '{topic}': {e}")
        raise HTTPException(status_code=500, detail=f"Error generating blog content: {e}")
