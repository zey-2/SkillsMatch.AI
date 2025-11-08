#!/usr/bin/env python3
"""
Performance Comparison: Current Vector Search vs ChromaDB
Test speed and efficiency of different vector search approaches
"""

import time
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def benchmark_current_system():
    """Benchmark current TF-IDF + scikit-learn system"""
    print("🔍 Benchmarking Current System (TF-IDF + scikit-learn)")
    print("-" * 60)
    
    try:
        from web.services.simple_vector_service import get_vector_service
        
        # Initialize service
        start_time = time.time()
        vector_service = get_vector_service()
        init_time = time.time() - start_time
        
        print(f"📊 System Stats:")
        print(f"   📄 Resumes: {len(vector_service.resume_data)}")
        print(f"   💼 Jobs: {len(vector_service.job_data)}")
        print(f"   ⚡ Initialization: {init_time:.3f}s")
        
        if len(vector_service.resume_data) > 0 and len(vector_service.job_data) > 0:
            # Test search performance
            sample_resume = vector_service.resume_data[0]
            test_text = sample_resume['text_content'][:1000]  # First 1000 chars
            
            # Warm-up run
            vector_service.search_similar_jobs(test_text, n_results=5)
            
            # Benchmark multiple searches
            search_times = []
            num_searches = 10
            
            for i in range(num_searches):
                start_search = time.time()
                results = vector_service.search_similar_jobs(test_text, n_results=5)
                search_time = time.time() - start_search
                search_times.append(search_time)
            
            avg_search_time = sum(search_times) / len(search_times)
            min_search_time = min(search_times)
            max_search_time = max(search_times)
            
            print(f"🔍 Search Performance ({num_searches} runs):")
            print(f"   ⚡ Average: {avg_search_time:.4f}s")
            print(f"   🚀 Fastest: {min_search_time:.4f}s")
            print(f"   🐌 Slowest: {max_search_time:.4f}s")
            print(f"   📊 Results per search: {len(results)}")
            
            # Test adding new documents
            test_job = {
                'id': 'benchmark_job',
                'title': 'Performance Test Job',
                'description': 'Testing vectorization speed for benchmark purposes',
                'company': 'Benchmark Corp',
                'location': 'Test City',
                'category': 'Testing',
                'skills': ['Performance', 'Testing', 'Benchmarking']
            }
            
            start_add = time.time()
            vector_service.add_job_to_vector_db('benchmark_job', test_job)
            add_time = time.time() - start_add
            
            print(f"➕ Add Document: {add_time:.4f}s")
            
            return {
                'system': 'Current (TF-IDF + scikit-learn)',
                'init_time': init_time,
                'avg_search_time': avg_search_time,
                'min_search_time': min_search_time,
                'max_search_time': max_search_time,
                'add_doc_time': add_time,
                'num_resumes': len(vector_service.resume_data),
                'num_jobs': len(vector_service.job_data)
            }
        else:
            return {
                'system': 'Current (TF-IDF + scikit-learn)',
                'init_time': init_time,
                'error': 'No data for benchmarking'
            }
            
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return {'system': 'Current (TF-IDF + scikit-learn)', 'error': str(e)}

def theoretical_chromadb_comparison():
    """Provide theoretical comparison with ChromaDB"""
    print("\n🧠 Theoretical ChromaDB Comparison")
    print("-" * 60)
    
    comparison = {
        'ChromaDB': {
            'embedding_model': 'all-MiniLM-L6-v2 (384 dimensions)',
            'storage': 'Optimized vector database',
            'similarity': 'Cosine similarity on embeddings',
            'strengths': [
                'Higher quality semantic understanding',
                'Better similarity precision',
                'Optimized for large-scale vector operations',
                'Built-in HNSW indexing for fast search'
            ],
            'weaknesses': [
                'Larger memory footprint',
                'Slower initialization (model loading)',
                'More dependencies',
                'Complex setup in some environments'
            ],
            'estimated_performance': {
                'init_time': '2-5 seconds (model loading)',
                'search_time': '0.01-0.05 seconds',
                'memory_usage': 'High (model + vectors)',
                'accuracy': 'Higher semantic accuracy'
            }
        },
        'Current System': {
            'embedding_model': 'TF-IDF (sparse vectors)',
            'storage': 'JSON + Pickle files',
            'similarity': 'Cosine similarity on TF-IDF',
            'strengths': [
                'Fast initialization',
                'Low memory usage',
                'Simple dependencies',
                'Good for keyword-based matching'
            ],
            'weaknesses': [
                'Less semantic understanding',
                'May miss context/meaning',
                'Limited to vocabulary overlap',
                'No state-of-the-art embeddings'
            ]
        }
    }
    
    print("📊 Feature Comparison:")
    print(f"{'Aspect':<20} {'Current System':<25} {'ChromaDB':<25}")
    print("-" * 70)
    print(f"{'Initialization':<20} {'Fast (~0.1s)':<25} {'Slower (~3s)':<25}")
    print(f"{'Search Speed':<20} {'Medium (~0.01s)':<25} {'Fast (~0.005s)':<25}")
    print(f"{'Memory Usage':<20} {'Low':<25} {'High':<25}")
    print(f"{'Semantic Quality':<20} {'Medium':<25} {'High':<25}")
    print(f"{'Setup Complexity':<20} {'Simple':<25} {'Complex':<25}")
    print(f"{'Dependencies':<20} {'Minimal':<25} {'Heavy':<25}")
    
    return comparison

def main():
    """Run performance comparison"""
    print("⚡ Vector Search Performance Comparison")
    print("=" * 70)
    
    # Benchmark current system
    current_results = benchmark_current_system()
    
    # Show theoretical ChromaDB comparison
    comparison = theoretical_chromadb_comparison()
    
    # Summary and recommendation
    print(f"\n🎯 Performance Summary:")
    print("=" * 50)
    
    if 'error' not in current_results:
        print(f"✅ Current System Performance:")
        print(f"   🚀 Initialization: {current_results['init_time']:.3f}s")
        print(f"   🔍 Average Search: {current_results['avg_search_time']:.4f}s")
        print(f"   ➕ Add Document: {current_results['add_doc_time']:.4f}s")
        print(f"   📊 Data: {current_results['num_resumes']} resumes, {current_results['num_jobs']} jobs")
        
        print(f"\n💡 Recommendation:")
        if current_results['avg_search_time'] < 0.1:
            print("✅ Current system is FAST enough for your use case!")
            print("   - Sub-100ms search times are excellent for web apps")
            print("   - Simple setup and maintenance")
            print("   - Good balance of speed vs complexity")
        else:
            print("⚠️ Current system might benefit from ChromaDB:")
            print("   - Search times > 100ms could impact user experience")
            print("   - ChromaDB would provide faster search at scale")
    
    print(f"\n🔮 When to Consider ChromaDB:")
    print("   📈 Scale: >10,000 documents")
    print("   🎯 Quality: Need better semantic understanding")
    print("   ⚡ Speed: Need <10ms search times")
    print("   🔄 Real-time: Frequent document updates")

if __name__ == "__main__":
    main()