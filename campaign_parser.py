import re
import json
from typing import Dict, List, Any, Optional


class CampaignParser:
    def __init__(self):
        self.activity_type_keywords = {
            "launchpool": ["launchpool", "质押挖矿", "stake to earn"],
            "learn_earn": ["learn & earn", "learn and earn", "答题", "学习赚币"],
            "trading_competition": ["trading competition", "交易大赛", "交易挑战", "排名赛"],
            "airdrop": ["airdrop", "空投"],
            "lottery": ["抽奖", "lottery", "raffle"],
            "deposit": ["充值", "deposit campaign"],
            "referral": ["邀请", "referral"],
            "staking": ["staking", "earn", "锁仓", "定期", "活期", "质押"]
        }

    def parse(self, raw_text: str) -> Dict[str, Any]:
        activity_name = self.extract_activity_name(raw_text)
        activity_type = self.detect_activity_type(raw_text)
        time_info = self.extract_time_info(raw_text)
        requirements = self.extract_requirements(raw_text)
        rewards = self.extract_rewards(raw_text)
        restrictions = self.extract_restrictions(raw_text)
        actions = self.extract_actions(raw_text)

        result = {
            "activity_name": activity_name,
            "activity_type": activity_type,
            "time_info": time_info,
            "requirements": requirements,
            "rewards": rewards,
            "restrictions": restrictions,
            "actions": actions,
            "plans": self.generate_plans(
                activity_type=activity_type,
                requirements=requirements,
                rewards=rewards,
                restrictions=restrictions,
                actions=actions
            ),
            "risk_notes": self.generate_risk_notes(raw_text, restrictions),
            "missing_items": self.find_missing_items(
                activity_name, activity_type, time_info, requirements, rewards
            ),
            "summary": ""
        }

        result["summary"] = self.render_markdown_summary(result)
        return result

    def extract_activity_name(self, text: str) -> str:
        patterns = [
            r"活动名称[:：]\s*(.+)",
            r"^\s*#\s*(.+)",
            r"^\s*##\s*(.+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()
        return "未识别活动名称"

    def detect_activity_type(self, text: str) -> str:
        lower_text = text.lower()
        for activity_type, keywords in self.activity_type_keywords.items():
            for keyword in keywords:
                if keyword.lower() in lower_text:
                    return activity_type
        return "unknown"

    def extract_time_info(self, text: str) -> Dict[str, Optional[str]]:
        time_patterns = {
            "start_time": [
                r"开始时间[:：]\s*(.+)",
                r"活动开始[:：]\s*(.+)"
            ],
            "end_time": [
                r"结束时间[:：]\s*(.+)",
                r"活动结束[:：]\s*(.+)"
            ]
        }

        result = {"start_time": None, "end_time": None}
        for field, patterns in time_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    result[field] = match.group(1).strip()
                    break
        return result

    def extract_requirements(self, text: str) -> List[str]:
        keywords = ["参与条件", "参与门槛", "资格要求", "要求", "条件"]
        return self.extract_section_lines(text, keywords)

    def extract_rewards(self, text: str) -> List[str]:
        keywords = ["奖励", "奖励机制", "奖池", "奖品", "收益", "APR", "年化"]
        return self.extract_section_lines(text, keywords)

    def extract_restrictions(self, text: str) -> List[str]:
        keywords = ["限制", "限制条件", "注意事项", "不适用", "仅限", "排除"]
        return self.extract_section_lines(text, keywords)

    def extract_actions(self, text: str) -> List[str]:
        keywords = ["参与步骤", "操作步骤", "如何参与", "完成以下任务", "任务要求"]
        return self.extract_section_lines(text, keywords)

    def extract_section_lines(self, text: str, section_keywords: List[str]) -> List[str]:
        lines = [line.strip("•-  \t") for line in text.splitlines() if line.strip()]
        hits = []
        for line in lines:
            if any(keyword in line for keyword in section_keywords):
                hits.append(line)
        return hits[:10]

    def generate_plans(
        self,
        activity_type: str,
        requirements: List[str],
        rewards: List[str],
        restrictions: List[str],
        actions: List[str]
    ) -> Dict[str, Any]:
        return {
            "low_threshold_plan": {
                "goal": "以最低成本获得参与资格",
                "steps": [
                    "确认是否完成 KYC、账户验证等基础门槛",
                    "仅完成官方要求的最低必要动作",
                    "避免额外锁仓或高频交易带来的成本"
                ]
            },
            "standard_plan": {
                "goal": "在成本与收益之间取得平衡",
                "steps": [
                    "完成全部基础资格验证",
                    "按官方推荐流程完成主要任务",
                    "在合理资金规模下参与，控制风险"
                ]
            },
            "optimal_plan": {
                "goal": "在规则允许范围内提升收益效率或中奖效率",
                "steps": [
                    "优先识别奖励分配核心变量",
                    "选择边际收益更高的参与路径",
                    "规避低效率动作，把资源集中在高权重环节"
                ]
            }
        }

    def generate_risk_notes(self, raw_text: str, restrictions: List[str]) -> List[str]:
        notes = [
            "请确认活动是否有地区限制、KYC限制或资产快照要求",
            "请确认奖励发放时间、解锁时间和是否支持提前退出",
            "如涉及 APR、收益率、中奖概率，实际结果可能因参与人数变化而改变"
        ]
        if restrictions:
            notes.append("检测到限制条件，请重点复核官方原文")
        return notes

    def find_missing_items(
        self,
        activity_name: str,
        activity_type: str,
        time_info: Dict[str, Optional[str]],
        requirements: List[str],
        rewards: List[str]
    ) -> List[str]:
        missing = []
        if activity_name == "未识别活动名称":
            missing.append("活动名称")
        if activity_type == "unknown":
            missing.append("活动类型")
        if not time_info.get("start_time"):
            missing.append("开始时间")
        if not time_info.get("end_time"):
            missing.append("结束时间")
        if not requirements:
            missing.append("参与门槛")
        if not rewards:
            missing.append("奖励机制")
        return missing

    def render_markdown_summary(self, result: Dict[str, Any]) -> str:
        return f"""
# 活动解析结果

## 活动识别
- 活动名称：{result['activity_name']}
- 活动类型：{result['activity_type']}

## 时间信息
- 开始时间：{result['time_info'].get('start_time') or '待确认'}
- 结束时间：{result['time_info'].get('end_time') or '待确认'}

## 规则拆解
- 参与门槛：{'; '.join(result['requirements']) if result['requirements'] else '待补充'}
- 奖励机制：{'; '.join(result['rewards']) if result['rewards'] else '待补充'}
- 限制条件：{'; '.join(result['restrictions']) if result['restrictions'] else '未识别'}
- 操作步骤：{'; '.join(result['actions']) if result['actions'] else '待补充'}

## 用户执行路径
### 最低门槛参与法
- 目标：{result['plans']['low_threshold_plan']['goal']}
- 步骤：{'；'.join(result['plans']['low_threshold_plan']['steps'])}

### 标准参与法
- 目标：{result['plans']['standard_plan']['goal']}
- 步骤：{'；'.join(result['plans']['standard_plan']['steps'])}

### 最优参与法
- 目标：{result['plans']['optimal_plan']['goal']}
- 步骤：{'；'.join(result['plans']['optimal_plan']['steps'])}

## 风险提醒
- {'; '.join(result['risk_notes'])}

## 待确认项
- {'; '.join(result['missing_items']) if result['missing_items'] else '无'}
""".strip()


if __name__ == "__main__":
    sample_text = """
活动名称：Binance Learn & Earn 活动
开始时间：2026-03-10 08:00 UTC
结束时间：2026-03-20 08:00 UTC
参与条件：完成身份认证；阅读指定文章；答对全部问题
奖励机制：前 10000 名符合条件用户平分奖池
限制条件：部分地区不可参与
参与步骤：登录 Binance；进入活动页；完成学习与答题
"""

    parser = CampaignParser()
    output = parser.parse(sample_text)

    print(json.dumps(output, ensure_ascii=False, indent=2))
    print("\n" + "=" * 80 + "\n")
    print(output["summary"])
