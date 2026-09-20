"""通过 SDK 的模拟传输验证真实 API 入口与产物，不发起外部请求。"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from artifacts import new_run
from config import Settings
from openai_model import OpenAIModel
from shared import FIXED_SOURCE
from live_run import run_stage


def sdk_model(stage):
    import httpx2 as httpx
    from openai import OpenAI
    index = 0

    def handle(request):
        nonlocal index
        payload = json.loads(request.content)
        index += 1
        if stage == 'v0':
            message = {'role': 'assistant', 'content': '算术平均值是总和除以个数。'}
        elif stage == 'v1':
            if index == 1:
                message = call('read_file', {'path': 'notes.txt'}, index)
            else:
                assert payload['messages'][-1]['role'] == 'tool'
                message = {'role': 'assistant', 'content': '本周完成了工具接入与循环日志。'}
        elif index == 1:
            message = call('read_file', {'path': 'stats.py'}, index)
        elif index == 2:
            message = call('write_file', {'path': 'stats.py', 'content': FIXED_SOURCE}, index)
        elif index == 3:
            message = call('check_tests', {}, index)
        elif stage == 'v2':
            message = {'role': 'assistant', 'content': '已修复并通过检查。'}
        else:
            message = call('finish', {'summary': '已修复并通过检查。'}, index)
        return httpx.Response(200, json={
            'id': 'test-response', 'object': 'chat.completion', 'created': 1,
            'model': 'test-model', 'choices': [{'index': 0, 'finish_reason': 'tool_calls' if message.get('tool_calls') else 'stop', 'message': message}],
        })

    client = OpenAI(base_url='https://example.invalid/v1', api_key='test-key', max_retries=0,
                    http_client=httpx.Client(transport=httpx.MockTransport(handle)))
    return OpenAIModel(client, 'test-model')


def call(name, arguments, index):
    return {'role': 'assistant', 'content': None, 'tool_calls': [{
        'id': f'call-{index}', 'type': 'function',
        'function': {'name': name, 'arguments': json.dumps(arguments, ensure_ascii=False)},
    }]}


class LiveEntrypointTests(unittest.TestCase):
    def test_sdk_entrypoints_save_complete_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            def create(stage):
                return new_run(stage, temporary)
            for stage in ('v1', 'v2', 'v3', 'v4'):
                with self.subTest(stage=stage), patch('live_run.OpenAIModel.from_env', return_value=sdk_model(stage)), patch('live_run.new_run', side_effect=create), contextlib.redirect_stdout(io.StringIO()):
                    result, directory = run_stage(stage)
                    self.assertEqual(result['status'], 'stopped')
                    for name in ('requests.jsonl', 'responses.jsonl', 'messages.json', 'trace.jsonl', 'answer.md', 'changes.diff', 'result.json', 'report.md'):
                        self.assertTrue((directory / name).is_file(), name)
                    self.assertNotIn('test-key', (directory / 'requests.jsonl').read_text())
                    if stage != 'v1':
                        self.assertTrue(result['acceptance']['passed'])
            with patch('live_run.OpenAIModel.from_env', return_value=sdk_model('v1')), patch('live_run.new_run', side_effect=create), contextlib.redirect_stdout(io.StringIO()):
                result, directory = run_stage('v1', manual=True)
                self.assertEqual(result['model_calls'], 2)
                requests = [json.loads(line)['request'] for line in (directory / 'requests.jsonl').read_text().splitlines()]
                self.assertEqual(requests[0]['tool_choice']['function']['name'], 'read_file')
                self.assertEqual(requests[1]['tool_choice'], 'none')
            from build_report import build_report
            with contextlib.redirect_stdout(io.StringIO()):
                rows = build_report(temporary)
            self.assertEqual(len(rows), 5)
            self.assertTrue((Path(temporary) / 'comparison.md').exists())

    def test_v0_uses_sdk_and_saves_original_response(self):
        import v0_model_call
        with tempfile.TemporaryDirectory() as temporary, patch('v0_model_call.load_settings', return_value=Settings('https://example.invalid/v1', 'test-key', 'test-model')), patch('v0_model_call.make_client', return_value=sdk_model('v0').client), patch('v0_model_call.new_run', side_effect=lambda stage: new_run(stage, temporary)), contextlib.redirect_stdout(io.StringIO()):
            v0_model_call.main()
            directory = next(Path(temporary).glob('v0-*'))
            result = json.loads((directory / 'result.json').read_text())
            self.assertEqual(result['model_calls'], 1)
            self.assertEqual(result['reason'], 'response_received')
            self.assertIn('算术平均值', (directory / 'answer.md').read_text())


if __name__ == '__main__':
    unittest.main()
