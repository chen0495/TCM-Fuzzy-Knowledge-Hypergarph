# HyperGraphRAG - 中医病案知识图谱提取工具 

## 项目概述 (Overview)

HyperGraphRAG 是一个旨在从非结构化的中医病案文本中自动提取实体和超关系，构建结构化知识图谱的工具。本项目通过自然语言处理技术（特别是大语言模型LLM）分析病案内容，识别关键医学概念（如疾病、症状、证候、方剂、药物）及其相互关系（可能为多元超关系），并将这些信息以JSON格式输出，为后续的知识存储、检索增强生成（RAG）和临床辅助决策等应用提供数据基础。 

## 功能特性 (Features)

- **病案自动分割**: 从包含多个病案的原始文本文件中，根据病名和病例编号（如"例一"、"例二"）自动分割成独立的病例文本文件。
- **基于LLM的知识提取**: 利用大语言模型（当前集成SiliconFlow API）从病案文本中提取中医知识元素。
- **结构化信息抽取**:
    - **实体识别**: 自动识别预定义的实体类型，包括：
        - `患者信息` (PatientInfo)
        - `症状` (Symptom)
        - `证候` (Syndrome)
        - `疾病` (Disease)
        - `处方` (Prescription)
    - **超关系识别**: 自动识别预定义的超关系类型，连接上述实体：
        - `辨证` (Diagnosis - linking symptoms, syndromes, patient to disease)
        - `论治` (Treatment - linking syndromes, diseases to prescriptions)
        - `随证加减` (PrescriptionAdjustment - linking original prescriptions to modified ones based on evolving symptoms/syndromes)
- **灵活的提示工程**: 在 `src/knowledge_extraction/prompts.py` 中定义详细的提示，指导LLM进行特定格式和内容的抽取，易于根据需求调整。
- **输出验证与格式化**: 对LLM的输出进行基本结构验证，并以规范的JSON格式保存提取的知识。
- **批量处理能力**: 支持对指定目录下的大量病例文本文件进行自动化批量提取。
- **处理进度跟踪**: 通过日志文件记录已成功处理的文件，避免重复提取，支持增量处理。
- **可配置化**: LLM API密钥、模型、URL等参数通过环境变量配置，方便切换和管理。 

## 技术栈 (Tech Stack)

- **主要语言**: Python 3.x
- **LLM交互**: OpenAI Python Library (`openai`) - 用于与兼容OpenAI API规范的LLM服务（如本项目中的SiliconFlow）进行通信。
- **环境管理**: `python-dotenv` - 用于从 `.env` 文件加载环境变量，如API密钥等敏感配置。
- **核心依赖**: 见 `requirements.txt` 文件。 

## 项目结构 (Project Structure)

```
HyperGraphRAG/
├── .gitignore
├── README.md
├── requirements.txt
├── TASK.md
├── input_data/               # 存放原始输入数据 (例如，包含多个病案的 .txt 文件)
│   └── example_cases.txt
├── output_data/              # 存放处理后的数据
│   ├── [病名]/              # 以病名命名的子目录，由 case_splitter.py 生成
│   │   └── 例X.txt          # 单个病例文件
│   └── extraction_results/   # 存放知识提取结果
│       └── [病名]/          # 保持与病例文件相同的目录结构
│           └── 例X.json     # 提取出的知识图谱 (JSON格式)
├── scripts/
│   ├── batch_process_output.py # 批量处理病例文件并提取知识的脚本
│   └── processed_output_files.log # 记录已处理的文件，避免重复操作
└── src/
    ├── common/                 # 通用模块 (目前为空)
    ├── data_processing/        # 数据预处理模块
    │   └── case_splitter.py    # 将原始文本分割为单个病例文件的脚本
    └── knowledge_extraction/   # 知识提取核心模块
        ├── extractor.py        # KnowledgeExtractor 类，编排提取流程
        ├── llm_client.py       # SiliconFlowClient 类，与LLM API交互
        ├── output_parser.py    # 验证LLM输出并保存为JSON
        └── prompts.py          # 定义LLM的提示模板和实体关系类型
```

**关键文件/目录说明:**

-   `input_data/`: 用户应将原始的、可能包含多个中医病案的文本文件（`.txt`）放置在此目录中。
-   `src/data_processing/case_splitter.py`: 此脚本负责读取 `input_data/` 中的文件，自动识别病名和各个病例（"例一"、"例二"等），并将每个病例分割成独立的文件。分割后的文件会保存在 `output_data/[病名]/例X.txt` 结构中。
-   `scripts/batch_process_output.py`: 在病例分割完成后，运行此脚本。它会遍历 `output_data/` 目录中所有由 `case_splitter.py` 生成的单个病例文件（`.txt`），调用知识提取模块，并将提取出的实体和超关系以 JSON 格式保存在 `output_data/extraction_results/[病名]/例X.json` 中。
-   `src/knowledge_extraction/`: 此目录包含知识提取的核心逻辑。
    -   `prompts.py`: 定义了向大语言模型（LLM）请求知识提取时使用的提示。其中详细说明了需要识别的实体类型（如患者信息、症状、证候、疾病、处方）和超关系类型（如辨证、论治、随证加减），以及期望的输出JSON结构。
    -   `llm_client.py`: 封装了与LLM API（当前为SiliconFlow）的通信细节。它负责发送请求并接收LLM的响应。
    -   `extractor.py`: `KnowledgeExtractor` 类是提取流程的协调器。它使用 `prompts.py` 来构建请求，通过 `llm_client.py` 与LLM交互，并使用 `output_parser.py` 来验证和处理输出。
    -   `output_parser.py`: 负责验证LLM返回的JSON数据是否符合预期的基本结构，并将有效的数据保存到文件。
-   `requirements.txt`: 列出了项目运行所需的Python依赖库。
-   `output_data/extraction_results/`: 最终提取的结构化知识（JSON文件）将存储在此处，保留了原始病例的目录层级。
-   `scripts/processed_output_files.log`: 用于记录 `batch_process_output.py` 已成功处理的病例文件路径，以防止重复处理，支持增量更新。 

## 安装指南 (Installation)

1.  **克隆仓库**

    ```bash
    git clone https://your-repository-url/HyperGraphRAG.git
    cd HyperGraphRAG
    ```

2.  **创建并激活Python虚拟环境** (推荐)

    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **安装依赖**

    ```bash
    pip install -r requirements.txt
    ``` 

## 配置 (Configuration)

项目需要通过环境变量配置LLM API的相关参数。请在项目根目录下创建一个 `.env` 文件，并填入以下内容：

```env
SILICONFLOW_API_KEY="YOUR_SILICONFLOW_API_KEY"
SILICONFLOW_MODEL="deepseek-ai/DeepSeek-V3"  # 或者您希望使用的其他兼容模型
SILICONFLOW_API_URL="https://api.siliconflow.cn/v1"
```

**环境变量说明:**

-   `SILICONFLOW_API_KEY`: 您的SiliconFlow API密钥。请替换 `YOUR_SILICONFLOW_API_KEY` 为您的实际密钥。
-   `SILICONFLOW_MODEL`: 指定要使用的LLM模型。默认配置为 `deepseek-ai/DeepSeek-V3`，您可以根据SiliconFlow提供的模型列表进行更改。
-   `SILICONFLOW_API_URL`: SiliconFlow API的接入点URL。

这些环境变量由 `src/knowledge_extraction/llm_client.py` 中的 `SiliconFlowClient` 类加载和使用。 

## 快速开始/使用方法 (Quick Start/Usage)

以下步骤将指导您完成从原始数据到提取知识图谱的整个流程。

### 步骤 1: 准备输入数据

1.  在项目根目录下找到或创建 `input_data` 文件夹。
2.  将包含一个或多个中医病案的原始文本文件（`.txt` 格式）放入 `input_data` 文件夹中。
    *   **文件格式要求**: `case_splitter.py` 脚本期望在文本文件中通过特定模式识别病名和每个病例的起始（例如，病名行如 `(一)感冒`，病例起始行如 `例一`）。请参考 `src/data_processing/case_splitter.py` 中的正则表达式或准备与示例数据相似结构的文本。
    *   例如，您可以创建一个名为 `example_medical_cases.txt` 的文件，其内容结构如下：

        ```text
        (一)感冒

        例一 张三，男，35岁...
        ... (病例一详情) ...

        例二 李四，女，42岁...
        ... (病例二详情) ...

        (二)咳嗽

        例一 王五，男，50岁...
        ... (病例一详情) ...
        ```

    *   **数据来源说明**:
        *   当前项目中使用的数据主要来源于：[近现代名医验案类编](https://github.com/lab99x/tcmoc/blob/master/books/683-近现代名医验案类编.txt)
        *   计划未来增加的数据来源包括：[中医临证经验与方法](https://github.com/lab99x/tcmoc/blob/master/books/686-中医临证经验与方法.txt)

### 步骤 2: 分割病例 (Data Preprocessing)

运行病例分割脚本，将 `input_data` 中的原始文本文件处理成单个独立的病例文件。

```bash
python src/data_processing/case_splitter.py
```

-   **作用**: 此脚本会读取 `input_data/` 目录下的所有 `.txt` 文件。
    -   它会首先尝试从每个文件中提取病名（例如，"感冒"、"咳嗽"）。
    -   然后，它会根据"例一"、"例二"等标记将文件内容分割成独立的病例。
-   **输出**: 分割后的单个病例文件将保存在 `output_data/` 目录下，并根据提取到的病名创建子文件夹。例如，`input_data/example_medical_cases.txt` 中"感冒"下的"例一"会被保存到 `output_data/感冒/例一.txt`。
-   **注意**: 脚本在执行时会先清空 `output_data/` 目录（如果已存在），请确保备份重要数据。

### 步骤 3: 批量知识提取 (Batch Processing)

在病例分割完成并且 `.env` 文件配置正确后，运行批量知识提取脚本。

```bash
python scripts/batch_process_output.py
```

-   **作用**: 此脚本会自动扫描 `output_data/` 目录（不包括 `output_data/extraction_results/` 子目录）中所有由步骤2生成的单个病例 `.txt` 文件。
    -   对于每个病例文件，它将调用 `KnowledgeExtractor` 使用LLM进行实体和关系的提取。
-   **输出**: 提取的知识将以JSON格式保存到 `output_data/extraction_results/` 目录中。输出的JSON文件将保持与 `output_data/` 中病例文件相对应的子目录结构。例如，`output_data/感冒/例一.txt` 的提取结果将保存为 `output_data/extraction_results/感冒/例一.json`。
-   **进度跟踪**: 脚本会将已成功处理的文件的绝对路径记录在 `scripts/processed_output_files.log` 文件中。下次运行时，已记录在该日志中的文件将被跳过，从而实现增量处理并避免重复调用LLM API。

### 运行完整流程总结

1.  将原始病案 `.txt` 文件放入 `input_data/`。
2.  确保已按照 **配置 (Configuration)** 部分创建并正确填写了 `.env` 文件。
3.  执行病例分割：`python src/data_processing/case_splitter.py`
4.  执行批量知识提取：`python scripts/batch_process_output.py`
5.  提取的JSON结果位于 `output_data/extraction_results/`。 

## 输出说明 (Output Description)

知识提取的结果将以JSON文件的形式存储在 `output_data/extraction_results/` 目录下，并保持与分割后病例文件相同的相对路径和文件名（扩展名改为 `.json`）。

每个JSON文件包含一个根对象，该对象具有两个主要的键：`entities` 和 `hyper_relationships`。

```json
{
  "entities": [
    {
      "entity_name": "实体的唯一名称",
      "entity_type": "实体类型", // 例如：患者信息, 症状, 证候, 疾病, 处方
      "description": "关于此实体的文本描述或提取的元数据"
    }
    // ... 可能有更多实体
  ],
  "hyper_relationships": [
    {
      "relationship_type": "超关系类型", // 例如：辨证, 论治, 随证加减
      "confidence": 0.95, // LLM评估的超关系置信度 (0-1)
      "participants": [
        {
          "entity_name": "参与此超关系的实体名称1", // 必须与 entities 列表中的 entity_name 对应
          "role": "实体在此超关系中的角色", // 例如：患者, 主症, 证候, 疾病, 原处方, 加减药物等
          "membership_degree": 1.0 // LLM评估的实体在超关系中的重要性/隶属度 (0-1)
        },
        {
          "entity_name": "参与此超关系的实体名称2",
          "role": "角色2",
          "membership_degree": 0.8
        }
        // ... 可能有更多参与者, 一个超关系可以连接两个或多个实体。
      ],
      "description": "关于此超关系的文本描述（可选）"
    }
    // ... 可能有更多超关系
  ]
}
```

**字段说明:**

-   **entities**: 一个对象列表，每个对象代表从文本中识别出的一个医学实体。
    -   `entity_name`: 实体的唯一标识符（字符串）。对于没有明确名称的处方，会根据主要疾病和证候生成一个名称。
    -   `entity_type`: 预定义的实体类型之一（字符串），具体类型定义见 `src/knowledge_extraction/prompts.py` 中的 `TCM_ANALYSIS_PROMPT`。
    -   `description`: 对实体的描述（字符串）。对于处方实体，这里通常包含药物组成和剂量。
-   **hyper_relationships**: 一个对象列表，每个对象代表一组实体之间识别出的一种超关系。一个超关系可以连接两个或多个实体。
    -   `relationship_type`: 预定义的超关系类型之一（字符串），具体类型定义见 `src/knowledge_extraction/prompts.py` 中的 `TCM_ANALYSIS_PROMPT`。
    -   `confidence`: 模型对该超关系成立可能性的置信度评分（浮点数，0到1之间）。
    -   `participants`: 一个对象列表，列出参与此超关系的所有实体及其在该超关系中的角色。
        -   `entity_name`: 参与实体的名称，必须与 `entities` 列表中定义的某个 `entity_name` 相匹配。
        -   `role`: 该实体在此特定超关系中扮演的角色（字符串）。例如，在"辨证"超关系中，角色可能是"患者"、"症状"、"证候"或"疾病"。
        -   `membership_degree`: 模型评估的该实体在此超关系中的重要性或隶属程度（浮点数，0到1之间）。
    -   `description`: 对超关系的简要描述（字符串），可选。

详细的实体类型、超关系类型以及它们之间的预期连接方式和角色，请参考 `src/knowledge_extraction/prompts.py` 文件中的 `TCM_ANALYSIS_PROMPT` 和 `EXAMPLE_OUTPUT`。该文件是理解LLM如何被指导进行提取的关键。 

-   **TODO**: 当前 `output_data/extraction_results/` 中的JSON输出需要按照 [LightRAG](https://github.com/embedchain/lightrag) 项目中自定义知识图谱的指定格式进行重新组织。计划采用星型链接模式，即定义一个中央超边节点 (Hyperedge Node)，所有实体节点都连接到这个超边节点。这将方便结果直接导入 LightRAG 系统。

## 核心模块详解 (Core Modules Deep Dive)

-   **`src/data_processing/case_splitter.py`**: 
    -   **功能**: 此脚本负责预处理原始病案文本。它会读取 `input_data/` 目录中的 `.txt` 文件，通过正则表达式识别病名和各病例的边界（如"例一"、"例二"等）。
    -   **处理逻辑**: 首先提取文件中的病名，然后将每个病例的内容（包括病名）分割并保存为独立的文件。
    -   **输出**: 生成的单个病例文件存放于 `output_data/[病名]/例X.txt`。脚本在开始处理前会清空 `output_data` 目录。

-   **`src/knowledge_extraction/prompts.py`**: 
    -   **功能**: 此文件是指导大语言模型（LLM）进行知识提取的关键。它包含 `TCM_ANALYSIS_PROMPT`，一个详细的提示模板。
    -   **提示内容**: 模板中定义了需要LLM识别的实体类型（`患者信息`、`症状`、`证候`、`疾病`、`处方`），超关系类型（`辨证`、`论治`、`随证加减`），以及期望的JSON输出结构（包括实体、超关系、置信度、参与者角色和隶属度等）。
    -   **重要性**: 提示的质量和清晰度直接影响LLM提取结果的准确性和一致性。这里还包含了一个 `EXAMPLE_CASE` 和对应的 `EXAMPLE_OUTPUT`，用于给LLM提供上下文学习的样本。

-   **`src/knowledge_extraction/llm_client.py`**: 
    -   **功能**: 定义了 `SiliconFlowClient` 类，封装了与SiliconFlow LLM API（通过OpenAI SDK兼容层）的交互逻辑。
    -   **配置加载**: 从 `.env` 文件或环境变量中加载API密钥、模型名称和API URL。
    -   **API调用**: `get_completion` 方法负责向LLM发送格式化后的提示（由`KnowledgeExtractor`构建），并以流式方式接收响应，确保可以处理可能较长的JSON输出。它还期望LLM返回JSON对象。

-   **`src/knowledge_extraction/extractor.py`**: 
    -   **功能**: 定义了 `KnowledgeExtractor` 类，是整个知识提取流程的编排者。
    -   **工作流程**: 
        1.  初始化 `SiliconFlowClient`。
        2.  `extract_knowledge` 方法接收文本输入（单个病例）。
        3.  调用 `prompts.format_prompt` 将输入文本嵌入到预定义的提示模板中。
        4.  使用 `llm_client.get_completion` 获取LLM的提取结果（期望是JSON）。
        5.  返回提取到的数据（一个包含`entities`和`hyper_relationships`的字典）。

-   **`src/knowledge_extraction/output_parser.py`**: 
    -   **功能**: 提供工具函数来处理和验证LLM的输出。
    -   `validate_llm_output`: 检查LLM返回的字典是否包含必须的键（`entities` 和 `hyper_relationships`）以及它们是否为列表类型，确保输出的基本结构正确。
    -   `save_knowledge_json`: 将验证通过的知识字典以格式化的JSON形式保存到指定的文件路径，同时确保输出目录存在。

-   **`scripts/batch_process_output.py`**: 
    -   **功能**: 自动化批量处理多个病例文件的脚本。
    -   **处理流程**: 
        1.  加载 `scripts/processed_output_files.log` 中记录的已处理文件列表，避免重复工作。
        2.  初始化 `KnowledgeExtractor`。
        3.  递归扫描 `output_data/` 目录（不包括 `extraction_results`）中的所有 `.txt` 病例文件。
        4.  对每个未处理过的文件：
            a.  读取文件内容。
            b.  调用 `knowledge_extractor.extract_knowledge` 进行提取。
            c.  调用 `validate_llm_output` 验证结果。
            d.  如果有效，则调用 `save_knowledge_json` 将结果保存到 `output_data/extraction_results/` 下对应的路径。
            e.  将成功处理的文件路径追加到 `processed_output_files.log`。
    -   **日志与错误处理**: 脚本包含日志记录功能，用于跟踪处理进度和错误。 

## 许可证 (License)

本项目采用 [MIT 许可证](LICENSE)。 
