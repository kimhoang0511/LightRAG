"""
Example: Using Vietnamese-Optimized Prompts in LightRAG
Ví dụ sử dụng prompts tối ưu tiếng Việt trong LightRAG

This example demonstrates how to use Vietnamese-optimized prompts
for better results with Vietnamese data.
"""

import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete

# Uncomment and configure your LLM provider
# from lightrag.llm import openai_complete_if_cache, openai_embedding
# from lightrag.llm import ollama_model_complete, ollama_embedding


WORKING_DIR = "./vietnamese_rag_example"

# Create working directory if not exists
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def main():
    print("=" * 60)
    print("🇻🇳 Vietnamese-Optimized LightRAG Example")
    print("=" * 60)
    print()
    
    # Initialize LightRAG with Vietnamese language setting
    print("📚 Initializing LightRAG with Vietnamese configuration...")
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,  # Configure your LLM
        # embedding_func=openai_embedding,  # Configure your embedding
        
        # ⭐ Key: Set language to Vietnamese
        addon_params={
            "language": "Vietnamese",  # This will trigger Vietnamese prompts
            "entity_types": [
                "organization",  # Tổ chức
                "person",        # Cá nhân
                "location",      # Địa điểm
                "product",       # Sản phẩm
                "event",         # Sự kiện
                "concept"        # Khái niệm
            ]
        }
    )
    print("✅ LightRAG initialized with Vietnamese prompts\n")
    
    # Sample Vietnamese documents
    vietnamese_documents = [
        """
        Ngân hàng TMCP Ngoại thương Việt Nam (Vietcombank) là một trong những ngân hàng 
        thương mại lớn nhất tại Việt Nam. Được thành lập năm 1963, Vietcombank hiện có 
        hơn 150 chi nhánh trên toàn quốc. Ông Phạm Quang Dũng hiện đang giữ chức vụ 
        Chủ tịch Hội đồng Quản trị.
        
        Trong quý 3/2024, Vietcombank đạt lợi nhuận trước thuế 12.500 tỷ đồng, tăng 
        18% so với cùng kỳ năm trước. Ngân hàng đã triển khai thành công hệ thống 
        ngân hàng số VCB Digibank, phục vụ hơn 10 triệu khách hàng.
        """,
        
        """
        Thành phố Đà Nẵng đang tập trung phát triển du lịch bền vững. Sở Du lịch Đà Nẵng 
        đã phối hợp với UBND thành phố triển khai chương trình "Du lịch xanh Đà Nẵng 2024-2030".
        
        Chương trình này nhằm bảo vệ môi trường biển, phát triển du lịch sinh thái và 
        nâng cao chất lượng dịch vụ. Các doanh nghiệp du lịch địa phương như Vinpearl, 
        Sun Group đã cam kết đầu tư 5.000 tỷ đồng vào các dự án du lịch xanh.
        """,
        
        """
        Chính phủ Việt Nam đã ban hành Nghị định mới về thuế giá trị gia tăng (VAT) 
        có hiệu lực từ ngày 1/1/2024. Theo đó, thuế suất VAT cho doanh nghiệp vừa và 
        nhỏ (SME) được giảm từ 10% xuống còn 8%.
        
        Bộ Tài chính cho biết chính sách này sẽ hỗ trợ khoảng 700.000 doanh nghiệp SME 
        trên toàn quốc, giúp tiết kiệm chi phí và tăng khả năng cạnh tranh. Tổng số tiền 
        thuế giảm ước tính khoảng 45.000 tỷ đồng/năm.
        """
    ]
    
    # Insert Vietnamese documents
    print("📝 Inserting Vietnamese documents...")
    for i, doc in enumerate(vietnamese_documents, 1):
        print(f"   Inserting document {i}/3...")
        await rag.ainsert(doc)
    print("✅ All documents inserted\n")
    
    # Example queries in Vietnamese
    vietnamese_queries = [
        "Thông tin về Vietcombank và kết quả kinh doanh quý 3/2024?",
        "Chính sách thuế mới của Chính phủ ảnh hưởng như thế nào đến doanh nghiệp vừa và nhỏ?",
        "Đà Nẵng đang phát triển du lịch bền vững như thế nào?",
        "Ai là Chủ tịch Hội đồng Quản trị Vietcombank?",
    ]
    
    print("🔍 Running Vietnamese queries...")
    print("=" * 60)
    
    for i, query in enumerate(vietnamese_queries, 1):
        print(f"\n📌 Query {i}: {query}")
        print("-" * 60)
        
        # Query with different modes
        modes = ["hybrid", "local", "global"]
        
        for mode in modes[:1]:  # Just show hybrid for brevity
            print(f"\n🔹 Mode: {mode}")
            
            result = await rag.aquery(
                query,
                param=QueryParam(
                    mode=mode,
                    top_k=5,
                    response_type="Multiple Paragraphs"
                )
            )
            
            print(f"\n{result[:500]}...")  # Show first 500 chars
    
    print("\n" + "=" * 60)
    print("✅ Example completed!")
    print("=" * 60)
    
    # Show comparison with English
    print("\n📊 Comparison: Vietnamese vs English Prompts")
    print("-" * 60)
    
    print("\n✅ With Vietnamese Prompts:")
    print("   • Entity extraction understands Vietnamese names with diacritics")
    print("   • Proper recognition: 'Ngân hàng TMCP Ngoại thương Việt Nam'")
    print("   • Correct entity types: 'Vietcombank' -> organization")
    print("   • Keywords: 'lợi nhuận', 'quý 3/2024', 'tăng 18%'")
    print("   • References section: '### Tài liệu Tham khảo'")
    print("   • Natural Vietnamese answers with proper grammar")
    
    print("\n❌ With English Prompts (original):")
    print("   • May lose diacritics: 'Vietcombank' ok, but 'Pham Quang Dung' loses tones")
    print("   • Entity extraction less accurate for Vietnamese names")
    print("   • Keywords may be English translations: 'profit', 'Q3/2024'")
    print("   • References section: '### References' (mixed language)")
    print("   • Answers may have unnatural Vietnamese phrasing")
    
    print("\n" + "=" * 60)


async def demo_prompt_detection():
    """
    Demo automatic language detection from queries
    """
    print("\n" + "=" * 60)
    print("🔍 DEMO: Automatic Language Detection")
    print("=" * 60)
    
    from lightrag.prompt_utils import detect_language, get_prompt
    
    queries = [
        "What is Vietcombank?",
        "Vietcombank là gì?",
        "Tell me about Ho Chi Minh City",
        "Cho tôi biết về Thành phố Hồ Chí Minh",
    ]
    
    print("\nAutomatic detection of query language:")
    for query in queries:
        lang = detect_language(query)
        print(f"\n  Query: {query}")
        print(f"  Detected: {lang}")
        print(f"  Will use: {lang} prompts")
    
    print("\n" + "=" * 60)


async def demo_entity_extraction():
    """
    Demo entity extraction with Vietnamese data
    """
    print("\n" + "=" * 60)
    print("🏢 DEMO: Entity Extraction from Vietnamese Text")
    print("=" * 60)
    
    text = """
    Công ty Cổ phần FPT là tập đoàn công nghệ hàng đầu Việt Nam, 
    được thành lập bởi ông Trương Gia Bình năm 1988 tại Hà Nội. 
    FPT có các công ty thành viên như FPT Software, FPT Telecom, 
    và FPT Education.
    """
    
    print("\n📄 Input text:")
    print(text)
    
    print("\n🎯 Expected entities with Vietnamese prompts:")
    print("  • FPT - organization - Tập đoàn công nghệ hàng đầu Việt Nam")
    print("  • Trương Gia Bình - person - Người sáng lập FPT năm 1988")
    print("  • Hà Nội - location - Nơi thành lập công ty FPT")
    print("  • FPT Software - organization - Công ty thành viên của FPT")
    
    print("\n🔗 Expected relationships:")
    print("  • Trương Gia Bình -(sáng lập)-> FPT")
    print("  • FPT -(có trụ sở)-> Hà Nội")
    print("  • FPT Software -(thuộc)-> FPT")
    
    print("\n✅ Vietnamese prompts preserve:")
    print("  • Diacritics: Trương Gia Bình, Hà Nội")
    print("  • Company types: Công ty Cổ phần, TNHH")
    print("  • Vietnamese relationship terms: sáng lập, thuộc, có trụ sở")
    
    print("\n" + "=" * 60)


async def demo_number_formatting():
    """
    Demo Vietnamese number formatting in results
    """
    print("\n" + "=" * 60)
    print("🔢 DEMO: Vietnamese Number Formatting")
    print("=" * 60)
    
    from lightrag.prompt_utils import format_vietnamese_number
    
    examples = [
        (12500000000000, "lợi nhuận 12.500 tỷ đồng"),
        (5000000000000, "đầu tư 5.000 tỷ đồng"),
        (700000, "700.000 doanh nghiệp"),
        (18.5, "tăng trưởng 18,5%"),
    ]
    
    print("\nVietnamese number formatting examples:")
    for number, context in examples:
        formatted = format_vietnamese_number(number)
        print(f"\n  Raw: {number}")
        print(f"  Formatted: {formatted}")
        print(f"  Context: {context}")
    
    print("\n✅ Follows Vietnamese conventions:")
    print("  • Period (.) for thousands separator: 1.234.567")
    print("  • Comma (,) for decimal separator: 3,14")
    print("  • Natural Vietnamese units: tỷ đồng, triệu, nghìn")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Vietnamese-Optimized LightRAG Example                       ║
║  Ví dụ LightRAG với Prompts Tối ưu cho Tiếng Việt          ║
╚══════════════════════════════════════════════════════════════╝

This example demonstrates:
1. Setting up LightRAG with Vietnamese language
2. Inserting Vietnamese documents
3. Querying in Vietnamese with optimized prompts
4. Automatic language detection
5. Entity extraction from Vietnamese text
6. Vietnamese number formatting

Note: Configure your LLM and embedding functions before running.
""")
    
    # Run all demos
    asyncio.run(main())
    asyncio.run(demo_prompt_detection())
    asyncio.run(demo_entity_extraction())
    asyncio.run(demo_number_formatting())
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Next Steps / Các Bước Tiếp Theo                            ║
╚══════════════════════════════════════════════════════════════╝

1. 📚 Read the full documentation:
   docs/VietnamesePromptOptimization.md

2. 🧪 Run the test suite:
   python3 test_vietnamese_prompts.py

3. 🔧 Configure your LLM:
   - OpenAI: Set OPENAI_API_KEY
   - Ollama: Install and run local model
   - Azure: Configure Azure endpoints

4. 📊 Test with your Vietnamese data:
   - Replace sample documents with your data
   - Adjust entity_types for your domain
   - Experiment with different query modes

5. 🚀 Deploy to production:
   - Use lightrag-api with Vietnamese config
   - Set up proper caching
   - Monitor performance with Vietnamese queries

For questions or issues:
- Check AGENTS.md for contribution guidelines
- Open an issue on GitHub
- Review existing Vietnamese examples
""")
