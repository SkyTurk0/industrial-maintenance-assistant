import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import FAISS as FAISSStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from settings import settings

st.set_page_config(page_title="Industrial Maintenance Assistant", page_icon="🛠️", layout="wide")
st.title("🛠️ Industrial Maintenance Assistant")


@st.cache_resource  # type: ignore
def load_db() -> FAISSStore:
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.embeddings_model,
        model_kwargs={"trust_remote_code": True},
        encode_kwargs={
            "task": "retrieval",
            "prompt_name": "passage",
            "truncate_dim": 128,
            "batch_size": 8,
        },
        query_encode_kwargs={
            "task": "retrieval",
            "prompt_name": "query",
            "truncate_dim": 128,
            "batch_size": 8,
        },
    )

    return FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)


db = load_db()

question = st.text_input(
    "Ask a question about the Siemens S7-1200/1500 programming guideline:",
    placeholder="e.g., What is OB1 and how is the scan cycle defined?",
)
top_k = st.slider("Retrieved passages", 2, 8, 4)

if st.button("Search") and question:
    docs = db.similarity_search(question, k=top_k)
    context = "\n\n---\n\n".join([d.page_content[:1200] for d in docs])

    prompt = ChatPromptTemplate.from_template(
        "You are a precise industrial maintenance assistant for Siemens PLCs. "
        "Answer using ONLY the context from manuals. "
        "If the answer is not in the context, say you don't know.\n\n"
        "Question:\n{q}\n\nContext:\n{ctx}\n\nAnswer:"
    ).format(q=question, ctx=context)

    if settings.llm_provider == "openai" and settings.openai_api_key:
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.1,
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
        )
        answer = llm.invoke(prompt).content
    else:
        answer = "No LLM configured. Showing retrieved context:\n\n" + context[:1000]

    st.subheader("Answer")
    st.write(answer)

    with st.expander("Sources (top passages)"):
        for i, d in enumerate(docs, start=1):
            st.markdown(f"**{i}.** {d.metadata.get('source','unknown')}")
