# Vietnamese Prompt Optimization for LightRAG

## Tổng quan / Overview

Module này cung cấp các prompt được tối ưu hóa đặc biệt cho tiếng Việt, giúp cải thiện chất lượng trích xuất thông tin, tạo câu trả lời và xử lý tri thức khi làm việc với dữ liệu tiếng Việt.

This module provides Vietnamese-optimized prompts that improve information extraction, answer generation, and knowledge processing when working with Vietnamese data.

## Tính năng chính / Key Features

### 1. **Prompt được tối ưu cho tiếng Việt**
- Hướng dẫn rõ ràng bằng tiếng Việt
- Xử lý đúng dấu thanh và chữ viết tiếng Việt
- Nhận diện từ ghép và cấu trúc ngữ pháp tiếng Việt
- Định dạng số và đơn vị theo chuẩn Việt Nam

### 2. **Tự động phát hiện ngôn ngữ**
- Phát hiện tự động văn bản tiếng Việt
- Chọn prompt phù hợp dựa trên ngôn ngữ
- Hỗ trợ cấu hình ngôn ngữ tường minh

### 3. **Ví dụ và hướng dẫn tiếng Việt**
- Ví dụ trích xuất entity với dữ liệu Việt Nam
- Từ khóa và ngữ cảnh địa phương
- Xử lý tên riêng, địa danh, tổ chức Việt

## Cài đặt / Installation

Các file đã được tạo:
```
lightrag/
├── prompt_vietnamese.py      # Vietnamese-optimized prompts
├── prompt_utils.py           # Utilities for prompt management
└── prompt.py                 # Original prompts (unchanged)
```

## Cách sử dụng / Usage

### 1. Sử dụng tự động (Recommended)

Prompts sẽ tự động được chọn dựa trên cấu hình ngôn ngữ:

```python
from lightrag import LightRAG

# Khởi tạo với ngôn ngữ tiếng Việt
rag = LightRAG(
    working_dir="./rag_storage",
    addon_params={
        "language": "Vietnamese"  # Hoặc "Việt Nam", "Tiếng Việt", "vi", "vn"
    }
)

# Insert Vietnamese documents
with open("document_tieng_viet.txt", "r", encoding="utf-8") as f:
    rag.insert(f.read())

# Query in Vietnamese - sẽ tự động dùng Vietnamese prompts
result = rag.query("Thông tin về kinh tế Việt Nam năm 2024?")
print(result)
```

### 2. Sử dụng thủ công với prompt_utils

```python
from lightrag.prompt_utils import get_prompt, detect_language

# Tự động phát hiện ngôn ngữ
query = "Báo cáo tài chính của Vietcombank?"
language = detect_language(query)
print(f"Detected language: {language}")  # Output: Vietnamese

# Lấy prompt phù hợp
rag_prompt = get_prompt(
    prompt_key='rag_response',
    language=language,
    response_type="Multiple Paragraphs",
    user_prompt="Hãy trả lời chi tiết",
    context_data="..."
)

# Hoặc tự động phát hiện từ text
keywords_prompt = get_prompt(
    prompt_key='keywords_extraction',
    auto_detect_text=query
)
```

### 3. Tích hợp vào operate.py (For developers)

Để tích hợp vào code hiện tại, thêm vào các hàm trong `operate.py`:

```python
from lightrag.prompt_utils import get_prompt, get_language_from_config

# Trong hàm kg_query()
async def kg_query(query, param, global_config, ...):
    # Xác định ngôn ngữ
    language = get_language_from_config(global_config, query)
    
    # Lấy prompt phù hợp
    sys_prompt_temp = system_prompt if system_prompt else get_prompt(
        'rag_response',
        language=language
    )
    
    # Format prompt
    sys_prompt = sys_prompt_temp.format(
        response_type=response_type,
        user_prompt=user_prompt,
        context_data=context_result.context,
    )
    # ... rest of code

# Trong hàm extract_keywords_only()
async def extract_keywords_only(text, param, global_config, ...):
    language = get_language_from_config(global_config, text)
    
    # Lấy examples phù hợp
    examples_list = get_prompt('keywords_extraction_examples', language=language)
    examples = "\n".join(examples_list)
    
    # Lấy prompt template
    kw_prompt_template = get_prompt('keywords_extraction', language=language)
    kw_prompt = kw_prompt_template.format(
        query=text,
        examples=examples,
        language=language,
    )
    # ... rest of code
```

## Cải tiến so với prompt gốc / Improvements over Original Prompts

### 1. **Hướng dẫn bằng tiếng Việt**
- ✅ Rõ ràng hơn cho LLM khi xử lý tiếng Việt
- ✅ Giảm nhầm lẫn khi dịch từ tiếng Anh
- ✅ Phù hợp với ngữ cảnh văn hóa Việt Nam

### 2. **Xử lý đặc điểm tiếng Việt**
```python
# Giữ nguyên dấu thanh
"Hà Nội" not "Ha Noi"
"Nguyễn Văn A" not "Nguyen Van A"

# Nhận diện từ ghép
"công nghệ thông tin" (một khái niệm)
"trí tuệ nhân tạo" (một khái niệm)

# Xử lý số và đơn vị
"100 triệu đồng" not "100000000 VND"
"năm 2024" not "2024 year"
```

### 3. **Ví dụ địa phương**
```python
# Entity extraction examples
- Vietcombank, Công ty ABC
- Hà Nội, TP.HCM, Đà Nẵng
- UBND, Sở Du lịch

# Keywords examples
- "kinh tế Việt Nam"
- "thị trường bất động sản TP.HCM"
- "chính sách thuế mới"
```

### 4. **Định dạng phù hợp**
```python
# Vietnamese reference format
"### Tài liệu Tham khảo" instead of "### References"

# Vietnamese number format
"1.234.567,89" instead of "1,234,567.89"
```

## Ví dụ so sánh / Comparison Examples

### Query in Vietnamese

**With Original English Prompts:**
```
Query: "Thông tin về Vietcombank?"
Result: May extract "vietcombank" (lowercase), miss Vietnamese context
References: "### References" (English heading)
```

**With Vietnamese-Optimized Prompts:**
```
Query: "Thông tin về Vietcombank?"
Result: Extracts "Vietcombank" (proper case), understands Vietnamese banking context
References: "### Tài liệu Tham khảo" (Vietnamese heading)
Better entity recognition: "Ngân hàng TMCP Ngoại thương Việt Nam (Vietcombank)"
```

### Entity Extraction

**Original Prompt Result:**
```
entity|Nguyen Van A|person|A person mentioned in text
relation|Company A|Nguyen Van A|manages|Person works for company
```

**Vietnamese Prompt Result:**
```
entity<|#|>Nguyễn Văn A<|#|>person<|#|>Nguyễn Văn A là Giám đốc Chi nhánh Hà Nội của Vietcombank
relation<|#|>Nguyễn Văn A<|#|>Chi Nhánh Hà Nội<|#|>quản lý, lãnh đạo<|#|>Nguyễn Văn A là Giám đốc của Chi nhánh Hà Nội
```

## Test và Validation / Testing

### Test tự động phát hiện ngôn ngữ

```python
from lightrag.prompt_utils import is_vietnamese_text, contains_vietnamese_keywords

# Test character detection
assert is_vietnamese_text("Xin chào Việt Nam") == True
assert is_vietnamese_text("Hello World") == False

# Test keyword detection
assert contains_vietnamese_keywords("Đây là gì?") == True
assert contains_vietnamese_keywords("What is this?") == False

# Test mixed text
mixed = "Hello, xin chào"
print(is_vietnamese_text(mixed))  # True (có dấu tiếng Việt)
```

### Test prompt selection

```python
from lightrag.prompt_utils import get_prompt

# Test Vietnamese prompt
vi_prompt = get_prompt('rag_response', language='Vietnamese')
assert 'Vai trò' in vi_prompt
assert 'Tài liệu Tham khảo' in vi_prompt

# Test English prompt (fallback)
en_prompt = get_prompt('rag_response', language='English')
assert 'Role' in en_prompt
assert 'References' in en_prompt
```

## Tích hợp vào API / API Integration

Nếu bạn sử dụng lightrag-api:

```python
# lightrag_server.py hoặc routers
from lightrag.prompt_utils import get_language_from_config

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    # Detect language from query
    language = get_language_from_config(
        rag.global_config, 
        request.query
    )
    
    # Update config if needed
    if language == 'Vietnamese':
        rag.addon_params['language'] = 'Vietnamese'
    
    result = await rag.aquery(request.query, param=request.param)
    return result
```

## Performance Tips

### 1. **Cache language detection**
```python
# Cache detected language per session
session_language_cache = {}

def get_cached_language(query: str, session_id: str):
    if session_id not in session_language_cache:
        session_language_cache[session_id] = detect_language(query)
    return session_language_cache[session_id]
```

### 2. **Pre-configure for known datasets**
```python
# If you know your data is Vietnamese, set it explicitly
rag = LightRAG(
    working_dir="./vietnamese_data",
    addon_params={
        "language": "Vietnamese",
        "entity_types": ["organization", "person", "location", "product"]
    }
)
```

### 3. **Mix languages if needed**
```python
# For bilingual datasets
from lightrag.prompt_utils import merge_prompts_with_custom

custom_prompts = {
    'rag_response': """Custom bilingual prompt...
    (English instructions / Hướng dẫn tiếng Việt)
    """
}

prompts = merge_prompts_with_custom(custom_prompts, language='Vietnamese')
```

## Roadmap / Kế hoạch phát triển

- [x] Vietnamese-optimized prompts
- [x] Auto language detection
- [x] Utility functions
- [ ] Integrate into main codebase (operate.py, lightrag.py)
- [ ] Add unit tests
- [ ] Support for other Vietnamese variants (formal/informal)
- [ ] Add more Vietnamese examples
- [ ] Optimize for Vietnamese LLMs (VietAI, PhoGPT, etc.)

## Contributing

Để đóng góp cải thiện prompts tiếng Việt:

1. Test với các domain khác nhau (y tế, luật, tài chính, v.v.)
2. Thêm ví dụ mới vào `prompt_vietnamese.py`
3. Báo cáo issues với các trường hợp edge case
4. Đề xuất cải tiến cho entity types tiếng Việt

## License

Tuân theo license của dự án LightRAG chính.

---

**Tác giả / Author:** LightRAG Team  
**Ngày tạo / Created:** 2025-01-26  
**Phiên bản / Version:** 1.0.0
