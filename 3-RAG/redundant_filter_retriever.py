from langchain.embeddings.base import Embeddings
from langchain.vectorstores.chroma import Chroma
from langchain.schema import BaseRetriever

class RedundantFilterRetriever(BaseRetriever):
    """
    Vector stores are required by LangChain to have an oject that functions 
    as a retriever and has two methods 
    (get_relevant_documents and aget_relevant_documents).
    Instead of using the built in object for Chroma, we are making a custom 
    retriever object.
    """
    #    Require the instantiator to 
    # 1. specify an embedding (named `embeddings`) that is the class Embeddings
    # 2. specify a vector store (named `chroma`) that is in the class Chroma
    embeddings: Embeddings 
    chroma: Chroma

    def get_relevant_documents(self, query_string ):
        """
        This method is required for any retriever object 
        """
        # Calculate image of query.
        query_vector = self.embeddings.embed_query(query_string)
        # Feed image to max_marginal_relevance_search_by_vector 
        results = self.chroma.max_marginal_relevance_search_by_vector(
            embedding = query_vector, # the parameter name is LangChain's fault. 
            lambda_mult=0.8 
            )
        return results
    
    async def aget_relevant_documents(self):
        return []