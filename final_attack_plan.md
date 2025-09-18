# `final_attack` 算法重构计划

## 1. 目标

重构 `final_attack` 的计算方式，将其从一个简单的公式转变为一个更复杂、更模块化的算法。新的算法将在一个独立的 `backend/final_attack.py` 文件中实现，以便于未来的维护和扩展。

## 2. 计划步骤

- **重构为两阶段算法**:
  - **阶段一：数据准备**。创建一个辅助函数（例如 `_prepare_attack_components`），负责从所有数据源（`char_data`、JSON 文件等）提取、计算并返回一个包含所有必需组件的结构化对象（如字典或 dataclass）。
  - **阶段二：最终计算**。创建一个纯函数（例如 `_execute_final_calculation`），它接收第一阶段准备好的数据对象，并执行最终的数学公式计算。
  - **主函数**: `calculate_final_attack` 将作为公共接口，依次调用上述两个函数。

- **分解算法**:

  - **步骤 1: 计算基础同步攻击力 (Base Breakthrough Attack)**
    - **输入**:
      - `sync_attack`: 从 `number.json` 中根据同步等级和角色职业查找到的基础同步攻击力。
      - `grade`: 角色的突破等级 (`limit_break_grade`)。
    - **公式**:
      ```
      base_breakthrough_attack = sync_attack * (1 + 0.02 * grade) + (20 * grade)
      ```
    - **伪代码**:
      ```python
      def calculate_base_breakthrough_attack(sync_attack: float, grade: int) -> float:
          return sync_attack * (1 + 0.02 * grade) + (20 * grade)
      ```

- **步骤 2: 计算好感度等级 (Favor Rank)**
    - **目的**: 这是一个独立的数据准备步骤，其结果可能会在后续的 `final_attack` 计算或其他地方使用。
    - **输入**:
      - `grade`: 角色的突破等级 (`limit_break_grade`)。
      - `corporation`: 角色所属的企业。
      - `character_id`: 角色的ID。
      - `super_character_ids`: 从 `super.json` 加载的特殊角色ID列表。
    - **公式**:
      1.  `rank = (grade + 1) * 10`
      2.  如果 `corporation == 'PILGRIM'` 或者 `character_id` 在 `super_character_ids` 列表中，则 `rank` 无上限。
      3.  否则，`rank = min(rank, 30)`。
    - **伪代码**:
      ```python
      def calculate_favor_rank(grade: int, corporation: str, character_id: int, super_character_ids: list) -> int:
          rank = (grade + 1) * 10
          
          is_pilgrim = (corporation == 'PILGRIM')
          is_super = (character_id in super_character_ids)
          
          if not is_pilgrim and not is_super:
              return min(rank, 30)
          
          return rank
      ```

- **步骤 3: 转换职业名称 (Translate Class Name)**
    - **目的**: 将从静态数据中获取的英文职业名称转换为 `rank.json` 中使用的中文键。
    - **逻辑**:
      - "Attacker" -> "火力型"
      - "Supporter" -> "辅助型"
      - "Defender" -> "防御型"
    - **伪代码**:
      ```python
      def translate_class_name(class_en: str) -> str:
          translation_map = {
              "Attacker": "火力型",
              "Supporter": "辅助型",
              "Defender": "防御型",
          }
          return translation_map.get(class_en, "")
      ```

- **步骤 4: 获取好感度攻击力加成 (Favor Attack Bonus)**
    - **目的**: 根据好感度等级和角色职业，查找对应的攻击力加成。
    - **输入**:
      - `rank`: 从步骤 2 计算出的好感度等级。
      - `character_class_en`: 角色的英文职业 (例如, "Attacker")。
      - `rank_data`: 从 `rank.json` 加载的数据。
    - **查找逻辑**:
      1.  调用 `translate_class_name` 将英文职业转换为中文。
      2.  将 `rank` 转换为字符串，作为 `rank_data` 的键。
      3.  在 `rank_data[str(rank)]` 中，使用转换后的中文职业名作为键。
      4.  获取 `attack` 字段的值。
    - **伪代码**:
      ```python
      def get_favor_attack_bonus(rank: int, character_class_en: str, rank_data: dict) -> float:
          class_cn = translate_class_name(character_class_en)
          if not class_cn:
              return 0
          
          try:
              bonus = rank_data[str(rank)][class_cn]['attack']
              return bonus
          except KeyError:
              # 如果找不到对应的 rank 或 class，返回 0
              return 0
      ```

- **步骤 5: 计算协同等级加成 (Coordination Level Bonus)**
    - **目的**: 引入一个新的、由用户输入的变量 `coor_level` 来提供额外的攻击力加成。
    - **输入**:
      - `coor_level`: 由用户在前端输入的协同等级。
    - **公式**:
      ```
      coor_bonus = coor_level * 25
      ```
    - **伪代码**:
      ```python
      def calculate_coor_bonus(coor_level: int) -> int:
          return coor_level * 25
      ```

- **步骤 6: 应用核心突破乘数 (Core Break Multiplier)**
    - **目的**: 将核心突破等级作为一个乘数应用到当前的攻击力总和上。
    - **输入**:
      - `current_attack_sum`: 前几个步骤计算出的攻击力总和。
      - `core`: 角色的核心突破等级。
    - **公式**:
      ```
      attack_with_core_bonus = current_attack_sum * (1 + 0.02 * core)
      ```
    - **伪代码**:
      ```python
      def apply_core_multiplier(current_attack_sum: float, core: int) -> float:
          return current_attack_sum * (1 + 0.02 * core)
      ```

- **步骤 7: 获取装备攻击力 (Equipment Attack)**
    - **目的**: 根据角色职业从 `equipment.json` 中查找固定的装备攻击力。
    - **输入**:
      - `character_class_en`: 角色的英文职业 (例如, "Attacker")。
      - `equipment_data`: 从 `equipment.json` 加载的数据。
    - **查找逻辑**:
      1.  将英文职业名（单数）映射到 `equipment.json` 使用的键（复数）。
      2.  从 `equipment_data` 中获取对应的值。
    - **伪代码**:
      ```python
      def get_equipment_attack(character_class_en: str, equipment_data: dict) -> int:
          key_map = {
              "Attacker": "attackers",
              "Defender": "defenders",
              "Supporter": "supports", # 注意这里 JSON 文件中是 supports
          }
          lookup_key = key_map.get(character_class_en)
          if not lookup_key:
              return 0
          
          # JSON 中的值是字符串，需要转换为整数
          return int(equipment_data.get(lookup_key, 0))
      ```

- **步骤 8: 获取收藏品攻击力 (Item Attack)**
    - **目的**: 计算收藏品（游戏内称为“物品”）提供的攻击力。
    - **逻辑**: 这部分逻辑已在 `services.py` 中实现，我们将把它迁移到新模块中。
    - **输入**:
      - `item_rare`: 物品稀有度 (例如, "SSR", "SR")。
      - `item_level`: 物品等级。
      - `number_data`: 从 `number.json` 加载的数据。
    - **伪代码**:
      ```python
      def get_item_attack(item_rare: str, item_level: int, number_data: dict) -> int:
          if item_rare == "SSR":
              return 9688
          elif item_rare == "SR":
              item_atk_list = number_data.get("item_atk", [])
              item_level_idx = item_level - 1
              if 0 <= item_level_idx < len(item_atk_list):
                  return item_atk_list[item_level_idx]
          return 0
      ```

- **最终 `final_attack` 公式**
  - **公式**: `((基础突破攻击力 + 好感度攻击力加成 + 协同等级加成) * (1 + 0.02 * core)) + 装备攻击力 + 收藏品攻击力`
  - **注意**: 这个公式目前**未包含**装备词条（如 `total_stat_atk`）、技能等级等其他因素。

## 3. 算法流程图

```mermaid
graph TD
    subgraph "输入数据"
        A[角色数据 char_data<br/>- limit_break.grade<br/>- limit_break.core<br/>- item_rare<br/>- item_level]
        B[同步等级 sync_level]
        C[协同等级 coor_level<br/>(从前端输入)]
        D[静态数据 NIKKE_STATIC_DATA<br/>- class]
        E[JSON数据文件<br/>- number.json<br/>- rank.json<br/>- equipment.json<br/>- super.json]
    end

    subgraph "计算步骤"
        S1[步骤1: 计算基础同步攻击力 sync_attack]
        S2[步骤1: 计算基础突破攻击力 base_breakthrough_attack]
        S3[步骤2: 计算好感度等级 favor_rank]
        S4[步骤3 & 4: 获取好感度攻击力加成 favor_attack_bonus]
        S5[步骤5: 计算协同等级加成 coor_bonus]
        S6[步骤6: 应用核心突破乘数]
        S7[步骤7: 获取装备攻击力 equipment_attack]
        S8[步骤8: 获取收藏品攻击力 item_attack]
        S_FINAL[组合最终公式]
    end

    B --> S1
    D --> S1
    E --> S1

    S1 --> S2
    A --> S2

    A --> S3
    E --> S3

    S3 --> S4
    D --> S4
    E --> S4

    C --> S5

    S2 --> S6
    S4 --> S6
    S5 --> S6
    A --> S6

    D --> S7
    E --> S7

    A --> S8
    E --> S8

    S6 --> S_FINAL
    S7 --> S_FINAL
    S8 --> S_FINAL

    subgraph "输出"
        FINAL_ATTACK[最终攻击力 final_attack]
    end

    S_FINAL --> FINAL_ATTACK

```

- **集成新算法**:
  - **前端修改**:
    - 需要在前端界面（可能是 `DamageSimulation.vue` 或相关组件）中添加一个输入框，允许用户输入 `coor_level`。
  - **API 修改**:
    - 需要修改相关的 Pydantic 请求模型（可能在 `schemas.py` 中），以接收前端传来的 `coor_level`。
  - **服务层修改**:
    - 修改 `backend/services.py` 中的 `calculate_character_attributes` 函数，使其能够接收并传递 `coor_level`。
  - **移除旧逻辑**:
    - 移除 `backend/services.py` 中旧的 `final_attack` 计算逻辑。
  - **集成新逻辑**:
    - 在 `backend/services.py` 中导入并调用 `backend/final_attack.py` 中的新函数来获取最终的攻击力。