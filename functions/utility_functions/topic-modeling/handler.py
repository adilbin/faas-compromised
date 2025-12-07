#!/usr/bin/env python3
"""
Topic Modeling using LDA (Latent Dirichlet Allocation)
Discover topics in document collections
"""

import json
import logging
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
models = {}


def extract_topics(documents, n_topics=5, model_id='default', 
                   method='lda', n_top_words=10, max_features=1000):
    """
    Extract topics from documents
    
    Args:
        documents: List of text documents
        n_topics: Number of topics to extract
        model_id: ID for model storage
        method: 'lda' or 'nmf'
        n_top_words: Number of top words per topic
        max_features: Maximum vocabulary size
    
    Returns:
        dict: Topics and their top words
    """
    # Create vectorizer
    if method == 'lda':
        vectorizer = CountVectorizer(max_features=max_features, 
                                      stop_words='english',
                                      min_df=2)
    else:
        vectorizer = TfidfVectorizer(max_features=max_features,
                                      stop_words='english',
                                      min_df=2)
    
    # Transform documents
    doc_term_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    
    # Create and fit model
    if method == 'lda':
        model = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=20,
            learning_method='online'
        )
    else:  # NMF
        model = NMF(
            n_components=n_topics,
            random_state=42,
            max_iter=200
        )
    
    # Fit model
    doc_topic_dist = model.fit_transform(doc_term_matrix)
    
    # Store model
    models[model_id] = {
        'model': model,
        'vectorizer': vectorizer,
        'feature_names': feature_names,
        'method': method
    }
    
    # Extract top words for each topic
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        top_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        top_weights = [float(topic[i]) for i in top_indices]
        
        topics.append({
            'topic_id': topic_idx,
            'top_words': top_words,
            'weights': top_weights
        })
    
    # Document-topic distribution
    doc_topics = []
    for doc_idx, doc in enumerate(documents):
        topic_dist = doc_topic_dist[doc_idx]
        dominant_topic = int(np.argmax(topic_dist))
        
        doc_topics.append({
            'document_index': doc_idx,
            'document_preview': doc[:100] + '...' if len(doc) > 100 else doc,
            'dominant_topic': dominant_topic,
            'topic_distribution': topic_dist.tolist()
        })
    
    return {
        'model_id': model_id,
        'method': method,
        'n_topics': n_topics,
        'n_documents': len(documents),
        'topics': topics,
        'document_topics': doc_topics
    }


def predict_topics(documents, model_id='default', n_top_words=10):
    """
    Predict topics for new documents
    
    Args:
        documents: List of text documents
        model_id: ID of trained model
        n_top_words: Number of top words to return
    
    Returns:
        dict: Topic predictions
    """
    if model_id not in models:
        raise ValueError(f"Model '{model_id}' not found. Train model first.")
    
    model_info = models[model_id]
    model = model_info['model']
    vectorizer = model_info['vectorizer']
    feature_names = model_info['feature_names']
    
    # Transform documents
    doc_term_matrix = vectorizer.transform(documents)
    doc_topic_dist = model.transform(doc_term_matrix)
    
    results = []
    for doc_idx, doc in enumerate(documents):
        topic_dist = doc_topic_dist[doc_idx]
        dominant_topic = int(np.argmax(topic_dist))
        
        # Get top words for dominant topic
        topic_components = model.components_[dominant_topic]
        top_indices = topic_components.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        
        results.append({
            'document_index': doc_idx,
            'document_preview': doc[:100] + '...' if len(doc) > 100 else doc,
            'dominant_topic': dominant_topic,
            'confidence': float(np.max(topic_dist)),
            'topic_distribution': topic_dist.tolist(),
            'topic_keywords': top_words
        })
    
    return results


def handle(event, context):
    """
    OpenFaaS handler for Topic Modeling
    
    Request body for training:
    {
        "operation": "train",
        "documents": ["doc1 text...", "doc2 text...", ...],
        "n_topics": 5,  # optional
        "model_id": "my_model",  # optional
        "method": "lda",  # optional: 'lda' or 'nmf'
        "n_top_words": 10,  # optional
        "max_features": 1000  # optional
    }
    
    Request body for prediction:
    {
        "operation": "predict",
        "documents": ["new doc text...", ...],
        "model_id": "my_model"  # optional
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received Topic Modeling request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        operation = payload.get('operation', 'train')
        model_id = payload.get('model_id', 'default')
        
        if operation == 'train':
            # Training mode
            documents = payload.get('documents', [])
            n_topics = payload.get('n_topics', 5)
            method = payload.get('method', 'lda')
            n_top_words = payload.get('n_top_words', 10)
            max_features = payload.get('max_features', 1000)
            
            if not documents:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'documents' for training"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            if len(documents) < n_topics:
                return {
                    "statusCode": 400,
                    "body": {"error": f"Need at least {n_topics} documents for {n_topics} topics"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Extracting {n_topics} topics from {len(documents)} documents...")
            result = extract_topics(documents, n_topics, model_id, method, 
                                   n_top_words, max_features)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "model": method.upper(),
                    "message": "Topic modeling complete"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'predict':
            # Prediction mode
            documents = payload.get('documents', [])
            n_top_words = payload.get('n_top_words', 10)
            
            if not documents:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'documents' for prediction"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Predicting topics for {len(documents)} documents...")
            results = predict_topics(documents, model_id, n_top_words)
            
            return {
                "statusCode": 200,
                "body": {
                    "results": results,
                    "statistics": {
                        "total_documents": len(results)
                    },
                    "model": "Topic Model",
                    "model_id": model_id
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        else:
            return {
                "statusCode": 400,
                "body": {"error": f"Unknown operation: {operation}"},
                "headers": {"Content-Type": "application/json"}
            }
    
    except Exception as e:
        logger.error(f"Error in Topic Modeling: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
