"""Actual Ollama calls only: python -m unittest evaluation.tests.test_live -v."""
import unittest

from shared.model_client import ModelClient
from evaluation.runner import execute_case


class RealModelTests(unittest.TestCase):
    def test_direct_answer_and_observed_usage(self):
        client = ModelClient()
        result = execute_case(client, "direct", {
            "id": "live-add", "question": "What is 7 + 8?", "answer": "15", "kind": "number"
        })
        self.assertEqual(result["status"], "success", result)
        self.assertTrue(result["correct"], result)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(client.calls[0]["role"], "direct")
        self.assertIn("usage", client.calls[0])

    def test_actual_strategy_flows(self):
        for method in ("ps", "ltm", "rar1", "rar2"):
            with self.subTest(method=method):
                client = ModelClient()
                result = execute_case(client, method, {
                    "id": "live-apples", "question": "I have 5 apples and get 2 more. How many apples do I have?",
                    "answer": "7", "kind": "number"
                })
                self.assertEqual(result["status"], "success", result)
                self.assertTrue(result["correct"], result)
                roles = [c["role"] for c in client.calls]
                if method == "ps":
                    self.assertEqual(roles, ["ps_generate", "ps_extract"])
                elif method == "rar1":
                    self.assertEqual(roles, ["rar_joint"])
                elif method == "rar2":
                    self.assertEqual(roles, ["rar_rewrite", "rar_respond"])
                    self.assertIn("Original question:", client.calls[1]["messages"][0]["content"])
                else:
                    self.assertEqual(roles[0], "ltm_decompose")
                    self.assertEqual(roles[-1], "ltm_final")
                    self.assertGreaterEqual(len(roles), 3)
                    self.assertIn("Previous questions and answers:", client.calls[-1]["messages"][0]["content"])


if __name__ == "__main__":
    unittest.main()
