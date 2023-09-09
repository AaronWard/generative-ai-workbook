from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import DuckDuckGoSearchRun

# Function to generate video script


def generate_script(prompt, data_text, video_length, creativity, api_key):

    # Template for generating 'Title'
    title_template = PromptTemplate(
        input_variables=["subject", "additional_context"],
        template='Please come up with a short and clever title for a YouTube video on the following topic: {subject}. {additional_context}')

    subject_template = PromptTemplate(
        input_variables=["subject", "title", "additional_context"],
        template='Please create a short but descriptive google search term for research for this proposed {subject} article titled: {title}. {additional_context}')

    # Template for generating 'Video Script' using search engine
    script_template = PromptTemplate(
        input_variables=['title', 'DuckDuckGo_Search',
                         'duration', "additional_context"],
        template='Create a script for a YouTube video based on this title for me. TITLE: {title} of duration: {duration} minutes using this search data {DuckDuckGo_Search}. {additional_context}'
    )

    # Setting up OpenAI LLM
    llm = OpenAI(temperature=creativity, openai_api_key=api_key,
                 model_name='gpt-4')

    # Creating chain for 'Title' & 'Video Script'
    title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True)
    subject_chain = LLMChain(llm=llm, prompt=subject_template, verbose=True)
    script_chain = LLMChain(llm=llm, prompt=script_template, verbose=True)

    # https://python.langchain.com/docs/modules/agents/tools/integrations/ddg
    search = DuckDuckGoSearchRun()

    # if data has been uploaded
    def add_context(data_text, context_len=100):
        context = ""
        if data_text != "":
            context = f"""Here is some text for additional context to base your answer on, but you are not limited to using what's in this text for your response: {data_text[:context_len]}
            """
        return context

    # Executing the chains we created for 'Title'
    title_context = add_context(data_text, context_len=100)
    title = title_chain.run(subject=prompt, additional_context=title_context)

    search_term = subject_chain.run(subject=prompt, title=title, additional_context=title_context)
    print(search_term)

    # Executing the chains we created for 'Video Script' by taking help of search engine 'DuckDuckGo'
    search_result = search.run(search_term)

    # Executing the chain for making the script
    script_context = add_context(data_text, context_len=3000)
    script = script_chain.run(title=title,
                              DuckDuckGo_Search=search_result,
                              duration=video_length,
                              additional_context=script_context)

    # Returning the output
    return search_result, title, script
