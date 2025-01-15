from typing import List
from openai import OpenAI
from ..models.dealer import Dealer
from ..models.card import Card

API_BASE_URL = ""
API_KEY = ""

class DealerAgent(Dealer):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
        
    def should_hit(self) -> bool:
        """
        Use GPT to decide whether dealer should hit
        Returns: True if should hit, False if should stand
        """
        # 构建游戏状态描述
        prompt = f"""
        你是一位21点游戏的庄家。你需要根据当前状态决定是否要牌。

        庄家规则提示:
        1. 17点及以上必须停牌
        2. 16点及以下必须要牌
        3. A可以算1点或11点
        4. 爆牌(超过21点)直接输

        当前状态:
        - 你的手牌: {', '.join(str(card) for card in self.hand.cards)}
        - 手牌总点数: {self.hand.get_value()}

        请分析当前状态，并严格按照以下格式回复:
        1. 如果决定要牌，只回复字母'H'
        2. 如果决定停牌，只回复字母'S'
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """你是一个21点庄家。
你必须严格遵守庄家规则：17及以上停牌，16及以下要牌。
你的回复必须简洁，只能是'H'或'S'。"""},
                    {"role": "assistant", "content": "明白。我会严格按照庄家规则行事，并只回复'H'或'S'。"},
                    {"role": "user", "content": "手牌: KING of ♠, SEVEN of ♣"},
                    {"role": "assistant", "content": "S"},
                    {"role": "user", "content": "手牌: NINE of ♥, FIVE of ♣"},
                    {"role": "assistant", "content": "H"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1,
                temperature=0.1
            )
            
            # 获取决策
            decision = response.choices[0].message.content.strip().upper()
            
            # 返回决策
            if decision and decision[0] in ['H', 'S']:
                return decision[0] == 'H'
            
            # 如果GPT返回的不是有效决策，使用基本规则
            return self.hand.get_value() < 17
            
        except Exception as e:
            print(f"Error using GPT API for dealer: {e}")
            # 发生错误时使用基本规则
            return self.hand.get_value() < 17
