"""
Генератор отчетов по результатам валидации
"""

from typing import Dict, List
import json
from datetime import datetime
from pathlib import Path

from ..core.constants import EXPORTS_DIR
from ..core.models import NetworkPolicy

class ReportGenerator:
    """Генератор отчетов"""
    
    def __init__(self):
        self.reports_dir = EXPORTS_DIR / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_validation_report(self, results: Dict, policy: NetworkPolicy) -> Path:
        """Сгенерировать отчет по валидации"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"validation_report_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'policy_name': policy.name,
                'policy_description': policy.description,
                'zone_count': len(policy.zones),
                'rule_count': len(policy.rules),
            },
            'validation_results': results,
            'policy_summary': {
                'zones': list(policy.zones.keys()),
                'success_rate': results.get('summary', {}).get('success_rate', '0%'),
                'overall_status': results.get('summary', {}).get('overall_status', 'unknown'),
            },
            'recommendations': results.get('summary', {}).get('recommendations', []),
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_html_report(self, results: Dict, policy: NetworkPolicy) -> Path:
        """Сгенерировать HTML отчет"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.html"
        filepath = self.reports_dir / filename
        
        html = self._create_html_template(results, policy)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath
    
    def _create_html_template(self, results: Dict, policy: NetworkPolicy) -> str:
        """Создать HTML шаблон отчета"""
        summary = results.get('summary', {})
        
        status_color = {
            'passed': 'green',
            'warning': 'orange',
            'failed': 'red',
        }.get(summary.get('overall_status', 'unknown'), 'gray')
        
        return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет по валидации ZeroTrust</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .status {{ color: {status_color}; font-weight: bold; }}
        .card {{ background: #f5f5f5; padding: 20px; margin: 15px 0; border-radius: 8px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Отчет по валидации ZeroTrust</h1>
        <p>Политика: <strong>{policy.name}</strong></p>
        <p>Сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Общий статус: <span class="status">{summary.get('overall_status', 'unknown').upper()}</span></p>
    </div>
    
    <div class="card">
        <h2>Сводка</h2>
        <p>Тестов выполнено: {summary.get('total_tests', 0)}</p>
        <p>Успешно: <span class="success">{summary.get('passed_tests', 0)}</span></p>
        <p>Неудачно: <span class="error">{summary.get('failed_tests', 0)}</span></p>
        <p>Успешность: {summary.get('success_rate', '0%')}</p>
    </div>
    
    <h2>Результаты тестов</h2>
    {"".join(self._generate_test_sections(results))}
    
    <h2>Рекомендации</h2>
    <ul>
        {"".join(f"<li>{rec}</li>" for rec in summary.get('recommendations', []))}
    </ul>
    
    <h2>Информация о политике</h2>
    <table>
        <tr><th>Параметр</th><th>Значение</th></tr>
        <tr><td>Имя политики</td><td>{policy.name}</td></tr>
        <tr><td>Описание</td><td>{policy.description}</td></tr>
        <tr><td>Зоны</td><td>{len(policy.zones)}</td></tr>
        <tr><td>Правила</td><td>{len(policy.rules)}</td></tr>
        <tr><td>Дата создания</td><td>{policy.created_at.strftime('%Y-%m-%d %H:%M')}</td></tr>
    </table>
</body>
</html>
        """
    
    def _generate_test_sections(self, results: Dict) -> List[str]:
        """Сгенерировать секции с результатами тестов"""
        sections = []
        
        for test_name, test_data in results.get('tests', {}).items():
            if test_name == 'summary':
                continue
            
            passed = test_data.get('passed', 0)
            failed = test_data.get('failed', 0)
            total = passed + failed
            
            status = "✅" if failed == 0 else "⚠️" if failed < total * 0.3 else "❌"
            
            sections.append(f"""
            <div class="card">
                <h3>{status} {test_data.get('name', test_name)}</h3>
                <p>{test_data.get('description', '')}</p>
                <p>Успешно: {passed} / {total} ({passed/total*100:.1f}%)</p>
            </div>
            """)
        
        return sections
