import json

from dotenv import load_dotenv

load_dotenv()

from app.services.assistants.tools.browser_tools import internet_search

from langsmith import traceable
from langchain_core.documents import Document
from marvin.beta import Application

from app.core.setup_logging import setup_logging

from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from pydantic import BaseModel
import datetime


class UserQuery(BaseModel):
    query: str
    answer: str
    created_at: datetime.datetime


class State(BaseModel):
    user_queries: list[UserQuery] = []


logger = setup_logging(__name__)
embeddings = OpenAIEmbeddings()

INSTRUCTIONS = f"""
        You are a helpful assistant who can answer questions about a given context. Your tasks include the following:
        1. First of all, create a detailed plan to understand the user's objectives and determine how to adjust the query to obtain the most comprehensive and qualified response. This plan should consider the intent and interpretation of the question.
        2. Refactor the user's question to make it more specific and answerable. Create at least two variations of the question to ensure that the answer is relevant and helpful.
        3. If after refactoring the question you are still unsure about the answer, create additional variations of the question to get more context.
        4. Answer the question based only on the <context> that you can obtain from the tool `get_context`. When generating queries, focus on specific and relevant aspects that directly address the user's objectives, such as:
           - For security, search for detailed reports and incidents relevant to the safety of the area.
           - For infrastructure, investigate the condition of public services, utilities, and urban planning.
           - For quality of life, consider factors that contribute to the overall well-being and satisfaction of residents.
           - For other aspects, identify and seek out the most pertinent and insightful information relevant to the user's query.
        5. Ensure to always provide the most recent and up-to-date information available, unless the user explicitly requests data from a specific past period.
        6. Remember to never use the user's query directly to obtain the context. First, understand the objectives, then use the tool to get the context.
        7. Consolidate all the relevant information into a single, comprehensive answer. Do not provide multiple separate responses; instead, synthesize the information to provide a clear and cohesive answer to the user's original question.
        8. If the information is not available within the given context, simply state that the information is not available. Do not suggest or recommend seeking other sources.
        
        Your responses should be precise, accurate, and provide comprehensive answers based on the refined questions. The ultimate goal is to ensure the user's query is addressed effectively, offering relevant and valuable information in a single, consolidated response.
        <parameters>
        Current Date Time: {str(datetime.datetime.now())}
        </parameters>
            """


@traceable(run_type="tool")
def get_context(query: str) -> str:
    """
    Fetches the context from the web for the given query.
    """
    data = internet_search(query)

    logger.info(f"Data fetched successfully for query `{query}`")
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents([Document(page_content=doc.get("content")) for doc in data.get("data")])

    logger.info(f"Text split successfully for query `{query}`")
    db = DocArrayInMemorySearch.from_documents(docs, embeddings)
    response = db.as_retriever(search_kwargs={
        "k": 3
    }).invoke(query)
    return json.dumps([{"content": doc.page_content} for doc in response])


@traceable(run_type="llm")
def internet_search_expert(query):
    """
    The Internet QueryAnswering Specialist answers questions by using internet searches and contextual data to provide comprehensive and accurate information.
    """
    app = Application(
        name='QueryAnswering Specialist',
        instructions=INSTRUCTIONS,
        model="gpt-4o",
        state=State(),
        tools=[get_context]
    )

    result = app.say(query)
    state = app.state

    return state, result


if __name__ == '__main__':
    query = "quais as escolas com maior indice de aprovaçao no vestibular em florianopolis?"
    state, result = internet_search_expert(query)
    print(result)
    print(state)
