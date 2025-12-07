#!/usr/bin/env python3
"""
Text Summarization using TF-IDF
Extractive summarization based on sentence importance scoring
"""

import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def sentence_tokenize(text):
    """Simple sentence tokenizer"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def summarize_text(text, num_sentences=3, method='tfidf'):
    """
    Generate extractive summary using TF-IDF
    
    Args:
        text: Input text to summarize
        num_sentences: Number of sentences in summary
        method: Summarization method ('tfidf', 'textrank')
    
    Returns:
        dict: Summary results
    """
    sentences = sentence_tokenize(text)
    
    if not sentences:
        raise ValueError("No sentences found in text")
    
    if len(sentences) <= num_sentences:
        return {
            "summary": text,
            "sentences": sentences,
            "compression_ratio": 1.0
        }
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    try:
        sentence_vectors = vectorizer.fit_transform(sentences)
    except ValueError:
        # If all words are stop words or text is too short
        return {
            "summary": ' '.join(sentences[:num_sentences]),
            "sentences": sentences[:num_sentences],
            "compression_ratio": num_sentences / len(sentences)
        }
    
    if method == 'textrank':
        # TextRank algorithm using cosine similarity
        similarity_matrix = cosine_similarity(sentence_vectors)
        
        # PageRank algorithm
        scores = np.ones(len(sentences))
        damping = 0.85
        iterations = 10
        
        for _ in range(iterations):
            new_scores = np.ones(len(sentences)) * (1 - damping)
            for i in range(len(sentences)):
                for j in range(len(sentences)):
                    if i != j and similarity_matrix[i][j] > 0:
                        new_scores[i] += damping * similarity_matrix[i][j] * scores[j] / similarity_matrix[j].sum()
            scores = new_scores
    else:
        # TF-IDF scoring (sum of TF-IDF values)
        scores = np.array(sentence_vectors.sum(axis=1)).flatten()
    
    # Get top sentences
    top_indices = scores.argsort()[-num_sentences:][::-1]
    top_indices = sorted(top_indices)  # Maintain original order
    
    summary_sentences = [sentences[i] for i in top_indices]
    summary = ' '.join(summary_sentences)
    
    return {
        "summary": summary,
        "sentences": summary_sentences,
        "scores": scores[top_indices].tolist(),
        "compression_ratio": num_sentences / len(sentences)
    }


def handle(event, context):
    """
    OpenFaaS handler for text summarization
    
    Request body:
    {
        "text": "Long text to summarize...",
        "num_sentences": 3,  # optional
        "method": "tfidf"    # optional: 'tfidf' or 'textrank'
    }
    
    OR batch processing:
    {
        "texts": ["Text 1...", "Text 2..."],
        "num_sentences": 3,
        "method": "tfidf"
    }
    """
    try:
        # Parse input
        if isinstance(event, str):
            body = json.loads(event)
        elif isinstance(event, dict):
            body = event.get('body', event)
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = {}
        
        # Validate input
        if 'text' not in body and 'texts' not in body:
            return {
                "statusCode": 400,
                "body": {"error": "Missing 'text' or 'texts' field in request"}
            }
        
        num_sentences = body.get('num_sentences', 3)
        method = body.get('method', 'tfidf')
        
        # Validate parameters
        if num_sentences < 1:
            return {
                "statusCode": 400,
                "body": {"error": "num_sentences must be >= 1"}
            }
        
        if method not in ['tfidf', 'textrank']:
            return {
                "statusCode": 400,
                "body": {"error": "method must be 'tfidf' or 'textrank'"}
            }
        
        # Process single text
        if 'text' in body:
            text = body['text']
            
            if not isinstance(text, str) or not text.strip():
                return {
                    "statusCode": 400,
                    "body": {"error": "text must be a non-empty string"}
                }
            
            result = summarize_text(text, num_sentences, method)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "statistics": {
                        "original_sentences": len(sentence_tokenize(text)),
                        "summary_sentences": len(result["sentences"]),
                        "compression_ratio": result["compression_ratio"]
                    },
                    "model": f"TF-IDF-{method.upper()}"
                }
            }
        
        # Process batch
        texts = body['texts']
        
        if not isinstance(texts, list) or not texts:
            return {
                "statusCode": 400,
                "body": {"error": "texts must be a non-empty array"}
            }
        
        results = []
        for text in texts:
            if not isinstance(text, str) or not text.strip():
                results.append({"error": "Invalid text"})
            else:
                try:
                    result = summarize_text(text, num_sentences, method)
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})
        
        return {
            "statusCode": 200,
            "body": {
                "results": results,
                "statistics": {
                    "total_samples": len(texts),
                    "successful": sum(1 for r in results if "error" not in r)
                },
                "model": f"TF-IDF-{method.upper()}"
            }
        }
    
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": {"error": "Invalid JSON in request body"}
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": f"Internal error: {str(e)}"}
        }


# For local testing
if __name__ == "__main__":
    # Test case
    test_input = {
        "text": """
        Artificial intelligence is transforming the technology landscape. 
        Machine learning algorithms can now process vast amounts of data. 
        Deep learning has revolutionized computer vision and natural language processing. 
        Companies are investing heavily in AI research and development. 
        The future of AI looks promising with many exciting applications ahead.
        """,
        "num_sentences": 2,
        "method": "tfidf"
    }
    
    result = handle(test_input, None)
    print(json.dumps(result, indent=2))

