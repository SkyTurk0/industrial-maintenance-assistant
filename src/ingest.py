from pathlib import Path
from typing import Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from settings import settings

DATA_DIR = Path("data")
INDEX_DIR = Path("vectorstore")


def load_docs() -> list[Any]:
    docs = []
    for pdf in DATA_DIR.glob("*.pdf"):
        docs.extend(PyPDFLoader(str(pdf)).load())
    for txt in DATA_DIR.glob("*.txt"):
        docs.extend(TextLoader(str(txt), encoding="utf-8").load())
    for md in DATA_DIR.glob("*.md"):
        docs.extend(TextLoader(str(md), encoding="utf-8").load())
    if not docs:
        raise SystemExit("No documents found in /data. Put your PDF/TXT/MD manuals there.")
    return docs


def main() -> None:
    INDEX_DIR.mkdir(exist_ok=True)
    raw_docs = load_docs()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    splits = splitter.split_documents(raw_docs)

    embeddings = HuggingFaceEmbeddings(
        model_name=settings.embeddings_model,
        model_kwargs={"trust_remote_code": True},
        # how to encode DOCUMENT chunks (passages)
        encode_kwargs={
            "task": "retrieval",
            "prompt_name": "passage",
            "truncate_dim": 128,
            "batch_size": 8,
        },
        # how to encode QUERIES (not used in ingest, but good to keep consistent)
        query_encode_kwargs={
            "task": "retrieval",
            "prompt_name": "query",
            "truncate_dim": 128,
            "batch_size": 8,
        },
    )

    db = FAISS.from_documents(splits, embeddings)
    db.save_local(str(INDEX_DIR))

    print(f"Indexed {len(splits)} chunks from {len(raw_docs)} source docs → {INDEX_DIR}")


if __name__ == "__main__":
    main()
