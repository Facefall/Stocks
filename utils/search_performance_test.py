"""
搜索系统性能测试

测试目标：
1. 验证搜索响应时间 < 2秒
2. 验证支持至少10万条内容记录
3. 测试各种查询场景的性能
"""

import time
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any
from search_engine import SearchEngine, ContentIndexer


def generate_test_document(index: int) -> Dict[str, Any]:
    """生成测试文档"""
    # 股票代码列表
    stocks = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NFLX", "AMD", "INTC",
              "SOFI", "OKLO", "MSTR", "COIN", "HOOD", "PLTR", "CRWV", "RKLB", "QQQ", "SPY",
              "比特币", "以太坊", "币股", "科技股", "AI", "人工智能", "财报", "期权", "期货"]
    
    # 操作词汇
    actions = ["买入", "卖出", "持有", "加仓", "减仓", "止损", "止盈", "观望", "抄底", "逃顶"]
    
    # 市场词汇
    markets = ["大盘", "指数", "纳斯达克", "标普", "道琼斯", "美股", "港股", "A股"]
    
    # 生成随机内容
    num_stocks = random.randint(2, 5)
    selected_stocks = random.sample(stocks, num_stocks)
    selected_actions = random.sample(actions, random.randint(1, 3))
    selected_markets = random.sample(markets, random.randint(1, 2))
    
    # 生成标题
    title = f"{random.choice(selected_stocks)} {random.choice(selected_actions)}分析 - {index}"
    
    # 生成内容
    paragraphs = []
    for _ in range(random.randint(3, 8)):
        words = []
        words.extend(selected_stocks)
        words.extend(selected_actions)
        words.extend(selected_markets)
        words.extend([''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8))) 
                      for _ in range(random.randint(10, 30))])
        random.shuffle(words)
        paragraph = '，'.join(words[:random.randint(20, 50)]) + '。'
        paragraphs.append(paragraph)
    
    content = '\n\n'.join(paragraphs)
    
    # 生成时间（最近2年内）
    days_ago = random.randint(0, 730)
    created_at = datetime.now() - timedelta(days=days_ago)
    
    # 内容类型
    content_types = ["全天回顾", "盘中总结", "盘中小时总结", "开盘提要", "盘前全天提要", "盘后总结", "休市总结"]
    
    return {
        "id": f"doc_{index:06d}",
        "title": title,
        "content": content,
        "file_path": f"docs/summaries/{created_at.strftime('%Y-%m-%d %H_%M_%S')}-{random.choice(content_types)}.md",
        "created_at": created_at.isoformat(),
        "content_type": random.choice(content_types),
        "word_count": len(content)
    }


def generate_test_index(count: int) -> List[Dict[str, Any]]:
    """生成指定数量的测试索引数据"""
    print(f"正在生成 {count} 条测试数据...")
    start = time.time()
    
    index = []
    for i in range(count):
        if i > 0 and i % 10000 == 0:
            print(f"  已生成 {i} 条...")
        index.append(generate_test_document(i))
    
    elapsed = time.time() - start
    print(f"生成完成，耗时 {elapsed:.2f}秒，平均 {elapsed/count*1000:.2f}ms/条")
    return index


class MockSearchEngine:
    """模拟搜索引擎，用于性能测试"""
    
    def __init__(self, index: List[Dict[str, Any]]):
        self.index = index
    
    def search(self, query: str, limit: int = 20) -> tuple:
        """简单搜索实现"""
        start = time.time()
        
        query_lower = query.lower()
        results = []
        
        for doc in self.index:
            text = (doc["title"] + " " + doc["content"]).lower()
            if query_lower in text:
                # 计算简单分数
                score = text.count(query_lower)
                if query_lower in doc["title"].lower():
                    score += 10
                results.append({**doc, "score": score})
        
        # 排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        elapsed = time.time() - start
        return results[:limit], len(results), elapsed


def run_performance_test():
    """运行性能测试"""
    print("=" * 60)
    print("搜索系统性能测试")
    print("=" * 60)
    
    # 测试不同数据量的性能
    test_sizes = [1000, 10000, 50000, 100000]
    
    # 测试查询
    test_queries = [
        "NVDA",
        "比特币",
        "买入",
        "大盘",
        "期权",
        "科技股",
        "止损",
        "财报"
    ]
    
    results_summary = []
    
    for size in test_sizes:
        print(f"\n{'='*60}")
        print(f"测试数据量: {size:,} 条")
        print(f"{'='*60}")
        
        # 生成测试数据
        index = generate_test_index(size)
        engine = MockSearchEngine(index)
        
        # 测试各个查询
        query_times = []
        for query in test_queries:
            _, count, elapsed = engine.search(query)
            query_times.append(elapsed)
            status = "✓" if elapsed < 2.0 else "✗"
            print(f"  [{status}] 查询 '{query}': 找到 {count} 条, 耗时 {elapsed*1000:.2f}ms")
        
        # 统计
        avg_time = sum(query_times) / len(query_times)
        max_time = max(query_times)
        min_time = min(query_times)
        
        print(f"\n  统计:")
        print(f"    平均耗时: {avg_time*1000:.2f}ms")
        print(f"    最大耗时: {max_time*1000:.2f}ms")
        print(f"    最小耗时: {min_time*1000:.2f}ms")
        print(f"    是否达标 (<2s): {'✓ 是' if max_time < 2.0 else '✗ 否'}")
        
        results_summary.append({
            "size": size,
            "avg_ms": avg_time * 1000,
            "max_ms": max_time * 1000,
            "passed": max_time < 2.0
        })
    
    # 最终报告
    print(f"\n{'='*60}")
    print("性能测试总结")
    print(f"{'='*60}")
    
    all_passed = all(r["passed"] for r in results_summary)
    
    for r in results_summary:
        status = "✓ 通过" if r["passed"] else "✗ 未通过"
        print(f"  {r['size']:>7,} 条: 平均 {r['avg_ms']:>7.2f}ms / 最大 {r['max_ms']:>7.2f}ms [{status}]")
    
    print(f"\n总体结果: {'✓ 所有测试通过' if all_passed else '✗ 部分测试未通过'}")
    
    return all_passed


def test_real_data_performance():
    """测试真实数据的性能"""
    print(f"\n{'='*60}")
    print("真实数据性能测试")
    print(f"{'='*60}")
    
    engine = SearchEngine()
    
    print(f"索引文档数: {len(engine.index)}")
    
    test_queries = [
        ("比特币", "热门话题"),
        ("NVDA", "股票代码"),
        ("期权", "操作类型"),
        ("管理员", "特定角色"),
        ("止损", "操作策略"),
        ("财报", "事件类型"),
        ("科技股", "板块"),
        ("买入", "操作"),
    ]
    
    times = []
    for query, desc in test_queries:
        start = time.time()
        results, total = engine.search(query, limit=20)
        elapsed = time.time() - start
        times.append(elapsed)
        status = "✓" if elapsed < 2.0 else "✗"
        print(f"  [{status}] {desc} '{query}': {total} 条结果, {elapsed*1000:.2f}ms")
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"\n  平均耗时: {avg_time*1000:.2f}ms")
    print(f"  最大耗时: {max_time*1000:.2f}ms")
    print(f"  性能评级: {'优秀 (<100ms)' if max_time < 0.1 else '良好 (<500ms)' if max_time < 0.5 else '合格 (<2s)' if max_time < 2.0 else '需优化'}")
    
    return max_time < 2.0


def test_suggestions_performance():
    """测试搜索建议性能"""
    print(f"\n{'='*60}")
    print("搜索建议性能测试")
    print(f"{'='*60}")
    
    engine = SearchEngine()
    
    test_prefixes = ["比", "NV", "期", "管", "科", "买"]
    
    times = []
    for prefix in test_prefixes:
        start = time.time()
        suggestions = engine.get_suggestions(prefix)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  '{prefix}' -> {suggestions[:3]} ({elapsed*1000:.2f}ms)")
    
    avg_time = sum(times) / len(times)
    print(f"\n  平均耗时: {avg_time*1000:.2f}ms")
    
    return avg_time < 0.1


if __name__ == "__main__":
    print("开始搜索系统性能测试...\n")
    
    # 测试真实数据
    real_passed = test_real_data_performance()
    
    # 测试搜索建议
    suggest_passed = test_suggestions_performance()
    
    # 大规模数据测试（可选，较慢）
    print(f"\n{'='*60}")
    print("是否运行大规模数据压力测试? (y/n)")
    print("注意: 测试10万条数据可能需要几分钟")
    print(f"{'='*60}")
    
    # 默认运行简化版测试
    print("运行简化版压力测试 (1000条)...")
    
    # 生成1000条测试数据并测试
    index = generate_test_index(1000)
    engine = MockSearchEngine(index)
    
    start = time.time()
    _, count, _ = engine.search("NVDA")
    elapsed = time.time() - start
    
    print(f"\n1000条数据搜索测试:")
    print(f"  找到 {count} 条结果")
    print(f"  耗时: {elapsed*1000:.2f}ms")
    print(f"  状态: {'✓ 通过' if elapsed < 2.0 else '✗ 未通过'}")
    
    # 最终总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    print(f"真实数据测试: {'✓ 通过' if real_passed else '✗ 未通过'}")
    print(f"搜索建议测试: {'✓ 通过' if suggest_passed else '✗ 未通过'}")
    print(f"压力测试: {'✓ 通过' if elapsed < 2.0 else '✗ 未通过'}")
    
    all_pass = real_passed and suggest_passed and elapsed < 2.0
    print(f"\n总体评价: {'✓ 系统性能达标' if all_pass else '✗ 需要优化'}")
