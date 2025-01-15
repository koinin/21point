from typing import Optional
from openai import OpenAI
from .player_agent import PlayerAgent
from ..models.card import Card

API_BASE_URL = ""
API_KEY = ""

class GPTPlayerAgent(PlayerAgent):
    def __init__(self, name: str = "GPT Player", style: str = "normal"):
        super().__init__(name)
        self.client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
        self.style = style  # "conservative" or "aggressive"
        
    def decide_bet(self) -> int:
        """
        Decide how much to bet based on available chips and style
        Returns: bet amount
        """
        prompt = f"""
        你是一位{'保守' if self.style == 'conservative' else '激进'}的21点玩家，需要决定这一局下注多少筹码。
        
        当前状态:
        - 你的筹码: {self.chips}
        - 最小下注: 10
        - 最大下注: {self.chips}
        
        {'保守策略提示:' if self.style == 'conservative' else '激进策略提示:'}
        {'1. 优先保护本金\n2. 建议每次下注不超过总筹码的10%\n3. 如果筹码较少，应该更保守' 
          if self.style == 'conservative' else 
         '1. 追求高回报\n2. 建议每次下注20%-30%的筹码\n3. 如果筹码充足，可以更激进'}
        
        请只回复一个数字，表示你要下注的筹码数量。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"你是一个{'保守' if self.style == 'conservative' else '激进'}的21点玩家，精通筹码管理和风险控制。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.3
            )
            
            # 获取决策
            bet_str = response.choices[0].message.content.strip()
            try:
                bet = int(bet_str)
                # 确保下注在合理范围内
                bet = max(10, min(bet, self.chips))
                return bet
            except ValueError:
                # 如果无法解析为数字，使用默认策略
                default_ratio = 0.1 if self.style == 'conservative' else 0.25
                return max(10, min(int(self.chips * default_ratio), self.chips))
            
        except Exception as e:
            print(f"Error deciding bet: {e}")
            # 发生错误时使用默认策略
            default_ratio = 0.1 if self.style == 'conservative' else 0.25
            return max(10, min(int(self.chips * default_ratio), self.chips))
        
    def decide_action(self, dealer_up_card: Card) -> str:
        """
        Use GPT to decide whether to hit or stand based on style
        Returns: 'H' for hit, 'S' for stand
        """
        # 构建游戏状态描述
        prompt = f"""
        你是一位{'保守' if self.style == 'conservative' else '激进'}的21点玩家。你需要根据当前游戏状态做出最优决策。

        游戏规则提示:
        1. A可以算1点或11点
        2. J/Q/K都算10点
        3. 爆牌(超过21点)直接输
        4. 庄家17点及以上必须停牌

        {'保守策略提示:' if self.style == 'conservative' else '激进策略提示:'}
        {'1. 优先避免爆牌\n2. 17及以上一定停牌\n3. 12-16时，庄家2-6停牌，否则要牌\n4. 尽量避免冒险' 
          if self.style == 'conservative' else 
         '1. 追求更大点数\n2. 16及以下经常要牌\n3. 即使有爆牌风险也要追求更大点数\n4. 敢于冒险'}

        当前游戏状态:
        - 你的手牌: {', '.join(str(card) for card in self.hand.cards)}
        - 手牌总点数: {self.hand.get_value()}
        - 庄家明牌: {dealer_up_card}

        请根据你的风格分析当前状态，并严格按照以下格式回复:
        1. 如果决定要牌，只回复字母'H'
        2. 如果决定停牌，只回复字母'S'
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"""你是一个{'保守' if self.style == 'conservative' else '激进'}的21点玩家。
你的任务是根据当前状态和你的风格做出决策。
{'你应该优先考虑安全，避免爆牌风险。' if self.style == 'conservative' else '你应该勇于冒险，追求更大的点数。'}
你的回复必须简洁，只能是'H'或'S'。"""},
                    {"role": "assistant", "content": "明白。我会根据基本策略和概率分析做出决策，并只回复'H'或'S'。"},
                    {"role": "user", "content": "手牌: KING of ♠, FIVE of ♣\n庄家明牌: SIX of ♥"},
                    {"role": "assistant", "content": "S"},
                    {"role": "user", "content": "手牌: ACE of ♥, FIVE of ♣\n庄家明牌: TEN of ♦"},
                    {"role": "assistant", "content": "H"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1,
                temperature=0.1
            )
            
            # 获取决策
            decision = response.choices[0].message.content.strip().upper()
            
            # 确保返回合法的决策
            if decision and decision[0] in ['H', 'S']:
                return decision[0]
            
            # 如果GPT返回的不是有效决策，使用基本策略
            return super().decide_action(dealer_up_card)
            
        except Exception as e:
            print(f"Error using GPT API: {e}")
            # 发生错误时使用基本策略
            return super().decide_action(dealer_up_card)
