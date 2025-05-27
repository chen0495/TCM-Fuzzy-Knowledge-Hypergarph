TCM_ANALYSIS_PROMPT = """
请分析以下中医病案文本，提取所有实体和超关系信息。请严格按照以下步骤和格式输出：

1. 实体识别：
   - 识别所有实体，实体类型为{{患者信息、症状、证候、疾病、处方}}
   - 为识别到的每个实体提供简单描述
   - 处方处理：
     - 识别所有处方。
     - 如果文本明确提供了处方名称（如"XXX方"），则使用该名称作为处方实体的 `entity_name`。
     - 如果仅列出药物组成而无名称，请根据提取到的主要`疾病`和`证候`，生成一个格式为 '[主要疾病名]_[主要证候名]_治疗方' 的 `entity_name`。
     - 将处方的完整药物组成（药物及剂量）和治法（如果提及）放入对应处方实体的 `description` 字段中。
     - **不要将单个处方成分识别为独立实体。**

2. 关系识别：
   - 识别三种超关系类型：辨证、论治、随证加减
   - 为每个关系提供隶属度和置信度
   - 隶属度表示实体在关系中的重要性（0-1）
   - 置信度表示关系成立的确定性（0-1）

请严格按照以下JSON格式输出：

{{
    "entities": [
        {{
            "entity_name": "实体名称",
            "entity_type": "实体类型",
            "description": "实体描述"
        }}
    ],
    "relationships": [
        {{
            "relationship_type": "关系类型（辨证/论治/随证加减）",
            "confidence": 关系置信度,
            "participants": [
                {{
                    "entity_name": "参与实体名称",
                    "role": "角色（如：患者/症状/证候等）",
                    "membership_degree": 隶属度
                }}
            ],
            "description": "关系描述"
        }}
    ]
}}

示例病案：
{example_case}

请分析以下病案文本：
{input_text}

注意：
1. 所有实体必须具有唯一名称
2. 关系中的实体名称必须与实体列表中的名称对应
3. 隶属度和置信度必须在0-1之间
4. 描述应当简洁明确
5. 请确保输出为合法的JSON格式
"""

EXAMPLE_CASE = """
病名: 口疮

例三龚、男，38岁，初诊日期：1954年4月28日。患者口腔溃疡数年，反复发作，久治不愈。局部剧痛，伴有口干。下唇内有一卵圆形豆大溃疡，舌尖红，苔薄白，脉沉细。辨证：脾肾阴虚，虚火上炎。治法：滋肾养阴，清热降火。方药：生菟丝子18克黄精12克天门冬15克黄柏（盐炒）12克知母12克金银花9克天花粉9克甘草6克淡竹叶9克5月1日

（二诊）：服上方3剂，溃疡较前缩小，疼痛减轻，仍口干。舌苔脉象同前。前方加玄参12克，麦门冬15克，生石膏24克。5月14日

（三诊）：服药六剂，溃疡愈合。后曾复发，但症状较轻，服上药仍有良效。（《刘惠民医案》）

例三反复发作已数年，久治不愈，证属脾肾阴虚，虚火上炎，治以滋肾养阴，清热降火，并重用滋阴补肾之品，使虚火下降而阳归于阴，即所谓"壮水之主，以制阳光"。
"""

EXAMPLE_OUTPUT = {
    "entities": [
        {
            "entity_name": "口疮",
            "entity_type": "疾病",
            "description": "口舌糜烂生疮"
        },
        {
            "entity_name": "龚",
            "entity_type": "患者信息",
            "description": "38岁男性患者，初诊日期1954年4月28日，患口腔溃疡数年，反复发作，久治不愈。"
        },
        {
            "entity_name": "口腔溃疡",
            "entity_type": "症状",
            "description": "患者主诉，病史数年，反复发作，久治不愈。"
        },
        {
            "entity_name": "局部剧痛",
            "entity_type": "症状",
            "description": "口腔溃疡处伴有剧烈疼痛。"
        },
        {
            "entity_name": "口干",
            "entity_type": "症状",
            "description": "患者自觉口干，初诊及二诊均提及。"
        },
        {
            "entity_name": "下唇内卵圆形豆大溃疡",
            "entity_type": "体征",
            "description": "体格检查发现：下唇内侧有一卵圆形、黄豆大小的溃疡。"
        },
        {
            "entity_name": "舌尖红",
            "entity_type": "舌象",
            "description": "舌诊表现：舌尖颜色偏红。"
        },
        {
            "entity_name": "苔薄白",
            "entity_type": "舌象",
            "description": "舌诊表现：舌苔薄，颜色白。"
        },
        {
            "entity_name": "脉沉细",
            "entity_type": "脉象",
            "description": "脉诊表现：脉象沉而且细。"
        },
        {
            "entity_name": "脾肾阴虚",
            "entity_type": "证候",
            "description": "根据症状、体征、舌脉综合分析得出的中医证候诊断之一。"
        },
        {
            "entity_name": "虚火上炎",
            "entity_type": "证候",
            "description": "根据症状、体征、舌脉综合分析得出的中医证候诊断之二，常与阴虚并见。"
        },
        {
            "entity_name": "口疮_脾肾阴虚，虚火上炎_治疗方",
            "entity_type": "处方",
            "description": "生菟丝子18克、黄精12克、天门冬15克、黄柏（盐炒）12克、知母12克、金银花9克、天花粉9克、甘草6克、淡竹叶9克。"
        },
        {
            "entity_name": "口疮_脾肾阴虚，虚火上炎_治疗方_加减",
            "entity_type": "处方",
            "description": "二诊方，前方加玄参12克，麦门冬15克，生石膏24克"
        }
    ],
    "relationships": [
        {
            "relationship_type": "辨证",
            "confidence": 0.95,
            "participants": [
                {
                    "entity_name": "龚",
                    "role": "患者",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "口腔溃疡",
                    "role": "主症",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "局部剧痛",
                    "role": "伴随症状",
                    "membership_degree": 0.9
                },
                {
                    "entity_name": "口干",
                    "role": "伴随症状",
                    "membership_degree": 0.8
                },
                {
                    "entity_name": "下唇内卵圆形豆大溃疡",
                    "role": "体征",
                    "membership_degree": 0.9
                },
                {
                    "entity_name": "舌尖红",
                    "role": "舌象",
                    "membership_degree": 0.8
                },
                {
                    "entity_name": "苔薄白",
                    "role": "舌象",
                    "membership_degree": 0.7
                },
                {
                    "entity_name": "脉沉细",
                    "role": "脉象",
                    "membership_degree": 0.8
                },
                {
                    "entity_name": "脾肾阴虚",
                    "role": "证候",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "虚火上炎",
                    "role": "证候",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "口疮",
                    "role": "疾病",
                    "membership_degree": 1.0
                }
            ]
        },
        {
            "relationship_type": "论治",
            "confidence": 0.9,
            "participants": [
                {
                    "entity_name": "脾肾阴虚",
                    "role": "证候",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "虚火上炎",
                    "role": "证候",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "口疮",
                    "role": "疾病",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "口疮_脾肾阴虚，虚火上炎_治疗方",
                    "role": "处方",
                    "membership_degree": 1.0
                }
            ],
            "description": "针对脾肾阴虚、虚火上炎的证候，采用滋肾养阴、清热降火的治法，选用口疮_脾肾阴虚，虚火上炎_治疗方进行治疗。"
        },
        {
            "relationship_type": "随证加减",
            "confidence": 0.9,
            "participants": [
                {
                    "entity_name": "口疮_脾肾阴虚，虚火上炎_治疗方",
                    "role": "原处方",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "口干",
                    "role": "持续症状",
                    "membership_degree": 0.8
                },
                {
                    "entity_name": "脾肾阴虚",
                    "role": "原证候",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "虚火上炎",
                    "role": "原证候",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "口疮",
                    "role": "原疾病",
                    "membership_degree": 1.0
                },
                {
                    "entity_name": "口疮_脾肾阴虚，虚火上炎_治疗方_加减",
                    "role": "调整后处方",
                    "membership_degree": 1.0
                }
            ],
            "description": "二诊时，患者服用初诊方后溃疡缩小、疼痛减轻，但仍感口干，故在原方基础上加玄参、麦门冬、生石膏以加强滋阴清热生津之力。"
        }
    ]
}

def format_prompt(input_text: str) -> str:
    """
    格式化提示模板，将输入文本插入到模板中
    
    Args:
        input_text: 需要分析的中医病案文本
        
    Returns:
        格式化后的完整提示文本
    """
    return TCM_ANALYSIS_PROMPT.format(
        example_case=EXAMPLE_CASE,
        input_text=input_text
    )

def get_entity_types() -> list:
    """
    返回所有支持的实体类型
    
    Returns:
        实体类型列表
    """
    return [
        "患者信息",
        "症状",
        "证候",
        "疾病",
        "处方"
    ]

def get_relationship_types() -> list:
    """
    返回所有支持的关系类型
    
    Returns:
        关系类型列表
    """
    return [
        "辨证",
        "论治",
        "随证加减"
    ]

def get_entity_roles() -> dict:
    """
    返回实体在不同关系中的可能角色
    
    Returns:
        角色字典，key为关系类型，value为该关系下的可能角色列表
    """
    return {
        "辨证": ["患者", "主症", "次症", "证候", "疾病"],
        "论治": ["证候", "疾病", "治法", "处方"],
        "随证加减": ["旧证候", "新症状", "新治法", "新处方"]
    } 